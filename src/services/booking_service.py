"""
Service: BookingService  ← KERNLOGIK DES SYSTEMS

Verantwortlich für:
    - Erstellung von Buchungen mit Konfliktprüfung
    - Stornierung von Buchungen
    - Abfrage von Buchungen (nutzer- und objektbezogen)
    - Verfügbarkeitsprüfung für Räume und Assets

Konfliktprüfungsalgorithmus:
    Zwei Buchungen für dasselbe Zielobjekt (Raum/Asset) konfligieren,
    wenn sich ihre Zeiträume überschneiden:

        A_start < B_end  UND  A_end > B_start

    Dieser Algorithmus ist in Booking.overlaps_with() (Model-Ebene)
    und BookingRepository.find_conflicts() (Repository-Ebene) implementiert.
    Der Service orchestriert die Prüfung und entscheidet über Genehmigung
    oder Ablehnung der Buchung.

Skalierungshinweis:
    Bei einer Datenbankimplementierung würde find_conflicts() durch eine
    SQL-Query mit Range-Overlap ersetzt:
        WHERE target_id = :id
          AND status = 'active'
          AND start_time < :end_time
          AND end_time > :start_time
    Für sehr hohe Last: optimistische Sperren (Optimistic Locking)
    oder Datenbankebenen-Transaktionen.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from ..models.booking import Booking, BookingStatus, BookingTargetType
from ..models.user import User
from ..repositories.booking_repository import BookingRepository
from ..repositories.room_repository import RoomRepository
from ..repositories.asset_repository import AssetRepository
from ..services.user_service import AuthError


class BookingConflictError(Exception):
    """Wird geworfen, wenn eine Buchung mit einer bestehenden kollidiert."""
    def __init__(self, message: str, conflicts: List[Booking] = None):
        super().__init__(message)
        self.conflicts = conflicts or []


class BookingNotFoundError(Exception):
    """Wird geworfen, wenn eine angeforderte Buchung nicht existiert."""
    pass


class BookingService:
    """
    Zentrale Buchungslogik des Systems.

    Abhängigkeiten (Dependency Injection für Testbarkeit):
        - booking_repository: Datenzugriff für Buchungen
        - room_repository:    Existenzprüfung für Räume
        - asset_repository:   Existenzprüfung für Assets
    """

    def __init__(
        self,
        booking_repository: BookingRepository = None,
        room_repository: RoomRepository = None,
        asset_repository: AssetRepository = None,
    ):
        self._booking_repo = booking_repository or BookingRepository()
        self._room_repo = room_repository or RoomRepository()
        self._asset_repo = asset_repository or AssetRepository()

    # ──────────────────────────────────────────────────────────────────────────
    # Kernmethode: Buchung erstellen
    # ──────────────────────────────────────────────────────────────────────────

    def create_booking(
        self,
        user: User,
        target_id: str,
        target_type: BookingTargetType,
        start_time: str,
        end_time: str,
        title: str = "Buchung",
    ) -> Booking:
        """
        Erstellt eine neue Buchung nach erfolgreicher Konfliktprüfung.

        Ablauf:
            1. Zeitraum-Validierung (start < end, nicht in der Vergangenheit)
            2. Existenzprüfung des Zielobjekts (Raum/Asset)
            3. Konfliktprüfung via Repository
            4. Buchung speichern und zurückgeben

        Args:
            user:        Buchender Nutzer (muss eingeloggt sein)
            target_id:   ID des Raums oder Assets
            target_type: BookingTargetType.ROOM oder .ASSET
            start_time:  ISO-8601 Startzeit (z. B. "2026-06-15T09:00:00")
            end_time:    ISO-8601 Endzeit
            title:       Titel der Buchung

        Returns:
            Das erstellte Booking-Objekt

        Raises:
            ValueError:           Ungültige Eingaben oder Zielobjekt nicht gefunden
            BookingConflictError: Zeitraum bereits vergeben
        """
        # 1. Zeitraum validieren
        self._validate_time_range(start_time, end_time)

        # 2. Zielobjekt prüfen
        self._validate_target_exists(target_id, target_type)

        # 3. Konflikte prüfen ← KERNLOGIK
        conflicts = self._booking_repo.find_conflicts(
            target_id, target_type, start_time, end_time
        )
        if conflicts:
            existing = conflicts[0]
            raise BookingConflictError(
                f"Der gewünschte Zeitraum ist bereits belegt "
                f"({existing.start_time} – {existing.end_time}). "
                f"Bitte wählen Sie einen anderen Zeitraum.",
                conflicts=conflicts,
            )

        # 4. Buchung erstellen und speichern
        booking = Booking(
            id=str(uuid.uuid4()),
            user_id=user.id,
            target_id=target_id,
            target_type=target_type,
            title=title.strip() if title else "Buchung",
            start_time=start_time,
            end_time=end_time,
        )
        return self._booking_repo.save(booking)

    # ──────────────────────────────────────────────────────────────────────────
    # Buchung stornieren
    # ──────────────────────────────────────────────────────────────────────────

    def cancel_booking(self, booking_id: str, requesting_user: User) -> Booking:
        """
        Storniert eine Buchung.

        Berechtigungsregeln:
            - Nutzer können nur ihre eigenen Buchungen stornieren
            - Admins können jede Buchung stornieren

        Raises:
            BookingNotFoundError: Buchung nicht gefunden oder bereits storniert
            AuthError:            Keine Berechtigung
        """
        booking = self._booking_repo.find_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(f"Buchung '{booking_id}' nicht gefunden.")
        if not booking.is_active():
            raise BookingNotFoundError("Diese Buchung ist bereits storniert.")

        if booking.user_id != requesting_user.id and not requesting_user.is_admin():
            raise AuthError("Sie können nur Ihre eigenen Buchungen stornieren.")

        booking.status = BookingStatus.CANCELLED
        self._booking_repo.update(booking)
        return booking

    # ──────────────────────────────────────────────────────────────────────────
    # Abfragemethoden
    # ──────────────────────────────────────────────────────────────────────────

    def get_user_bookings(self, user_id: str) -> List[Booking]:
        """Gibt alle Buchungen (aktiv + storniert) eines Nutzers zurück."""
        return self._booking_repo.find_by_user(user_id)

    def get_user_active_bookings(self, user_id: str) -> List[Booking]:
        """Gibt nur aktive Buchungen eines Nutzers zurück."""
        return self._booking_repo.find_active_by_user(user_id)

    def get_all_bookings(self, requesting_user: User) -> List[Booking]:
        """Gibt alle Buchungen zurück. Nur für Admins."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können alle Buchungen einsehen.")
        return self._booking_repo.find_all()

    def get_by_id(self, booking_id: str) -> Optional[Booking]:
        return self._booking_repo.find_by_id(booking_id)

    def check_availability(
        self,
        target_id: str,
        target_type: BookingTargetType,
        start_time: str,
        end_time: str,
    ) -> Tuple[bool, List[Booking]]:
        """
        Prüft Verfügbarkeit eines Objekts für einen Zeitraum.

        Returns:
            (True, [])          → verfügbar
            (False, [conflicts]) → nicht verfügbar, mit Konfliktliste
        """
        self._validate_time_range(start_time, end_time)
        conflicts = self._booking_repo.find_conflicts(
            target_id, target_type, start_time, end_time
        )
        return len(conflicts) == 0, conflicts

    def get_available_rooms(
        self, start_time: str, end_time: str
    ) -> List[str]:
        """
        Gibt IDs aller Räume zurück, die im angegebenen Zeitraum frei sind.

        Wird in RoomService genutzt, um freie Räume anzuzeigen.
        """
        self._validate_time_range(start_time, end_time)
        all_rooms = self._room_repo.find_active()
        available = []
        for room in all_rooms:
            conflicts = self._booking_repo.find_conflicts(
                room.id, BookingTargetType.ROOM, start_time, end_time
            )
            if not conflicts:
                available.append(room.id)
        return available

    def get_available_assets(
        self, start_time: str, end_time: str
    ) -> List[str]:
        """Gibt IDs aller Assets zurück, die im Zeitraum frei sind."""
        self._validate_time_range(start_time, end_time)
        all_assets = self._asset_repo.find_active()
        available = []
        for asset in all_assets:
            conflicts = self._booking_repo.find_conflicts(
                asset.id, BookingTargetType.ASSET, start_time, end_time
            )
            if not conflicts:
                available.append(asset.id)
        return available

    # ──────────────────────────────────────────────────────────────────────────
    # Private Hilfsmethoden
    # ──────────────────────────────────────────────────────────────────────────

    def _validate_time_range(self, start_time: str, end_time: str) -> None:
        """
        Validiert den Buchungszeitraum.

        Regeln:
            - Beide Zeitangaben müssen im ISO-8601 Format vorliegen
            - start_time muss vor end_time liegen
            - Buchungen in der Vergangenheit sind nicht erlaubt
        """
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
        except (ValueError, TypeError):
            raise ValueError(
                "Ungültiges Zeitformat. Bitte ISO-8601 verwenden (z. B. '2026-06-15T09:00:00')."
            )

        if start_dt >= end_dt:
            raise ValueError("Die Startzeit muss vor der Endzeit liegen.")

        if start_dt < datetime.utcnow():
            raise ValueError("Buchungen können nicht in der Vergangenheit erstellt werden.")

    def _validate_target_exists(
        self, target_id: str, target_type: BookingTargetType
    ) -> None:
        """Stellt sicher, dass das Buchungsziel (Raum/Asset) existiert und aktiv ist."""
        if target_type == BookingTargetType.ROOM:
            obj = self._room_repo.find_by_id(target_id)
            if not obj or not obj.is_active:
                raise ValueError(f"Raum mit ID '{target_id}' nicht gefunden oder nicht verfügbar.")
        elif target_type == BookingTargetType.ASSET:
            obj = self._asset_repo.find_by_id(target_id)
            if not obj or not obj.is_active:
                raise ValueError(f"Asset mit ID '{target_id}' nicht gefunden oder nicht verfügbar.")
        else:
            raise ValueError(f"Unbekannter Buchungstyp: '{target_type}'.")
