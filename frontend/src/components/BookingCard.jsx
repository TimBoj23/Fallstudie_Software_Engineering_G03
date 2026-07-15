import { XCircle } from "lucide-react";
import Button from "./Button.jsx";

const typeLabels = {
  room: "Raum",
  seat: "Arbeitsplatz",
  asset: "Ausstattung",
};

export default function BookingCard({ booking, onCancel }) {
  const active = booking.status === "active";

  return (
    <article className="booking-card">
      <div>
        <div className="booking-title-row">
          <h3>{booking.title || "Buchung"}</h3>
          <span className={`badge ${active ? "success" : "muted"}`}>
            {active ? "Aktiv" : "Storniert"}
          </span>
        </div>
        <p className="resource-meta">
          {typeLabels[booking.target_type] || booking.target_type} · {booking.target_id}
        </p>
        <p>{formatDate(booking.start_time)} bis {formatDate(booking.end_time)}</p>
      </div>
      {active && onCancel && (
        <Button variant="danger" icon={XCircle} onClick={() => onCancel(booking.id)}>
          Stornieren
        </Button>
      )}
    </article>
  );
}

function formatDate(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("de-DE", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}
