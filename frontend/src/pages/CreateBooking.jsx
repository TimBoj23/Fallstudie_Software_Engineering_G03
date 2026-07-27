import { useEffect, useMemo, useState } from "react";
import { CalendarPlus, Copy, Link as LinkIcon } from "lucide-react";
import { getAssets } from "../api/assetsApi.js";
import { createBooking } from "../api/bookingsApi.js";
import { getRooms } from "../api/roomsApi.js";
import { getSeats } from "../api/seatsApi.js";
import Button from "../components/Button.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";
import { toDateTimeLocal } from "../utils/dateTime.js";

const targetTypes = [
  { value: "room", label: "Raum vollständig reservieren" },
  { value: "shared_office_auto", label: "Shared Office – freien Platz automatisch wählen" },
  { value: "seat", label: "Shared Office – bestimmten Arbeitsplatz wählen" },
  { value: "asset", label: "Ausstattung" },
];

const targetTypeHelp = {
  room: "Der ausgewählte Raum ist im Zeitraum vollständig für andere Buchungen gesperrt.",
  shared_office_auto: "RePlan weist zufällig einen der freien Arbeitsplätze im ausgewählten Shared Office zu.",
  seat: "Sie wählen einen ganz bestimmten Arbeitsplatz innerhalb eines Shared Office.",
  asset: "Sie reservieren ein einzelnes Gerät oder Ausstattungsobjekt.",
};

const targetTypeLabels = Object.fromEntries(targetTypes.map((type) => [type.value, type.label]));

