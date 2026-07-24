import { useEffect, useState } from "react";
import { Plus, RefreshCw } from "lucide-react";
import { createAsset, getAssets } from "../api/assetsApi.js";
import { getAllBookings } from "../api/bookingsApi.js";
import { mediaUrl } from "../api/client.js";
import { uploadPicture } from "../api/picturesApi.js";
import { createRoom, getRooms } from "../api/roomsApi.js";
import { createSeat, getSeats } from "../api/seatsApi.js";
import { createUser, getUsers, resetUserPassword, updateUser } from "../api/usersApi.js";
import Button from "../components/Button.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function Admin({ isLoggedIn, isAdmin }) {
  const [tab, setTab] = useState("rooms");
  const [state, setState] = useState({ loading: false, error: "", success: "", data: {} });
  const [forms, setForms] = useState({
    room: { name: "", number: "", capacity: 1, location: "", equipment: "", description: "", image_url: "" },
    seat: { room_id: "", label: "", description: "", monitor_count: 1, image_url: "" },
    asset: { name: "", asset_type: "other", location: "", description: "", image_url: "" },
    user: { name: "", email: "", password: "", role: "user", image_url: "" },
    editUser: { id: "", name: "", email: "", role: "user", image_url: "", is_active: true },
    reset: { user_id: "", new_password: "" },
  });
  const [bookingFilters, setBookingFilters] = useState({
    user_id: "",
    target_type: "",
    status: "",
    q: "",
  });

  async function load() {
    if (!isAdmin) return;
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      const [rooms, seats, assets, bookings, users] = await Promise.all([
        getRooms(),
        getSeats(),
        getAssets(),
        getAllBookings(),
        getUsers(),
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
          users: users.users || [],
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
      if (tab === "users") {
        await createUser(forms.user);
      }
      await load();
      setState((current) => ({ ...current, success: "Eintrag wurde angelegt." }));
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error.message, success: "" }));
    }
  }

  async function resetPassword(event) {
    event.preventDefault();
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      const result = await resetUserPassword(forms.reset.user_id, {
        new_password: forms.reset.new_password,
      });
      await load();
      setState((current) => ({
        ...current,
        loading: false,
        success: `Passwort wurde zurückgesetzt: ${result.temporary_password}`,
      }));
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error.message, success: "" }));
    }
  }

  async function handlePictureFile(entity, file) {
    if (!file) return;
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      const result = await uploadPicture(file);
      setForms((current) => ({
        ...current,
        [entity]: { ...current[entity], image_url: result.image_url },
      }));
      setState((current) => ({ ...current, loading: false, success: "Bild wurde hochgeladen." }));
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error.message, success: "" }));
    }
  }

  function selectUser(userId) {
    const user = (state.data.users || []).find((item) => item.id === userId);
    setForms((current) => ({
      ...current,
      editUser: user
        ? {
            id: user.id,
            name: user.name,
            email: user.email,
            role: user.role,
            image_url: user.image_url || "",
            is_active: user.is_active,
          }
        : { id: "", name: "", email: "", role: "user", image_url: "", is_active: true },
    }));
  }

  async function saveUser(event) {
    event.preventDefault();
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      await updateUser(forms.editUser.id, {
        name: forms.editUser.name,
        email: forms.editUser.email,
        role: forms.editUser.role,
        image_url: forms.editUser.image_url,
        is_active: forms.editUser.is_active,
      });
      await load();
      setState((current) => ({ ...current, loading: false, success: "Nutzer wurde aktualisiert." }));
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
          {["rooms", "seats", "assets", "bookings", "users"].map((item) => (
            <button key={item} className={tab === item ? "active" : ""} onClick={() => setTab(item)} type="button">
              {label(item)}
            </button>
          ))}
        </div>
        {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
        {state.success && <StatusMessage type="success">{state.success}</StatusMessage>}
      </Panel>

      {!["bookings", "users"].includes(tab) && (
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
                <PictureInput
                  label="Raumbild"
                  value={forms.room.image_url}
                  onChange={(file) => handlePictureFile("room", file)}
                />
                <textarea placeholder="Beschreibung" value={forms.room.description} onChange={(e) => setForms({ ...forms, room: { ...forms.room, description: e.target.value } })} />
              </>
            )}
            {tab === "seats" && (
              <>
                <input placeholder="Zugehöriger Raum" value={forms.seat.room_id} onChange={(e) => setForms({ ...forms, seat: { ...forms.seat, room_id: e.target.value } })} required />
                <input placeholder="Label" value={forms.seat.label} onChange={(e) => setForms({ ...forms, seat: { ...forms.seat, label: e.target.value } })} required />
                <input type="number" min="1" placeholder="Monitore" value={forms.seat.monitor_count} onChange={(e) => setForms({ ...forms, seat: { ...forms.seat, monitor_count: e.target.value } })} />
                <PictureInput
                  label="Sitzplatzbild"
                  value={forms.seat.image_url}
                  onChange={(file) => handlePictureFile("seat", file)}
                />
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
                <PictureInput
                  label="Assetbild"
                  value={forms.asset.image_url}
                  onChange={(file) => handlePictureFile("asset", file)}
                />
                <textarea placeholder="Beschreibung" value={forms.asset.description} onChange={(e) => setForms({ ...forms, asset: { ...forms.asset, description: e.target.value } })} />
              </>
            )}
            <Button type="submit" icon={Plus} disabled={state.loading}>Anlegen</Button>
          </form>
        </Panel>
      )}

      {tab === "users" && (
        <Panel title="Nutzer verwalten">
          <form className="form-stack" onSubmit={createCurrent}>
            <div className="form-grid two">
              <input placeholder="Name" value={forms.user.name} onChange={(e) => setForms({ ...forms, user: { ...forms.user, name: e.target.value } })} required />
              <input type="email" placeholder="E-Mail" value={forms.user.email} onChange={(e) => setForms({ ...forms, user: { ...forms.user, email: e.target.value } })} required />
            </div>
            <div className="form-grid two">
              <input type="password" placeholder="Passwort" value={forms.user.password} onChange={(e) => setForms({ ...forms, user: { ...forms.user, password: e.target.value } })} required />
              <select value={forms.user.role} onChange={(e) => setForms({ ...forms, user: { ...forms.user, role: e.target.value } })}>
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <PictureInput
              label="Nutzerfoto"
              value={forms.user.image_url}
              onChange={(file) => handlePictureFile("user", file)}
            />
            <Button type="submit" icon={Plus} disabled={state.loading}>Nutzer anlegen</Button>
          </form>
          <form className="form-stack" onSubmit={resetPassword}>
            <div className="form-grid two">
              <select value={forms.reset.user_id} onChange={(e) => setForms({ ...forms, reset: { ...forms.reset, user_id: e.target.value } })} required>
                <option value="">Nutzer auswählen</option>
                {(state.data.users || []).map((user) => (
                  <option key={user.id} value={user.id}>{user.name} ({user.email})</option>
                ))}
              </select>
              <input type="password" placeholder="Neues Passwort, leer = generieren" value={forms.reset.new_password} onChange={(e) => setForms({ ...forms, reset: { ...forms.reset, new_password: e.target.value } })} />
            </div>
            <Button type="submit" variant="secondary" disabled={state.loading}>Passwort zurücksetzen</Button>
          </form>
          <form className="form-stack" onSubmit={saveUser}>
            <div className="form-grid two">
              <select value={forms.editUser.id} onChange={(e) => selectUser(e.target.value)} required>
                <option value="">Nutzer zum Bearbeiten auswählen</option>
                {(state.data.users || []).map((user) => (
                  <option key={user.id} value={user.id}>{user.name} ({user.email})</option>
                ))}
              </select>
              <select value={forms.editUser.role} onChange={(e) => setForms({ ...forms, editUser: { ...forms.editUser, role: e.target.value } })}>
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <div className="form-grid two">
              <input placeholder="Name" value={forms.editUser.name} onChange={(e) => setForms({ ...forms, editUser: { ...forms.editUser, name: e.target.value } })} required />
              <input type="email" placeholder="E-Mail" value={forms.editUser.email} onChange={(e) => setForms({ ...forms, editUser: { ...forms.editUser, email: e.target.value } })} required />
            </div>
            <PictureInput
              label="Nutzerfoto"
              value={forms.editUser.image_url}
              onChange={(file) => handlePictureFile("editUser", file)}
            />
            <label className="inline-check">
              <input type="checkbox" checked={forms.editUser.is_active} onChange={(e) => setForms({ ...forms, editUser: { ...forms.editUser, is_active: e.target.checked } })} />
              <span>Nutzer ist aktiv</span>
            </label>
            <Button type="submit" variant="secondary" disabled={state.loading || !forms.editUser.id}>Nutzer speichern</Button>
          </form>
        </Panel>
      )}

      {state.loading ? <LoadingState /> : (
        <AdminList
          tab={tab}
          data={state.data}
          bookingFilters={bookingFilters}
          setBookingFilters={setBookingFilters}
          selectUser={selectUser}
        />
      )}
    </div>
  );
}

