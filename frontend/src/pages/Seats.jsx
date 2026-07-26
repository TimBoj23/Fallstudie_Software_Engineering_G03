import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import { getRooms } from "../api/roomsApi.js";
import { getSeats } from "../api/seatsApi.js";
import Button from "../components/Button.jsx";
import DateTimeRangeFields from "../components/DateTimeRangeFields.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import ResourceCard from "../components/ResourceCard.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function Seats({ openCreateBooking, favorites = [], onToggleFavorite }) {
  const [filters, setFilters] = useState({ q: "", room_id: "", start: "", end: "" });
  const [state, setState] = useState({ loading: true, error: "", seats: [] });
  const [rooms, setRooms] = useState([]);

  async function load(params = filters) {
    setState((current) => ({ ...current, loading: true, error: "" }));
    try {
      const [seatData, roomData] = await Promise.all([getSeats(withAvailabilityMode(params)), getRooms({ room_type: "shared_desk" })]);
      setRooms(roomData.rooms || []);
      setState({ loading: false, error: "", seats: seatData.seats || [] });
    } catch (error) {
      setState({ loading: false, error: error.message, seats: [] });
    }
  }

  useEffect(() => {
    load();
  }, []);

  function submit(event) {
    event.preventDefault();
    load(filters);
  }

  const roomNames = Object.fromEntries(rooms.map((room) => [room.id, room.name]));

  return (
    <div className="page-stack">
      <Panel title="Arbeitsplätze" caption="Einzelne Plätze innerhalb eines Raums finden und reservieren.">
        <form className="filter-bar" onSubmit={submit}>
          <input placeholder="Suchbegriff" value={filters.q} onChange={(event) => setFilters({ ...filters, q: event.target.value })} />
          <select value={filters.room_id} onChange={(event) => setFilters({ ...filters, room_id: event.target.value })}>
            <option value="">Alle Räume</option>
            {rooms.map((room) => (
              <option key={room.id} value={room.id}>{room.name}</option>
            ))}
          </select>
          <DateTimeRangeFields values={filters} onChange={setFilters} />
          <Button type="submit" icon={Search}>Suchen</Button>
        </form>
      </Panel>

      {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
      {state.loading ? <LoadingState /> : (
        <div className="resource-grid">
          {state.seats.length === 0 ? (
            <EmptyState title="Keine Arbeitsplätze gefunden" text="Passe Filter oder Zeitraum an." />
          ) : state.seats.map((seat) => (
            <ResourceCard
              key={seat.id}
              title={seat.label}
              meta={roomNames[seat.room_id] || "Arbeitsplatz"}
              description={seat.description}
              chips={[`${seat.monitor_count || 1} Monitor(e)`]}
              imageUrl={seat.image_url}
              available={seat.available}
              favorite={favorites.some((favorite) => favorite.key === `seat:${seat.id}`)}
              onToggleFavorite={onToggleFavorite ? () => onToggleFavorite("seat", seat.id) : null}
              onBook={() => openCreateBooking({ targetType: "seat", targetId: seat.id })}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function withAvailabilityMode(params) {
  return params.start && params.end ? { ...params, availability: "all" } : params;
}
