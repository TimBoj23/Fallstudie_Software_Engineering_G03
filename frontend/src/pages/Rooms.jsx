import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import { getRooms } from "../api/roomsApi.js";
import Button from "../components/Button.jsx";
import DateTimeRangeFields from "../components/DateTimeRangeFields.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import ResourceCard from "../components/ResourceCard.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function Rooms({ openCreateBooking }) {
  const [filters, setFilters] = useState({ q: "", location: "", min_capacity: "", equipment: "", start: "", end: "" });
  const [state, setState] = useState({ loading: true, error: "", rooms: [] });

  async function load(params = filters) {
    setState((current) => ({ ...current, loading: true, error: "" }));
    try {
      const data = await getRooms(withAvailabilityMode(params));
      setState({ loading: false, error: "", rooms: data.rooms || [] });
    } catch (error) {
      setState({ loading: false, error: error.message, rooms: [] });
    }
  }

  useEffect(() => {
    load();
  }, []);

  function submit(event) {
    event.preventDefault();
    load(filters);
  }

  return (
    <div className="page-stack">
      <Panel title="Räume" caption="Passende Meeting-, Projekt- und Arbeitsräume finden.">
        <form className="filter-bar" onSubmit={submit}>
          <input placeholder="Suchbegriff" value={filters.q} onChange={(event) => setFilters({ ...filters, q: event.target.value })} />
          <input placeholder="Standort" value={filters.location} onChange={(event) => setFilters({ ...filters, location: event.target.value })} />
          <input type="number" min="0" placeholder="Kapazität ab" value={filters.min_capacity} onChange={(event) => setFilters({ ...filters, min_capacity: event.target.value })} />
          <input placeholder="Ausstattung" value={filters.equipment} onChange={(event) => setFilters({ ...filters, equipment: event.target.value })} />
          <DateTimeRangeFields values={filters} onChange={setFilters} />
          <Button type="submit" icon={Search}>Suchen</Button>
        </form>
      </Panel>

      {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
      {state.loading ? <LoadingState /> : (
        <div className="resource-grid">
          {state.rooms.length === 0 ? (
            <EmptyState title="Keine Räume gefunden" text="Passe Filter oder Zeitraum an." />
          ) : state.rooms.map((room) => (
            <ResourceCard
              key={room.id}
              title={room.name}
              meta={room.number || "Raum ohne Nummer"}
              location={room.location}
              capacity={room.capacity}
              description={room.description}
              chips={room.equipment || []}
              imageUrl={room.image_url}
              available={room.available}
              onBook={() => openCreateBooking({ targetType: "room", targetId: room.id })}
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
