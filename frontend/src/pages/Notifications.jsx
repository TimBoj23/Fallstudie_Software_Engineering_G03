import { Bell, CheckCheck, RefreshCw, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { getNotifications } from "../api/bookingsApi.js";
import Button from "../components/Button.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";


export default function Notifications({ isLoggedIn, user, setPage }) {
  const readStorageKey = `replan_read_notifications_${user?.id || "anonymous"}`;
  const dismissedStorageKey = `replan_dismissed_notifications_${user?.id || "anonymous"}`;
  const [state, setState] = useState({ loading: false, error: "", notifications: [] });
  const [readIds, setReadIds] = useState(() => readStored(readStorageKey));
  const [dismissedIds, setDismissedIds] = useState(() => readStored(dismissedStorageKey));

  async function load() {
    if (!isLoggedIn) return;
    setState((current) => ({ ...current, loading: true, error: "" }));
    try {
      const result = await getNotifications();
      setState({ loading: false, error: "", notifications: result.notifications || [] });
    } catch (error) {
      setState({ loading: false, error: error.message, notifications: [] });
    }
  }

  useEffect(() => { load(); }, [isLoggedIn, user?.id]);
  useEffect(() => { setReadIds(readStored(readStorageKey)); }, [readStorageKey]);
  useEffect(() => { setDismissedIds(readStored(dismissedStorageKey)); }, [dismissedStorageKey]);
  const visible = useMemo(
    () => filterDismissedNotifications(state.notifications, dismissedIds),
    [state.notifications, dismissedIds],
  );
  const unread = useMemo(() => visible.filter((item) => !readIds.includes(item.id)).length, [visible, readIds]);

  function markAllRead() {
    const next = visible.map((item) => item.id);
    localStorage.setItem(readStorageKey, JSON.stringify(next));
    setReadIds(next);
  }

  function dismiss(ids) {
    const next = [...new Set([...dismissedIds, ...ids])];
    localStorage.setItem(dismissedStorageKey, JSON.stringify(next));
    setDismissedIds(next);
  }

  function dismissAll() {
    if (visible.length === 0 || !window.confirm("Alle angezeigten Benachrichtigungen löschen? Die Buchungen bleiben bestehen.")) return;
    dismiss(visible.map((item) => item.id));
  }

  if (!isLoggedIn) {
    return <Panel title="Benachrichtigungen"><EmptyState title="Login erforderlich" action={<Button onClick={() => setPage("login")}>Zum Login</Button>} /></Panel>;
  }

  return (
    <div className="page-stack">
      <Panel
        title="Benachrichtigungen"
        caption={`${unread} ungelesene Hinweise · vollständig innerhalb von RePlan, ohne E-Mail-Versand`}
        actions={(
          <div className="panel-actions">
            <Button variant="secondary" icon={RefreshCw} onClick={load}>Aktualisieren</Button>
            <Button variant="secondary" icon={CheckCheck} onClick={markAllRead}>Alle gelesen</Button>
            <Button variant="secondary" icon={Trash2} onClick={dismissAll} disabled={visible.length === 0}>Alle löschen</Button>
          </div>
        )}
      >
        {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
      </Panel>
      {state.loading ? <LoadingState label="Hinweise werden geladen…" /> : (
        <div className="notification-list">
          {visible.length === 0 ? (
            <EmptyState title="Keine aktuellen Hinweise" text="Bevorstehende Termine, Check-ins und Stornierungen erscheinen hier automatisch." />
          ) : visible.map((item) => (
            <article className={`notification-card ${readIds.includes(item.id) ? "read" : "unread"}`} key={item.id}>
              <span className={`notification-icon ${item.priority}`}><Bell size={18} /></span>
              <div>
                <strong>{item.title}</strong>
                <p>{item.message}</p>
                <small>{formatDate(item.event_time)}</small>
              </div>
              <div className="notification-actions">
                {!readIds.includes(item.id) && <span className="badge info">Neu</span>}
                <Button
                  variant="ghost"
                  size="sm"
                  icon={Trash2}
                  aria-label={`Benachrichtigung „${item.title}“ löschen`}
                  title="Benachrichtigung löschen"
                  onClick={() => dismiss([item.id])}
                />
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}


export function filterDismissedNotifications(notifications, dismissedIds) {
  const dismissed = new Set(dismissedIds || []);
  return (notifications || []).filter((item) => !dismissed.has(item.id));
}


function readStored(key) {
  try {
    return JSON.parse(localStorage.getItem(key) || "[]");
  } catch {
    return [];
  }
}


function formatDate(value) {
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}
