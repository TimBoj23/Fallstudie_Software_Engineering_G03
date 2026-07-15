import { useState } from "react";
import { LogIn } from "lucide-react";
import { loginUser } from "../api/authApi.js";
import Button from "../components/Button.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function Login({ onLogin, setPage }) {
  const [form, setForm] = useState({ email: "", password: "" });
  const [state, setState] = useState({ loading: false, error: "" });

  async function submit(event) {
    event.preventDefault();
    setState({ loading: true, error: "" });
    try {
      const result = await loginUser(form);
      onLogin(result.token, result.user);
    } catch (error) {
      setState({ loading: false, error: error.message });
    }
  }

  return (
    <div className="auth-page">
      <Panel title="Login" caption="Mit E-Mail und Passwort anmelden.">
        <form className="form-stack" onSubmit={submit}>
          {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
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
    </div>
  );
}
