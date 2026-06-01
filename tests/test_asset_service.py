"""
Tests: AssetService
"""
import os, sys, uuid, tempfile, shutil, threading, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.user import User, UserRole
from src.models.asset import AssetType
from src.repositories.asset_repository import AssetRepository
from src.services.asset_service import AssetService
from src.services.user_service import AuthError


@pytest.fixture
def tmp_asset_repo():
    d = tempfile.mkdtemp()
    repo = AssetRepository.__new__(AssetRepository)
    repo._filepath = os.path.join(d, "assets.json")
    import threading
    repo._lock = threading.Lock()
    repo._ensure_file_exists()
    yield repo
    shutil.rmtree(d)


@pytest.fixture
def asset_service(tmp_asset_repo):
    return AssetService(asset_repository=tmp_asset_repo)


@pytest.fixture
def admin():
    return User(id=str(uuid.uuid4()), name="Admin", email="a@a.de", role=UserRole.ADMIN)


@pytest.fixture
def user():
    return User(id=str(uuid.uuid4()), name="User", email="u@u.de", role=UserRole.USER)


class TestAssetService:

    def test_asset_anlegen(self, asset_service, admin):
        asset = asset_service.create(
            name="Beamer X1", asset_type=AssetType.BEAMER,
            description="HD Beamer", requesting_user=admin,
        )
        assert asset.id is not None
        assert asset.asset_type == AssetType.BEAMER

    def test_asset_ohne_admin_abgelehnt(self, asset_service, user):
        with pytest.raises(AuthError):
            asset_service.create(
                name="Verboten", asset_type=AssetType.LAPTOP,
                requesting_user=user,
            )

    def test_leerer_name_wird_abgelehnt(self, asset_service, admin):
        with pytest.raises(ValueError):
            asset_service.create(name="  ", asset_type=AssetType.MONITOR, requesting_user=admin)

    def test_asset_abrufen(self, asset_service, admin):
        a = asset_service.create(name="Laptop L1", asset_type=AssetType.LAPTOP, requesting_user=admin)
        found = asset_service.get_by_id(a.id)
        assert found is not None

    def test_nach_typ_filtern(self, asset_service, admin):
        asset_service.create(name="Beamer A", asset_type=AssetType.BEAMER, requesting_user=admin)
        asset_service.create(name="Laptop B", asset_type=AssetType.LAPTOP, requesting_user=admin)
        beamer = asset_service.get_by_type(AssetType.BEAMER)
        assert all(a.asset_type == AssetType.BEAMER for a in beamer)

    def test_asset_deaktivieren(self, asset_service, admin):
        a = asset_service.create(name="Whiteboard", asset_type=AssetType.WHITEBOARD, requesting_user=admin)
        asset_service.deactivate(a.id, admin)
        assert asset_service.get_by_id(a.id) is None
