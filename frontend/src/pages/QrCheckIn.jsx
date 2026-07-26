import { useEffect, useState } from "react";
import { QrCode } from "lucide-react";
import { qrCheckIn } from "../api/bookingsApi.js";
import Button from "../components/Button.jsx";
import EmptyState from "../components/EmptyState.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function QrCheckIn({ token, isLoggedIn, setPage }) {
  const [state, setState] = useState({ loading: false, error: "", success: "" });

  useEffect(() => {
    if (!isLoggedIn || !token) return;
    setState({ loading: true, error: "", success: "" });
    qrCheckIn(token)
      .then(() => setState({ loading: false, error: "", success: "QR-Check-in erfolgreich." }))
      .catch((error) => setState({ loading: false, error: error.message, success: "" }));
  }, [isLoggedIn, token]);

  if (!isLoggedIn) {
    return <Panel title="QR-Check-in"><EmptyState title="Bitte anmelden" text="Melde dich an und öffne den QR-Code anschließend erneut." action={<Button onClick={() => setPage("login")}>Zum Login</Button>} /></Panel>;
  }
  return (
    <Panel title="QR-Check-in" caption="Signierter Check-in für deine Buchung.">
      {state.loading && <StatusMessage>Check-in wird geprüft…</StatusMessage>}
      {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
      {state.success && <StatusMessage type="success">{state.success}</StatusMessage>}
      {!token && <EmptyState title="Kein QR-Code" text="Öffne den QR-Code aus deiner Buchungsübersicht." />}
      <Button icon={QrCode} variant="secondary" onClick={() => setPage("bookings")}>Zu meinen Buchungen</Button>
    </Panel>
  );
}
