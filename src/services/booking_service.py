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
import hmac
import secrets
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
        series_id: str = "",
        recurrence_index: int = 0,
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
        invitation_emails = self._normalize_invitation_emails(invitation_emails)
        if (access_password or invitation_emails) and target_type != BookingTargetType.ROOM:
            raise ValueError("Passwortschutz und Einladungen sind nur für Ganzraumbuchungen möglich.")
        if invitation_emails and not access_password:
            raise ValueError("Für externe Einladungen muss ein Buchungspasswort gesetzt werden.")

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
            invitation_code=self._create_invitation_code() if access_password else "",
            access_password_hash=self._create_access_password_hash(access_password),
            invitation_emails=invitation_emails,
            series_id=series_id,
            recurrence_index=recurrence_index,
        )
        return self._booking_repo.save(booking)

    def create_recurring_bookings(
        self,
        user: User,
        target_id: str,
        target_type: BookingTargetType,
        start_time: str,
        end_time: str,
        title: str = "Buchung",
        recurrence_count: int = 1,
        recurrence_interval: str = "weekly",
        seat_id: str = None,
        access_password: str = "",
        invitation_emails: list = None,
    ) -> List[Booking]:
        """Erstellt bis zu zwölf wöchentliche Termine als atomare Buchungsserie."""
        count = int(recurrence_count or 1)
        if count < 1 or count > 12:
            raise ValueError("Eine Buchungsserie darf zwischen 1 und 12 Termine enthalten.")
        if recurrence_interval != "weekly":
            raise ValueError("Aktuell werden Buchungsserien wöchentlich unterstützt.")
        if count > 1 and (access_password or invitation_emails):
            raise ValueError("Geschützte Einladungen können nur für einen einzelnen Termin erstellt werden.")
        if count == 1:
            return [self.create_booking(
                user=user, target_id=target_id, target_type=target_type,
                start_time=start_time, end_time=end_time, title=title,
                seat_id=seat_id, access_password=access_password,
                invitation_emails=invitation_emails,
            )]

        series_id = str(uuid.uuid4())
        start = parse_iso_datetime(start_time)
        end = parse_iso_datetime(end_time)
        created = []
        try:
            for index in range(count):
                offset = timedelta(weeks=index)
                created.append(self.create_booking(
                    user=user,
                    target_id=target_id,
                    target_type=target_type,
                    start_time=(start + offset).isoformat(),
                    end_time=(end + offset).isoformat(),
                    title=title,
                    seat_id=seat_id,
                    access_password=access_password,
                    invitation_emails=invitation_emails,
                    series_id=series_id,
                    recurrence_index=index + 1,
                ))
        except Exception:
            for booking in created:
                self._booking_repo.delete(booking.id)
            raise
        return created

    def suggest_alternatives(
        self,
        target_id: str,
        target_type: BookingTargetType,
        start_time: str,
        end_time: str,
        limit: int = 3,
    ) -> List[dict]:
        """Sucht die nächsten freien Zeitfenster gleicher Dauer für dasselbe Ziel."""
        start = parse_iso_datetime(start_time)
        end = parse_iso_datetime(end_time)
        duration = end - start
        suggestions = []
        candidate = start + timedelta(hours=1)
        for _ in range(14 * 24):
            if len(suggestions) >= max(1, min(limit, 6)):
                break
            candidate_end = candidate + duration
            try:
                available, _ = self.check_availability(
                    target_id, target_type, candidate.isoformat(), candidate_end.isoformat()
                )
            except (ValueError, BookingConflictError):
                available = False
            if available:
                suggestions.append({
                    "target_id": target_id,
                    "target_type": target_type.value,
                    "start_time": candidate.isoformat(),
                    "end_time": candidate_end.isoformat(),
                })
            candidate += timedelta(hours=1)
        return suggestions

    def get_utilization_stats(self, requesting_user: User, days: int = 30) -> dict:
        """Kompakte Admin-Kennzahlen für den gewählten Rückblickzeitraum."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können Auslastungsdaten einsehen.")
        day_count = max(1, min(int(days or 30), 365))
        period_end = utc_now()
        period_start = period_end - timedelta(days=day_count)
        bookings = [
            booking for booking in self._booking_repo.find_all()
            if parse_iso_datetime(booking.end_time) >= period_start
            and parse_iso_datetime(booking.start_time) <= period_end
        ]
        active = [booking for booking in bookings if booking.is_active()]
        by_type = {target_type.value: {"count": 0, "hours": 0.0} for target_type in BookingTargetType}
        for booking in active:
            hours = max(0.0, (parse_iso_datetime(booking.end_time) - parse_iso_datetime(booking.start_time)).total_seconds() / 3600)
            bucket = by_type[booking.target_type.value]
            bucket["count"] += 1
            bucket["hours"] = round(bucket["hours"] + hours, 1)
        attendance_candidates = [booking for booking in active if booking.target_type != BookingTargetType.ASSET]
        checked_in = [booking for booking in attendance_candidates if booking.checked_in_at]
        return {
            "days": day_count,
            "booking_count": len(bookings),
            "active_count": len(active),
            "cancelled_count": len(bookings) - len(active),
            "booked_hours": round(sum(item["hours"] for item in by_type.values()), 1),
            "check_in_rate": round((len(checked_in) / len(attendance_candidates) * 100), 1) if attendance_candidates else 0,
            "by_type": by_type,
        }

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
        booking.updated_at = utc_now().isoformat()
        self._booking_repo.update(booking)
        return booking

    def cancel_booking_scope(
        self, booking_id: str, requesting_user: User, scope: str = "single"
    ) -> List[Booking]:
        """Storniert einen Termin oder ihn und alle folgenden Serientermine."""
        booking = self._get_manageable_active_booking(booking_id, requesting_user)
        if scope not in {"single", "future"}:
            raise ValueError("scope muss 'single' oder 'future' sein.")
        if scope == "single" or not booking.series_id:
            return [self.cancel_booking(booking_id, requesting_user)]

        affected = [
            item for item in self._booking_repo.find_all()
            if item.series_id == booking.series_id
            and item.recurrence_index >= booking.recurrence_index
            and item.is_active()
        ]
        for item in affected:
            item.status = BookingStatus.CANCELLED
            item.updated_at = utc_now().isoformat()
            self._booking_repo.update(item)
        return affected

    def update_booking(
        self,
        booking_id: str,
        requesting_user: User,
        title: str = None,
        start_time: str = None,
        end_time: str = None,
        target_id: str = None,
        target_type: BookingTargetType = None,
        scope: str = "single",
    ) -> List[Booking]:
        """Bearbeitet eine zukünftige Buchung oder alle folgenden Serientermine atomar."""
        original = self._get_editable_booking(booking_id, requesting_user)
        if scope not in {"single", "future"}:
            raise ValueError("scope muss 'single' oder 'future' sein.")

        originals = [original]
        if scope == "future" and original.series_id:
            originals = sorted(
                [
                    item for item in self._booking_repo.find_all()
                    if item.series_id == original.series_id
                    and item.recurrence_index >= original.recurrence_index
                    and item.is_active()
                ],
                key=lambda item: item.recurrence_index,
            )
            for item in originals:
                self._get_editable_booking(item.id, requesting_user)

        requested_start = start_time or original.start_time
        requested_end = end_time or original.end_time
        self._validate_time_range(requested_start, requested_end)
        start_shift = parse_iso_datetime(requested_start) - parse_iso_datetime(original.start_time)
        end_shift = parse_iso_datetime(requested_end) - parse_iso_datetime(original.end_time)
        affected_ids = {item.id for item in originals}
        candidates = []

        for item in originals:
            candidate = Booking.from_dict(item.to_dict())
            candidate.title = str(title).strip() if title is not None else item.title
            if not candidate.title:
                candidate.title = "Buchung"
            candidate.start_time = (parse_iso_datetime(item.start_time) + start_shift).isoformat()
            candidate.end_time = (parse_iso_datetime(item.end_time) + end_shift).isoformat()
            self._validate_time_range(candidate.start_time, candidate.end_time)

            desired_type = target_type or item.target_type
            desired_id = target_id or item.target_id
            resolved_id, resolved_type, room_id, auto_assigned = self._resolve_booking_target(
                desired_id,
                desired_type,
                candidate.start_time,
                candidate.end_time,
                exclude_booking_ids=affected_ids,
            )
            if item.access_password_hash and resolved_type != BookingTargetType.ROOM:
                raise ValueError("Eine geschützte Einladung muss einer Ganzraumbuchung zugeordnet bleiben.")
            candidate.target_id = resolved_id
            candidate.target_type = resolved_type
            candidate.room_id = room_id
            candidate.auto_assigned_seat = auto_assigned
            candidate.updated_at = utc_now().isoformat()
            candidates.append(candidate)

        for candidate in candidates:
            conflicts = self._find_booking_conflicts(
                candidate.target_id,
                candidate.target_type,
                candidate.start_time,
                candidate.end_time,
                exclude_booking_ids=affected_ids,
            )
            if candidate.target_type == BookingTargetType.SEAT:
                conflicts.extend(self._find_user_seat_conflicts(
                    candidate.user_id,
                    candidate.start_time,
                    candidate.end_time,
                    exclude_booking_ids=affected_ids,
                ))
            if conflicts:
                raise BookingConflictError(
                    "Die geänderte Buchung überschneidet sich mit einer bestehenden Reservierung.",
                    conflicts=conflicts,
                )

        self._validate_candidate_conflicts(candidates)
        for candidate in candidates:
            self._booking_repo.update(candidate)
        return candidates

    def extend_booking(
        self, booking_id: str, requesting_user: User, minutes: int = 30
    ) -> Booking:
        """Verlängert eine aktive Buchung, wenn der Folgezeitraum frei ist."""
        booking = self._get_manageable_active_booking(booking_id, requesting_user)
        extension = int(minutes or 30)
        if extension not in {15, 30, 60, 90, 120}:
            raise ValueError("Eine Verlängerung ist um 15, 30, 60, 90 oder 120 Minuten möglich.")
        if parse_iso_datetime(booking.end_time) <= utc_now():
            raise ValueError("Eine bereits beendete Buchung kann nicht verlängert werden.")

        new_end = (parse_iso_datetime(booking.end_time) + timedelta(minutes=extension)).isoformat()
        conflicts = self._find_booking_conflicts(
            booking.target_id,
            booking.target_type,
            booking.start_time,
            new_end,
            exclude_booking_ids={booking.id},
        )
        if booking.target_type == BookingTargetType.SEAT:
            conflicts.extend(self._find_user_seat_conflicts(
                booking.user_id,
                booking.start_time,
                new_end,
                exclude_booking_ids={booking.id},
            ))
        if conflicts:
            raise BookingConflictError(
                "Die Buchung kann nicht verlängert werden, weil der Folgezeitraum belegt ist.",
                conflicts=conflicts,
            )
        booking.end_time = new_end
        booking.updated_at = utc_now().isoformat()
        self._booking_repo.update(booking)
        return booking

    def check_in_booking(self, booking_id: str, requesting_user: User) -> Booking:
        """Checkt den Buchungsinhaber während des gebuchten Zeitraums ein."""
        booking = self._get_manageable_active_booking(booking_id, requesting_user)
        if booking.target_type == BookingTargetType.ASSET:
            raise ValueError("Ein Check-in ist nur für Räume und Arbeitsplätze vorgesehen.")
        now = utc_now()
        if now < parse_iso_datetime(booking.start_time):
            raise ValueError("Der Check-in ist erst ab Beginn der Buchung möglich.")
        if now >= parse_iso_datetime(booking.end_time):
            raise ValueError("Der Buchungszeitraum ist bereits beendet.")
        if booking.checked_out_at:
            raise ValueError("Diese Buchung wurde bereits ausgecheckt.")
        if not booking.checked_in_at:
            booking.checked_in_at = now.isoformat()
            self._booking_repo.update(booking)
        return booking

    def check_out_booking(self, booking_id: str, requesting_user: User) -> Booking:
        """Checkt den Buchungsinhaber aus einer laufenden Belegung aus."""
        booking = self._get_manageable_active_booking(booking_id, requesting_user)
        if not booking.checked_in_at:
            raise ValueError("Für diese Buchung wurde noch kein Check-in durchgeführt.")
        if not booking.checked_out_at:
            booking.checked_out_at = utc_now().isoformat()
            self._booking_repo.update(booking)
        return booking

    def _get_manageable_active_booking(self, booking_id: str, requesting_user: User) -> Booking:
        booking = self._booking_repo.find_by_id(booking_id)
        if not booking or not booking.is_active():
            raise BookingNotFoundError("Buchung nicht gefunden oder nicht mehr aktiv.")
        if booking.user_id != requesting_user.id and not requesting_user.is_admin():
            raise AuthError("Sie können nur Ihre eigenen Buchungen verwalten.")
        return booking

    def _get_editable_booking(self, booking_id: str, requesting_user: User) -> Booking:
        booking = self._get_manageable_active_booking(booking_id, requesting_user)
        if booking.checked_in_at:
            raise ValueError("Eine bereits eingecheckte Buchung kann nicht bearbeitet werden.")
        if parse_iso_datetime(booking.start_time) <= utc_now():
            raise ValueError("Nur zukünftige Buchungen können bearbeitet werden.")
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

    def get_by_invitation_code(self, invitation_code: str) -> Optional[Booking]:
        normalized = str(invitation_code or "").strip().upper()
        if not normalized:
            return None
        return next(
            (booking for booking in self._booking_repo.find_all()
             if booking.invitation_code.upper() == normalized),
            None,
        )

    def get_user_notifications(self, user: User, limit: int = 30) -> List[dict]:
        """Erzeugt In-App-Hinweise aus den eigenen Buchungen, ohne externen Versand."""
        now = utc_now()
        notifications = []
        for booking in self._booking_repo.find_by_user(user.id):
            start = parse_iso_datetime(booking.start_time)
            end = parse_iso_datetime(booking.end_time)
            if booking.status == BookingStatus.CANCELLED and end >= now - timedelta(days=30):
                notifications.append({
                    "id": f"cancelled:{booking.id}",
                    "booking_id": booking.id,
                    "kind": "cancelled",
                    "priority": "normal",
                    "title": "Buchung storniert",
                    "message": f"„{booking.title}“ wurde storniert.",
                    "event_time": booking.updated_at,
                })
            elif booking.is_active() and start <= now < end and booking.target_type != BookingTargetType.ASSET:
                notifications.append({
                    "id": f"checkin:{booking.id}",
                    "booking_id": booking.id,
                    "kind": "checkin",
                    "priority": "high",
                    "title": "Check-in möglich",
                    "message": f"„{booking.title}“ läuft gerade; der Check-in ist jetzt möglich.",
                    "event_time": booking.start_time,
                })
            elif booking.is_active() and now < start <= now + timedelta(hours=24):
                notifications.append({
                    "id": f"upcoming:{booking.id}",
                    "booking_id": booking.id,
                    "kind": "upcoming",
                    "priority": "high" if start <= now + timedelta(hours=2) else "normal",
                    "title": "Buchung steht bevor",
                    "message": f"„{booking.title}“ beginnt innerhalb der nächsten 24 Stunden.",
                    "event_time": booking.start_time,
                })
        notifications.sort(key=lambda item: item["event_time"], reverse=True)
        return notifications[:max(1, min(int(limit or 30), 100))]

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
            room = self._room_repo.find_by_id(target_id)
            seats = self._seat_repo.find_by_room(target_id)
            if seats and room and getattr(room, "room_type", "") == "shared_desk":
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
                room = self._room_repo.find_by_id(target_id) if target_type == BookingTargetType.ROOM else None
                room_seats = self._seat_repo.find_by_room(target_id) if room and room.room_type == "shared_desk" else []
                occupied_seat_ids = {
                    conflict.target_id for conflict in conflicts
                    if conflict.target_type == BookingTargetType.SEAT
                }
                whole_room_blocked = any(
                    conflict.target_type == BookingTargetType.ROOM for conflict in conflicts
                )
                slots.append({
                    "start_time": block_start,
                    "end_time": block_end,
                    "label": f"{hour:02d}:00-{hour + 1:02d}:00",
                    "available": available,
                    "booked": bool(conflicts),
                    "conflict_count": len(conflicts),
                    "total_seats": len(room_seats),
                    "occupied_seats": len(room_seats) if whole_room_blocked else len(occupied_seat_ids),
                    "available_seats": 0 if whole_room_blocked else (max(0, len(room_seats) - len(occupied_seat_ids)) if room_seats else 0),
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
            if seats and getattr(room, "room_type", "") == "shared_desk":
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
        exclude_booking_ids: set = None,
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
                raise ValueError("Arbeitsplätze können nur in Shared Offices separat gebucht werden.")
            seat = self._seat_repo.find_by_id(seat_id)
            if not seat or not seat.is_active or seat.room_id != target_id:
                raise ValueError("Der angegebene Sitzplatz gehört nicht zum Raum oder ist nicht verfügbar.")
            return seat.id, BookingTargetType.SEAT, target_id, False

        seats = self._seat_repo.find_by_room(target_id)
        if not seats or not is_shared_desk:
            return target_id, BookingTargetType.ROOM, "", False

        seat = self._find_available_seat(
            target_id, start_time, end_time, exclude_booking_ids=exclude_booking_ids
        )
        if not seat:
            raise BookingConflictError(
                "Für den gewünschten Zeitraum ist kein Sitzplatz in diesem Raum verfügbar.",
                conflicts=self._find_room_seat_conflicts(
                    target_id, start_time, end_time, exclude_booking_ids=exclude_booking_ids
                ),
            )
        return seat.id, BookingTargetType.SEAT, target_id, True

    def _find_available_seat(
        self, room_id: str, start_time: str, end_time: str, exclude_booking_ids: set = None
    ):
        available_seats = []
        for seat in self._seat_repo.find_by_room(room_id):
            conflicts = self._find_booking_conflicts(
                seat.id,
                BookingTargetType.SEAT,
                start_time,
                end_time,
                exclude_booking_ids=exclude_booking_ids,
            )
            if not conflicts:
                available_seats.append(seat)
        return secrets.choice(available_seats) if available_seats else None

    def _find_booking_conflicts(
        self,
        target_id: str,
        target_type: BookingTargetType,
        start_time: str,
        end_time: str,
        exclude_booking_ids: set = None,
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
            conflicts.extend(self._find_room_seat_conflicts(
                target_id,
                start_time,
                end_time,
                exclude_booking_ids=exclude_booking_ids,
            ))

        excluded = exclude_booking_ids or set()
        unique = {}
        for conflict in conflicts:
            if conflict.id not in excluded:
                unique[conflict.id] = conflict
        return list(unique.values())

    def verify_booking_access(self, booking_id: str, access_password: str) -> bool:
        """Prüft das Passwort einer geschützten Seminarraumbuchung."""
        booking = self._booking_repo.find_by_id(booking_id)
        if not booking or not booking.access_password_hash:
            return False
        return self._verify_access_password_hash(booking.access_password_hash, access_password)

    def verify_invitation_access(self, invitation_code: str, access_password: str) -> bool:
        booking = self.get_by_invitation_code(invitation_code)
        return bool(
            booking
            and booking.access_password_hash
            and self._verify_access_password_hash(booking.access_password_hash, access_password)
        )

    def join_protected_booking(self, booking_id: str, email: str, access_password: str) -> Booking:
        """Bucht eine externe Person mit gültigem Passwort in ein Seminar ein."""
        booking = self._booking_repo.find_by_id(booking_id)
        if not booking or not booking.is_active():
            raise BookingNotFoundError("Buchung nicht gefunden oder nicht mehr aktiv.")
        if parse_iso_datetime(booking.end_time) <= utc_now():
            raise ValueError("Die Einladung ist abgelaufen, weil die Buchung bereits beendet ist.")
        if booking.target_type != BookingTargetType.ROOM:
            raise ValueError("Der Einladungsbeitritt ist nur für Ganzraumbuchungen möglich.")

        normalized_email = str(email or "").strip().lower()
        if "@" not in normalized_email:
            raise ValueError("Bitte eine gültige E-Mail-Adresse angeben.")
        if booking.invitation_emails and normalized_email not in booking.invitation_emails:
            raise AuthError("Diese E-Mail-Adresse steht nicht auf der Einladungsliste.")
        if not self.verify_booking_access(booking_id, access_password):
            raise AuthError("Das Buchungspasswort ist nicht korrekt.")

        if normalized_email not in booking.participant_emails:
            room = self._room_repo.find_by_id(booking.target_id)
            capacity = max(1, int(getattr(room, "capacity", 1) or 1))
            if len(booking.participant_emails) + 1 >= capacity:
                raise ValueError("Die maximale Raumkapazität ist bereits erreicht.")
            booking.participant_emails.append(normalized_email)
            self._booking_repo.update(booking)
        return booking

    def join_by_invitation_code(
        self, invitation_code: str, email: str, access_password: str
    ) -> Booking:
        booking = self.get_by_invitation_code(invitation_code)
        if not booking:
            raise BookingNotFoundError("Einladungscode nicht gefunden oder ungültig.")
        return self.join_protected_booking(booking.id, email, access_password)

    def get_active_room_occupancy(self, requesting_user: User) -> List[dict]:
        """Admin-Übersicht: aktive Personen/Buchungen je Raum."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können die Raumbelegung einsehen.")

        occupancy = []
        now = utc_now()
        for booking in self._booking_repo.find_active():
            if not booking.checked_in_at or booking.checked_out_at:
                continue
            if not (
                parse_iso_datetime(booking.start_time) <= now
                < parse_iso_datetime(booking.end_time)
            ):
                continue
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
                "participant_emails": booking.participant_emails,
                "checked_in_at": booking.checked_in_at,
            })
        return occupancy

    def _create_access_password_hash(self, access_password: str) -> str:
        if not access_password:
            return ""
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256", access_password.encode("utf-8"), salt, 200_000
        )
        return f"pbkdf2_sha256$200000${salt.hex()}${digest.hex()}"

    def _create_invitation_code(self) -> str:
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        for _ in range(50):
            value = "RPL-" + "".join(secrets.choice(alphabet) for _ in range(6))
            if not self.get_by_invitation_code(value):
                return value
        raise RuntimeError("Es konnte kein eindeutiger Einladungscode erzeugt werden.")

    def _verify_access_password_hash(self, stored_hash: str, access_password: str) -> bool:
        if not stored_hash or not access_password:
            return False
        if not stored_hash.startswith("pbkdf2_sha256$"):
            legacy = hashlib.sha256(access_password.encode("utf-8")).hexdigest()
            return hmac.compare_digest(stored_hash, legacy)
        try:
            _, iterations, salt_hex, digest_hex = stored_hash.split("$", 3)
            candidate = hashlib.pbkdf2_hmac(
                "sha256",
                access_password.encode("utf-8"),
                bytes.fromhex(salt_hex),
                int(iterations),
            )
        except (TypeError, ValueError):
            return False
        return hmac.compare_digest(candidate.hex(), digest_hex)

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
        self,
        user_id: str,
        start_time: str,
        end_time: str,
        exclude_booking_ids: set = None,
    ) -> List[Booking]:
        """Verhindert, dass ein Nutzer parallel mehrere Sitzplätze bucht."""
        excluded = exclude_booking_ids or set()
        return [
            booking for booking in self._booking_repo.find_active_by_user(user_id)
            if booking.target_type == BookingTargetType.SEAT
            and booking.id not in excluded
            and booking.overlaps_with(start_time, end_time)
        ]

    def _find_room_seat_conflicts(
        self,
        room_id: str,
        start_time: str,
        end_time: str,
        exclude_booking_ids: set = None,
    ) -> List[Booking]:
        excluded = exclude_booking_ids or set()
        conflicts = []
        for seat in self._seat_repo.find_by_room(room_id):
            conflicts.extend(
                self._booking_repo.find_conflicts(
                    seat.id, BookingTargetType.SEAT, start_time, end_time
                )
            )
        return [conflict for conflict in conflicts if conflict.id not in excluded]

    def _validate_candidate_conflicts(self, candidates: List[Booking]) -> None:
        """Verhindert Überschneidungen innerhalb eines gemeinsam bearbeiteten Satzes."""
        for index, left in enumerate(candidates):
            for right in candidates[index + 1:]:
                if not left.overlaps_with(right.start_time, right.end_time):
                    continue
                same_target = left.target_type == right.target_type and left.target_id == right.target_id
                same_user_seats = (
                    left.user_id == right.user_id
                    and left.target_type == right.target_type == BookingTargetType.SEAT
                )
                same_room_dependency = (
                    left.target_type == BookingTargetType.SEAT
                    and right.target_type == BookingTargetType.ROOM
                    and left.room_id == right.target_id
                ) or (
                    right.target_type == BookingTargetType.SEAT
                    and left.target_type == BookingTargetType.ROOM
                    and right.room_id == left.target_id
                )
                if same_target or same_user_seats or same_room_dependency:
                    raise BookingConflictError(
                        "Die geänderten Serientermine überschneiden sich gegenseitig.",
                        conflicts=[left, right],
                    )

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
