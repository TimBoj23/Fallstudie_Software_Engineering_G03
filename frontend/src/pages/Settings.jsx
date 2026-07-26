import { useEffect, useState } from "react";
import { KeyRound, Save, Trash2, Upload, UserRound } from "lucide-react";
import Button from "../components/Button.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";
import { mediaUrl } from "../api/client.js";
import { uploadProfilePicture } from "../api/picturesApi.js";
import { changeOwnPassword, deleteOwnAccount, updateOwnProfile } from "../api/usersApi.js";

const DELETE_CONFIRMATION = "KONTO LÖSCHEN";

export default function Settings({ user, isLoggedIn, setPage, onUserUpdated, onAccountDeleted }) {
  const [profile, setProfile] = useState({ name: user?.name || "", email: user?.email || "", image_url: user?.image_url || "" });
  const [pictureFile, setPictureFile] = useState(null);
  const [passwords, setPasswords] = useState({ current_password: "", new_password: "", repeat_password: "" });
  const [deletion, setDeletion] = useState({ current_password: "", confirmation: "" });
  const [profileState, setProfileState] = useState({ loading: false, error: "", success: "" });
  const [passwordState, setPasswordState] = useState({ loading: false, error: "", success: "" });
  const [deleteState, setDeleteState] = useState({ loading: false, error: "" });

  useEffect(() => {
    setProfile({ name: user?.name || "", email: user?.email || "", image_url: user?.image_url || "" });
  }, [user]);

  if (!isLoggedIn) {
    return (
      <div className="auth-page">
        <Panel title="Login erforderlich" caption="Melde dich an, um dein Konto zu verwalten.">
          <Button onClick={() => setPage("login")}>Zum Login</Button>
        </Panel>
      </div>
    );
  }

  async function saveProfile(event) {
    event.preventDefault();
    setProfileState({ loading: true, error: "", success: "" });
    try {
      let imageUrl = profile.image_url;
      if (pictureFile) {
        const upload = await uploadProfilePicture(pictureFile);
        imageUrl = upload.image_url;
      }
      const result = await updateOwnProfile({ name: profile.name, email: profile.email, image_url: imageUrl });
      setProfile({ name: result.user.name, email: result.user.email, image_url: result.user.image_url || "" });
      setPictureFile(null);
      onUserUpdated(result.user);
      setProfileState({ loading: false, error: "", success: "Profil wurde gespeichert." });
    } catch (error) {
      setProfileState({ loading: false, error: error.message, success: "" });
    }
  }

  async function savePassword(event) {
    event.preventDefault();
    if (passwords.new_password !== passwords.repeat_password) {
      setPasswordState({ loading: false, error: "Die neuen Passwörter stimmen nicht überein.", success: "" });
      return;
    }
    setPasswordState({ loading: true, error: "", success: "" });
    try {
      await changeOwnPassword({ current_password: passwords.current_password, new_password: passwords.new_password });
      setPasswords({ current_password: "", new_password: "", repeat_password: "" });
      setPasswordState({ loading: false, error: "", success: "Passwort wurde geändert." });
    } catch (error) {
      setPasswordState({ loading: false, error: error.message, success: "" });
    }
  }

  async function deleteAccount(event) {
    event.preventDefault();
    if (deletion.confirmation !== DELETE_CONFIRMATION) {
      setDeleteState({ loading: false, error: `Bitte „${DELETE_CONFIRMATION}“ vollständig eingeben.` });
      return;
    }
    setDeleteState({ loading: true, error: "" });
    try {
      await deleteOwnAccount(deletion.current_password);
      onAccountDeleted();
    } catch (error) {
      setDeleteState({ loading: false, error: error.message });
    }
  }

  return (
    <div className="page-stack settings-page">
      <section className="page-intro">
        <div>
          <p className="eyebrow">Mein Konto</p>
          <h2>Einstellungen</h2>
          <p>Persönliche Daten, Profilbild und Passwort selbst verwalten.</p>
        </div>
      </section>

      <div className="settings-grid">
        <Panel title="Profil" caption="Name, Login-E-Mail und Profilbild ändern.">
          <form className="form-stack" onSubmit={saveProfile}>
            <div className="settings-profile-picture">
              {profile.image_url ? (
                <img src={mediaUrl(profile.image_url)} alt="Aktuelles Profilbild" />
              ) : (
                <span className="settings-avatar-fallback"><UserRound size={28} /></span>
              )}
              <label className="picture-input">
                Neues Profilbild
                <input
                  type="file"
                  accept="image/avif,image/png,image/jpeg,image/webp"
                  onChange={(event) => setPictureFile(event.target.files?.[0] || null)}
                />
                {pictureFile && <small>{pictureFile.name}</small>}
              </label>
            </div>
            <label>
              Name
              <input value={profile.name} onChange={(event) => setProfile({ ...profile, name: event.target.value })} required />
            </label>
            <label>
              E-Mail-Adresse
              <input type="email" value={profile.email} onChange={(event) => setProfile({ ...profile, email: event.target.value })} required />
            </label>
            {profileState.error && <StatusMessage type="danger">{profileState.error}</StatusMessage>}
            {profileState.success && <StatusMessage type="success">{profileState.success}</StatusMessage>}
            <Button type="submit" icon={Save} disabled={profileState.loading}>
              {profileState.loading ? "Speichert …" : "Profil speichern"}
            </Button>
          </form>
        </Panel>

        <Panel title="Passwort ändern" caption="Zur Sicherheit ist dein aktuelles Passwort erforderlich.">
          <form className="form-stack" onSubmit={savePassword}>
            <label>
              Aktuelles Passwort
              <input type="password" autoComplete="current-password" value={passwords.current_password} onChange={(event) => setPasswords({ ...passwords, current_password: event.target.value })} required />
            </label>
            <label>
              Neues Passwort
              <input type="password" minLength="6" autoComplete="new-password" value={passwords.new_password} onChange={(event) => setPasswords({ ...passwords, new_password: event.target.value })} required />
            </label>
            <label>
              Neues Passwort wiederholen
              <input type="password" minLength="6" autoComplete="new-password" value={passwords.repeat_password} onChange={(event) => setPasswords({ ...passwords, repeat_password: event.target.value })} required />
            </label>
            {passwordState.error && <StatusMessage type="danger">{passwordState.error}</StatusMessage>}
            {passwordState.success && <StatusMessage type="success">{passwordState.success}</StatusMessage>}
            <Button type="submit" icon={KeyRound} disabled={passwordState.loading}>
              {passwordState.loading ? "Ändert …" : "Passwort ändern"}
            </Button>
          </form>
        </Panel>
      </div>

      <Panel title="Konto löschen" caption="Gefahrenbereich: Dieser Schritt beendet sofort deinen Zugriff." className="danger-panel">
        <form className="form-stack" onSubmit={deleteAccount}>
          <StatusMessage type="warning">
            Das Konto wird anonymisiert und deaktiviert. Buchungs- und Auditdaten bleiben zur Nachvollziehbarkeit erhalten; deine bisherige E-Mail-Adresse kann danach neu registriert werden. Das letzte aktive Admin-Konto ist geschützt.
          </StatusMessage>
          <div className="form-grid two">
            <label>
              Aktuelles Passwort
              <input type="password" autoComplete="current-password" value={deletion.current_password} onChange={(event) => setDeletion({ ...deletion, current_password: event.target.value })} required />
            </label>
            <label>
              Zur Bestätigung „{DELETE_CONFIRMATION}“ eingeben
              <input value={deletion.confirmation} onChange={(event) => setDeletion({ ...deletion, confirmation: event.target.value })} required />
            </label>
          </div>
          {deleteState.error && <StatusMessage type="danger">{deleteState.error}</StatusMessage>}
          <Button type="submit" variant="danger" icon={Trash2} disabled={deleteState.loading || deletion.confirmation !== DELETE_CONFIRMATION}>
            {deleteState.loading ? "Löscht …" : "Eigenes Konto löschen"}
          </Button>
        </form>
      </Panel>
    </div>
  );
}
