"""Bereinigt lokale Demoaktivität, ohne Ressourcen oder aktive Admins zu löschen.

Beispiele:
    REPLAN_STORAGE=sqlite python3 scripts/reset_demo_activity.py --yes
    REPLAN_STORAGE=json python3 scripts/reset_demo_activity.py --yes
"""

import argparse
import os
import shutil
import sys
from datetime import datetime


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.models.user import UserRole
from src.repositories.audit_repository import AuditRepository
from src.repositories.booking_repository import BookingRepository
from src.repositories.seat_repository import SeatRepository
from src.repositories.user_repository import UserRepository


def backup_sqlite() -> str:
    database = os.environ.get("REPLAN_DB_PATH", os.path.join(ROOT, "data", "replan.sqlite"))
    if not os.path.exists(database):
        return ""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = os.path.join("/private/tmp", f"replan-before-reset-{stamp}.sqlite")
    shutil.copy2(database, backup)
    return backup


def reset() -> dict:
    users = UserRepository()
    bookings = BookingRepository()
    audit = AuditRepository()
    seats = SeatRepository()
    removed_bookings = bookings.delete_all()
    removed_audit = audit.delete_all()
    removed_users = users.retain(
        lambda user: user.role == UserRole.ADMIN and user.is_active
    )
    removed_inactive_seats = seats.retain(lambda seat: seat.is_active)
    for admin in users.find_by_role(UserRole.ADMIN):
        admin.favorite_targets = []
        admin.reset_token = ""
        admin.reset_token_expires_at = ""
        users.update(admin)
    return {
        "Buchungen": removed_bookings,
        "Protokolle": removed_audit,
        "Nicht-Admin-Konten": removed_users,
        "inaktive Sitzplatzreste": removed_inactive_seats,
        "verbleibende Admins": len(users.find_by_role(UserRole.ADMIN)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes", action="store_true", help="Bestätigt die endgültige lokale Bereinigung.")
    args = parser.parse_args()
    if not args.yes:
        raise SystemExit("Abgebrochen. Für die bewusste Ausführung --yes ergänzen.")
    backup = backup_sqlite() if os.environ.get("REPLAN_STORAGE", "sqlite").lower() == "sqlite" else ""
    result = reset()
    if backup:
        print(f"Sicherung: {backup}")
    for label, value in result.items():
        print(f"{label}: {value}")


if __name__ == "__main__":
    main()
