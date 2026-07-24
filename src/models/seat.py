"""
Model: Seat (Sitzplatz)
Repräsentiert einen einzelnen buchbaren Sitzplatz innerhalb eines Raums.
"""

from dataclasses import dataclass, field

from ..utils.time import utc_now_iso


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
    image_url: str = ""
    monitor_count: int = 1
    is_active: bool = True
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict:
        """Serialisiert den Sitzplatz für JSON-Persistenz."""
        return {
            "id": self.id,
            "room_id": self.room_id,
            "label": self.label,
            "description": self.description,
            "image_url": self.image_url,
            "monitor_count": self.monitor_count,
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
            image_url=data.get("image_url", ""),
            monitor_count=int(data.get("monitor_count", 1)),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", utc_now_iso()),
        )

    def __repr__(self) -> str:
        return f"<Seat '{self.label}' room={self.room_id[:8]}...>"
