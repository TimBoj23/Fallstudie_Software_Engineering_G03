import { useEffect, useRef, useState } from "react";
import { Pencil, Plus, RefreshCw, Save, Trash2, X } from "lucide-react";
import { createAsset, deleteAsset, getAssets, updateAsset } from "../api/assetsApi.js";
import { getAllBookings, getBookingAnalytics, getRoomOccupancy } from "../api/bookingsApi.js";
import { getAuditEvents } from "../api/auditApi.js";
import { mediaUrl } from "../api/client.js";
import { uploadPicture } from "../api/picturesApi.js";
import { createRoom, deleteRoom, getRooms, updateRoom } from "../api/roomsApi.js";
import { createSeat, deleteSeat, getSeats, updateSeat } from "../api/seatsApi.js";
import { createUser, getUsers, resetUserPassword, updateUser } from "../api/usersApi.js";
import { resetDemoActivity } from "../api/maintenanceApi.js";
import Button from "../components/Button.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function Admin({ isLoggedIn, isAdmin }) {
  const [tab, setTab] = useState("rooms");
  const [editing, setEditing] = useState(null);
  const [state, setState] = useState({ loading: false, error: "", success: "", data: {} });
  const [forms, setForms] = useState({
    room: { name: "", number: "", capacity: 1, room_type: "seminarraum", location: "", equipment: "", description: "", image_url: "" },
    seat: { room_id: "", label: "", description: "", monitor_count: 1, image_url: "" },
    asset: { name: "", asset_type: "other", location: "", description: "", image_url: "" },
    user: { name: "", email: "", password: "", role: "user", image_url: "" },
    editUser: { id: "", name: "", email: "", role: "user", image_url: "", is_active: true },
    reset: { user_id: "", new_password: "" },
    maintenance: { current_password: "", confirmation: "" },
  });
  const [bookingFilters, setBookingFilters] = useState({
    user_id: "",
    target_type: "",
    status: "",
    q: "",
  });
  const [userFilters, setUserFilters] = useState({ q: "", role: "", status: "" });

  async function load() {
    if (!isAdmin) return;
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      const [rooms, seats, assets, bookings, users, occupancy, analytics, audit] = await Promise.all([
        getRooms(),
        getSeats(),
        getAssets(),
        getAllBookings(),
        getUsers({ status: "" }),
        getRoomOccupancy(),
        getBookingAnalytics(30),
        getAuditEvents({ limit: 100 }),
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
          occupancy: occupancy.occupancy || [],
          analytics: analytics.analytics || {},
          audit: audit.events || [],
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
        const payload = {
          ...forms.room,
          capacity: Number(forms.room.capacity),
          equipment: forms.room.equipment.split(",").map((item) => item.trim()).filter(Boolean),
        };
        if (editing?.tab === tab) await updateRoom(editing.id, payload);
        else await createRoom(payload);
      }
      if (tab === "seats") {
        const payload = { ...forms.seat, monitor_count: Number(forms.seat.monitor_count) };
        if (editing?.tab === tab) await updateSeat(editing.id, payload);
        else await createSeat(payload);
      }
      if (tab === "assets") {
        if (editing?.tab === tab) await updateAsset(editing.id, forms.asset);
        else await createAsset(forms.asset);
      }
      if (tab === "users") {
        await createUser(forms.user);
      }
      const wasEditing = Boolean(editing?.id);
      setEditing(null);
      resetResourceForm(tab);
      await load();
      setState((current) => ({ ...current, success: wasEditing ? "Eintrag wurde aktualisiert." : "Eintrag wurde angelegt." }));
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error.message, success: "" }));
    }
  }

  function resetResourceForm(resourceTab) {
    if (!RESOURCE_DEFAULTS[resourceTab]) return;
    const formKey = resourceFormKey(resourceTab);
    setForms((current) => ({ ...current, [formKey]: { ...RESOURCE_DEFAULTS[resourceTab] } }));
  }

  function switchTab(nextTab) {
    setTab(nextTab);
    setEditing(null);
  }

  function beginEdit(resourceTab, item) {
    const formKey = resourceFormKey(resourceTab);
    setTab(resourceTab);
    setEditing({ tab: resourceTab, id: item.id });
    setForms((current) => ({
      ...current,
      [formKey]: resourceFormFromItem(resourceTab, item),
    }));
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function cancelEdit() {
    resetResourceForm(tab);
    setEditing(null);
  }

  async function deactivateResource(resourceTab, item) {
    const itemName = item.name || item.label || "Eintrag";
    if (!window.confirm(`„${itemName}“ wirklich deaktivieren? Bestehende Buchungen bleiben erhalten.`)) return;
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      if (resourceTab === "rooms") await deleteRoom(item.id);
      if (resourceTab === "seats") await deleteSeat(item.id);
      if (resourceTab === "assets") await deleteAsset(item.id);
      if (editing?.id === item.id) cancelEdit();
      await load();
      setState((current) => ({ ...current, success: `${itemName} wurde deaktiviert.` }));
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

  async function resetDemo(event) {
    event.preventDefault();
    if (!window.confirm("Alle Buchungen, Protokolle und Nicht-Admin-Konten wirklich endgültig entfernen?")) return;
    setState((current) => ({ ...current, loading: true, error: "", success: "" }));
    try {
      const result = await resetDemoActivity(forms.maintenance);
      setForms((current) => ({ ...current, maintenance: { current_password: "", confirmation: "" } }));
      await load();
      setState((current) => ({
        ...current,
        loading: false,
        success: `${result.message} Entfernt: ${result.result.removed_bookings} Buchungen, ${result.result.removed_audit_events} Protokolle, ${result.result.removed_users} Nutzer.`,
      }));
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
          {["rooms", "seats", "assets", "bookings", "occupancy", "analytics", "users", "audit", "maintenance"].map((item) => (
            <button key={item} className={tab === item ? "active" : ""} onClick={() => switchTab(item)} type="button">
              {label(item)}
            </button>
          ))}
        </div>
        {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
        {state.success && <StatusMessage type="success">{state.success}</StatusMessage>}
      </Panel>

      {!["bookings", "occupancy", "analytics", "users", "audit", "maintenance"].includes(tab) && (
        <Panel title={editing?.tab === tab ? `${label(tab)} bearbeiten` : `${label(tab)} anlegen`}>
          <form className="form-stack" onSubmit={createCurrent}>
            {tab === "rooms" && (
              <>
                <div className="form-grid two">
                  <input placeholder="Name" value={forms.room.name} onChange={(e) => setForms({ ...forms, room: { ...forms.room, name: e.target.value } })} required />
                  <input placeholder="Raumnummer" value={forms.room.number} onChange={(e) => setForms({ ...forms, room: { ...forms.room, number: e.target.value } })} required />
                </div>
                <div className="form-grid two">
                  <input type="number" min="1" placeholder="Kapazität" value={forms.room.capacity} onChange={(e) => setForms({ ...forms, room: { ...forms.room, capacity: e.target.value } })} required />
                  <select value={forms.room.room_type} onChange={(e) => setForms({ ...forms, room: { ...forms.room, room_type: e.target.value } })}>
                    <option value="shared_desk">Shared Office</option>
                    <option value="seminarraum">Seminarraum</option>
                    <option value="meetingraum">Meetingraum</option>
                    <option value="studio">Studio</option>
                  </select>
                </div>
                <input placeholder="Standort" value={forms.room.location} onChange={(e) => setForms({ ...forms, room: { ...forms.room, location: e.target.value } })} />
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
                <select value={forms.seat.room_id} onChange={(e) => setForms({ ...forms, seat: { ...forms.seat, room_id: e.target.value } })} required disabled={editing?.tab === "seats"}>
                  <option value="">Shared Office auswählen</option>
                  {(state.data.rooms || []).filter((room) => room.room_type === "shared_desk").map((room) => (
                    <option key={room.id} value={room.id}>{room.name} ({room.number})</option>
                  ))}
                </select>
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
            <div className="resource-editor-actions">
              <Button type="submit" icon={editing?.tab === tab ? Save : Plus} disabled={state.loading}>
                {editing?.tab === tab ? "Speichern" : "Anlegen"}
              </Button>
              {editing?.tab === tab && (
                <Button variant="secondary" icon={X} onClick={cancelEdit}>Abbrechen</Button>
              )}
            </div>
          </form>
        </Panel>
      )}

      {tab === "users" && (
        <Panel title="Nutzer verwalten">
          <form className="form-stack admin-user-form" onSubmit={createCurrent}>
            <h3 className="admin-form-heading">Nutzer anlegen</h3>
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
            <div className="admin-form-actions">
              <Button type="submit" icon={Plus} disabled={state.loading}>Nutzer anlegen</Button>
            </div>
          </form>
          <form className="form-stack admin-user-form" onSubmit={resetPassword}>
            <h3 className="admin-form-heading">Passwort zurücksetzen</h3>
            <div className="form-grid two">
              <select value={forms.reset.user_id} onChange={(e) => setForms({ ...forms, reset: { ...forms.reset, user_id: e.target.value } })} required>
                <option value="">Nutzer auswählen</option>
                {(state.data.users || []).map((user) => (
                  <option key={user.id} value={user.id}>{user.name} ({user.email})</option>
                ))}
              </select>
              <input type="password" placeholder="Neues Passwort, leer = generieren" value={forms.reset.new_password} onChange={(e) => setForms({ ...forms, reset: { ...forms.reset, new_password: e.target.value } })} />
            </div>
            <div className="admin-form-actions">
              <Button type="submit" variant="secondary" disabled={state.loading}>Passwort zurücksetzen</Button>
            </div>
          </form>
          <form className="form-stack admin-user-form" onSubmit={saveUser}>
            <h3 className="admin-form-heading">Nutzer bearbeiten</h3>
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
            <div className="admin-form-actions">
              <Button type="submit" variant="secondary" disabled={state.loading || !forms.editUser.id}>Nutzer speichern</Button>
            </div>
          </form>
        </Panel>
      )}

      {tab === "maintenance" && (
        <Panel
          title="Demo-Daten zurücksetzen"
          caption="Räume, Shared-Office-Arbeitsplätze, Ausstattung und aktive Admin-Konten bleiben erhalten."
          className="danger-panel"
        >
          <form className="form-stack" onSubmit={resetDemo}>
            <StatusMessage type="warning">
              Diese Aktion löscht alle Buchungen, Statistiken, Check-ins, Protokolle und sämtliche Nicht-Admin-Konten. Admin-Profile und Ressourcen bleiben bestehen.
            </StatusMessage>
            <div className="form-grid two">
              <label>
                Eigenes Admin-Passwort
                <input type="password" autoComplete="current-password" value={forms.maintenance.current_password} onChange={(event) => setForms({ ...forms, maintenance: { ...forms.maintenance, current_password: event.target.value } })} required />
              </label>
              <label>
                Zur Bestätigung „DEMODATEN LÖSCHEN“ eingeben
                <input value={forms.maintenance.confirmation} onChange={(event) => setForms({ ...forms, maintenance: { ...forms.maintenance, confirmation: event.target.value } })} required />
              </label>
            </div>
            <div className="admin-form-actions">
              <Button type="submit" variant="danger" icon={Trash2} disabled={state.loading || forms.maintenance.confirmation !== "DEMODATEN LÖSCHEN"}>
                Demo-Daten endgültig zurücksetzen
              </Button>
            </div>
          </form>
        </Panel>
      )}

      {tab !== "maintenance" && (state.loading ? <LoadingState /> : (
        <AdminList
          tab={tab}
          data={state.data}
          bookingFilters={bookingFilters}
          setBookingFilters={setBookingFilters}
          userFilters={userFilters}
          setUserFilters={setUserFilters}
          selectUser={selectUser}
          onEdit={beginEdit}
          onDeactivate={deactivateResource}
        />
      ))}
    </div>
  );
}

function AdminList({ tab, data, bookingFilters, setBookingFilters, userFilters, setUserFilters, selectUser, onEdit, onDeactivate }) {
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
    return <UserAdminList users={items} selectUser={selectUser} filters={userFilters} setFilters={setUserFilters} />;
  }
  if (tab === "occupancy") {
    return <OccupancyAdminList entries={items} />;
  }
  if (tab === "analytics") {
    return <AnalyticsAdmin analytics={data.analytics || {}} />;
  }
  if (tab === "audit") {
    return <AuditAdmin events={items} />;
  }
  return (
    <Panel title={`${label(tab)} Übersicht`}>
      <div className="data-table">
        {items.length === 0 ? <EmptyState title="Keine Einträge" /> : items.map((item) => (
          <div className="data-row resource-admin-row" key={item.id}>
            <div className="resource-admin-main">
              <strong>{item.name || item.label || item.title || item.target_name || "Eintrag"}</strong>
              <span>{detail(item)}</span>
            </div>
            <div className="resource-admin-actions">
              <Button variant="secondary" icon={Pencil} onClick={() => onEdit(tab, item)}>Bearbeiten</Button>
              <Button variant="danger" icon={Trash2} onClick={() => onDeactivate(tab, item)}>Deaktivieren</Button>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
}

const RESOURCE_DEFAULTS = {
  rooms: { name: "", number: "", capacity: 1, room_type: "seminarraum", location: "", equipment: "", description: "", image_url: "" },
  seats: { room_id: "", label: "", description: "", monitor_count: 1, image_url: "" },
  assets: { name: "", asset_type: "other", location: "", description: "", image_url: "" },
};

function resourceFormFromItem(resourceTab, item) {
  if (resourceTab === "rooms") {
    return {
      name: item.name || "",
      number: item.number || "",
      capacity: item.capacity || 1,
      room_type: item.room_type || "seminarraum",
      location: item.location || "",
      equipment: (item.equipment || []).join(", "),
      description: item.description || "",
      image_url: item.image_url || "",
    };
  }
  if (resourceTab === "seats") {
    return {
      room_id: item.room_id || "",
      label: item.label || "",
      description: item.description || "",
      monitor_count: item.monitor_count || 1,
      image_url: item.image_url || "",
    };
  }
  return {
    name: item.name || "",
    asset_type: item.asset_type || "other",
    location: item.location || "",
    description: item.description || "",
    image_url: item.image_url || "",
  };
}

function resourceFormKey(resourceTab) {
  return { rooms: "room", seats: "seat", assets: "asset" }[resourceTab];
}

function OccupancyAdminList({ entries }) {
  const rooms = entries.reduce((groups, entry) => {
    const roomKey = entry.room_id || "unknown";
    const current = groups[roomKey] || {
      roomName: entry.room_name || "Unbekannter Raum",
      entries: [],
    };
    current.entries.push(entry);
    return { ...groups, [roomKey]: current };
  }, {});

  return (
    <Panel title="Aktuelle Raumbelegung" caption="Nur Personen mit aktivem Check-in in einer gerade laufenden Buchung.">
      <div className="data-table">
        {Object.keys(rooms).length === 0 ? (
          <EmptyState title="Aktuell ist niemand eingecheckt" text="Der Check-in erfolgt in der eigenen Buchungsübersicht." />
        ) : Object.entries(rooms).map(([roomId, room]) => (
          <div className="occupancy-room" key={roomId}>
            <strong>{room.roomName}</strong>
            {room.entries.map((entry) => (
              <div className="data-row" key={entry.booking_id}>
                <span>{entry.user_name || entry.user_email || "Buchungsinhaber"}</span>
                <small>{formatDateRange(entry.start_time, entry.end_time)}</small>
                <small>Eingecheckt: {formatDate(entry.checked_in_at)}</small>
                {(entry.participant_emails || []).map((email) => (
                  <small key={email}>Teilnehmend: {email}</small>
                ))}
              </div>
            ))}
          </div>
        ))}
      </div>
    </Panel>
  );
}

function UserAdminList({ users, selectUser, filters, setFilters }) {
  const visibleUsers = users.filter((user) => {
    const query = filters.q.trim().toLowerCase();
    return (!query || user.name.toLowerCase().includes(query) || user.email.toLowerCase().includes(query))
      && (!filters.role || user.role === filters.role)
      && (!filters.status || (filters.status === "active") === Boolean(user.is_active));
  });
  return (
    <Panel title="Nutzer Übersicht" caption={`${users.filter((user) => user.role === "admin").length} Admin-Konto/Konten vorhanden.`}>
      <div className="booking-admin-filters">
        <input placeholder="Name oder E-Mail suchen" value={filters.q} onChange={(event) => setFilters({ ...filters, q: event.target.value })} />
        <select value={filters.role} onChange={(event) => setFilters({ ...filters, role: event.target.value })}>
          <option value="">Alle Rollen</option><option value="admin">Nur Admins</option><option value="user">Nur User</option>
        </select>
        <select value={filters.status} onChange={(event) => setFilters({ ...filters, status: event.target.value })}>
          <option value="">Alle Status</option><option value="active">Aktiv</option><option value="inactive">Inaktiv</option>
        </select>
      </div>
      <div className="user-card-grid">
        {visibleUsers.length === 0 ? <EmptyState title="Keine Nutzer" /> : visibleUsers.map((user) => (
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

function AnalyticsAdmin({ analytics }) {
  const types = analytics.by_type || {};
  const usageRate = Math.max(0, Math.min(Number(analytics.actual_usage_rate || 0), 100));
  return (
    <Panel title="Auslastungsstatistik" caption={`Rückblick: ${analytics.days || 30} Tage`}>
      <div className="metric-grid">
        <div className="metric-card"><strong>{analytics.active_count || 0}</strong><span>gültige Buchungen</span></div>
        <div className="metric-card"><strong>{analytics.cancelled_count || 0}</strong><span>stornierte Buchungen</span></div>
        <div className="metric-card"><strong>{analytics.meeting_booked_hours || 0} h</strong><span>geplante Meetingzeit</span></div>
        <div className="metric-card success"><strong>{analytics.used_hours || 0} h</strong><span>tatsächlich genutzt</span></div>
        <div className="metric-card"><strong>{analytics.unused_hours || 0} h</strong><span>nicht genutzte Planzeit</span></div>
        <div className="metric-card success"><strong>{usageRate} %</strong><span>reale Nutzungsquote</span></div>
        <div className="metric-card"><strong>{analytics.check_in_rate || 0} %</strong><span>Check-in-Quote</span></div>
        <div className="metric-card"><strong>{analytics.no_show_count || 0}</strong><span>No-Shows</span></div>
      </div>

      <div className="analytics-usage-card">
        <div className="analytics-usage-heading">
          <div>
            <strong>Tatsächliche Nutzung der geplanten Meetingzeit</strong>
            <span>Räume und Shared-Office-Arbeitsplätze, ohne reine Ausstattung</span>
          </div>
          <strong>{analytics.used_hours || 0} von {analytics.meeting_booked_hours || 0} Stunden</strong>
        </div>
        <div className="analytics-progress" role="progressbar" aria-valuenow={usageRate} aria-valuemin="0" aria-valuemax="100">
          <span style={{ width: `${usageRate}%` }} />
        </div>
        <div className="analytics-usage-footer">
          <span>{analytics.completed_count || 0} abgeschlossene Termine</span>
          <span>{analytics.currently_used_count || 0} aktuell in Nutzung</span>
          <span>{analytics.no_show_count || 0} ohne Check-in</span>
        </div>
      </div>

      <div className="data-table">
        {Object.entries(types).map(([type, values]) => (
          <div className="data-row analytics-data-row" key={type}>
            <strong>{typeLabel(type)}</strong>
            <span>{values.count} Buchung(en)</span>
            <span>{values.hours} h geplant</span>
            <span>{type === "asset" ? "keine Anwesenheitsmessung" : `${values.used_hours || 0} h genutzt`}</span>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function AuditAdmin({ events }) {
  return (
    <Panel title="Änderungsprotokoll" caption="Neue sicherheits- und buchungsrelevante Aktionen, ohne Passwörter oder Tokens.">
      <div className="data-table">
        {events.length === 0 ? <EmptyState title="Noch keine protokollierten Änderungen" /> : events.map((event) => (
          <div className="data-row audit-row" key={event.id}>
            <strong>{event.summary}</strong>
            <span>{event.actor_name || "System"} · {event.action}</span>
            <small>{formatDate(event.created_at)}</small>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function typeLabel(type) {
  return { room: "Räume", seat: "Arbeitsplätze", asset: "Ausstattung" }[type] || type;
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
  const inputRef = useRef(null);
  return (
    <div className="picture-input">
      <span>{label}</span>
      <input ref={inputRef} type="file" accept="image/avif,image/png,image/jpeg,image/webp" onChange={(event) => onChange(event.target.files?.[0])} />
      <div className="picture-buttons">
        <Button type="button" variant="secondary" onClick={() => inputRef.current?.click()}>Bild auswählen</Button>
      </div>
      {value && (
        <div className="picture-preview">
          <img src={mediaUrl(value)} alt={label} />
        </div>
      )}
    </div>
  );
}

function label(tab) {
  return {
    rooms: "Räume",
    seats: "Sitzplätze",
    assets: "Ausstattung",
    bookings: "Buchungen",
    occupancy: "Belegung",
    analytics: "Statistik",
    users: "Nutzer",
    audit: "Protokoll",
    maintenance: "Wartung",
  }[tab];
}

function formatDateRange(start, end) {
  const formatter = new Intl.DateTimeFormat("de-DE", { dateStyle: "short", timeStyle: "short" });
  return `${formatter.format(new Date(start))} bis ${formatter.format(new Date(end))}`;
}

function formatDate(value) {
  if (!value) return "–";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
}
