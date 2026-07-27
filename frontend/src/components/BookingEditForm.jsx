import { Save, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { getAssets } from "../api/assetsApi.js";
import { getRooms } from "../api/roomsApi.js";
import { getSeats } from "../api/seatsApi.js";
import Button from "./Button.jsx";
import LoadingState from "./LoadingState.jsx";
import Panel from "./Panel.jsx";
import StatusMessage from "./StatusMessage.jsx";


export default function BookingEditForm({ booking, onSave, onClose, saving = false, error = "" }) {
  const [form, setForm] = useState(() => fromBooking(booking));
  const [resources, setResources] = useState({ loading: true, error: "", rooms: [], seats: [], assets: [] });

  useEffect(() => {
    setForm(fromBooking(booking));
  }, [booking.id]);

  useEffect(() => {
    let ignore = false;
    Promise.all([getRooms(), getSeats({ shared_desk_only: true }), getAssets()])
      .then(([rooms, seats, assets]) => {
        if (!ignore) setResources({ loading: false, error: "", rooms: rooms.rooms || [], seats: seats.seats || [], assets: assets.assets || [] });
      })
      .catch((loadError) => {
        if (!ignore) setResources({ loading: false, error: loadError.message, rooms: [], seats: [], assets: [] });
      });
    return () => { ignore = true; };
  }, []);

  const options = useMemo(() => resourceOptions(form.target_type, resources), [form.target_type, resources]);
  const protectedBooking = Boolean(booking.has_access_password);

  function submit(event) {
    event.preventDefault();
    onSave({
      ...form,
      start_time: form.start_time,
      end_time: form.end_time,
    });
  }

  return (
    <Panel title="Buchung bearbeiten" caption="Die Verfügbarkeit wird beim Speichern vollständig neu geprüft.">
      {resources.loading ? <LoadingState label="Buchungsdaten werden geladen…" /> : (
        <form className="form-stack" onSubmit={submit}>
          {(error || resources.error) && <StatusMessage type="danger">{error || resources.error}</StatusMessage>}
          <label>
            Titel
            <input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required />
          </label>
          <div className="form-grid two">
            <label>
              Typ
              <select
                value={form.target_type}
                disabled={protectedBooking}
                onChange={(event) => setForm({ ...form, target_type: event.target.value, target_id: "" })}
              >
                <option value="room">Raum</option>
                <option value="seat">Shared-Office-Arbeitsplatz</option>
                <option value="asset">Ausstattung</option>
              </select>
            </label>
            <label>
              Objekt
              <select value={form.target_id} onChange={(event) => setForm({ ...form, target_id: event.target.value })} required>
                <option value="">Bitte auswählen</option>
                {options.map((option) => <option key={option.id} value={option.id}>{option.label}</option>)}
              </select>
            </label>
          </div>
          {protectedBooking && <small>Bei einer geschützten Einladung kann der Buchungstyp nicht geändert werden.</small>}
          <div className="form-grid two">
            <label>
              Start
              <input type="datetime-local" value={form.start_time} onChange={(event) => setForm({ ...form, start_time: event.target.value })} required />
            </label>
            <label>
              Ende
              <input type="datetime-local" value={form.end_time} onChange={(event) => setForm({ ...form, end_time: event.target.value })} required />
            </label>
          </div>
          {booking.series_id && (
            <label>
              Umfang der Änderung
              <select value={form.scope} onChange={(event) => setForm({ ...form, scope: event.target.value })}>
                <option value="single">Nur diesen Termin</option>
                <option value="future">Diesen und alle folgenden Serientermine</option>
              </select>
            </label>
          )}
          <div className="resource-editor-actions">
            <Button type="submit" icon={Save} disabled={saving}>{saving ? "Speichert…" : "Änderungen speichern"}</Button>
            <Button type="button" variant="secondary" icon={X} onClick={onClose}>Abbrechen</Button>
          </div>
        </form>
      )}
    </Panel>
  );
}


function fromBooking(booking) {
  return {
    title: booking.title || "Buchung",
    target_type: booking.target_type,
    target_id: booking.target_id,
    start_time: String(booking.start_time || "").slice(0, 16),
    end_time: String(booking.end_time || "").slice(0, 16),
    scope: "single",
  };
}


function resourceOptions(type, resources) {
  if (type === "room") return resources.rooms.map((room) => ({ id: room.id, label: `${room.name} · ${room.location || room.number}` }));
  if (type === "seat") {
    const roomNames = Object.fromEntries(resources.rooms.map((room) => [room.id, room.name]));
    return resources.seats.map((seat) => ({ id: seat.id, label: `${seat.label} · ${roomNames[seat.room_id] || "Shared Office"}` }));
  }
  return resources.assets.map((asset) => ({ id: asset.id, label: `${asset.name} · ${asset.location || "Ausstattung"}` }));
}
