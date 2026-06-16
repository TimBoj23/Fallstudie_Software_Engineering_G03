"""
Model: Seat (Sitzplatz)
Repräsentiert einen einzelnen buchbaren Sitzplatz innerhalb eines Raums.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Seat:
    """
    Kernobjekt: Buchbarer Sitzplatz.

    Attribute:
        id:          Eindeutige Sitzplatz-ID (UUID-String)
        room_id:     ID des zugehörigen Raums
        label:       Sitzplatzbezeichnung (z. B. "A1", "Fensterplatz")
        description: Freitext-Beschreibung
        is_active:   Soft-Delete-Flag
        created_at:  ISO-8601 Erstellungszeitpunkt
    """
    id: str
    room_id: str
    label: str
    description: str = ""
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        """Serialisiert den Sitzplatz für JSON-Persistenz."""
        return {
            "id": self.id,
            "room_id": self.room_id,
            "label": self.label,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Seat":
        """Deserialisiert aus einem Dictionary."""
        return cls(
            id=data["id"],
            room_id=data["room_id"],
            label=data["label"],
            description=data.get("description", ""),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
        )

    def __repr__(self) -> str:
        return f"<Seat '{self.label}' room={self.room_id[:8]}...>"
