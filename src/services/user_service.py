"""
Service: UserService
Verantwortlich für Registrierung, Authentifizierung und Nutzerverwaltung.

Architekturentscheidung Passwort-Hashing:
    Passwörter werden mit bcrypt gehasht (Salting inbegriffen).
    Im MVP wird hashlib.pbkdf2_hmac als stdlib-Alternative genutzt,
    um externe Abhängigkeiten minimal zu halten.
    Für Produktion: bcrypt oder argon2-cffi empfohlen.
"""

import hashlib
import os
import uuid
from typing import Optional

from ..models.user import User, UserRole
from ..repositories.user_repository import UserRepository


class AuthError(Exception):
    """Fehler bei Authentifizierung oder Autorisierung."""
    pass


class UserService:
    """
    Verwaltet alle nutzerbezogenen Operationen.

    Verantwortlichkeiten:
        - Registrierung neuer Nutzer mit Passwort-Hashing
        - Login-Prüfung (E-Mail + Passwort)
        - Nutzerprofile abrufen und aktualisieren
        - Admin-Nutzerverwaltung
    """

    def __init__(self, user_repository: UserRepository = None):
        self._repo = user_repository or UserRepository()

    # ──────────────────────────────────────────────
    # Passwort-Hashing (PBKDF2 mit SHA-256)
    # ──────────────────────────────────────────────

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hasht ein Passwort sicher mit PBKDF2-HMAC-SHA256 + Random Salt."""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return salt.hex() + ":" + key.hex()

    @staticmethod
    def _verify_password(password: str, stored_hash: str) -> bool:
        """Prüft ein Passwort gegen den gespeicherten Hash."""
        try:
            salt_hex, key_hex = stored_hash.split(":")
            salt = bytes.fromhex(salt_hex)
            key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
            return key.hex() == key_hex
        except Exception:
            return False

    # ──────────────────────────────────────────────
    # Öffentliche Methoden
    # ──────────────────────────────────────────────

    def register(
        self,
        name: str,
        email: str,
        password: str,
        role: UserRole = UserRole.USER,
    ) -> User:
        """
        Registriert einen neuen Nutzer.

        Args:
            name:     Vollständiger Name
            email:    E-Mail-Adresse (muss eindeutig sein)
            password: Klartext-Passwort (wird sofort gehasht)
            role:     Rolle (Standard: user)

        Returns:
            Das neu erstellte User-Objekt

        Raises:
            ValueError: E-Mail bereits vergeben oder Eingaben ungültig
        """
        if not name or not name.strip():
            raise ValueError("Name darf nicht leer sein.")
        if not email or "@" not in email:
            raise ValueError("Ungültige E-Mail-Adresse.")
        if not password or len(password) < 6:
            raise ValueError("Passwort muss mindestens 6 Zeichen lang sein.")
        if self._repo.email_exists(email):
            raise ValueError(f"E-Mail-Adresse '{email}' ist bereits registriert.")

        user = User(
            id=str(uuid.uuid4()),
            name=name.strip(),
            email=email.lower().strip(),
            role=role,
            password_hash=self._hash_password(password),
        )
        return self._repo.save(user)

    def login(self, email: str, password: str) -> User:
        """
        Authentifiziert einen Nutzer anhand von E-Mail und Passwort.

        Returns:
            Das authentifizierte User-Objekt

        Raises:
            AuthError: E-Mail nicht gefunden oder Passwort falsch
        """
        user = self._repo.find_by_email(email)
        if not user:
            raise AuthError("E-Mail-Adresse oder Passwort ist falsch.")
        if not user.is_active:
            raise AuthError("Dieses Konto wurde deaktiviert.")
        if not self._verify_password(password, user.password_hash):
            raise AuthError("E-Mail-Adresse oder Passwort ist falsch.")
        return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self._repo.find_by_id(user_id)

    def get_all(self) -> list:
        return self._repo.find_active()

    def deactivate(self, user_id: str, requesting_user: User) -> User:
        """Deaktiviert einen Nutzer (Soft-Delete). Nur Admins erlaubt."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können Nutzer deaktivieren.")
        user = self._repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"Nutzer mit ID '{user_id}' nicht gefunden.")
        user.is_active = False
        self._repo.update(user)
        return user

    def promote_to_admin(self, user_id: str, requesting_user: User) -> User:
        """Befördert einen Nutzer zum Admin. Nur Admins erlaubt."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können andere Nutzer befördern.")
        user = self._repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"Nutzer mit ID '{user_id}' nicht gefunden.")
        user.role = UserRole.ADMIN
        self._repo.update(user)
        return user
