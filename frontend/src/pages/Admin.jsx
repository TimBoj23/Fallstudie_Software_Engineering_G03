import { useEffect, useState } from "react";
import { Plus, RefreshCw } from "lucide-react";
import { createAsset, getAssets } from "../api/assetsApi.js";
import { getAllBookings } from "../api/bookingsApi.js";
import { createRoom, getRooms } from "../api/roomsApi.js";
import { createSeat, getSeats } from "../api/seatsApi.js";
import Button from "../components/Button.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function Admin({ isLoggedIn, isAdmin }) {
  const [tab, setTab] = useState("rooms");
  const [state, setState] = useState({ loading: false, error: "", success: "", data: {} });
  const [forms, setForms] = useState({
    room: { name: "", number: "", capacity: 1, location: "", equipment: "", description: "" },
    seat: { room_id: "", label: "", description: "" },
    asset: { name: "", asset_type: "other", location: "", description: "" },
  });

  async function load() {
    if (!isAdmin) return;
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      const [rooms, seats, assets, bookings] = await Promise.all([
        getRooms(),
        getSeats(),
        getAssets(),
        getAllBookings(),
      ]);
      setState({
        loading: false,
        error: "",
        success: "",
        data: {
          rooms: rooms.rooms || [],
          seats: seats.seats || [],
          assets: assets.assets || [],
          bookings: bookings.bookings || [],
        },
      });
    } catch (error) {
      setState({ loading: false, error: error.message, success: "", data: {} });
    }
  }

  useEffect(() => {
    load();
  }, [isAdmin]);

  if (!isLoggedIn || !isAdmin) {
    return (
      <Panel title="Admin" caption="Admin-Rechte erforderlich.">
        <EmptyState title="Kein Zugriff" text="Dieser Bereich ist für administrative Verwaltung vorgesehen." />
      </Panel>
    );
  }

  async function createCurrent(event) {
    event.preventDefault();
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      if (tab === "rooms") {
        await createRoom({
          ...forms.room,
          capacity: Number(forms.room.capacity),
          equipment: forms.room.equipment.split(",").map((item) => item.trim()).filter(Boolean),
        });
      }
      if (tab === "seats") {
        await createSeat(forms.seat);
      }
      if (tab === "assets") {
        await createAsset(forms.asset);
      }
      await load();
      setState((current) => ({ ...current, success: "Eintrag wurde angelegt." }));
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error.message, success: "" }));
    }
  }

  return (
    <div className="page-stack">
      <Panel
        title="Admin"
        caption="Räume, Arbeitsplätze und Ausstattung zentral verwalten."
        actions={<Button variant="secondary" icon={RefreshCw} onClick={load}>Aktualisieren</Button>}
      >
        <div className="tabs">
          {["rooms", "seats", "assets", "bookings"].map((item) => (
            <button key={item} className={tab === item ? "active" : ""} onClick={() => setTab(item)} type="button">
              {label(item)}
            </button>
          ))}
        </div>
        {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
        {state.success && <StatusMessage type="success">{state.success}</StatusMessage>}
      </Panel>

      {tab !== "bookings" && (
        <Panel title={`${label(tab)} anlegen`}>
          <form className="form-stack" onSubmit={createCurrent}>
            {tab === "rooms" && (
              <>
                <div className="form-grid two">
                  <input placeholder="Name" value={forms.room.name} onChange={(e) => setForms({ ...forms, room: { ...forms.room, name: e.target.value } })} required />
                  <input placeholder="Raumnummer" value={forms.room.number} onChange={(e) => setForms({ ...forms, room: { ...forms.room, number: e.target.value } })} required />
                </div>
                <div className="form-grid two">
                  <input type="number" min="1" placeholder="Kapazität" value={forms.room.capacity} onChange={(e) => setForms({ ...forms, room: { ...forms.room, capacity: e.target.value } })} required />
                  <input placeholder="Standort" value={forms.room.location} onChange={(e) => setForms({ ...forms, room: { ...forms.room, location: e.target.value } })} />
                </div>
                <input placeholder="Ausstattung, kommagetrennt" value={forms.room.equipment} onChange={(e) => setForms({ ...forms, room: { ...forms.room, equipment: e.target.value } })} />
                <textarea placeholder="Beschreibung" value={forms.room.description} onChange={(e) => setForms({ ...forms, room: { ...forms.room, description: e.target.value } })} />
              </>
            )}
            {tab === "seats" && (
              <>
                <input placeholder="Zugehöriger Raum" value={forms.seat.room_id} onChange={(e) => setForms({ ...forms, seat: { ...forms.seat, room_id: e.target.value } })} required />
                <input placeholder="Label" value={forms.seat.label} onChange={(e) => setForms({ ...forms, seat: { ...forms.seat, label: e.target.value } })} required />
                <textarea placeholder="Beschreibung" value={forms.seat.description} onChange={(e) => setForms({ ...forms, seat: { ...forms.seat, description: e.target.value } })} />
              </>
            )}
            {tab === "assets" && (
              <>
                <div className="form-grid two">
                  <input placeholder="Name" value={forms.asset.name} onChange={(e) => setForms({ ...forms, asset: { ...forms.asset, name: e.target.value } })} required />
                  <select value={forms.asset.asset_type} onChange={(e) => setForms({ ...forms, asset: { ...forms.asset, asset_type: e.target.value } })}>
                    <option value="beamer">Beamer</option>
                    <option value="whiteboard">Whiteboard</option>
                    <option value="laptop">Laptop</option>
                    <option value="monitor">Monitor</option>
                    <option value="adapter">Adapter</option>
                    <option value="moderation">Moderation</option>
                    <option value="presentation_tech">Präsentationstechnik</option>
                    <option value="other">Sonstiges</option>
                  </select>
                </div>
                <input placeholder="Standort" value={forms.asset.location} onChange={(e) => setForms({ ...forms, asset: { ...forms.asset, location: e.target.value } })} />
                <textarea placeholder="Beschreibung" value={forms.asset.description} onChange={(e) => setForms({ ...forms, asset: { ...forms.asset, description: e.target.value } })} />
              </>
            )}
            <Button type="submit" icon={Plus} disabled={state.loading}>Anlegen</Button>
          </form>
        </Panel>
      )}

      {state.loading ? <LoadingState /> : <AdminList tab={tab} data={state.data} />}
    </div>
  );
}

function AdminList({ tab, data }) {
  const items = data[tab] || [];
  return (
    <Panel title={`${label(tab)} Übersicht`}>
      <div className="data-table">
        {items.length === 0 ? <EmptyState title="Keine Einträge" /> : items.map((item) => (
          <div className="data-row" key={item.id}>
            <strong>{item.name || item.label || item.title || item.id}</strong>
            <span>{item.number || item.asset_type || item.target_type || item.room_id || item.location}</span>
            <code>{item.id}</code>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function label(tab) {
  return {
    rooms: "Räume",
    seats: "Sitzplätze",
    assets: "Ausstattung",
    bookings: "Buchungen",
  }[tab];
}
