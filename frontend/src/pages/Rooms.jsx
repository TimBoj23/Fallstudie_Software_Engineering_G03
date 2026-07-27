import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import { getRooms } from "../api/roomsApi.js";
import Button from "../components/Button.jsx";
import DateTimeRangeFields from "../components/DateTimeRangeFields.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import ObjectCalendar from "../components/ObjectCalendar.jsx";
import Panel from "../components/Panel.jsx";
import ResourceCard from "../components/ResourceCard.jsx";
import StatusMessage from "../components/StatusMessage.jsx";
import SharedOfficeMap from "../components/SharedOfficeMap.jsx";

export default function Rooms({ category = "rooms", openCreateBooking, favorites = [], onToggleFavorite }) {
  const isSharedOfficeView = category === "sharedOffices";
  const [filters, setFilters] = useState({ q: "", location: "", min_capacity: "", room_type: isSharedOfficeView ? "shared_desk" : "", equipment: "", start: "", end: "" });
  const [state, setState] = useState({ loading: true, error: "", rooms: [] });
  const [selectedRoom, setSelectedRoom] = useState(null);

  async function load(params = filters) {
    setState((current) => ({ ...current, loading: true, error: "" }));
    try {
      const requestParams = isSharedOfficeView ? { ...params, room_type: "shared_desk" } : params;
      const data = await getRooms(withAvailabilityMode(requestParams));
      const rooms = isSharedOfficeView
        ? (data.rooms || [])
        : (data.rooms || []).filter((room) => room.room_type !== "shared_desk");
      setState({ loading: false, error: "", rooms });
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
      <Panel
        title={isSharedOfficeView ? "Shared Offices" : "Räume"}
        caption={isSharedOfficeView
          ? "Office-Bereiche ansehen und automatisch oder über den Sitzplan einen Arbeitsplatz buchen."
          : "Vollständig reservierbare Meeting-, Seminar-, Projekt- und Studioräume finden."}
      >
        <form className="filter-bar" onSubmit={submit}>
          <input placeholder="Suchbegriff" value={filters.q} onChange={(event) => setFilters({ ...filters, q: event.target.value })} />
          <input placeholder="Standort" value={filters.location} onChange={(event) => setFilters({ ...filters, location: event.target.value })} />
          <input type="number" min="0" placeholder="Kapazität ab" value={filters.min_capacity} onChange={(event) => setFilters({ ...filters, min_capacity: event.target.value })} />
          {!isSharedOfficeView && (
            <select value={filters.room_type} onChange={(event) => setFilters({ ...filters, room_type: event.target.value })}>
              <option value="">Alle Raumtypen</option>
              <option value="seminarraum">Seminarraum</option>
              <option value="meetingraum">Meetingraum</option>
              <option value="studio">Studio</option>
            </select>
          )}
          <input placeholder="Ausstattung" value={filters.equipment} onChange={(event) => setFilters({ ...filters, equipment: event.target.value })} />
          <DateTimeRangeFields values={filters} onChange={setFilters} />
          <Button type="submit" icon={Search}>Suchen</Button>
        </form>
      </Panel>

      {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
      {selectedRoom && (
        <>
          <ObjectCalendar
            target={{
              id: selectedRoom.id,
              targetType: "room",
              bookingTargetType: isSharedOfficeView ? "shared_office_auto" : "room",
              name: selectedRoom.name,
              meta: selectedRoom.location || selectedRoom.number,
            }}
            onSelectBlock={(defaults) => openCreateBooking(defaults)}
          />
          {isSharedOfficeView && (
            <SharedOfficeMap room={selectedRoom} openCreateBooking={openCreateBooking} />
          )}
        </>
      )}
      {state.loading ? <LoadingState /> : (
        <div className="resource-grid">
          {state.rooms.length === 0 ? (
            <EmptyState
              title={isSharedOfficeView ? "Keine Shared Offices gefunden" : "Keine Räume gefunden"}
              text="Passe Filter oder Zeitraum an."
            />
          ) : state.rooms.map((room) => (
            <ResourceCard
              key={room.id}
              title={room.name}
              meta={room.number || "Raum ohne Nummer"}
              location={room.location}
              capacity={room.capacity}
              description={room.description}
              chips={[roomTypeLabel(room.room_type), ...(room.equipment || [])]}
              imageUrl={room.image_url}
              available={room.available}
              favorite={favorites.some((favorite) => favorite.key === `room:${room.id}`)}
              onToggleFavorite={onToggleFavorite ? () => onToggleFavorite("room", room.id) : null}
              onViewCalendar={() => setSelectedRoom(room)}
              onBook={() => openCreateBooking({ targetType: isSharedOfficeView ? "shared_office_auto" : "room", targetId: room.id })}
              bookLabel={isSharedOfficeView ? "Zufälligen freien Platz buchen" : "Raum reservieren"}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function roomTypeLabel(type) {
  return {
    shared_desk: "Shared Office",
    seminarraum: "Seminarraum",
    meetingraum: "Meetingraum",
    studio: "Studio",
  }[type] || "Raum";
}

function withAvailabilityMode(params) {
  return params.start && params.end ? { ...params, availability: "all" } : params;
}
