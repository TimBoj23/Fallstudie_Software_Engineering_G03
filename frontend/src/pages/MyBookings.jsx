import { useEffect, useState } from "react";
import { PlusCircle, RefreshCw } from "lucide-react";
import { cancelBooking, getBookings } from "../api/bookingsApi.js";
import BookingCard from "../components/BookingCard.jsx";
import Button from "../components/Button.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function MyBookings({ isLoggedIn, setPage }) {
  const [state, setState] = useState({ loading: false, error: "", success: "", bookings: [] });

  async function load() {
    if (!isLoggedIn) return;
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      const data = await getBookings();
      setState({ loading: false, error: "", success: "", bookings: data.bookings || [] });
    } catch (error) {
      setState({ loading: false, error: error.message, success: "", bookings: [] });
    }
  }

  useEffect(() => {
    load();
  }, [isLoggedIn]);

  async function handleCancel(id) {
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      await cancelBooking(id);
      const data = await getBookings();
      setState({ loading: false, error: "", success: "Buchung wurde storniert.", bookings: data.bookings || [] });
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error.message, success: "" }));
    }
  }

  if (!isLoggedIn) {
    return (
      <Panel title="Meine Buchungen" caption="Login erforderlich.">
        <EmptyState
          title="Bitte zuerst einloggen"
          text="Eigene Buchungen können nur einem angemeldeten Nutzer angezeigt werden."
          action={<Button onClick={() => setPage("login")}>Zum Login</Button>}
        />
      </Panel>
    );
  }

  return (
    <div className="page-stack">
      <Panel
        title="Meine Buchungen"
        caption="Aktive und stornierte Reservierungen deines Kontos."
        actions={<Button variant="secondary" icon={RefreshCw} onClick={load}>Aktualisieren</Button>}
      >
        {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
        {state.success && <StatusMessage type="success">{state.success}</StatusMessage>}
      </Panel>

      {state.loading ? <LoadingState /> : (
        <div className="booking-list">
          {state.bookings.length === 0 ? (
            <EmptyState
              title="Noch keine Buchungen"
              text="Erstelle deine erste Reservierung für einen Raum, Arbeitsplatz oder Ausstattung."
              action={<Button icon={PlusCircle} onClick={() => setPage("createBooking")}>Buchung erstellen</Button>}
            />
          ) : state.bookings.map((booking) => (
            <BookingCard key={booking.id} booking={booking} onCancel={handleCancel} />
          ))}
        </div>
      )}
    </div>
  );
}
