import { useEffect, useMemo, useState } from "react";
import { CalendarPlus } from "lucide-react";
import { getAssets } from "../api/assetsApi.js";
import { createBooking } from "../api/bookingsApi.js";
import { getRooms } from "../api/roomsApi.js";
import { getSeats } from "../api/seatsApi.js";
import Button from "../components/Button.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

const targetTypes = [
  { value: "room", label: "Raum" },
  { value: "seat", label: "Arbeitsplatz" },
  { value: "asset", label: "Ausstattung" },
];

export default function CreateBooking({ isLoggedIn, setPage }) {
  const [form, setForm] = useState({
    target_type: "room",
    target_id: "",
    title: "",
    start_time: "",
    end_time: "",
  });
  const [resources, setResources] = useState({ rooms: [], seats: [], assets: [] });
  const [state, setState] = useState({ loading: false, loadingResources: true, error: "", success: "", conflicts: [] });

  useEffect(() => {
    if (!isLoggedIn) return;
    let ignore = false;
    async function loadResources() {
      try {
        const [rooms, seats, assets] = await Promise.all([getRooms(), getSeats(), getAssets()]);
        if (!ignore) {
          setResources({
            rooms: rooms.rooms || [],
            seats: seats.seats || [],
            assets: assets.assets || [],
          });
          setState((current) => ({ ...current, loadingResources: false }));
        }
      } catch (error) {
        if (!ignore) {
          setState((current) => ({ ...current, loadingResources: false, error: error.message }));
        }
      }
    }
    loadResources();
    return () => {
      ignore = true;
    };
  }, [isLoggedIn]);

  const options = useMemo(() => buildOptions(form.target_type, resources), [form.target_type, resources]);

  async function submit(event) {
    event.preventDefault();
    setState((current) => ({ ...current, loading: true, error: "", success: "", conflicts: [] }));
    try {
      await createBooking({
        target_type: form.target_type,
        target_id: form.target_id,
        title: form.title || "Reservierung",
        start_time: form.start_time,
        end_time: form.end_time,
      });
      setState((current) => ({ ...current, loading: false, success: "Ihre Reservierung wurde erstellt.", conflicts: [] }));
      setForm({ ...form, target_id: "", title: "" });
    } catch (error) {
      setState((current) => ({
        ...current,
        loading: false,
        error: error.message,
        success: "",
        conflicts: error.data?.conflicts || [],
      }));
    }
  }

  if (!isLoggedIn) {
    return (
      <Panel title="Buchung erstellen" caption="Login erforderlich.">
        <EmptyState
          title="Bitte zuerst einloggen"
          text="Buchungen können nur für angemeldete Nutzer erstellt werden."
          action={<Button onClick={() => setPage("login")}>Zum Login</Button>}
        />
      </Panel>
    );
  }

  return (
    <div className="page-stack">
      <Panel title="Buchung erstellen" caption="Wählen Sie Raum, Arbeitsplatz oder Ausstattung und legen Sie den Zeitraum fest.">
        {state.loadingResources ? <LoadingState label="Auswahl wird geladen..." /> : (
          <form className="form-stack" onSubmit={submit}>
            {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
            {state.success && <StatusMessage type="success">{state.success}</StatusMessage>}

            <div className="form-grid two">
              <label>
                <span>Was möchten Sie reservieren?</span>
                <select
                  value={form.target_type}
                  onChange={(event) => setForm({ ...form, target_type: event.target.value, target_id: "" })}
                >
                  {targetTypes.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
                </select>
              </label>
              <label>
                <span>Auswahl</span>
                <select
                  value={form.target_id}
                  onChange={(event) => setForm({ ...form, target_id: event.target.value })}
                  required
                >
                  <option value="">Bitte auswählen</option>
                  {options.map((option) => (
                    <option key={option.id} value={option.id}>{option.label}</option>
                  ))}
                </select>
              </label>
            </div>

            <label>
              <span>Titel</span>
              <input placeholder="z.B. Teammeeting oder Arbeitsplatz Vormittag" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} />
            </label>

            <div className="form-grid two">
              <label>
                <span>Start</span>
                <input type="datetime-local" value={form.start_time} onChange={(event) => setForm({ ...form, start_time: event.target.value })} required />
              </label>
              <label>
                <span>Ende</span>
                <input type="datetime-local" value={form.end_time} onChange={(event) => setForm({ ...form, end_time: event.target.value })} required />
              </label>
            </div>

            <Button type="submit" icon={CalendarPlus} disabled={state.loading}>
              {state.loading ? "Reservierung wird erstellt..." : "Reservierung erstellen"}
            </Button>
          </form>
        )}
      </Panel>

      {state.conflicts.length > 0 && (
        <Panel title="Zeitraum nicht verfügbar" caption="Für diese Auswahl gibt es bereits eine Reservierung.">
          <div className="conflict-list">
            {state.conflicts.map((conflict) => (
              <span className="conflict-item" key={conflict.id}>{conflict.title}: {formatDate(conflict.start_time)} bis {formatDate(conflict.end_time)}</span>
            ))}
          </div>
        </Panel>
      )}
    </div>
  );
}

function buildOptions(type, resources) {
  if (type === "room") {
    return resources.rooms.map((room) => ({
      id: room.id,
      label: `${room.name}${room.location ? `, ${room.location}` : ""}`,
    }));
  }
  if (type === "seat") {
    const roomNames = Object.fromEntries(resources.rooms.map((room) => [room.id, room.name]));
    return resources.seats.map((seat) => ({
      id: seat.id,
      label: `${seat.label}${roomNames[seat.room_id] ? `, ${roomNames[seat.room_id]}` : ""}`,
    }));
  }
  return resources.assets.map((asset) => ({
    id: asset.id,
    label: `${asset.name}${asset.location ? `, ${asset.location}` : ""}`,
  }));
}

function formatDate(value) {
  return new Intl.DateTimeFormat("de-DE", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}
