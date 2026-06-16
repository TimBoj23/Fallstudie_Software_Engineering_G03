"""
Tests: BookingService – KERNLOGIK

Testet die zentrale Buchungslogik:
    - Erfolgreiche Buchungserstellung
    - Doppelbuchungs-Prävention (verschiedene Überschneidungsarten)
    - Stornierung
    - Berechtigungsprüfungen
    - Verfügbarkeitsprüfung
"""

import os
import sys
import uuid
import tempfile
import shutil
import pytest
from datetime import datetime, timedelta

# Projekt-Root zum Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.user import User, UserRole
from src.models.room import Room
from src.models.seat import Seat
from src.models.asset import Asset, AssetType
from src.models.booking import BookingTargetType, BookingStatus
from src.repositories.booking_repository import BookingRepository
from src.repositories.room_repository import RoomRepository
from src.repositories.seat_repository import SeatRepository
from src.repositories.asset_repository import AssetRepository
from src.services.booking_service import BookingService, BookingConflictError, BookingNotFoundError
from src.services.user_service import AuthError


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_data_dir():
    """Erstellt ein temporäres Verzeichnis für Test-JSON-Dateien."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


@pytest.fixture
def booking_repo(tmp_data_dir):
    repo = BookingRepository.__new__(BookingRepository)
    repo.__init__.__func__(repo) if False else None
    # Direkt initialisieren mit tmp path
    from src.repositories.base_repository import JsonRepository
    import threading
    repo._filepath = os.path.join(tmp_data_dir, "bookings.json")
    repo._lock = threading.Lock()
    repo._ensure_file_exists()
    return repo


@pytest.fixture
def room_repo(tmp_data_dir):
    from src.repositories.base_repository import JsonRepository
    import threading
    repo = RoomRepository.__new__(RoomRepository)
    repo._filepath = os.path.join(tmp_data_dir, "rooms.json")
    repo._lock = threading.Lock()
    repo._ensure_file_exists()
    return repo


@pytest.fixture
def asset_repo(tmp_data_dir):
    import threading
    repo = AssetRepository.__new__(AssetRepository)
    repo._filepath = os.path.join(tmp_data_dir, "assets.json")
    repo._lock = threading.Lock()
    repo._ensure_file_exists()
    return repo


@pytest.fixture
def seat_repo(tmp_data_dir):
    import threading
    repo = SeatRepository.__new__(SeatRepository)
    repo._filepath = os.path.join(tmp_data_dir, "seats.json")
    repo._lock = threading.Lock()
    repo._ensure_file_exists()
    return repo


@pytest.fixture
def demo_room(room_repo):
    room = Room(
        id=str(uuid.uuid4()),
        name="Meetingraum Alpha",
        number="TEST-001",
        capacity=10,
        location="EG",
    )
    room_repo.save(room)
    return room


@pytest.fixture
def demo_asset(asset_repo):
    asset = Asset(
        id=str(uuid.uuid4()),
        name="Beamer Test",
        asset_type=AssetType.BEAMER,
    )
    asset_repo.save(asset)
    return asset


@pytest.fixture
def user():
    return User(
        id=str(uuid.uuid4()),
        name="Test Nutzer",
        email="test@replan.de",
        role=UserRole.USER,
    )


@pytest.fixture
def admin():
    return User(
        id=str(uuid.uuid4()),
        name="Admin Nutzer",
        email="admin@replan.de",
        role=UserRole.ADMIN,
    )


@pytest.fixture
def booking_service(booking_repo, room_repo, seat_repo, asset_repo):
    return BookingService(
        booking_repository=booking_repo,
        room_repository=room_repo,
        seat_repository=seat_repo,
        asset_repository=asset_repo,
    )


def future(hours=2, duration=2):
    """Gibt ISO-8601 Zeitraum in der Zukunft zurück."""
    start = datetime.utcnow() + timedelta(hours=hours)
    end = start + timedelta(hours=duration)
    return start.strftime("%Y-%m-%dT%H:%M:%S"), end.strftime("%Y-%m-%dT%H:%M:%S")


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Buchung erstellen (Positiv-Fälle)
# ─────────────────────────────────────────────────────────────────────────────

class TestCreateBooking:

    def test_raum_erfolgreich_buchen(self, booking_service, demo_room, user):
        """Ein freier Raum kann erfolgreich gebucht werden."""
        start, end = future(hours=2, duration=2)
        booking = booking_service.create_booking(
            user=user,
            target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start,
            end_time=end,
            title="Teammeeting",
        )
        assert booking.id is not None
        assert booking.user_id == user.id
        assert booking.target_id == demo_room.id
        assert booking.target_type == BookingTargetType.ROOM
        assert booking.status == BookingStatus.ACTIVE
        assert booking.title == "Teammeeting"

    def test_asset_erfolgreich_buchen(self, booking_service, demo_asset, user):
        """Ein freies Asset kann erfolgreich gebucht werden."""
        start, end = future(hours=2, duration=1)
        booking = booking_service.create_booking(
            user=user,
            target_id=demo_asset.id,
            target_type=BookingTargetType.ASSET,
            start_time=start,
            end_time=end,
            title="Präsentation",
        )
        assert booking.id is not None
        assert booking.status == BookingStatus.ACTIVE

    def test_unterschiedliche_raeume_gleicher_zeitraum(
        self, booking_service, room_repo, user
    ):
        """Zwei verschiedene Räume können gleichzeitig gebucht werden."""
        r1 = Room(id=str(uuid.uuid4()), name="R1", number="R1", capacity=5)
        r2 = Room(id=str(uuid.uuid4()), name="R2", number="R2", capacity=5)
        room_repo.save(r1)
        room_repo.save(r2)

        start, end = future(hours=3, duration=2)
        b1 = booking_service.create_booking(
            user=user, target_id=r1.id,
            target_type=BookingTargetType.ROOM,
            start_time=start, end_time=end, title="Meeting R1",
        )
        b2 = booking_service.create_booking(
            user=user, target_id=r2.id,
            target_type=BookingTargetType.ROOM,
            start_time=start, end_time=end, title="Meeting R2",
        )
        assert b1.id != b2.id  # Beide Buchungen existieren

    def test_sitzplatz_direkt_erfolgreich_buchen(
        self, booking_service, demo_room, seat_repo, user
    ):
        """Ein einzelner Sitzplatz kann als eigene Entität gebucht werden."""
        seat = Seat(id=str(uuid.uuid4()), room_id=demo_room.id, label="A1")
        seat_repo.save(seat)
        start, end = future(hours=4, duration=1)

        booking = booking_service.create_booking(
            user=user,
            target_id=seat.id,
            target_type=BookingTargetType.SEAT,
            start_time=start,
            end_time=end,
            title="Arbeitsplatz",
        )

        assert booking.target_type == BookingTargetType.SEAT
        assert booking.target_id == seat.id
        assert booking.room_id == demo_room.id
        assert booking.auto_assigned_seat is False

    def test_raumbuchung_ohne_sitzplatz_weist_freien_sitzplatz_zu(
        self, booking_service, demo_room, seat_repo, user
    ):
        """Wenn ein Raum Sitzplätze hat, wird ohne Auswahl automatisch ein freier Platz gewählt."""
        seat = Seat(id=str(uuid.uuid4()), room_id=demo_room.id, label="A1")
        seat_repo.save(seat)
        start, end = future(hours=5, duration=1)

        booking = booking_service.create_booking(
            user=user,
            target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start,
            end_time=end,
            title="Automatische Platzwahl",
        )

        assert booking.target_type == BookingTargetType.SEAT
        assert booking.target_id == seat.id
        assert booking.room_id == demo_room.id
        assert booking.auto_assigned_seat is True

    def test_raumbuchung_mit_explizitem_sitzplatz(
        self, booking_service, demo_room, seat_repo, user
    ):
        """Bei einer Raumbuchung kann ein konkreter Sitzplatz angegeben werden."""
        seat = Seat(id=str(uuid.uuid4()), room_id=demo_room.id, label="Fenster")
        seat_repo.save(seat)
        start, end = future(hours=6, duration=1)

        booking = booking_service.create_booking(
            user=user,
            target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start,
            end_time=end,
            title="Explizite Platzwahl",
            seat_id=seat.id,
        )

        assert booking.target_type == BookingTargetType.SEAT
        assert booking.target_id == seat.id
        assert booking.auto_assigned_seat is False


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Doppelbuchungs-Prävention (KERN)
# ─────────────────────────────────────────────────────────────────────────────

class TestConflictPrevention:

    def test_identische_zeitraeume_werden_verhindert(
        self, booking_service, demo_room, user
    ):
        """Identischer Zeitraum → BookingConflictError."""
        start, end = future(hours=4, duration=2)
        booking_service.create_booking(
            user=user, target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start, end_time=end, title="Erste Buchung",
        )
        with pytest.raises(BookingConflictError):
            booking_service.create_booking(
                user=user, target_id=demo_room.id,
                target_type=BookingTargetType.ROOM,
                start_time=start, end_time=end, title="Doppelbuchung",
            )

    def test_ueberschneidung_am_anfang(self, booking_service, demo_room, user):
        """Neue Buchung beginnt VOR Ende der bestehenden → Konflikt."""
        # Bestehend: 10:00–12:00
        # Neu:       11:00–13:00  → Überschneidung!
        base = datetime.utcnow() + timedelta(hours=5)
        existing_start = base.strftime("%Y-%m-%dT%H:%M:%S")
        existing_end   = (base + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S")
        overlap_start  = (base + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
        overlap_end    = (base + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")

        booking_service.create_booking(
            user=user, target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=existing_start, end_time=existing_end,
            title="Bestehend",
        )
        with pytest.raises(BookingConflictError):
            booking_service.create_booking(
                user=user, target_id=demo_room.id,
                target_type=BookingTargetType.ROOM,
                start_time=overlap_start, end_time=overlap_end,
                title="Überschneidend",
            )

    def test_ueberschneidung_am_ende(self, booking_service, demo_room, user):
        """Neue Buchung endet NACH Beginn der bestehenden → Konflikt."""
        base = datetime.utcnow() + timedelta(hours=8)
        existing_start = (base + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
        existing_end   = (base + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")
        overlap_start  = base.strftime("%Y-%m-%dT%H:%M:%S")
        overlap_end    = (base + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S")

        booking_service.create_booking(
            user=user, target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=existing_start, end_time=existing_end,
            title="Bestehend",
        )
        with pytest.raises(BookingConflictError):
            booking_service.create_booking(
                user=user, target_id=demo_room.id,
                target_type=BookingTargetType.ROOM,
                start_time=overlap_start, end_time=overlap_end,
                title="Überschneidend",
            )

    def test_eingebettete_buchung_wird_verhindert(self, booking_service, demo_room, user):
        """Neue Buchung liegt VOLLSTÄNDIG innerhalb bestehender → Konflikt."""
        base = datetime.utcnow() + timedelta(hours=12)
        outer_start = base.strftime("%Y-%m-%dT%H:%M:%S")
        outer_end   = (base + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%S")
        inner_start = (base + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
        inner_end   = (base + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")

        booking_service.create_booking(
            user=user, target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=outer_start, end_time=outer_end,
            title="Äußere Buchung",
        )
        with pytest.raises(BookingConflictError):
            booking_service.create_booking(
                user=user, target_id=demo_room.id,
                target_type=BookingTargetType.ROOM,
                start_time=inner_start, end_time=inner_end,
                title="Innere Buchung",
            )

    def test_direkt_angrenzende_buchungen_erlaubt(self, booking_service, demo_room, user):
        """Buchung direkt nach Ende der vorherigen → KEIN Konflikt."""
        base = datetime.utcnow() + timedelta(hours=20)
        first_start  = base.strftime("%Y-%m-%dT%H:%M:%S")
        first_end    = (base + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S")
        second_start = first_end  # Genau am Ende der ersten!
        second_end   = (base + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%S")

        booking_service.create_booking(
            user=user, target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=first_start, end_time=first_end,
            title="Erste Buchung",
        )
        # Darf KEIN Fehler werfen
        b2 = booking_service.create_booking(
            user=user, target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=second_start, end_time=second_end,
            title="Direkt anschließend",
        )
        assert b2 is not None

    def test_belegter_sitzplatz_wird_bei_autozuweisung_uebersprungen(
        self, booking_service, demo_room, seat_repo, user
    ):
        """Automatische Zuweisung wählt den nächsten freien Sitzplatz."""
        s1 = Seat(id=str(uuid.uuid4()), room_id=demo_room.id, label="A1")
        s2 = Seat(id=str(uuid.uuid4()), room_id=demo_room.id, label="A2")
        seat_repo.save(s1)
        seat_repo.save(s2)
        start, end = future(hours=22, duration=2)

        booking_service.create_booking(
            user=user,
            target_id=s1.id,
            target_type=BookingTargetType.SEAT,
            start_time=start,
            end_time=end,
            title="Sitz A1",
        )
        auto_booking = booking_service.create_booking(
            user=user,
            target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start,
            end_time=end,
            title="Automatisch",
        )

        assert auto_booking.target_id == s2.id

    def test_sitzplatz_doppelbuchung_wird_verhindert(
        self, booking_service, demo_room, seat_repo, user
    ):
        """Derselbe Sitzplatz kann nicht doppelt gebucht werden."""
        seat = Seat(id=str(uuid.uuid4()), room_id=demo_room.id, label="A1")
        seat_repo.save(seat)
        start, end = future(hours=24, duration=2)
        booking_service.create_booking(
            user=user,
            target_id=seat.id,
            target_type=BookingTargetType.SEAT,
            start_time=start,
            end_time=end,
            title="Erste Sitzplatzbuchung",
        )

        with pytest.raises(BookingConflictError):
            booking_service.create_booking(
                user=user,
                target_id=seat.id,
                target_type=BookingTargetType.SEAT,
                start_time=start,
                end_time=end,
                title="Doppelte Sitzplatzbuchung",
            )

    def test_ganze_raumbuchung_blockiert_sitzplaetze(
        self, booking_service, demo_room, seat_repo, user
    ):
        """Eine klassische Raumbuchung ohne Sitzplatzdaten blockiert spätere Sitzplatzbuchungen."""
        seat = Seat(id=str(uuid.uuid4()), room_id=demo_room.id, label="A1")
        start, end = future(hours=26, duration=2)

        booking_service.create_booking(
            user=user,
            target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start,
            end_time=end,
            title="Ganze Raumbuchung",
        )
        seat_repo.save(seat)

        with pytest.raises(BookingConflictError):
            booking_service.create_booking(
                user=user,
                target_id=seat.id,
                target_type=BookingTargetType.SEAT,
                start_time=start,
                end_time=end,
                title="Sitzplatz im blockierten Raum",
            )


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Stornierung
# ─────────────────────────────────────────────────────────────────────────────

class TestCancellation:

    def test_nutzer_kann_eigene_buchung_stornieren(
        self, booking_service, demo_room, user
    ):
        start, end = future(hours=30, duration=2)
        booking = booking_service.create_booking(
            user=user, target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start, end_time=end, title="Zu stornieren",
        )
        cancelled = booking_service.cancel_booking(booking.id, user)
        assert cancelled.status == BookingStatus.CANCELLED

    def test_nutzer_kann_nicht_fremde_buchung_stornieren(
        self, booking_service, demo_room, user, admin
    ):
        """Ein normaler Nutzer darf nur eigene Buchungen stornieren."""
        other_user = User(
            id=str(uuid.uuid4()), name="Anderer", email="other@test.de", role=UserRole.USER
        )
        start, end = future(hours=32, duration=2)
        booking = booking_service.create_booking(
            user=other_user, target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start, end_time=end, title="Fremd",
        )
        with pytest.raises(AuthError):
            booking_service.cancel_booking(booking.id, user)

    def test_admin_kann_jede_buchung_stornieren(
        self, booking_service, demo_room, user, admin
    ):
        """Admin darf beliebige Buchungen stornieren."""
        start, end = future(hours=34, duration=2)
        booking = booking_service.create_booking(
            user=user, target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start, end_time=end, title="Fremd",
        )
        cancelled = booking_service.cancel_booking(booking.id, admin)
        assert cancelled.status == BookingStatus.CANCELLED

    def test_stornierte_buchung_gibt_slot_frei(
        self, booking_service, demo_room, user
    ):
        """Nach Stornierung kann derselbe Zeitraum neu gebucht werden."""
        start, end = future(hours=36, duration=2)
        b1 = booking_service.create_booking(
            user=user, target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start, end_time=end, title="Original",
        )
        booking_service.cancel_booking(b1.id, user)

        # Jetzt nochmals buchen – soll klappen
        b2 = booking_service.create_booking(
            user=user, target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start, end_time=end, title="Neubuchen",
        )
        assert b2.status == BookingStatus.ACTIVE


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Validierung
# ─────────────────────────────────────────────────────────────────────────────

class TestValidation:

    def test_start_nach_ende_wird_abgelehnt(self, booking_service, demo_room, user):
        """start_time >= end_time → ValueError."""
        base = datetime.utcnow() + timedelta(hours=50)
        start = base.strftime("%Y-%m-%dT%H:%M:%S")
        end   = (base - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
        with pytest.raises(ValueError):
            booking_service.create_booking(
                user=user, target_id=demo_room.id,
                target_type=BookingTargetType.ROOM,
                start_time=start, end_time=end, title="Ungültig",
            )

    def test_buchung_in_vergangenheit_wird_abgelehnt(
        self, booking_service, demo_room, user
    ):
        """Buchungen in der Vergangenheit → ValueError."""
        past_start = "2020-01-01T10:00:00"
        past_end   = "2020-01-01T12:00:00"
        with pytest.raises(ValueError):
            booking_service.create_booking(
                user=user, target_id=demo_room.id,
                target_type=BookingTargetType.ROOM,
                start_time=past_start, end_time=past_end, title="Vergangenheit",
            )

    def test_ungültiges_zeitformat_wird_abgelehnt(
        self, booking_service, demo_room, user
    ):
        """Ungültiges Zeitformat → ValueError."""
        with pytest.raises(ValueError):
            booking_service.create_booking(
                user=user, target_id=demo_room.id,
                target_type=BookingTargetType.ROOM,
                start_time="kein-datum", end_time="auch-nicht",
                title="Formatfehler",
            )

    def test_nicht_existenter_raum_wird_abgelehnt(self, booking_service, user):
        """Buchung für nicht existenten Raum → ValueError."""
        start, end = future(hours=60, duration=1)
        with pytest.raises(ValueError):
            booking_service.create_booking(
                user=user, target_id="nicht-existente-id",
                target_type=BookingTargetType.ROOM,
                start_time=start, end_time=end, title="Ghost",
            )


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Verfügbarkeitsprüfung
# ─────────────────────────────────────────────────────────────────────────────

class TestAvailability:

    def test_freier_raum_ist_verfügbar(self, booking_service, demo_room):
        start, end = future(hours=70, duration=2)
        is_avail, conflicts = booking_service.check_availability(
            target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start, end_time=end,
        )
        assert is_avail is True
        assert len(conflicts) == 0

    def test_gebuchter_raum_ist_nicht_verfügbar(
        self, booking_service, demo_room, user
    ):
        start, end = future(hours=72, duration=2)
        booking_service.create_booking(
            user=user, target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start, end_time=end, title="Blockiert",
        )
        is_avail, conflicts = booking_service.check_availability(
            target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start, end_time=end,
        )
        assert is_avail is False
        assert len(conflicts) > 0

    def test_raum_mit_freiem_sitzplatz_bleibt_verfuegbar(
        self, booking_service, demo_room, seat_repo, user
    ):
        """Bei Sitzplatzräumen reicht ein freier Sitzplatz für Raum-Verfügbarkeit."""
        s1 = Seat(id=str(uuid.uuid4()), room_id=demo_room.id, label="A1")
        s2 = Seat(id=str(uuid.uuid4()), room_id=demo_room.id, label="A2")
        seat_repo.save(s1)
        seat_repo.save(s2)
        start, end = future(hours=74, duration=2)
        booking_service.create_booking(
            user=user,
            target_id=s1.id,
            target_type=BookingTargetType.SEAT,
            start_time=start,
            end_time=end,
            title="Sitz A1",
        )

        is_avail, conflicts = booking_service.check_availability(
            target_id=demo_room.id,
            target_type=BookingTargetType.ROOM,
            start_time=start,
            end_time=end,
        )

        assert is_avail is True
        assert conflicts == []
