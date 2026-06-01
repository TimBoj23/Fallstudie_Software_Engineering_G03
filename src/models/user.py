"""
Model: User
Repräsentiert einen Nutzer des Systems.
Rollen: 'user' (Mitarbeitender) | 'admin' (Administrator)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


@dataclass
class User:
    """
    Kernobjekt: Nutzer des Raum- und Ressourcenplanungssystems.

    Attribute:
        id:            Eindeutige Nutzer-ID (UUID-String)
        name:          Vollständiger Name
        email:         E-Mail-Adresse (eindeutig, wird als Login-Kennung verwendet)
        role:          Rolle im System (user | admin)
        password_hash: Gehashtes Passwort (bcrypt)
        created_at:    ISO-8601 Timestamp der Erstellung
        is_active:     Weicher Lösch-Flag (soft-delete)
    """
    id: str
    name: str
    email: str
    role: UserRole = UserRole.USER
    password_hash: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    is_active: bool = True

    def to_dict(self) -> dict:
        """Serialisiert das Objekt für JSON-Persistenz."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value if isinstance(self.role, UserRole) else self.role,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "is_active": self.is_active,
        }

    def to_public_dict(self) -> dict:
        """Serialisiert ohne sensitives Passwort-Hash (für API-Responses)."""
        d = self.to_dict()
        d.pop("password_hash", None)
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Deserialisiert aus einem Dictionary (z. B. aus JSON)."""
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            role=UserRole(data.get("role", UserRole.USER.value)),
            password_hash=data.get("password_hash", ""),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            is_active=data.get("is_active", True),
        )

    def is_admin(self) -> bool:
        """Kurzprüfung ob der Nutzer Admin-Rechte hat."""
        return self.role == UserRole.ADMIN

    def __repr__(self) -> str:
        return f"<User id={self.id} name='{self.name}' role={self.role.value}>"