export default function CreateBooking({ isLoggedIn, setPage, bookingDefaults = {} }) {
  const [form, setForm] = useState({
    target_type: bookingDefaults.targetType || "room",
    target_id: bookingDefaults.targetId || "",
    title: bookingDefaults.title || "",
    start_time: toDateTimeLocal(bookingDefaults.startTime || ""),
    end_time: toDateTimeLocal(bookingDefaults.endTime || ""),
    access_password: "",
    invitation_emails: "",
  });
  const [resources, setResources] = useState({ rooms: [], seats: [], assets: [] });
  const [recurrenceCount, setRecurrenceCount] = useState(1);
  const [state, setState] = useState({ loading: false, loadingResources: true, error: "", success: "", conflicts: [], suggestions: [], invitation: null });
  const fixedTargetType = Boolean(bookingDefaults.targetType);

  useEffect(() => {
    if (!isLoggedIn) return;
    let ignore = false;
    async function loadResources() {
      try {
        const [rooms, seats, assets] = await Promise.all([
          getRooms(),
          getSeats({ shared_desk_only: true }),
          getAssets(),
        ]);
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
  }, [isLoggedIn]);

  useEffect(() => {
    setForm((current) => ({
      ...current,
      target_type: bookingDefaults.targetType || "room",
      target_id: bookingDefaults.targetId || "",
      title: bookingDefaults.title || current.title,
      start_time: toDateTimeLocal(bookingDefaults.startTime || current.start_time),
      end_time: toDateTimeLocal(bookingDefaults.endTime || current.end_time),
    }));
  }, [bookingDefaults.endTime, bookingDefaults.startTime, bookingDefaults.targetId, bookingDefaults.targetType, bookingDefaults.title]);

  const options = useMemo(() => buildOptions(form.target_type, resources), [form.target_type, resources]);
  const invitationEnabled = form.target_type === "room" && Boolean(
    form.access_password.trim() || form.invitation_emails.trim()
  );
  const selectedTargetLabel = targetTypeLabels[form.target_type] || "Objekt";
  const panelCaption = fixedTargetType
    ? `${selectedTargetLabel} auswählen und Zeitraum festlegen.`
    : "Wählen Sie Seminarraum, Arbeitsplatz oder Ausstattung und legen Sie den Zeitraum fest.";

  useEffect(() => {
    if (invitationEnabled) setRecurrenceCount(1);
  }, [invitationEnabled]);

  async function submit(event) {
    event.preventDefault();
    setState((current) => ({ ...current, loading: true, error: "", success: "", conflicts: [], suggestions: [], invitation: null }));
    try {
      const backendTargetType = toApiTargetType(form.target_type);
      const result = await createBooking({
        target_type: backendTargetType,
        target_id: form.target_id,
        title: form.title || "Reservierung",
        start_time: form.start_time,
        end_time: form.end_time,
        access_password: form.target_type === "room" ? form.access_password : "",
        invitation_emails: form.target_type === "room"
          ? parseEmails(form.invitation_emails)
          : [],
        recurrence_count: Number(recurrenceCount),
        recurrence_interval: "weekly",
      });
      const invitationCount = result.invitations?.length || 0;
      setState((current) => ({
        ...current,
        loading: false,
        success: result.series_count > 1
          ? `${result.series_count} wöchentliche Reservierungen wurden erstellt.`
          : invitationCount
          ? `Ihre Reservierung wurde erstellt und ${invitationCount} Einladung(en) wurden vorbereitet.`
          : "Ihre Reservierung wurde erstellt.",
        conflicts: [],
        suggestions: [],
        invitation: result.invitation ? {
          ...result.invitation,
          password: form.access_password,
        } : null,
      }));
      setForm({ ...form, title: "", access_password: "", invitation_emails: "" });
    } catch (error) {
      setState((current) => ({
        ...current,
        loading: false,
        error: error.message,
        success: "",
        conflicts: error.data?.conflicts || [],
        suggestions: error.data?.suggestions || [],
        invitation: null,
      }));
    }
  }

  if (!isLoggedIn) {
    return (
      <Panel title="Buchung erstellen" caption="Login erforderlich.">
        <EmptyState
          title="Bitte zuerst einloggen"
          text="Buchungen können nur für angemeldete Nutzer erstellt werden."
          action={<Button onClick={() => setPage("login")}>Zum Login</Button>}
        />
      </Panel>
    );
  }

  return (
    <div className="page-stack">
      <Panel title="Buchung erstellen" caption={panelCaption}>
        {state.loadingResources ? <LoadingState label="Auswahl wird geladen..." /> : (
          <form className="form-stack" onSubmit={submit}>
            {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
            {state.success && <StatusMessage type="success">{state.success}</StatusMessage>}

            <div className={`form-grid ${fixedTargetType ? "" : "two"}`}>
              {!fixedTargetType && (
                <label>
                  <span>Was möchten Sie reservieren?</span>
                  <select
                    value={form.target_type}
                    onChange={(event) => setForm({ ...form, target_type: event.target.value, target_id: "" })}
                  >
                    {targetTypes.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
                  </select>
                </label>
              )}
              <label>
                <span>{selectedTargetLabel}</span>
                <select
                  value={form.target_id}
                  onChange={(event) => setForm({ ...form, target_id: event.target.value })}
                  required
                >
                  <option value="">Bitte auswählen</option>
                  {options.map((option) => (
                    <option key={option.id} value={option.id}>{option.label}</option>
                  ))}
                </select>
              </label>
            </div>
            <small>{targetTypeHelp[form.target_type]}</small>

            <label>
              <span>Titel</span>
              <input placeholder="z.B. Teammeeting oder Arbeitsplatz Vormittag" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} />
            </label>

            {form.target_type === "room" && (
              <div className="form-grid two">
                <label>
                  <span>Buchungspasswort (optional)</span>
                  <input
                    type="password"
                    value={form.access_password}
                    onChange={(event) => setForm({ ...form, access_password: event.target.value })}
                    placeholder="Für externe Teilnehmende"
                  />
                </label>
                <label>
                  <span>Erlaubte E-Mail-Adressen (optional, kein Versand)</span>
                  <textarea
                    value={form.invitation_emails}
                    onChange={(event) => setForm({ ...form, invitation_emails: event.target.value })}
                    placeholder="anna@example.de, max@example.de"
                  />
                </label>
              </div>
            )}
            {form.target_type === "room" && (
              <small>RePlan versendet nichts. Die Liste beschränkt nur, welche Adressen mit dem später manuell geteilten Code und Passwort beitreten dürfen.</small>
            )}

            <div className="form-grid two">
              <label>
                <span>Start</span>
                <input type="datetime-local" value={form.start_time} onChange={(event) => setForm({ ...form, start_time: event.target.value })} required />
              </label>
              <label>
                <span>Ende</span>
                <input type="datetime-local" value={form.end_time} onChange={(event) => setForm({ ...form, end_time: event.target.value })} required />
              </label>
            </div>

            <label>
              <span>Wiederholung</span>
              <select value={recurrenceCount} disabled={invitationEnabled} onChange={(event) => setRecurrenceCount(Number(event.target.value))}>
                <option value={1}>Einmalig</option>
                <option value={2}>2 Wochen</option>
                <option value={4}>4 Wochen</option>
                <option value={8}>8 Wochen</option>
                <option value={12}>12 Wochen</option>
              </select>
              {invitationEnabled && <small>Geschützte Einladungen gelten eindeutig für einen einzelnen Termin.</small>}
            </label>

            <Button type="submit" icon={CalendarPlus} disabled={state.loading}>
              {state.loading ? "Reservierung wird erstellt..." : "Reservierung erstellen"}
            </Button>
          </form>
        )}
      </Panel>

      {state.invitation && (
        <Panel
          title="Einladung manuell teilen"
          caption="Es wird keine E-Mail versendet. Das Klartextpasswort wird nur jetzt angezeigt und im Backend ausschließlich als sicherer Hash gespeichert."
        >
          <div className="invitation-share-card">
            {(!state.invitation.recipients || state.invitation.recipients.length === 0) && (
              <StatusMessage type="warning">Ohne Empfängerliste kann jede Person mit Link, Code und Passwort beitreten.</StatusMessage>
            )}
            <div><span>Einladungscode</span><strong>{state.invitation.code}</strong></div>
            <div><span>Buchungspasswort</span><strong>{state.invitation.password}</strong></div>
            <div><span>Empfänger</span><strong>{state.invitation.recipients?.join(", ") || "Mit Link und Passwort teilbar"}</strong></div>
            <div className="invitation-share-actions">
              <Button variant="secondary" icon={Copy} onClick={() => copyText(invitationText(state.invitation))}>Einladung kopieren</Button>
              <Button variant="secondary" icon={LinkIcon} onClick={() => copyText(state.invitation.share_url)}>Link kopieren</Button>
            </div>
          </div>
        </Panel>
      )}

      {state.conflicts.length > 0 && (
        <Panel title="Zeitraum nicht verfügbar" caption="Für diese Auswahl gibt es bereits eine Reservierung.">
          <div className="conflict-list">
            {state.conflicts.map((conflict) => (
              <span className="conflict-item" key={conflict.id}>{conflict.title}: {formatDate(conflict.start_time)} bis {formatDate(conflict.end_time)}</span>
            ))}
          </div>
        </Panel>
      )}
      {state.suggestions.length > 0 && (
        <Panel title="Alternative Zeiten" caption="Diese freien Zeitfenster können direkt übernommen werden.">
          <div className="suggestion-grid">
            {state.suggestions.map((suggestion) => (
              <Button
                key={suggestion.start_time}
                variant="secondary"
                onClick={() => setForm({ ...form, start_time: toDateTimeLocal(suggestion.start_time), end_time: toDateTimeLocal(suggestion.end_time) })}
              >
                {formatDate(suggestion.start_time)} – {formatDate(suggestion.end_time)}
              </Button>
            ))}
          </div>
        </Panel>
      )}
    </div>
  );
}

export function buildOptions(type, resources) {
  if (type === "room") {
    return resources.rooms.filter((room) => room.room_type !== "shared_desk").map((room) => ({
      id: room.id,
      label: `${room.name}${room.location ? `, ${room.location}` : ""}`,
    }));
  }
  if (type === "shared_office_auto") {
    return resources.rooms.filter((room) => room.room_type === "shared_desk").map((room) => ({
      id: room.id,
      label: `${room.name} – freier Platz wird automatisch gewählt${room.location ? `, ${room.location}` : ""}`,
    }));
  }
  if (type === "seat") {
    const roomNames = Object.fromEntries(resources.rooms.map((room) => [room.id, room.name]));
    return resources.seats.map((seat) => ({
      id: seat.id,
      label: `${seat.label}${roomNames[seat.room_id] ? `, ${roomNames[seat.room_id]}` : ""}`,
    }));
  }
  return resources.assets.map((asset) => ({
    id: asset.id,
    label: `${asset.name}${asset.location ? `, ${asset.location}` : ""}`,
  }));
}

export function toApiTargetType(type) {
  return type === "shared_office_auto" ? "room" : type;
}

function invitationText(invitation) {
  return [
    "RePlan-Einladung",
    `Link: ${invitation.share_url}`,
    `Einladungscode: ${invitation.code}`,
    `Buchungspasswort: ${invitation.password}`,
  ].join("\n");
}

async function copyText(value) {
  await navigator.clipboard.writeText(value);
}

function formatDate(value) {
  return new Intl.DateTimeFormat("de-DE", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

export function parseEmails(value) {
  return String(value || "")
    .split(/[\s,;]+/)
    .map((email) => email.trim().toLowerCase())
    .filter((email, index, values) => email.includes("@") && values.indexOf(email) === index);
}
