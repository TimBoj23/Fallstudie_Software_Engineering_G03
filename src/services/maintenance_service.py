"""Abgesicherte Wartungsfunktionen für den lokalen Demo-Datenbestand."""

from ..models.user import UserRole
from ..repositories.audit_repository import AuditRepository
from ..repositories.booking_repository import BookingRepository
from ..repositories.user_repository import UserRepository
from .user_service import AuthError, UserService


RESET_CONFIRMATION = "DEMODATEN LÖSCHEN"


class MaintenanceService:
    def __init__(
        self,
        booking_repository=None,
        audit_repository=None,
        user_repository=None,
        user_service=None,
    ):
        self._bookings = booking_repository or BookingRepository()
        self._audit = audit_repository or AuditRepository()
        self._users = user_repository or UserRepository()
        self._user_service = user_service or UserService(self._users)

    def reset_demo_activity(self, requesting_user, current_password: str, confirmation: str) -> dict:
        """Entfernt Buchungen, Auditdaten und Nicht-Admins; Ressourcen bleiben erhalten."""
        if not requesting_user.is_admin():
            raise AuthError("Nur Administratoren dürfen Demodaten zurücksetzen.")
        if confirmation != RESET_CONFIRMATION:
            raise ValueError(f"Zur Bestätigung muss „{RESET_CONFIRMATION}“ eingegeben werden.")
        self._user_service.login(requesting_user.email, current_password)

        removed_bookings = self._bookings.delete_all()
        removed_audit_events = self._audit.delete_all()
        removed_users = self._users.retain(
            lambda user: user.role == UserRole.ADMIN and user.is_active
        )

        for admin in self._users.find_by_role(UserRole.ADMIN):
            admin.favorite_targets = []
            admin.reset_token = ""
            admin.reset_token_expires_at = ""
            self._users.update(admin)

        return {
            "removed_bookings": removed_bookings,
            "removed_audit_events": removed_audit_events,
            "removed_users": removed_users,
            "remaining_admins": len(self._users.find_by_role(UserRole.ADMIN)),
        }
