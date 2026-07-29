import { useEffect, useMemo, useState } from "react";
import { CalendarPlus, CheckCircle2, Clock3, SearchCheck, XCircle } from "lucide-react";
import { getAssets } from "../api/assetsApi.js";
import { checkAvailability } from "../api/bookingsApi.js";
import { getRooms } from "../api/roomsApi.js";
import { getSeats } from "../api/seatsApi.js";
import Button from "../components/Button.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function Availability({ openCreateBooking }) {
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

  function updateForm(patch) {
    setForm((current) => ({ ...current, ...patch }));
    setState((current) => ({ ...current, result: null, error: "" }));
  }

  async function submit(event) {
    event.preventDefault();
    setState((current) => ({ ...current, loading: true, error: "", result: null }));
    try {
      const result = await checkAvailability(form);
      setState((current) => ({
        ...current,
        loading: false,
        error: "",
        result: {
          ...result,
          checkedForm: { ...form },
          resource: options.find((option) => option.id === form.target_id),
        },
      }));
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
                <select value={form.target_type} onChange={(event) => updateForm({ target_type: event.target.value, target_id: "" })}>
                  <option value="room">Raum</option>
                  <option value="seat">Arbeitsplatz</option>
                  <option value="asset">Ausstattung</option>
                </select>
              </label>
              <label>
                <span>Auswahl</span>
                <select value={form.target_id} onChange={(event) => updateForm({ target_id: event.target.value })} required>
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
                <input type="datetime-local" value={form.start} onChange={(event) => updateForm({ start: event.target.value })} required />
              </label>
              <label>
                <span>Ende</span>
                <input type="datetime-local" value={form.end} onChange={(event) => updateForm({ end: event.target.value })} required />
              </label>
            </div>
            <Button type="submit" icon={SearchCheck} disabled={state.loading}>
              {state.loading ? "Prüfung läuft..." : "Verfügbarkeit prüfen"}
            </Button>
          </form>
        )}
      </Panel>

      {state.result && (
        <AvailabilityResult
          result={state.result}
          onBook={state.result.available && openCreateBooking ? () => openCreateBooking({
            targetType: state.result.resource?.bookingTargetType || state.result.checkedForm.target_type,
            targetId: state.result.checkedForm.target_id,
            startTime: state.result.checkedForm.start,
            endTime: state.result.checkedForm.end,
          }) : null}
        />
      )}
    </div>
  );
}

function buildOptions(type, resources) {
  if (type === "room") {
    return resources.rooms.map((room) => ({
      id: room.id,
      label: `${room.name}${room.location ? `, ${room.location}` : ""}`,
      bookingTargetType: room.room_type === "shared_desk" ? "shared_office_auto" : "room",
    }));
  }
  if (type === "seat") {
    const roomNames = Object.fromEntries(resources.rooms.map((room) => [room.id, room.name]));
    return resources.seats.map((seat) => ({
      id: seat.id,
      label: `${seat.label}${roomNames[seat.room_id] ? `, ${roomNames[seat.room_id]}` : ""}`,
      bookingTargetType: "seat",
    }));
  }
  return resources.assets.map((asset) => ({
    id: asset.id,
    label: `${asset.name}${asset.location ? `, ${asset.location}` : ""}`,
    bookingTargetType: "asset",
  }));
}

function AvailabilityResult({ result, onBook }) {
  const presentation = availabilityPresentation(result);
  const Icon = result.available ? CheckCircle2 : XCircle;
  return (
    <section className={`availability-result-card ${result.available ? "is-free" : "is-blocked"}`}>
      <div className="availability-result-heading">
        <span className="availability-result-icon"><Icon size={30} /></span>
        <div>
          <p className="eyebrow">Ergebnis der Prüfung</p>
          <h2>{presentation.title}</h2>
          <p>{presentation.message}</p>
        </div>
      </div>

      <div className="availability-result-details">
        <div><strong>Ressource</strong><span>{result.resource?.label || result.checkedForm.target_id}</span></div>
        <div><strong>Zeitraum</strong><span><Clock3 size={15} />{formatDateRange(result.checkedForm.start, result.checkedForm.end)}</span></div>
      </div>

      <div className="availability-visual" aria-label={presentation.title}>
        {Array.from({ length: 12 }, (_, index) => (
          <span key={index} className={result.available ? "free" : "blocked"} />
        ))}
      </div>
      <div className="availability-legend">
        <span><i className={`legend-dot ${result.available ? "free" : "full"}`} />{result.available ? "Zeitraum frei" : "Überschneidung vorhanden"}</span>
      </div>

      {!result.available && (result.conflicts || []).length > 0 && (
        <div className="conflict-list">
          <strong>Bestehende Buchungen in diesem Zeitraum</strong>
          {result.conflicts.map((conflict) => (
            <div className="conflict-item" key={conflict.id}>
              <strong>{conflict.title || conflict.target_name || "Bestehende Buchung"}</strong>
              <span>{formatDateRange(conflict.start_time, conflict.end_time)}</span>
            </div>
          ))}
        </div>
      )}

      {onBook && (
        <div className="availability-result-actions">
          <Button icon={CalendarPlus} onClick={onBook}>Diesen Zeitraum buchen</Button>
        </div>
      )}
    </section>
  );
}

export function availabilityPresentation(result) {
  return result?.available
    ? {
        title: "Frei und buchbar",
        message: "Für den gesamten ausgewählten Zeitraum wurde keine Überschneidung gefunden.",
      }
    : {
        title: "Bereits belegt",
        message: "Mindestens eine bestehende Reservierung überschneidet sich mit dem ausgewählten Zeitraum.",
      };
}

function formatDateRange(start, end) {
  const formatter = new Intl.DateTimeFormat("de-DE", { dateStyle: "short", timeStyle: "short" });
  const parsedStart = new Date(start);
  const parsedEnd = new Date(end);
  if (Number.isNaN(parsedStart.getTime()) || Number.isNaN(parsedEnd.getTime())) return `${start} bis ${end}`;
  return `${formatter.format(parsedStart)} bis ${formatter.format(parsedEnd)}`;
}
