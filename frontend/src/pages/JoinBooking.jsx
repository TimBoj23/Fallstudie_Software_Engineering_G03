import { useState } from "react";
import { LogIn } from "lucide-react";
import { joinBookingByCode } from "../api/bookingsApi.js";
import Button from "../components/Button.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function JoinBooking({ initialCode = "" }) {
  const [form, setForm] = useState({ invitation_code: initialCode, email: "", access_password: "" });
  const [state, setState] = useState({ loading: false, error: "", success: "" });

  async function submit(event) {
    event.preventDefault();
    setState({ loading: true, error: "", success: "" });
    try {
      const result = await joinBookingByCode({
        invitation_code: form.invitation_code.trim().toUpperCase(),
        email: form.email,
        access_password: form.access_password,
      });
      setState({ loading: false, error: "", success: result.message });
      setForm({ ...form, access_password: "" });
    } catch (error) {
      setState({ loading: false, error: error.message, success: "" });
    }
  }

  return (
    <Panel
      title="Seminareinladung"
      caption="Mit Einladungscode, eingeladener E-Mail-Adresse und Passwort teilnehmen."
    >
      <form className="form-stack" onSubmit={submit}>
        {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
        {state.success && <StatusMessage type="success">{state.success}</StatusMessage>}
        <label>
          <span>Einladungscode</span>
          <input
            value={form.invitation_code}
            onChange={(event) => setForm({ ...form, invitation_code: event.target.value.toUpperCase() })}
            placeholder="RPL-ABC123"
            autoComplete="off"
            required
          />
          <small>Den Code erhältst du von der Person, die den Raum gebucht hat.</small>
        </label>
        <label>
          <span>E-Mail</span>
          <input type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required />
        </label>
        <label>
          <span>Buchungspasswort</span>
          <input type="password" value={form.access_password} onChange={(event) => setForm({ ...form, access_password: event.target.value })} required />
        </label>
        <Button type="submit" icon={LogIn} disabled={state.loading}>
          {state.loading ? "Einbuchung läuft..." : "Einladung annehmen"}
        </Button>
      </form>
    </Panel>
  );
}
