import { Heart, Monitor, RefreshCw, Users } from "lucide-react";
import { useEffect, useState } from "react";

import { getSeats } from "../api/seatsApi.js";
import Button from "./Button.jsx";
import DateTimeRangeFields from "./DateTimeRangeFields.jsx";
import LoadingState from "./LoadingState.jsx";
import Panel from "./Panel.jsx";
import StatusMessage from "./StatusMessage.jsx";


export default function SharedOfficeMap({ room, openCreateBooking, favorites = [], onToggleFavorite }) {
  const [range, setRange] = useState(defaultRange);
  const [state, setState] = useState({ loading: true, error: "", seats: [] });

  async function load(values = range) {
    setState((current) => ({ ...current, loading: true, error: "" }));
    try {
      const result = await getSeats({
        room_id: room.id,
        start: values.start,
        end: values.end,
        availability: "all",
        shared_desk_only: true,
      });
      setState({ loading: false, error: "", seats: result.seats || [] });
    } catch (error) {
      setState({ loading: false, error: error.message, seats: [] });
    }
  }

  useEffect(() => {
    const nextRange = defaultRange();
    setRange(nextRange);
    load(nextRange);
  }, [room.id]);

  const freeCount = state.seats.filter((seat) => seat.available !== false).length;

  return (
    <Panel
      title={`${room.name}: grafischer Sitzplan`}
      caption="Wähle Zeitraum und anschließend direkt einen freien Arbeitsplatz."
      actions={<span className="badge info"><Users size={14} /> {freeCount}/{state.seats.length} frei</span>}
    >
      <form className="seat-map-filters" onSubmit={(event) => { event.preventDefault(); load(range); }}>
        <DateTimeRangeFields values={range} onChange={setRange} />
        <Button type="submit" variant="secondary" icon={RefreshCw}>Belegung prüfen</Button>
      </form>
      {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
      {state.loading ? <LoadingState label="Sitzplan wird geladen…" /> : (
        <div className="seat-map" role="list" aria-label={`Arbeitsplätze in ${room.name}`}>
          {state.seats.map((seat) => {
            const available = seat.available !== false;
            return (
              <div
                key={seat.id}
                role="listitem"
                className={`seat-map-place ${available ? "available" : "occupied"}`}
              >
                <button
                  type="button"
                  className="seat-map-book-button"
                  disabled={!available}
                  onClick={() => openCreateBooking({
                    targetType: "seat",
                    targetId: seat.id,
                    startTime: range.start,
                    endTime: range.end,
                    title: `${room.name} – Arbeitsplatz ${seat.label}`,
                  })}
                >
                  <span className="seat-map-monitor"><Monitor size={22} /></span>
                  <strong>{seat.label}</strong>
                  <small>{seat.monitor_count || 1} Monitor(e)</small>
                  <span>{available ? "Frei" : "Belegt"}</span>
                </button>
                {onToggleFavorite && (
                  <button
                    type="button"
                    className={`favorite-button seat-favorite-button ${favorites.some((favorite) => favorite.key === `seat:${seat.id}`) ? "active" : ""}`}
                    aria-label="Arbeitsplatz als Favorit speichern"
                    onClick={() => onToggleFavorite("seat", seat.id)}
                  >
                    <Heart
                      size={17}
                      fill={favorites.some((favorite) => favorite.key === `seat:${seat.id}`) ? "currentColor" : "none"}
                    />
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
      <div className="calendar-legend seat-map-legend">
        <span><i className="legend-dot free" />Direkt buchbar</span>
        <span><i className="legend-dot full" />Im gewählten Zeitraum belegt</span>
      </div>
    </Panel>
  );
}


function defaultRange() {
  const start = new Date();
  start.setMinutes(0, 0, 0);
  start.setHours(start.getHours() + 1);
  if (start.getHours() < 8 || start.getHours() >= 21) {
    if (start.getHours() >= 21) start.setDate(start.getDate() + 1);
    start.setHours(9, 0, 0, 0);
  }
  const end = new Date(start.getTime() + 60 * 60 * 1000);
  return { start: toLocalInput(start), end: toLocalInput(end) };
}


function toLocalInput(value) {
  const offset = value.getTimezoneOffset() * 60_000;
  return new Date(value.getTime() - offset).toISOString().slice(0, 16);
}