function AdminList({ tab, data, bookingFilters, setBookingFilters, selectUser }) {
  const items = data[tab] || [];
  if (tab === "bookings") {
    return (
      <BookingAdminList
        bookings={items}
        users={data.users || []}
        filters={bookingFilters}
        setFilters={setBookingFilters}
      />
    );
  }
  if (tab === "users") {
    return <UserAdminList users={items} selectUser={selectUser} />;
  }
  return (
    <Panel title={`${label(tab)} Übersicht`}>
      <div className="data-table">
        {items.length === 0 ? <EmptyState title="Keine Einträge" /> : items.map((item) => (
          <div className="data-row" key={item.id}>
            <strong>{item.name || item.label || item.title || item.target_name || "Eintrag"}</strong>
            <span>{detail(item)}</span>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function UserAdminList({ users, selectUser }) {
  return (
    <Panel title="Nutzer Übersicht">
      <div className="user-card-grid">
        {users.length === 0 ? <EmptyState title="Keine Nutzer" /> : users.map((user) => (
          <button className="user-card" key={user.id} type="button" onClick={() => selectUser(user.id)}>
            <UserPhoto user={user} />
            <span>
              <strong>{user.name}</strong>
              <small>{user.email}</small>
              <small>{user.role === "admin" ? "Admin" : "User"} · {user.is_active ? "aktiv" : "inaktiv"}</small>
            </span>
          </button>
        ))}
      </div>
    </Panel>
  );
}

function BookingAdminList({ bookings, users, filters, setFilters }) {
  const visibleBookings = bookings.filter((booking) => {
    const search = filters.q.trim().toLowerCase();
    const matchesUser = !filters.user_id || booking.user_id === filters.user_id;
    const matchesType = !filters.target_type || booking.target_type === filters.target_type;
    const matchesStatus = !filters.status || booking.status === filters.status;
    const searchable = [
      booking.title,
      booking.target_name,
      booking.target_meta,
      booking.user_name,
      booking.user_email,
    ].filter(Boolean).join(" ").toLowerCase();
    return matchesUser && matchesType && matchesStatus && (!search || searchable.includes(search));
  });

  return (
    <Panel title="Buchungen Übersicht">
      <div className="booking-admin-filters">
        <select value={filters.user_id} onChange={(event) => setFilters({ ...filters, user_id: event.target.value })}>
          <option value="">Alle Nutzer</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>{user.name} ({user.email})</option>
          ))}
        </select>
        <select value={filters.target_type} onChange={(event) => setFilters({ ...filters, target_type: event.target.value })}>
          <option value="">Alle Typen</option>
          <option value="room">Räume</option>
          <option value="seat">Sitzplätze</option>
          <option value="asset">Ausstattung</option>
        </select>
        <select value={filters.status} onChange={(event) => setFilters({ ...filters, status: event.target.value })}>
          <option value="">Alle Status</option>
          <option value="active">Aktiv</option>
          <option value="cancelled">Storniert</option>
        </select>
        <input placeholder="Suchen" value={filters.q} onChange={(event) => setFilters({ ...filters, q: event.target.value })} />
      </div>
      <div className="data-table">
        {visibleBookings.length === 0 ? <EmptyState title="Keine Buchungen" /> : visibleBookings.map((booking) => (
          <div className="booking-admin-row" key={booking.id}>
            <UserBadge booking={booking} />
            <div className="booking-admin-main">
              <strong>{booking.title || "Buchung"}</strong>
              <span>{booking.target_name || "Gebuchtes Objekt"}</span>
            </div>
            <span className="booking-admin-meta">{booking.user_name || booking.user_email || "Unbekannter Nutzer"}</span>
            <span className={`badge ${booking.status === "active" ? "success" : "muted"}`}>
              {booking.status === "active" ? "Aktiv" : "Storniert"}
            </span>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function UserBadge({ booking }) {
  const initials = booking.user_initials || initialsFrom(booking.user_name || booking.user_email || booking.user_id);
  if (booking.user_image_url) {
    return <img className="user-avatar" src={mediaUrl(booking.user_image_url)} alt={booking.user_name || booking.user_email || "Nutzer"} loading="lazy" />;
  }
  return (
    <span className="user-initials" title={booking.user_email || booking.user_name || booking.user_id}>
      {initials}
    </span>
  );
}

function UserPhoto({ user }) {
  if (user.image_url) {
    return <img className="user-photo" src={mediaUrl(user.image_url)} alt={user.name} loading="lazy" />;
  }
  return <span className="user-photo fallback">{initialsFrom(user.name || user.email)}</span>;
}

function initialsFrom(value) {
  const parts = String(value || "?").replace("@", " ").replace(".", " ").split(/\s+/).filter(Boolean);
  return parts.slice(0, 2).map((part) => part[0]).join("").toUpperCase() || "?";
}

function detail(item) {
  if (item.email) {
    return `${item.email} · ${item.role}`;
  }
  return item.email || item.target_name || item.number || item.asset_type || item.target_type || item.room_id || item.location || item.role;
}

function PictureInput({ label, value, onChange }) {
  return (
    <label className="picture-input">
      <span>{label}</span>
      <input type="file" accept="image/avif,image/png,image/jpeg,image/webp" onChange={(event) => onChange(event.target.files?.[0])} />
      {value && (
        <div className="picture-preview">
          <img src={mediaUrl(value)} alt={label} />
        </div>
      )}
    </label>
  );
}

function label(tab) {
  return {
    rooms: "Räume",
    seats: "Sitzplätze",
    assets: "Ausstattung",
    bookings: "Buchungen",
    users: "Nutzer",
  }[tab];
}
