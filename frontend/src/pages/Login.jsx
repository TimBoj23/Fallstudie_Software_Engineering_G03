import { useState } from "react";
import { KeyRound, LogIn } from "lucide-react";
import { loginUser, requestPasswordReset, resetPassword } from "../api/authApi.js";
import Button from "../components/Button.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function Login({ onLogin, setPage }) {
  const [form, setForm] = useState({ email: "", password: "" });
  const [resetForm, setResetForm] = useState({ email: "", token: "", new_password: "" });
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

  async function requestReset(event) {
    event.preventDefault();
    setState({ loading: true, error: "", success: "" });
    try {
      const result = await requestPasswordReset({ email: resetForm.email });
      const token = result.reset?.reset_token || "";
      setResetForm((current) => ({ ...current, token }));
      setState({
        loading: false,
        error: "",
        success: token
          ? "Reset-Token wurde für die lokale Demo erzeugt und eingetragen."
          : "Reset-Anfrage wurde erstellt. Bitte prüfen Sie Ihre E-Mail.",
      });
    } catch (error) {
      setState({ loading: false, error: error.message, success: "" });
    }
  }

  async function submitReset(event) {
    event.preventDefault();
    setState({ loading: true, error: "", success: "" });
    try {
      await resetPassword({ token: resetForm.token, new_password: resetForm.new_password });
      setState({ loading: false, error: "", success: "Passwort wurde sicher zurückgesetzt." });
      setResetForm({ email: "", token: "", new_password: "" });
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
      <Panel title="Passwort vergessen" caption="Zuerst Reset-Token anfordern, danach ein neues Passwort setzen.">
        <form className="form-stack" onSubmit={requestReset}>
          <label>
            <span>E-Mail</span>
            <input type="email" value={resetForm.email} onChange={(event) => setResetForm({ ...resetForm, email: event.target.value })} required />
          </label>
          <Button type="submit" variant="secondary" icon={KeyRound} disabled={state.loading}>
            Reset-Token anfordern
          </Button>
        </form>
        {resetForm.token && (
          <form className="form-stack" onSubmit={submitReset}>
            <label>
              <span>Reset-Token</span>
              <input value={resetForm.token} onChange={(event) => setResetForm({ ...resetForm, token: event.target.value })} required />
            </label>
            <label>
              <span>Neues Passwort</span>
              <input type="password" value={resetForm.new_password} onChange={(event) => setResetForm({ ...resetForm, new_password: event.target.value })} required />
            </label>
            <Button type="submit" variant="secondary" icon={KeyRound} disabled={state.loading}>
              Passwort zurücksetzen
            </Button>
          </form>
        )}
      </Panel>
    </div>
  );
}
