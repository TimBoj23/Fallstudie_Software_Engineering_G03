import { useState } from "react";
import { KeyRound, LogIn } from "lucide-react";
import { forgotPassword, loginUser } from "../api/authApi.js";
import Button from "../components/Button.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function Login({ onLogin, setPage }) {
  const [form, setForm] = useState({ email: "", password: "" });
  const [resetForm, setResetForm] = useState({ email: "", new_password: "" });
  const [state, setState] = useState({ loading: false, error: "", success: "" });

  async function submit(event) {
    event.preventDefault();
    setState({ loading: true, error: "", success: "" });
    try {
      const result = await loginUser(form);
      onLogin(result.token, result.user);
    } catch (error) {
      setState({ loading: false, error: error.message, success: "" });
    }
  }

  async function submitReset(event) {
    event.preventDefault();
    setState({ loading: true, error: "", success: "" });
    try {
      await forgotPassword(resetForm);
      setState({ loading: false, error: "", success: "Passwort wurde zurückgesetzt." });
      setResetForm({ email: "", new_password: "" });
    } catch (error) {
      setState({ loading: false, error: error.message, success: "" });
    }
  }

  return (
    <div className="auth-page">
      <Panel title="Login" caption="Mit E-Mail und Passwort anmelden.">
        <form className="form-stack" onSubmit={submit}>
          {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
          {state.success && <StatusMessage type="success">{state.success}</StatusMessage>}
          <label>
            <span>E-Mail</span>
            <input
              type="email"
              value={form.email}
              onChange={(event) => setForm({ ...form, email: event.target.value })}
              required
            />
          </label>
          <label>
            <span>Passwort</span>
            <input
              type="password"
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
              required
            />
          </label>
          <Button type="submit" icon={LogIn} disabled={state.loading}>
            {state.loading ? "Anmeldung..." : "Einloggen"}
          </Button>
        </form>
        <div className="form-footer">
          <span>Noch kein Konto?</span>
          <button type="button" onClick={() => setPage("register")}>Registrieren</button>
        </div>
      </Panel>
      <Panel title="Passwort vergessen" caption="MVP-Funktion: neues Passwort direkt setzen.">
        <form className="form-stack" onSubmit={submitReset}>
          <label>
            <span>E-Mail</span>
            <input type="email" value={resetForm.email} onChange={(event) => setResetForm({ ...resetForm, email: event.target.value })} required />
          </label>
          <label>
            <span>Neues Passwort</span>
            <input type="password" value={resetForm.new_password} onChange={(event) => setResetForm({ ...resetForm, new_password: event.target.value })} required />
          </label>
          <Button type="submit" variant="secondary" icon={KeyRound} disabled={state.loading}>
            Passwort zurücksetzen
          </Button>
        </form>
      </Panel>
    </div>
  );
}
