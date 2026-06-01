"""
Repository: Booking

Enthält die datenbanknahen Abfragen für Buchungen.
Die Konfliktprüfungs-Abfrage find_conflicts() ist die
datenseitige Grundlage der Kernlogik im BookingService.
"""
import os
from typing import List
from ..models.booking import Booking, BookingStatus, BookingTargetType
from .base_repository import JsonRepository

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


class BookingRepository(JsonRepository[Booking]):
    def __init__(self):
        super().__init__(os.path.join(DATA_DIR, "bookings.json"))

    def from_dict(self, data: dict) -> Booking:
        return Booking.from_dict(data)

    def to_dict(self, obj: Booking) -> dict:
        return obj.to_dict()

    def find_active(self) -> List[Booking]:
        """Alle nicht-stornierten Buchungen."""
        return [b for b in self.find_all() if b.is_active()]

    def find_by_user(self, user_id: str) -> List[Booking]:
        """Alle Buchungen eines bestimmten Nutzers (inkl. stornierte)."""
        return [b for b in self.find_all() if b.user_id == user_id]

    def find_active_by_user(self, user_id: str) -> List[Booking]:
        """Nur aktive Buchungen eines Nutzers."""
        return [b for b in self.find_by_user(user_id) if b.is_active()]

    def find_by_target(self, target_id: str, target_type: BookingTargetType) -> List[Booking]:
        """Alle Buchungen für einen bestimmten Raum oder ein bestimmtes Asset."""
        return [
            b for b in self.find_all()
            if b.target_id == target_id and b.target_type == target_type
        ]

    def find_conflicts(
        self,
        target_id: str,
        target_type: BookingTargetType,
        start_time: str,
        end_time: str,
        exclude_booking_id: str = None,
    ) -> List[Booking]:
        """
        Sucht nach aktiven Buchungen, die sich mit dem gegebenen Zeitraum überschneiden.

        Konfliktalgorithmus (Interval-Overlap):
            Zwei Zeiträume [A_start, A_end) und [B_start, B_end) überschneiden sich
            genau dann, wenn: A_start < B_end UND A_end > B_start

        Dies schließt folgende Konflikte ein:
            - Buchung B liegt vollständig innerhalb von A
            - Buchung A liegt vollständig innerhalb von B
            - Buchung B beginnt während A
            - Buchung B endet während A

        Args:
            target_id:         ID des zu prüfenden Raums / Assets
            target_type:       Typ (room | asset)
            start_time:        Startzeit der neuen Buchung (ISO-8601)
            end_time:          Endzeit der neuen Buchung (ISO-8601)
            exclude_booking_id: Buchungs-ID, die von der Prüfung ausgeschlossen wird
                                (nützlich bei Bearbeitungen einer bestehenden Buchung)

        Returns:
            Liste aller konfliktierenden Buchungen (leer = kein Konflikt)
        """
        conflicts = []
        for b in self.find_by_target(target_id, target_type):
            if not b.is_active():
                continue
            if exclude_booking_id and b.id == exclude_booking_id:
                continue
            if b.overlaps_with(start_time, end_time):
                conflicts.append(b)
        return conflicts
