import { useEffect, useMemo, useState } from "react";
import { Heart, RefreshCw } from "lucide-react";
import { getAssets } from "../api/assetsApi.js";
import { getRooms } from "../api/roomsApi.js";
import { getSeats } from "../api/seatsApi.js";
import Button from "../components/Button.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import ResourceCard from "../components/ResourceCard.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

const assetTypeLabels = {
  beamer: "Beamer",
  whiteboard: "Whiteboard",
  laptop: "Laptop",
  monitor: "Monitor",
  adapter: "Adapter",
  moderation: "Moderation",
  presentation_tech: "Präsentationstechnik",
  other: "Ausstattung",
};

export default function Favorites({ isLoggedIn, favorites, onToggleFavorite, openCreateBooking, setPage }) {
  const [state, setState] = useState({ loading: true, error: "", resources: { rooms: [], seats: [], assets: [] } });

  async function load() {
    if (!isLoggedIn) return;
    setState((current) => ({ ...current, loading: true, error: "" }));
    try {
      const [rooms, seats, assets] = await Promise.all([getRooms(), getSeats(), getAssets()]);
      setState({
        loading: false,
        error: "",
        resources: {
          rooms: rooms.rooms || [],
          seats: seats.seats || [],
          assets: assets.assets || [],
        },
      });
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error.message }));
    }
  }

  useEffect(() => {
    load();
  }, [isLoggedIn]);

  const entries = useMemo(
    () => resolveFavorites(favorites, state.resources),
    [favorites, state.resources],
  );

  if (!isLoggedIn) {
    return (
      <Panel title="Favoriten" caption="Login erforderlich.">
        <EmptyState
          title="Bitte zuerst einloggen"
          text="Favoriten werden dauerhaft in deinem RePlan-Konto gespeichert."
          action={<Button onClick={() => setPage("login")}>Zum Login</Button>}
        />
      </Panel>
    );
  }

  return (
    <div className="page-stack">
      <Panel
        title="Meine Favoriten"
        caption="Gespeicherte Räume, Arbeitsplätze und Ausstattung an einem Ort."
        actions={<Button variant="secondary" icon={RefreshCw} onClick={load}>Aktualisieren</Button>}
      >
        {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
        <p className="resource-meta">
          <Heart size={15} fill="currentColor" /> {favorites.length} Favorit{favorites.length === 1 ? "" : "en"} im Konto gespeichert
        </p>
      </Panel>

      {state.loading ? <LoadingState label="Favoriten werden geladen..." /> : (
        <div className="resource-grid">
          {entries.length === 0 ? (
            <EmptyState
              title="Noch keine Favoriten"
              text="Markiere Räume, Arbeitsplätze oder Ausstattung über das Herzsymbol."
              action={<Button onClick={() => setPage("rooms")}>Räume ansehen</Button>}
            />
          ) : entries.map((entry) => (
            <ResourceCard
              key={entry.key}
              title={entry.title}
              meta={entry.meta}
              location={entry.location}
              capacity={entry.capacity}
              description={entry.description}
              chips={entry.chips}
              imageUrl={entry.imageUrl}
              imageFit={entry.imageFit}
              favorite
              onToggleFavorite={() => onToggleFavorite(entry.favoriteType, entry.targetId)}
              onBook={entry.missing ? null : () => openCreateBooking({
                targetType: entry.bookingTargetType,
                targetId: entry.targetId,
              })}
              bookLabel={entry.bookLabel}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function resolveFavorites(favorites = [], resources = {}) {
  const rooms = resources.rooms || [];
  const seats = resources.seats || [];
  const assets = resources.assets || [];
  const roomById = Object.fromEntries(rooms.map((room) => [room.id, room]));
  const seatById = Object.fromEntries(seats.map((seat) => [seat.id, seat]));
  const assetById = Object.fromEntries(assets.map((asset) => [asset.id, asset]));

  return favorites.map((favorite) => {
    if (favorite.target_type === "room" && roomById[favorite.target_id]) {
      const room = roomById[favorite.target_id];
      const sharedOffice = room.room_type === "shared_desk";
      return {
        key: favorite.key,
        favoriteType: "room",
        targetId: room.id,
        bookingTargetType: sharedOffice ? "shared_office_auto" : "room",
        title: room.name,
        meta: sharedOffice ? "Shared Office" : "Raum",
        location: room.location,
        capacity: room.capacity,
        description: room.description,
        chips: [sharedOffice ? "Shared Office" : roomTypeLabel(room.room_type), ...(room.equipment || [])],
        imageUrl: room.image_url,
        bookLabel: sharedOffice ? "Freien Platz buchen" : "Raum reservieren",
      };
    }

    if (favorite.target_type === "seat" && seatById[favorite.target_id]) {
      const seat = seatById[favorite.target_id];
      const room = roomById[seat.room_id];
      return {
        key: favorite.key,
        favoriteType: "seat",
        targetId: seat.id,
        bookingTargetType: "seat",
        title: seat.label,
        meta: room?.name || "Shared-Office-Arbeitsplatz",
        location: room?.location,
        description: seat.description,
        chips: [`${seat.monitor_count || 0} Monitor${seat.monitor_count === 1 ? "" : "e"}`, "Arbeitsplatz"],
        imageUrl: seat.image_url || room?.image_url,
        bookLabel: "Arbeitsplatz buchen",
      };
    }

    if (favorite.target_type === "asset" && assetById[favorite.target_id]) {
      const asset = assetById[favorite.target_id];
      return {
        key: favorite.key,
        favoriteType: "asset",
        targetId: asset.id,
        bookingTargetType: "asset",
        title: asset.name,
        meta: assetTypeLabels[asset.asset_type] || "Ausstattung",
        location: asset.location,
        description: asset.description,
        chips: [assetTypeLabels[asset.asset_type] || "Ausstattung"],
        imageUrl: asset.image_url,
        imageFit: "contain",
        bookLabel: "Ausstattung buchen",
      };
    }

    return {
      key: favorite.key,
      favoriteType: favorite.target_type,
      targetId: favorite.target_id,
      title: "Nicht mehr verfügbare Ressource",
      meta: favorite.key,
      description: "Dieser gespeicherte Favorit wurde deaktiviert oder entfernt. Du kannst ihn über das Herzsymbol aus deiner Liste löschen.",
      chips: ["Nicht verfügbar"],
      missing: true,
    };
  });
}

function roomTypeLabel(type) {
  return {
    seminarraum: "Seminarraum",
    meetingraum: "Meetingraum",
    studio: "Studio",
  }[type] || "Raum";
}
