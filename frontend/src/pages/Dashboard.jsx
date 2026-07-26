import { useEffect, useState } from "react";
import { CalendarPlus, CheckCircle2, ClipboardList, SearchCheck } from "lucide-react";
import { getAssets } from "../api/assetsApi.js";
import { getRooms } from "../api/roomsApi.js";
import { getSeats } from "../api/seatsApi.js";
import Button from "../components/Button.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

export default function Dashboard({ setPage, isLoggedIn }) {
  const [summary, setSummary] = useState({ loading: true, error: "", data: null });

  useEffect(() => {
    let ignore = false;
    async function load() {
      try {
        const [rooms, seats, assets] = await Promise.all([
          getRooms(),
          getSeats(),
          getAssets(),
        ]);
        if (!ignore) {
          setSummary({
            loading: false,
            error: "",
            data: {
              rooms: rooms.count ?? rooms.rooms?.length ?? 0,
              seats: seats.count ?? seats.seats?.length ?? 0,
              assets: assets.count ?? assets.assets?.length ?? 0,
            },
          });
        }
      } catch (error) {
        if (!ignore) {
          setSummary({ loading: false, error: error.message, data: null });
        }
      }
    }
    load();
    return () => {
      ignore = true;
    };
  }, []);

  return (
    <div className="page-stack">
      <section className="page-intro">
        <div>
          <p className="eyebrow">Buchungszentrale</p>
          <h2>Finden Sie den passenden Raum für Ihren Arbeitstag.</h2>
          <p>
            Reservieren Sie Räume, Arbeitsplätze und Ausstattung an einem Ort. RePlan zeigt
            verfügbare Optionen übersichtlich an und verhindert doppelte Buchungen automatisch.
          </p>
        </div>
        <div className="intro-actions">
          <Button icon={SearchCheck} onClick={() => setPage("availability")}>Verfügbarkeit prüfen</Button>
          <Button variant="secondary" icon={CalendarPlus} onClick={() => setPage("createBooking")} disabled={!isLoggedIn}>
            Buchung erstellen
          </Button>
        </div>
      </section>

      {summary.loading ? (
        <LoadingState label="Übersicht wird geladen..." />
      ) : summary.error ? (
        <StatusMessage type="warning">
          Die Übersicht konnte gerade nicht geladen werden. Bitte versuchen Sie es gleich erneut.
        </StatusMessage>
      ) : (
        <div className="metric-grid">
          <Metric label="Räume insgesamt" value={summary.data.rooms} />
          <Metric label="Arbeitsplätze" value={summary.data.seats} />
          <Metric label="Ausstattung" value={summary.data.assets} />
          <Metric label="Konfliktprüfung" value="Aktiv" tone="success" />
        </div>
      )}

      <Panel title="So funktioniert RePlan" caption="In wenigen Schritten zur passenden Reservierung.">
        <div className="workflow-grid">
          <WorkflowStep index="1" title="Auswahl treffen" text="Raum, Arbeitsplatz oder Ausstattung auswählen." />
          <WorkflowStep index="2" title="Zeitraum festlegen" text="Start und Ende der gewünschten Nutzung eintragen." />
          <WorkflowStep index="3" title="Reservieren" text="RePlan prüft automatisch, ob der Zeitraum frei ist." />
          <WorkflowStep index="4" title="Überblick behalten" text="Eigene Buchungen jederzeit einsehen oder stornieren." />
        </div>
      </Panel>

      <Panel title="Direkt loslegen">
        <div className="quick-actions">
          <Button variant="secondary" icon={ClipboardList} onClick={() => setPage("rooms")}>Räume ansehen</Button>
          <Button variant="secondary" icon={ClipboardList} onClick={() => setPage("seats")}>Arbeitsplätze ansehen</Button>
          <Button variant="secondary" icon={ClipboardList} onClick={() => setPage("assets")}>Ausstattung ansehen</Button>
          <Button variant="secondary" icon={CheckCircle2} onClick={() => setPage("bookings")} disabled={!isLoggedIn}>
            Meine Buchungen
          </Button>
        </div>
      </Panel>
    </div>
  );
}

function Metric({ label, value, tone }) {
  return (
    <div className={`metric-card ${tone || ""}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function WorkflowStep({ index, title, text }) {
  return (
    <div className="workflow-step">
      <span>{index}</span>
      <h3>{title}</h3>
      <p>{text}</p>
    </div>
  );
}
