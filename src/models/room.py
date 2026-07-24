"""
Model: Room (Raum)
Repräsentiert einen buchbaren Raum im System.
Beispiele: Meetingraum, Konferenzraum, Schulungsraum, Arbeitsplatz
"""

from dataclasses import dataclass, field
from typing import List, Optional

from ..utils.time import utc_now_iso


@dataclass
class Room:
    """
    Kernobjekt: Buchbarer Raum.

    Attribute:
        id:          Eindeutige Raum-ID (UUID-String)
        name:        Bezeichnung des Raums (z. B. "Meetingraum Alpha")
        number:      Raumnummer für interne Referenz (z. B. "1001-23")
        capacity:    Maximale Personenanzahl
        room_type:   Raumtyp (seminarraum | shared_desk | meetingraum | studio)
        location:    Standort / Gebäude / Etage
        equipment:   Liste der Ausstattungsmerkmale (z. B. ["Beamer", "Whiteboard"])
        description: Freitext-Beschreibung
        is_active:   Soft-Delete-Flag
        created_at:  ISO-8601 Erstellungszeitpunkt
    """
    id: str
    name: str
    number: str
    capacity: int
    room_type: str = "seminarraum"
    location: str = ""
    equipment: List[str] = field(default_factory=list)
    description: str = ""
    image_url: str = ""
    is_active: bool = True
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict:
        """Serialisiert den Raum für JSON-Persistenz."""
        return {
            "id": self.id,
            "name": self.name,
            "number": self.number,
            "capacity": self.capacity,
            "room_type": self.room_type,
            "location": self.location,
            "equipment": self.equipment,
            "description": self.description,
            "image_url": self.image_url,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Room":
        """Deserialisiert aus einem Dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            number=data["number"],
            capacity=int(data.get("capacity", 1)),
            room_type=data.get("room_type", "seminarraum"),
            location=data.get("location", ""),
            equipment=data.get("equipment", []),
            description=data.get("description", ""),
            image_url=data.get("image_url", ""),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", utc_now_iso()),
        )

    def __repr__(self) -> str:
        return f"<Room [{self.number}] '{self.name}' cap={self.capacity}>"
