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
import hashlib
from datetime import date, timedelta
from typing import List, Optional, Tuple

from ..models.booking import Booking, BookingStatus, BookingTargetType
from ..models.user import User
from ..repositories.booking_repository import BookingRepository
from ..repositories.room_repository import RoomRepository
from ..repositories.seat_repository import SeatRepository
from ..repositories.asset_repository import AssetRepository
from ..services.user_service import AuthError
from ..utils.time import parse_iso_datetime, utc_now


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
        seat_repository: SeatRepository = None,
        asset_repository: AssetRepository = None,
    ):
        self._booking_repo = booking_repository or BookingRepository()
        self._room_repo = room_repository or RoomRepository()
        self._seat_repo = seat_repository or SeatRepository()
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
        seat_id: str = None,
        access_password: str = "",
        invitation_emails: list = None,
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

        # 2. Zielobjekt prüfen und bei Raum-Sitzplatzbuchung Ziel auf Sitzplatz normalisieren
        target_id, target_type, room_id, auto_assigned_seat = self._resolve_booking_target(
            target_id=target_id,
            target_type=target_type,
            start_time=start_time,
            end_time=end_time,
            seat_id=seat_id,
        )

        # 3. Konflikte prüfen ← KERNLOGIK
        conflicts = self._find_booking_conflicts(target_id, target_type, start_time, end_time)
        if target_type == BookingTargetType.SEAT:
            conflicts.extend(self._find_user_seat_conflicts(user.id, start_time, end_time))
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
            room_id=room_id,
            auto_assigned_seat=auto_assigned_seat,
            access_password_hash=self._hash_access_password(access_password),
            invitation_emails=self._normalize_invitation_emails(invitation_emails),
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

    def search_bookings(
        self,
        requesting_user: User,
        user_id: str = None,
        status: str = None,
        target_type: str = None,
        target_id: str = None,
        start: str = None,
        end: str = None,
        q: str = "",
    ) -> List[Booking]:
        """
        Backend-Such- und Filterlogik für Buchungen.

        Normale Nutzer dürfen nur eigene Buchungen sehen; Admins können optional
        nach user_id filtern oder alle Buchungen durchsuchen.
        """
        if not requesting_user.is_admin():
            user_id = requesting_user.id

        bookings = self._booking_repo.find_all()
        if user_id:
            bookings = [b for b in bookings if b.user_id == user_id]
        if status:
            try:
                booking_status = BookingStatus(status)
            except ValueError:
                raise ValueError(f"Unbekannter Buchungsstatus: '{status}'.")
            bookings = [b for b in bookings if b.status == booking_status]
        if target_type:
            try:
                booking_target_type = BookingTargetType(target_type)
            except ValueError:
                raise ValueError(f"Unbekannter Buchungstyp: '{target_type}'.")
            bookings = [b for b in bookings if b.target_type == booking_target_type]
        if target_id:
            bookings = [b for b in bookings if b.target_id == target_id or b.room_id == target_id]
        if start and end:
            self._validate_time_range(start, end, allow_past=True)
            bookings = [b for b in bookings if b.overlaps_with(start, end)]
        if q:
            query = q.lower().strip()
            bookings = [
                b for b in bookings
                if query in b.title.lower()
                or query in (b.target_id or "").lower()
                or query in (b.room_id or "").lower()
            ]
        return bookings

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
        self._validate_target_exists(target_id, target_type)

        if target_type == BookingTargetType.ROOM:
            seats = self._seat_repo.find_by_room(target_id)
            if seats:
                seat = self._find_available_seat(target_id, start_time, end_time)
                if seat:
                    return True, []
                return False, self._find_room_seat_conflicts(target_id, start_time, end_time)

        conflicts = self._find_booking_conflicts(target_id, target_type, start_time, end_time)
        return len(conflicts) == 0, conflicts

    def get_time_block_schedule(
        self,
        target_id: str,
        target_type: BookingTargetType,
        start_date: str = "",
        days: int = 7,
        first_hour: int = 8,
        last_hour: int = 22,
    ) -> List[dict]:
        """Erzeugt eine Kalenderansicht mit stündlichen Buchungsblöcken."""
        self._validate_target_exists(target_id, target_type)
        try:
            current_date = date.fromisoformat(start_date) if start_date else date.today()
        except ValueError:
            raise ValueError("start_date muss im Format YYYY-MM-DD angegeben werden.")

        day_count = max(1, min(int(days or 7), 31))
        schedule = []
        for day_offset in range(day_count):
            block_date = current_date + timedelta(days=day_offset)
            slots = []
            booked_blocks = 0
            unavailable_blocks = 0

            for hour in range(first_hour, last_hour):
                block_start = f"{block_date.isoformat()}T{hour:02d}:00:00"
                block_end = f"{block_date.isoformat()}T{hour + 1:02d}:00:00"
                conflicts = self._find_booking_conflicts(
                    target_id,
                    target_type,
                    block_start,
                    block_end,
                )
                available = self._is_block_available(
                    target_id,
                    target_type,
                    block_start,
                    block_end,
                )
                if conflicts:
                    booked_blocks += 1
                if not available:
                    unavailable_blocks += 1
                slots.append({
                    "start_time": block_start,
                    "end_time": block_end,
                    "label": f"{hour:02d}:00-{hour + 1:02d}:00",
                    "available": available,
                    "booked": bool(conflicts),
                    "conflict_count": len(conflicts),
                })

            total_blocks = len(slots)
            if booked_blocks == 0:
                status = "free"
            elif unavailable_blocks == total_blocks:
                status = "full"
            else:
                status = "partial"
            schedule.append({
                "date": block_date.isoformat(),
                "status": status,
                "booked_blocks": booked_blocks,
                "available_blocks": total_blocks - unavailable_blocks,
                "total_blocks": total_blocks,
                "slots": slots,
            })
        return schedule

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
            seats = self._seat_repo.find_by_room(room.id)
            if seats:
                if self._find_available_seat(room.id, start_time, end_time):
                    available.append(room.id)
            elif not self._find_booking_conflicts(
                room.id, BookingTargetType.ROOM, start_time, end_time
            ):
                available.append(room.id)
        return available

    def get_available_seats(
        self, room_id: str, start_time: str, end_time: str
    ) -> List[str]:
        """Gibt IDs aller freien Sitzplätze eines Raums zurück."""
        self._validate_time_range(start_time, end_time)
        room = self._room_repo.find_by_id(room_id)
        if not room or not room.is_active:
            raise ValueError(f"Raum mit ID '{room_id}' nicht gefunden oder nicht verfügbar.")
        return [
            seat.id
            for seat in self._seat_repo.find_by_room(room_id)
            if not self._find_booking_conflicts(
                seat.id, BookingTargetType.SEAT, start_time, end_time
            )
        ]

    def get_available_seat_ids(
        self, start_time: str, end_time: str
    ) -> List[str]:
        """Gibt IDs aller freien Sitzplätze zurück."""
        self._validate_time_range(start_time, end_time)
        return [
            seat.id
            for seat in self._seat_repo.find_active()
            if not self._find_booking_conflicts(
                seat.id, BookingTargetType.SEAT, start_time, end_time
            )
        ]

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

    def _validate_time_range(self, start_time: str, end_time: str, allow_past: bool = False) -> None:
        """
        Validiert den Buchungszeitraum.

        Regeln:
            - Beide Zeitangaben müssen im ISO-8601 Format vorliegen
            - start_time muss vor end_time liegen
            - Buchungen in der Vergangenheit sind nicht erlaubt
        """
        try:
            start_dt = parse_iso_datetime(start_time)
            end_dt = parse_iso_datetime(end_time)
        except (ValueError, TypeError):
            raise ValueError(
                "Ungültiges Zeitformat. Bitte ISO-8601 verwenden (z. B. '2026-06-15T09:00:00')."
            )

        if start_dt >= end_dt:
            raise ValueError("Die Startzeit muss vor der Endzeit liegen.")

        if not allow_past and start_dt < utc_now():
            raise ValueError("Buchungen können nicht in der Vergangenheit erstellt werden.")

    def _validate_target_exists(
        self, target_id: str, target_type: BookingTargetType
    ) -> None:
        """Stellt sicher, dass das Buchungsziel (Raum/Asset/Sitzplatz) existiert und aktiv ist."""
        if target_type == BookingTargetType.ROOM:
            obj = self._room_repo.find_by_id(target_id)
            if not obj or not obj.is_active:
                raise ValueError(f"Raum mit ID '{target_id}' nicht gefunden oder nicht verfügbar.")
        elif target_type == BookingTargetType.ASSET:
            obj = self._asset_repo.find_by_id(target_id)
            if not obj or not obj.is_active:
                raise ValueError(f"Asset mit ID '{target_id}' nicht gefunden oder nicht verfügbar.")
        elif target_type == BookingTargetType.SEAT:
            obj = self._seat_repo.find_by_id(target_id)
            if not obj or not obj.is_active:
                raise ValueError(f"Sitzplatz mit ID '{target_id}' nicht gefunden oder nicht verfügbar.")
            room = self._room_repo.find_by_id(obj.room_id)
            if not room or not room.is_active:
                raise ValueError("Der zugehörige Raum ist nicht verfügbar.")
        else:
            raise ValueError(f"Unbekannter Buchungstyp: '{target_type}'.")

    def _resolve_booking_target(
        self,
        target_id: str,
        target_type: BookingTargetType,
        start_time: str,
        end_time: str,
        seat_id: str = None,
    ) -> Tuple[str, BookingTargetType, str, bool]:
        """
        Normalisiert Raum-Sitzplatzbuchungen.

        Räume ohne Sitzplatzdaten werden wie bisher als Raum gebucht.
        Räume mit Sitzplätzen werden auf einen expliziten oder automatisch freien
        Sitzplatz abgebildet, damit Sitzplätze als eigene Entität buchbar sind.
        """
        self._validate_target_exists(target_id, target_type)

        if target_type == BookingTargetType.SEAT:
            seat = self._seat_repo.find_by_id(target_id)
            return seat.id, BookingTargetType.SEAT, seat.room_id, False

        if target_type != BookingTargetType.ROOM:
            return target_id, target_type, "", False

        room = self._room_repo.find_by_id(target_id)
        is_shared_desk = room and getattr(room, "room_type", "seminarraum") == "shared_desk"

        if seat_id:
            if not is_shared_desk:
                raise ValueError("Sitzplätze können nur in Shared-Desk-Räumen separat gebucht werden.")
            seat = self._seat_repo.find_by_id(seat_id)
            if not seat or not seat.is_active or seat.room_id != target_id:
                raise ValueError("Der angegebene Sitzplatz gehört nicht zum Raum oder ist nicht verfügbar.")
            return seat.id, BookingTargetType.SEAT, target_id, False

        seats = self._seat_repo.find_by_room(target_id)
        if not seats or not is_shared_desk:
            return target_id, BookingTargetType.ROOM, "", False

        seat = self._find_available_seat(target_id, start_time, end_time)
        if not seat:
            raise BookingConflictError(
                "Für den gewünschten Zeitraum ist kein Sitzplatz in diesem Raum verfügbar.",
                conflicts=self._find_room_seat_conflicts(target_id, start_time, end_time),
            )
        return seat.id, BookingTargetType.SEAT, target_id, True

    def _find_available_seat(self, room_id: str, start_time: str, end_time: str):
        for seat in self._seat_repo.find_by_room(room_id):
            conflicts = self._find_booking_conflicts(
                seat.id, BookingTargetType.SEAT, start_time, end_time
            )
            if not conflicts:
                return seat
        return None

    def _find_booking_conflicts(
        self,
        target_id: str,
        target_type: BookingTargetType,
        start_time: str,
        end_time: str,
    ) -> List[Booking]:
        """Prüft direkte Konflikte und Raum/Sitzplatz-Abhängigkeiten."""
        conflicts = self._booking_repo.find_conflicts(
            target_id, target_type, start_time, end_time
        )

        if target_type == BookingTargetType.SEAT:
            seat = self._seat_repo.find_by_id(target_id)
            if seat:
                conflicts.extend(
                    self._booking_repo.find_conflicts(
                        seat.room_id, BookingTargetType.ROOM, start_time, end_time
                    )
                )
        elif target_type == BookingTargetType.ROOM:
            conflicts.extend(self._find_room_seat_conflicts(target_id, start_time, end_time))

        return conflicts

    def verify_booking_access(self, booking_id: str, access_password: str) -> bool:
        """Prüft das Passwort einer geschützten Seminarraumbuchung."""
        booking = self._booking_repo.find_by_id(booking_id)
        if not booking or not booking.access_password_hash:
            return False
        return booking.access_password_hash == self._hash_access_password(access_password)

    def get_active_room_occupancy(self, requesting_user: User) -> List[dict]:
        """Admin-Übersicht: aktive Personen/Buchungen je Raum."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können die Raumbelegung einsehen.")

        occupancy = []
        for booking in self._booking_repo.find_active():
            room_id = booking.room_id
            if booking.target_type == BookingTargetType.ROOM:
                room_id = booking.target_id
            elif booking.target_type == BookingTargetType.SEAT and not room_id:
                seat = self._seat_repo.find_by_id(booking.target_id)
                room_id = seat.room_id if seat else ""
            if not room_id:
                continue
            room = self._room_repo.find_by_id(room_id)
            occupancy.append({
                "room_id": room_id,
                "room_name": room.name if room else "",
                "booking_id": booking.id,
                "user_id": booking.user_id,
                "title": booking.title,
                "target_type": booking.target_type.value,
                "target_id": booking.target_id,
                "start_time": booking.start_time,
                "end_time": booking.end_time,
                "status": booking.status.value,
            })
        return occupancy

    def _hash_access_password(self, access_password: str) -> str:
        if not access_password:
            return ""
        return hashlib.sha256(access_password.encode("utf-8")).hexdigest()

    def _normalize_invitation_emails(self, invitation_emails: list) -> List[str]:
        if not invitation_emails:
            return []
        cleaned = []
        for email in invitation_emails:
            value = str(email).strip().lower()
            if value and "@" in value and value not in cleaned:
                cleaned.append(value)
        return cleaned

    def _find_user_seat_conflicts(
        self, user_id: str, start_time: str, end_time: str
    ) -> List[Booking]:
        """Verhindert, dass ein Nutzer parallel mehrere Sitzplätze bucht."""
        return [
            booking for booking in self._booking_repo.find_active_by_user(user_id)
            if booking.target_type == BookingTargetType.SEAT
            and booking.overlaps_with(start_time, end_time)
        ]

    def _find_room_seat_conflicts(
        self, room_id: str, start_time: str, end_time: str
    ) -> List[Booking]:
        conflicts = []
        for seat in self._seat_repo.find_by_room(room_id):
            conflicts.extend(
                self._booking_repo.find_conflicts(
                    seat.id, BookingTargetType.SEAT, start_time, end_time
                )
            )
        return conflicts

    def _is_block_available(
        self,
        target_id: str,
        target_type: BookingTargetType,
        start_time: str,
        end_time: str,
    ) -> bool:
        if target_type == BookingTargetType.ROOM:
            room = self._room_repo.find_by_id(target_id)
            seats = self._seat_repo.find_by_room(target_id)
            if seats and room and getattr(room, "room_type", "seminarraum") == "shared_desk":
                return self._find_available_seat(target_id, start_time, end_time) is not None
        return len(self._find_booking_conflicts(target_id, target_type, start_time, end_time)) == 0
