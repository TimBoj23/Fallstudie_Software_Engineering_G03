import { useState } from "react";
import { UserPlus } from "lucide-react";
import { registerUser } from "../api/authApi.js";
import Button from "../components/Button.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function Register({ setPage }) {
  const [form, setForm] = useState({ name: "", email: "", password: "", repeat: "" });
  const [state, setState] = useState({ loading: false, error: "", success: "" });

  async function submit(event) {
    event.preventDefault();
    if (form.password !== form.repeat) {
      setState({ loading: false, error: "Passwoerter stimmen nicht überein.", success: "" });
      return;
    }
    setState({ loading: true, error: "", success: "" });
    try {
      await registerUser({ name: form.name, email: form.email, password: form.password });
      setState({ loading: false, error: "", success: "Konto erstellt. Du kannst dich jetzt einloggen." });
    } catch (error) {
      setState({ loading: false, error: error.message, success: "" });
    }
  }

  return (
    <div className="auth-page">
      <Panel title="Registrieren" caption="Ein neues Nutzerkonto für Buchungen anlegen.">
        <form className="form-stack" onSubmit={submit}>
          {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
          {state.success && <StatusMessage type="success">{state.success}</StatusMessage>}
          <label>
            <span>Name</span>
            <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
          </label>
          <label>
            <span>E-Mail</span>
            <input type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required />
          </label>
          <div className="form-grid two">
            <label>
              <span>Passwort</span>
              <input type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} required />
            </label>
            <label>
              <span>Wiederholen</span>
              <input type="password" value={form.repeat} onChange={(event) => setForm({ ...form, repeat: event.target.value })} required />
            </label>
          </div>
          <Button type="submit" icon={UserPlus} disabled={state.loading}>
            {state.loading ? "Registrierung..." : "Konto erstellen"}
          </Button>
        </form>
        <div className="form-footer">
          <span>Schon registriert?</span>
          <button type="button" onClick={() => setPage("login")}>Zum Login</button>
        </div>
      </Panel>
    </div>
  );
}
