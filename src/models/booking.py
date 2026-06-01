"""
Model: Booking (Buchung)
Repräsentiert eine zeitbasierte Reservierung eines Raums oder einer Ressource.
Dieses Modell ist zentral für die Konfliktprüfung.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class BookingStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class BookingTargetType(str, Enum):
    ROOM = "room"
    ASSET = "asset"


@dataclass
class Booking:
    """
    Kernobjekt: Buchung eines Raums oder einer Ressource.

    Attribute:
        id:           Eindeutige Buchungs-ID (UUID-String)
        user_id:      ID des buchenden Nutzers
        target_id:    ID des gebuchten Raums oder der gebuchten Ressource
        target_type:  Typ des Buchungsobjekts (room | asset)
        title:        Kurze Beschreibung/Titel der Buchung (z. B. "Teammeeting")
        start_time:   Startzeit im ISO-8601 Format (z. B. "2026-06-15T09:00:00")
        end_time:     Endzeit im ISO-8601 Format
        status:       Buchungsstatus (active | cancelled)
        created_at:   ISO-8601 Zeitpunkt der Buchungserstellung

    Invarianten:
        - start_time muss vor end_time liegen
        - Zwei aktive Buchungen für dasselbe Zielobjekt dürfen sich zeitlich nicht überschneiden
    """
    id: str
    user_id: str
    target_id: str
    target_type: BookingTargetType
    title: str
    start_time: str
    end_time: str
    status: BookingStatus = BookingStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

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
            "status": self.status.value if isinstance(self.status, BookingStatus) else self.status,
            "created_at": self.created_at,
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
            status=BookingStatus(data.get("status", BookingStatus.ACTIVE.value)),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
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
        return self.start_time < end and self.end_time > start

    def __repr__(self) -> str:
        return (
            f"<Booking id={self.id[:8]}… "
            f"target={self.target_type.value}:{self.target_id[:8]}… "
            f"[{self.start_time} → {self.end_time}] "
            f"status={self.status.value}>"
        )
