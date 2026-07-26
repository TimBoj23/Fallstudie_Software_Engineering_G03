"""
Model: User
Repräsentiert einen Nutzer des Systems.
Rollen: 'user' (Mitarbeitender) | 'admin' (Administrator)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from ..utils.time import utc_now_iso


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
        password_hash: Mit PBKDF2 gehashtes Passwort
        created_at:    ISO-8601 Timestamp der Erstellung
        is_active:     Weicher Lösch-Flag (soft-delete)
    """
    id: str
    name: str
    email: str
    role: UserRole = UserRole.USER
    password_hash: str = ""
    image_url: str = ""
    reset_token: str = ""
    reset_token_expires_at: str = ""
    created_at: str = field(default_factory=utc_now_iso)
    is_active: bool = True
    favorite_targets: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialisiert das Objekt für JSON-Persistenz."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value if isinstance(self.role, UserRole) else self.role,
            "password_hash": self.password_hash,
            "image_url": self.image_url,
            "reset_token": self.reset_token,
            "reset_token_expires_at": self.reset_token_expires_at,
            "created_at": self.created_at,
            "is_active": self.is_active,
            "favorite_targets": self.favorite_targets,
        }

    def to_public_dict(self) -> dict:
        """Serialisiert ohne sensitives Passwort-Hash (für API-Responses)."""
        d = self.to_dict()
        d.pop("password_hash", None)
        d.pop("reset_token", None)
        d.pop("reset_token_expires_at", None)
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
            image_url=data.get("image_url", ""),
            reset_token=data.get("reset_token", ""),
            reset_token_expires_at=data.get("reset_token_expires_at", ""),
            created_at=data.get("created_at", utc_now_iso()),
            is_active=data.get("is_active", True),
            favorite_targets=data.get("favorite_targets", []),
        )

    def is_admin(self) -> bool:
        """Kurzprüfung ob der Nutzer Admin-Rechte hat."""
        return self.role == UserRole.ADMIN

    def __repr__(self) -> str:
        return f"<User id={self.id} name='{self.name}' role={self.role.value}>"
