"""
Tests: RoomService
"""
import os, sys, uuid, tempfile, shutil, threading, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.user import User, UserRole
from src.models.room import Room
from src.repositories.room_repository import RoomRepository
from src.services.room_service import RoomService
from src.services.user_service import AuthError


@pytest.fixture
def tmp_room_repo():
    d = tempfile.mkdtemp()
    repo = RoomRepository.__new__(RoomRepository)
    repo._filepath = os.path.join(d, "rooms.json")
    repo._lock = threading.Lock()
    repo._ensure_file_exists()
    yield repo
    shutil.rmtree(d)


@pytest.fixture
def room_service(tmp_room_repo):
    return RoomService(room_repository=tmp_room_repo)


@pytest.fixture
def admin():
    return User(id=str(uuid.uuid4()), name="Admin", email="a@a.de", role=UserRole.ADMIN)


@pytest.fixture
def user():
    return User(id=str(uuid.uuid4()), name="User", email="u@u.de", role=UserRole.USER)


class TestRoomService:

    def test_raum_anlegen(self, room_service, admin):
        room = room_service.create(
            name="Testraum", number="T-001", capacity=8,
            location="EG", requesting_user=admin,
        )
        assert room.id is not None
        assert room.name == "Testraum"
        assert room.number == "T-001"
        assert room.capacity == 8
        assert room.is_active is True

    def test_raum_ohne_admin_wird_abgelehnt(self, room_service, user):
        with pytest.raises(AuthError):
            room_service.create(
                name="Verboten", number="X-001", capacity=5,
                requesting_user=user,
            )

    def test_doppelte_raumnummer_wird_abgelehnt(self, room_service, admin):
        room_service.create(name="R1", number="DUP-001", capacity=5, requesting_user=admin)
        with pytest.raises(ValueError):
            room_service.create(name="R2", number="DUP-001", capacity=3, requesting_user=admin)

    def test_kapazitaet_null_wird_abgelehnt(self, room_service, admin):
        with pytest.raises(ValueError):
            room_service.create(name="Leer", number="L-001", capacity=0, requesting_user=admin)

    def test_raum_abrufen(self, room_service, admin):
        created = room_service.create(name="Abruf", number="A-001", capacity=4, requesting_user=admin)
        found = room_service.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id

    def test_nicht_existenter_raum_gibt_none(self, room_service):
        assert room_service.get_by_id("nicht-existent") is None

    def test_raum_aktualisieren(self, room_service, admin):
        room = room_service.create(name="Alt", number="U-001", capacity=5, requesting_user=admin)
        updated = room_service.update(
            room_id=room.id, requesting_user=admin, name="Neu", capacity=12
        )
        assert updated.name == "Neu"
        assert updated.capacity == 12

    def test_raum_deaktivieren(self, room_service, admin):
        room = room_service.create(name="Aktiv", number="D-001", capacity=3, requesting_user=admin)
        room_service.deactivate(room.id, admin)
        assert room_service.get_by_id(room.id) is None

    def test_alle_raeume_abrufen(self, room_service, admin):
        room_service.create(name="R1", number="ALL-001", capacity=2, requesting_user=admin)
        room_service.create(name="R2", number="ALL-002", capacity=3, requesting_user=admin)
        rooms = room_service.get_all()
        numbers = [r.number for r in rooms]
        assert "ALL-001" in numbers
        assert "ALL-002" in numbers

    def test_filter_nach_kapazitaet(self, room_service, admin):
        room_service.create(name="Klein", number="K-001", capacity=3, requesting_user=admin)
        room_service.create(name="Groß", number="K-002", capacity=20, requesting_user=admin)
        big = room_service.filter_by_capacity(10)
        assert all(r.capacity >= 10 for r in big)
