"""Repository: User"""
import os
from typing import Optional
from ..models.user import User, UserRole
from .base_repository import JsonRepository

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

class UserRepository(JsonRepository[User]):
    def __init__(self):
        super().__init__(os.path.join(DATA_DIR, "users.json"))

    def from_dict(self, data: dict) -> User:
        return User.from_dict(data)

    def to_dict(self, obj: User) -> dict:
        return obj.to_dict()

    def find_by_email(self, email: str) -> Optional[User]:
        """Sucht einen aktiven Nutzer anhand seiner E-Mail-Adresse."""
        with self._lock:
            for d in self._read_all_raw():
                if d.get("email", "").lower() == email.lower() and d.get("is_active", True):
                    return User.from_dict(d)
        return None

    def email_exists(self, email: str) -> bool:
        return self.find_by_email(email) is not None

    def find_active(self) -> list:
        return [u for u in self.find_all() if u.is_active]

    def find_by_role(self, role: UserRole) -> list:
        return [u for u in self.find_active() if u.role == role]
