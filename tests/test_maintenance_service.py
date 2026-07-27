import os
import threading
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from src.models.audit_event import AuditEvent
from src.models.booking import Booking, BookingTargetType
from src.models.user import UserRole
from src.repositories.audit_repository import AuditRepository
from src.repositories.booking_repository import BookingRepository
from src.repositories.user_repository import UserRepository
from src.services.maintenance_service import MaintenanceService, RESET_CONFIRMATION
from src.services.user_service import AuthError, UserService


def repository(repository_type, directory, name):
    repo = repository_type.__new__(repository_type)
    repo._filepath = os.path.join(directory, name)
    repo._lock = threading.Lock()
    repo._storage = "json"
    repo._ensure_file_exists()
    return repo


def test_demo_reset_behaelt_admins_und_entfernt_aktivitaet(tmp_path):
    users = repository(UserRepository, str(tmp_path), "users.json")
    bookings = repository(BookingRepository, str(tmp_path), "bookings.json")
    audit = repository(AuditRepository, str(tmp_path), "audit_events.json")
    user_service = UserService(users)
    admin = user_service.register("Admin", "admin@replan.de", "admin123", UserRole.ADMIN)
    normal = user_service.register("Normal", "normal@replan.de", "normal123")
    start = datetime.now(timezone.utc) + timedelta(days=1)
    bookings.save(Booking(
        id=str(uuid.uuid4()), user_id=normal.id, target_id="room-1",
        target_type=BookingTargetType.ROOM, title="Test",
        start_time=start.isoformat(), end_time=(start + timedelta(hours=1)).isoformat(),
    ))
    audit.save(AuditEvent(
        id=str(uuid.uuid4()), actor_user_id=normal.id, action="booking.created",
        entity_type="booking", entity_id="booking-1", summary="Test",
    ))
    service = MaintenanceService(bookings, audit, users, user_service)

    result = service.reset_demo_activity(admin, "admin123", RESET_CONFIRMATION)

    assert result == {
        "removed_bookings": 1,
        "removed_audit_events": 1,
        "removed_users": 1,
        "remaining_admins": 1,
    }
    assert users.find_by_email("admin@replan.de").id == admin.id
    assert users.find_by_email("normal@replan.de") is None
    assert bookings.count() == 0
    assert audit.count() == 0


def test_demo_reset_erfordert_passwort_und_bestaetigung(tmp_path):
    users = repository(UserRepository, str(tmp_path), "users.json")
    bookings = repository(BookingRepository, str(tmp_path), "bookings.json")
    audit = repository(AuditRepository, str(tmp_path), "audit_events.json")
    user_service = UserService(users)
    admin = user_service.register("Admin", "admin@replan.de", "admin123", UserRole.ADMIN)
    service = MaintenanceService(bookings, audit, users, user_service)

    with pytest.raises(ValueError, match="DEMODATEN LÖSCHEN"):
        service.reset_demo_activity(admin, "admin123", "falsch")
    with pytest.raises(AuthError):
        service.reset_demo_activity(admin, "falsch", RESET_CONFIRMATION)
