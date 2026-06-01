"""
Model: Asset (Ressource)
Repräsentiert eine buchbare Ressource/ein Gerät.
Beispiele: Beamer, Whiteboard, Laptop, Monitor, Adapter
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AssetType(str, Enum):
    BEAMER = "beamer"
    WHITEBOARD = "whiteboard"
    LAPTOP = "laptop"
    MONITOR = "monitor"
    ADAPTER = "adapter"
    MODERATION = "moderation"
    PRESENTATION_TECH = "presentation_tech"
    OTHER = "other"


@dataclass
class Asset:
    """
    Kernobjekt: Buchbare Ressource / Gerät.

    Attribute:
        id:           Eindeutige Asset-ID (UUID-String)
        name:         Bezeichnung (z. B. "Beamer Samsung EX-1")
        asset_type:   Typ der Ressource (AssetType Enum)
        description:  Freitext-Beschreibung
        location:     Standort / Raum, wo die Ressource standardmäßig liegt
        is_active:    Soft-Delete-Flag
        created_at:   ISO-8601 Erstellungszeitpunkt
    """
    id: str
    name: str
    asset_type: AssetType = AssetType.OTHER
    description: str = ""
    location: str = ""
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        """Serialisiert das Asset für JSON-Persistenz."""
        return {
            "id": self.id,
            "name": self.name,
            "asset_type": self.asset_type.value if isinstance(self.asset_type, AssetType) else self.asset_type,
            "description": self.description,
            "location": self.location,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Asset":
        """Deserialisiert aus einem Dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            asset_type=AssetType(data.get("asset_type", AssetType.OTHER.value)),
            description=data.get("description", ""),
            location=data.get("location", ""),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
        )

    def __repr__(self) -> str:
        return f"<Asset '{self.name}' type={self.asset_type.value}>"
