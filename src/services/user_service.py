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
import secrets
import uuid
from datetime import timedelta
from typing import Optional

from ..models.user import User, UserRole
from ..repositories.user_repository import UserRepository
from ..utils.time import parse_iso_datetime, utc_now


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
        image_url: str = "",
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
            image_url=image_url,
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

    def get_by_email(self, email: str, include_inactive: bool = False) -> Optional[User]:
        """Liefert einen Nutzer optional unabhängig vom Aktivstatus."""
        if include_inactive:
            return self._repo.find_any_by_email(email)
        return self._repo.find_by_email(email)

    def get_all(self) -> list:
        return self._repo.find_active()

    def search_users(self, query: str = "", role: str = "", status: str = "") -> list:
        """Filtert die Admin-Nutzerübersicht ohne sensitive Felder."""
        users = self._repo.find_all()
        normalized_query = str(query or "").strip().lower()
        if normalized_query:
            users = [u for u in users if normalized_query in u.name.lower() or normalized_query in u.email.lower()]
        if role:
            users = [u for u in users if u.role.value == role]
        if status == "active":
            users = [u for u in users if u.is_active]
        elif status == "inactive":
            users = [u for u in users if not u.is_active]
        return users

    def get_favorites(self, user_id: str) -> list:
        user = self._repo.find_by_id(user_id)
        if not user:
            raise ValueError("Nutzer nicht gefunden.")
        return [self._favorite_from_key(key) for key in user.favorite_targets]

    def set_favorite(self, user_id: str, target_type: str, target_id: str, enabled: bool = True) -> list:
        if target_type not in {"room", "seat", "asset"} or not target_id:
            raise ValueError("Ungültiges Favoritenziel.")
        user = self._repo.find_by_id(user_id)
        if not user:
            raise ValueError("Nutzer nicht gefunden.")
        key = f"{target_type}:{target_id}"
        favorites = set(user.favorite_targets)
        if enabled:
            favorites.add(key)
        else:
            favorites.discard(key)
        user.favorite_targets = sorted(favorites)
        self._repo.update(user)
        return [self._favorite_from_key(item) for item in user.favorite_targets]

    @staticmethod
    def _favorite_from_key(key: str) -> dict:
        target_type, _, target_id = str(key).partition(":")
        return {"key": key, "target_type": target_type, "target_id": target_id}

    def create_user(
        self,
        name: str,
        email: str,
        password: str,
        requesting_user: User,
        role: UserRole = UserRole.USER,
        image_url: str = "",
    ) -> User:
        """Legt als Admin einen Nutzer an."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können Nutzer anlegen.")
        return self.register(name=name, email=email, password=password, role=role, image_url=image_url)

    def reset_password(self, user_id: str, new_password: str, requesting_user: User) -> User:
        """Setzt als Admin das Passwort eines Nutzers zurück."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können Passwörter zurücksetzen.")
        user = self._repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"Nutzer mit ID '{user_id}' nicht gefunden.")
        self._validate_password(new_password)
        user.password_hash = self._hash_password(new_password)
        self._repo.update(user)
        return user

    def update_user(
        self,
        user_id: str,
        requesting_user: User,
        name: str = None,
        email: str = None,
        role: UserRole = None,
        image_url: str = None,
        is_active: bool = None,
    ) -> User:
        """Bearbeitet wesentliche Nutzereigenschaften als Admin."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren können Nutzer bearbeiten.")
        user = self._repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"Nutzer mit ID '{user_id}' nicht gefunden.")

        if name is not None:
            if not name.strip():
                raise ValueError("Name darf nicht leer sein.")
            user.name = name.strip()
        if email is not None:
            normalized_email = email.lower().strip()
            if "@" not in normalized_email:
                raise ValueError("Ungültige E-Mail-Adresse.")
            existing = self._repo.find_any_by_email(normalized_email)
            if existing and existing.id != user.id:
                raise ValueError(f"E-Mail-Adresse '{normalized_email}' ist bereits registriert.")
            user.email = normalized_email
        if role is not None:
            user.role = role
        if image_url is not None:
            user.image_url = image_url
        if is_active is not None:
            user.is_active = bool(is_active)

        self._repo.update(user)
        return user

    def update_own_profile(
        self,
        user_id: str,
        name: str = None,
        email: str = None,
        image_url: str = None,
    ) -> User:
        """Aktualisiert ausschließlich die selbst verwaltbaren Profildaten."""
        user = self._repo.find_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("Nutzer nicht gefunden.")

        if name is not None:
            if not str(name).strip():
                raise ValueError("Name darf nicht leer sein.")
            user.name = str(name).strip()

        if email is not None:
            normalized_email = str(email).lower().strip()
            if "@" not in normalized_email:
                raise ValueError("Ungültige E-Mail-Adresse.")
            existing = self._repo.find_any_by_email(normalized_email)
            if existing and existing.id != user.id:
                raise ValueError(f"E-Mail-Adresse '{normalized_email}' ist bereits registriert.")
            user.email = normalized_email

        if image_url is not None:
            user.image_url = str(image_url).strip()

        self._repo.update(user)
        return user

    def change_own_password(self, user_id: str, current_password: str, new_password: str) -> User:
        """Ändert das eigene Passwort nach erneuter Passwortprüfung."""
        user = self._repo.find_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("Nutzer nicht gefunden.")
        if not self._verify_password(current_password, user.password_hash):
            raise AuthError("Das aktuelle Passwort ist falsch.")
        self._validate_password(new_password)
        if self._verify_password(new_password, user.password_hash):
            raise ValueError("Das neue Passwort muss sich vom aktuellen Passwort unterscheiden.")

        user.password_hash = self._hash_password(new_password)
        user.reset_token = ""
        user.reset_token_expires_at = ""
        self._repo.update(user)
        return user

    def deactivate_own_account(self, user_id: str, current_password: str) -> User:
        """Anonymisiert und deaktiviert das eigene Konto als Soft-Delete."""
        user = self._repo.find_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("Nutzer nicht gefunden.")
        if not self._verify_password(current_password, user.password_hash):
            raise AuthError("Das aktuelle Passwort ist falsch.")
        if user.is_admin():
            active_admins = self._repo.find_by_role(UserRole.ADMIN)
            if len(active_admins) <= 1:
                raise ValueError("Das letzte aktive Admin-Konto kann nicht gelöscht werden.")

        # Die interne ID bleibt für bestehende Buchungen und Audit-Ereignisse
        # erhalten. Personenbezogene Daten werden entfernt und die bisherige
        # E-Mail-Adresse wird dadurch für eine Neuregistrierung freigegeben.
        user.name = "Gelöschtes Konto"
        user.email = f"deleted+{user.id}@replan.invalid"
        user.image_url = ""
        user.password_hash = self._hash_password(secrets.token_urlsafe(32))
        user.reset_token = ""
        user.reset_token_expires_at = ""
        user.favorite_targets = []
        user.is_active = False
        self._repo.update(user)
        return user

    def request_password_reset(self, email: str) -> dict:
        """
        Generiert ein zeitlich begrenztes Reset-Token.

        Für die Demo wird das Token in der API-Antwort zurückgegeben. In einer
        produktiven Umgebung würde nur ein Link per E-Mail versendet.
        """
        user = self._repo.find_by_email(email)
        if not user:
            raise AuthError("E-Mail-Adresse nicht gefunden.")
        token = secrets.token_urlsafe(24)
        expires_at = (utc_now() + timedelta(hours=1)).isoformat()
        user.reset_token = token
        user.reset_token_expires_at = expires_at
        self._repo.update(user)
        return {
            "email": user.email,
            "reset_token": token,
            "expires_at": expires_at,
        }

    def reset_password_with_token(self, token: str, new_password: str) -> User:
        """Setzt ein Passwort anhand eines gültigen Reset-Tokens."""
        if not token:
            raise AuthError("Reset-Token fehlt.")
        self._validate_password(new_password)
        for user in self._repo.find_active():
            if user.reset_token != token:
                continue
            if not user.reset_token_expires_at or parse_iso_datetime(user.reset_token_expires_at) < utc_now():
                raise AuthError("Reset-Token ist abgelaufen.")
            user.password_hash = self._hash_password(new_password)
            user.reset_token = ""
            user.reset_token_expires_at = ""
            self._repo.update(user)
            return user
        raise AuthError("Reset-Token ist ungültig.")

    def generate_temporary_password(self) -> str:
        return secrets.token_urlsafe(9)

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

    def _validate_password(self, password: str) -> None:
        if not password or len(password) < 6:
            raise ValueError("Passwort muss mindestens 6 Zeichen lang sein.")

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
