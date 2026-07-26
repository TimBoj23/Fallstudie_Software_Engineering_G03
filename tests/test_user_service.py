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

    def test_passwort_reset_token(self, user_service):
        user_service.register("Reset", "reset@test.de", "altpass123")
        reset = user_service.request_password_reset("reset@test.de")
        updated = user_service.reset_password_with_token(reset["reset_token"], "neupass123")

        assert updated.email == "reset@test.de"
        assert user_service.login("reset@test.de", "neupass123") is not None
        with pytest.raises(AuthError):
            user_service.login("reset@test.de", "altpass123")

    def test_favoriten_koennen_gesetzt_und_entfernt_werden(self, user_service):
        user = user_service.register("Favorit", "favorit@test.de", "pass123")
        favorites = user_service.set_favorite(user.id, "room", "room-1", True)
        assert favorites == [{"key": "room:room-1", "target_type": "room", "target_id": "room-1"}]

        assert user_service.set_favorite(user.id, "room", "room-1", False) == []

    def test_nutzersuche_filtert_admins(self, user_service):
        user_service.register("Normal", "normal@test.de", "pass123")
        user_service.register("Alex Admin", "alex@test.de", "pass123", role=UserRole.ADMIN)

        result = user_service.search_users(query="alex", role="admin", status="active")
        assert [user.email for user in result] == ["alex@test.de"]

    def test_eigenes_profil_kann_aktualisiert_werden(self, user_service):
        user = user_service.register("Alt", "alt@test.de", "pass123")

        updated = user_service.update_own_profile(
            user.id,
            name="Neuer Name",
            email="NEU@test.de",
            image_url="/pictures/profil.png",
        )

        assert updated.name == "Neuer Name"
        assert updated.email == "neu@test.de"
        assert updated.image_url == "/pictures/profil.png"
        assert updated.role == UserRole.USER

    def test_eigene_email_darf_nicht_doppelt_sein_auch_wenn_konto_inaktiv(self, user_service):
        admin = user_service.register("Admin", "admin@test.de", "admin123", role=UserRole.ADMIN)
        inactive = user_service.register("Inaktiv", "belegt@test.de", "pass123")
        user_service.deactivate(inactive.id, admin)
        current = user_service.register("Aktiv", "aktiv@test.de", "pass123")

        with pytest.raises(ValueError):
            user_service.update_own_profile(current.id, email="belegt@test.de")

    def test_eigenes_passwort_erfordert_aktuelles_passwort(self, user_service):
        user = user_service.register("Passwort", "passwort@test.de", "altpass123")

        with pytest.raises(AuthError):
            user_service.change_own_password(user.id, "falsch", "neupass123")

        user_service.change_own_password(user.id, "altpass123", "neupass123")
        assert user_service.login("passwort@test.de", "neupass123").id == user.id
        with pytest.raises(AuthError):
            user_service.login("passwort@test.de", "altpass123")

    def test_eigenes_konto_wird_sicher_deaktiviert(self, user_service):
        user = user_service.register("Delete", "delete@test.de", "pass123")

        user_service.deactivate_own_account(user.id, "pass123")

        deleted = user_service.get_by_id(user.id)
        assert deleted.is_active is False
        assert deleted.name == "Gelöschtes Konto"
        assert deleted.email == f"deleted+{user.id}@replan.invalid"
        with pytest.raises(AuthError):
            user_service.login("delete@test.de", "pass123")

        replacement = user_service.register("Neu", "delete@test.de", "neupass123")
        assert replacement.email == "delete@test.de"

    def test_letzter_admin_kann_sich_nicht_deaktivieren(self, user_service):
        admin = user_service.register("Admin", "admin@test.de", "admin123", role=UserRole.ADMIN)

        with pytest.raises(ValueError, match="letzte aktive Admin"):
            user_service.deactivate_own_account(admin.id, "admin123")
