"""
Tests: UserService
"""
import os, sys, uuid, tempfile, shutil, threading, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.user import UserRole
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService, AuthError


@pytest.fixture
def tmp_user_repo():
    d = tempfile.mkdtemp()
    repo = UserRepository.__new__(UserRepository)
    repo._filepath = os.path.join(d, "users.json")
    repo._lock = threading.Lock()
    repo._ensure_file_exists()
    yield repo
    shutil.rmtree(d)


@pytest.fixture
def user_service(tmp_user_repo):
    return UserService(user_repository=tmp_user_repo)


class TestUserService:

    def test_registrierung_erfolgreich(self, user_service):
        user = user_service.register("Max Muster", "max@test.de", "sicher123")
        assert user.id is not None
        assert user.email == "max@test.de"
        assert user.role == UserRole.USER
        assert user.password_hash != "sicher123"  # Muss gehasht sein

    def test_doppelte_email_wird_abgelehnt(self, user_service):
        user_service.register("User A", "doppelt@test.de", "pass123")
        with pytest.raises(ValueError):
            user_service.register("User B", "doppelt@test.de", "pass456")

    def test_kurzes_passwort_wird_abgelehnt(self, user_service):
        with pytest.raises(ValueError):
            user_service.register("User", "x@x.de", "12345")  # < 6 Zeichen

    def test_ungültige_email_wird_abgelehnt(self, user_service):
        with pytest.raises(ValueError):
            user_service.register("User", "kein-at-zeichen", "passwort123")

    def test_login_erfolgreich(self, user_service):
        user_service.register("Login Test", "login@test.de", "richtig123")
        logged_in = user_service.login("login@test.de", "richtig123")
        assert logged_in.email == "login@test.de"

    def test_falsches_passwort_abgelehnt(self, user_service):
        user_service.register("Fail Test", "fail@test.de", "richtig123")
        with pytest.raises(AuthError):
            user_service.login("fail@test.de", "falsch!")

    def test_nicht_registrierte_email_abgelehnt(self, user_service):
        with pytest.raises(AuthError):
            user_service.login("niemals@registriert.de", "egal")

    def test_email_gross_kleinschreibung_ignoriert(self, user_service):
        user_service.register("Case Test", "CASE@test.de", "pass123")
        user = user_service.login("case@TEST.de", "pass123")
        assert user is not None

    def test_admin_registrierung(self, user_service):
        admin = user_service.register("Admin", "admin@test.de", "admin123", role=UserRole.ADMIN)
        assert admin.role == UserRole.ADMIN
        assert admin.is_admin() is True

    def test_nutzer_abrufen(self, user_service):
        created = user_service.register("Abruf", "abruf@test.de", "pass123")
        found = user_service.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id
