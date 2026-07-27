"""
Model: Booking (Buchung)
Repräsentiert eine zeitbasierte Reservierung eines Raums oder einer Ressource.
Dieses Modell ist zentral für die Konfliktprüfung.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from ..utils.time import parse_iso_datetime, utc_now_iso


class BookingStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class BookingTargetType(str, Enum):
    ROOM = "room"
    ASSET = "asset"
    SEAT = "seat"


@dataclass
class Booking:
    """
    Kernobjekt: Buchung eines Raums oder einer Ressource.

    Attribute:
        id:           Eindeutige Buchungs-ID (UUID-String)
        user_id:      ID des buchenden Nutzers
        target_id:    ID des gebuchten Raums oder der gebuchten Ressource
        target_type:  Typ des Buchungsobjekts (room | asset | seat)
        title:        Kurze Beschreibung/Titel der Buchung (z. B. "Teammeeting")
        start_time:   Startzeit im ISO-8601 Format (z. B. "2026-06-15T09:00:00")
        end_time:     Endzeit im ISO-8601 Format
        status:       Buchungsstatus (active | cancelled)
        created_at:   ISO-8601 Zeitpunkt der Buchungserstellung

    Invarianten:
        - start_time muss vor end_time liegen
        - Zwei aktive Buchungen für dasselbe Zielobjekt dürfen sich zeitlich nicht überschneiden
        - Bei Sitzplatzbuchungen kann room_id als Kontext gespeichert werden
    """
    id: str
    user_id: str
    target_id: str
    target_type: BookingTargetType
    title: str
    start_time: str
    end_time: str
    room_id: str = ""
    auto_assigned_seat: bool = False
    invitation_code: str = ""
    access_password_hash: str = ""
    invitation_emails: List[str] = field(default_factory=list)
    participant_emails: List[str] = field(default_factory=list)
    checked_in_at: str = ""
    checked_out_at: str = ""
    series_id: str = ""
    recurrence_index: int = 0
    status: BookingStatus = BookingStatus.ACTIVE
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict:
        """Serialisiert die Buchung für JSON-Persistenz."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "target_id": self.target_id,
            "target_type": self.target_type.value if isinstance(self.target_type, BookingTargetType) else self.target_type,
            "title": self.title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "room_id": self.room_id,
            "auto_assigned_seat": self.auto_assigned_seat,
            "invitation_code": self.invitation_code,
            "access_password_hash": self.access_password_hash,
            "invitation_emails": self.invitation_emails,
            "participant_emails": self.participant_emails,
            "checked_in_at": self.checked_in_at,
            "checked_out_at": self.checked_out_at,
            "series_id": self.series_id,
            "recurrence_index": self.recurrence_index,
            "status": self.status.value if isinstance(self.status, BookingStatus) else self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Booking":
        """Deserialisiert aus einem Dictionary."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            target_id=data["target_id"],
            target_type=BookingTargetType(data["target_type"]),
            title=data.get("title", ""),
            start_time=data["start_time"],
            end_time=data["end_time"],
            room_id=data.get("room_id", ""),
            auto_assigned_seat=data.get("auto_assigned_seat", False),
            invitation_code=data.get("invitation_code", ""),
            access_password_hash=data.get("access_password_hash", ""),
            invitation_emails=data.get("invitation_emails", []),
            participant_emails=data.get("participant_emails", []),
            checked_in_at=data.get("checked_in_at", ""),
            checked_out_at=data.get("checked_out_at", ""),
            series_id=data.get("series_id", ""),
            recurrence_index=int(data.get("recurrence_index", 0)),
            status=BookingStatus(data.get("status", BookingStatus.ACTIVE.value)),
            created_at=data.get("created_at", utc_now_iso()),
            updated_at=data.get("updated_at", data.get("created_at", utc_now_iso())),
        )

    def is_active(self) -> bool:
        """Prüft ob die Buchung noch aktiv (nicht storniert) ist."""
        return self.status == BookingStatus.ACTIVE

    def overlaps_with(self, start: str, end: str) -> bool:
        """
        Prüft zeitliche Überschneidung mit einem gegebenen Zeitraum.

        Zwei Zeiträume [A_start, A_end) und [B_start, B_end) überschneiden sich,
        wenn A_start < B_end UND A_end > B_start.

        Diese Methode ist der Kern der Konfliktprüfung im BookingService.
        """
        if not self.is_active():
            return False
        return (
            parse_iso_datetime(self.start_time) < parse_iso_datetime(end)
            and parse_iso_datetime(self.end_time) > parse_iso_datetime(start)
        )

    def __repr__(self) -> str:
        return (
            f"<Booking id={self.id[:8]}… "
            f"target={self.target_type.value}:{self.target_id[:8]}… "
            f"[{self.start_time} → {self.end_time}] "
            f"status={self.status.value}>"
        )
