import { XCircle } from "lucide-react";
import { mediaUrl } from "../api/client.js";
import Button from "./Button.jsx";

const typeLabels = {
  room: "Raum",
  seat: "Arbeitsplatz",
  asset: "Ausstattung",
};

export default function BookingCard({ booking, onCancel }) {
  const active = booking.status === "active";
  const targetName = booking.target_name || booking.target_id;
  const targetMeta = [typeLabels[booking.target_type] || booking.target_type, booking.target_meta].filter(Boolean).join(" · ");

  return (
    <article className="booking-card">
      {booking.target_image_url && (
        <img className="booking-image" src={mediaUrl(booking.target_image_url)} alt={targetName} loading="lazy" />
      )}
      <div className="booking-card-content">
        <div className="booking-title-row">
          <h3>{booking.title || "Buchung"}</h3>
          <span className={`badge ${active ? "success" : "muted"}`}>
            {active ? "Aktiv" : "Storniert"}
          </span>
        </div>
        <strong>{targetName}</strong>
        <p className="resource-meta">
          {targetMeta}
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
