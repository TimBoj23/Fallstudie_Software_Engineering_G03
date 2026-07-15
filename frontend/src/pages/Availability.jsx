import { useEffect, useMemo, useState } from "react";
import { SearchCheck } from "lucide-react";
import { getAssets } from "../api/assetsApi.js";
import { checkAvailability } from "../api/bookingsApi.js";
import { getRooms } from "../api/roomsApi.js";
import { getSeats } from "../api/seatsApi.js";
import Button from "../components/Button.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function Availability() {
  const [form, setForm] = useState({ target_type: "room", target_id: "", start: "", end: "" });
  const [resources, setResources] = useState({ rooms: [], seats: [], assets: [] });
  const [state, setState] = useState({ loading: false, loadingResources: true, error: "", result: null });

  useEffect(() => {
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
  }, []);

  const options = useMemo(() => buildOptions(form.target_type, resources), [form.target_type, resources]);

  async function submit(event) {
    event.preventDefault();
    setState((current) => ({ ...current, loading: true, error: "", result: null }));
    try {
      const result = await checkAvailability(form);
      setState((current) => ({ ...current, loading: false, error: "", result }));
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error.message, result: null }));
    }
  }

  return (
    <div className="page-stack">
      <Panel title="Verfügbarkeit prüfen" caption="Prüfen Sie vorab, ob eine gewünschte Reservierung möglich ist.">
        {state.loadingResources ? <LoadingState label="Auswahl wird geladen..." /> : (
          <form className="form-stack" onSubmit={submit}>
            {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
            <div className="form-grid two">
              <label>
                <span>Was möchten Sie prüfen?</span>
                <select value={form.target_type} onChange={(event) => setForm({ ...form, target_type: event.target.value, target_id: "" })}>
                  <option value="room">Raum</option>
                  <option value="seat">Arbeitsplatz</option>
                  <option value="asset">Ausstattung</option>
                </select>
              </label>
              <label>
                <span>Auswahl</span>
                <select value={form.target_id} onChange={(event) => setForm({ ...form, target_id: event.target.value })} required>
                  <option value="">Bitte auswählen</option>
                  {options.map((option) => (
                    <option key={option.id} value={option.id}>{option.label}</option>
                  ))}
                </select>
              </label>
            </div>
            <div className="form-grid two">
              <label>
                <span>Start</span>
                <input type="datetime-local" value={form.start} onChange={(event) => setForm({ ...form, start: event.target.value })} required />
              </label>
              <label>
                <span>Ende</span>
                <input type="datetime-local" value={form.end} onChange={(event) => setForm({ ...form, end: event.target.value })} required />
              </label>
            </div>
            <Button type="submit" icon={SearchCheck} disabled={state.loading}>
              {state.loading ? "Prüfung läuft..." : "Verfügbarkeit prüfen"}
            </Button>
          </form>
        )}
      </Panel>

      {state.result && (
        <StatusMessage type={state.result.available ? "success" : "danger"}>
          {state.result.available
            ? "Die Auswahl ist im gewünschten Zeitraum verfügbar."
            : `Diese Auswahl ist im gewünschten Zeitraum bereits reserviert.`}
        </StatusMessage>
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
