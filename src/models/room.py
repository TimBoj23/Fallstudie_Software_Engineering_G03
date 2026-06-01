"""
Model: Room (Raum)
Repräsentiert einen buchbaren Raum im System.
Beispiele: Meetingraum, Konferenzraum, Schulungsraum, Arbeitsplatz
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Room:
    """
    Kernobjekt: Buchbarer Raum.

    Attribute:
        id:          Eindeutige Raum-ID (UUID-String)
        name:        Bezeichnung des Raums (z. B. "Meetingraum Alpha")
        number:      Raumnummer für interne Referenz (z. B. "1001-23")
        capacity:    Maximale Personenanzahl
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
    location: str = ""
    equipment: List[str] = field(default_factory=list)
    description: str = ""
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        """Serialisiert den Raum für JSON-Persistenz."""
        return {
            "id": self.id,
            "name": self.name,
            "number": self.number,
            "capacity": self.capacity,
            "location": self.location,
            "equipment": self.equipment,
            "description": self.description,
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
            location=data.get("location", ""),
            equipment=data.get("equipment", []),
            description=data.get("description", ""),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
        )

    def __repr__(self) -> str:
        return f"<Room [{self.number}] '{self.name}' cap={self.capacity}>"
