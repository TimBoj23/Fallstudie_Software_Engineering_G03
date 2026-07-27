import { useEffect, useState } from "react";
import { PlusCircle, RefreshCw } from "lucide-react";
import { cancelBooking, checkInBooking, checkOutBooking, extendBooking, getBookings, updateBooking } from "../api/bookingsApi.js";
import BookingCard from "../components/BookingCard.jsx";
import BookingEditForm from "../components/BookingEditForm.jsx";
import Button from "../components/Button.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function MyBookings({ isLoggedIn, setPage, openCreateBooking }) {
  const [state, setState] = useState({ loading: false, error: "", success: "", bookings: [] });
  const [filters, setFilters] = useState({ target_type: "", start: "", end: "" });
  const [editing, setEditing] = useState(null);

  async function load(params = filters) {
    if (!isLoggedIn) return;
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      const data = await getBookings(params);
      setState({ loading: false, error: "", success: "", bookings: data.bookings || [] });
    } catch (error) {
      setState({ loading: false, error: error.message, success: "", bookings: [] });
    }
  }

  useEffect(() => {
    load();
  }, [isLoggedIn]);

  async function handleCancel(id, scope = "single") {
    const question = scope === "future"
      ? "Diesen und alle folgenden Serientermine wirklich stornieren?"
      : "Diese Buchung wirklich stornieren?";
    if (!window.confirm(question)) return;
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      await cancelBooking(id, scope);
      const data = await getBookings(filters);
      setState({ loading: false, error: "", success: "Buchung wurde storniert.", bookings: data.bookings || [] });
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error.message, success: "" }));
    }
  }

  async function handleEdit(payload) {
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      await updateBooking(editing.id, payload);
      const data = await getBookings(filters);
      setEditing(null);
      setState({ loading: false, error: "", success: "Buchung wurde aktualisiert.", bookings: data.bookings || [] });
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error.message, success: "" }));
    }
  }

  async function handleExtend(id, minutes) {
    if (!window.confirm(`Buchung um ${minutes} Minuten verlängern?`)) return;
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      await extendBooking(id, minutes);
      const data = await getBookings(filters);
      setState({ loading: false, error: "", success: `Buchung wurde um ${minutes} Minuten verlängert.`, bookings: data.bookings || [] });
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error.message, success: "" }));
    }
  }

  async function handleAttendance(id, action) {
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      if (action === "check-in") await checkInBooking(id);
      else await checkOutBooking(id);
      const data = await getBookings(filters);
      setState({
        loading: false,
        error: "",
        success: action === "check-in" ? "Check-in erfolgreich." : "Check-out erfolgreich.",
        bookings: data.bookings || [],
      });
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
        <form className="filter-bar" onSubmit={(event) => { event.preventDefault(); load(filters); }}>
          <select value={filters.target_type} onChange={(event) => setFilters({ ...filters, target_type: event.target.value })}>
            <option value="">Alle Typen</option>
            <option value="room">Seminarräume</option>
            <option value="seat">Sitzplätze</option>
            <option value="asset">Assets</option>
          </select>
          <input type="datetime-local" value={filters.start} onChange={(event) => setFilters({ ...filters, start: event.target.value })} />
          <input type="datetime-local" value={filters.end} onChange={(event) => setFilters({ ...filters, end: event.target.value })} />
          <Button type="submit" variant="secondary">Historie filtern</Button>
        </form>
      </Panel>

      {editing && (
        <BookingEditForm
          booking={editing}
          onSave={handleEdit}
          onClose={() => setEditing(null)}
          saving={state.loading}
          error={state.error}
        />
      )}

      {state.loading ? <LoadingState /> : (
        <div className="booking-list">
          {state.bookings.length === 0 ? (
            <EmptyState
              title="Noch keine Buchungen"
              text="Erstelle deine erste Reservierung für einen Raum, Arbeitsplatz oder Ausstattung."
              action={<Button icon={PlusCircle} onClick={() => setPage("createBooking")}>Buchung erstellen</Button>}
            />
          ) : state.bookings.map((booking) => (
            <BookingCard
              key={booking.id}
              booking={booking}
              onCancel={handleCancel}
              onAttendance={handleAttendance}
              onEdit={setEditing}
              onExtend={handleExtend}
              onCopy={(item) => openCreateBooking({
                targetType: item.target_type,
                targetId: item.target_id,
                title: item.title,
              })}
            />
          ))}
        </div>
      )}
    </div>
  );
}
