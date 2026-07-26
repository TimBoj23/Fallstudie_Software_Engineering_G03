import { useState } from "react";
import QRCode from "qrcode";
import { CalendarArrowDown, Copy, LogIn, LogOut, QrCode, XCircle } from "lucide-react";
import { mediaUrl } from "../api/client.js";
import { getCheckInCode } from "../api/bookingsApi.js";
import { downloadBookingIcs } from "../utils/calendar.js";
import Button from "./Button.jsx";

const typeLabels = {
  room: "Raum",
  seat: "Arbeitsplatz",
  asset: "Ausstattung",
};

export default function BookingCard({ booking, onCancel, onAttendance, onCopy }) {
  const [qr, setQr] = useState({ loading: false, image: "", error: "" });
  const active = booking.status === "active";
  const now = Date.now();
  const isCurrent = active && now >= new Date(booking.start_time).getTime() && now < new Date(booking.end_time).getTime();
  const isCheckedIn = Boolean(booking.checked_in_at && !booking.checked_out_at);
  const targetName = booking.target_name || booking.target_id;
  const targetMeta = [typeLabels[booking.target_type] || booking.target_type, booking.target_meta].filter(Boolean).join(" · ");

  async function showQr() {
    setQr({ loading: true, image: "", error: "" });
    try {
      const result = await getCheckInCode(booking.id);
      const image = await QRCode.toDataURL(result.check_in_url, { width: 280, margin: 2, errorCorrectionLevel: "M" });
      setQr({ loading: false, image, error: "" });
    } catch (error) {
      setQr({ loading: false, image: "", error: error.message });
    }
  }

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
          {isCheckedIn && <span className="badge info">Eingecheckt</span>}
          {booking.checked_out_at && <span className="badge muted">Ausgecheckt</span>}
        </div>
        <strong>{targetName}</strong>
        <p className="resource-meta">
          {targetMeta}
        </p>
        <p>{formatDate(booking.start_time)} bis {formatDate(booking.end_time)}</p>
      </div>
      <div className="booking-card-actions">
        <Button variant="secondary" icon={CalendarArrowDown} onClick={() => downloadBookingIcs(booking)}>Kalender</Button>
        {onCopy && <Button variant="secondary" icon={Copy} onClick={() => onCopy(booking)}>Kopieren</Button>}
        {active && booking.target_type !== "asset" && <Button variant="secondary" icon={QrCode} onClick={showQr}>QR-Code</Button>}
        {booking.target_type !== "asset" && isCurrent && onAttendance && !booking.checked_in_at && (
          <Button icon={LogIn} onClick={() => onAttendance(booking.id, "check-in")}>Check-in</Button>
        )}
        {isCheckedIn && onAttendance && (
          <Button variant="secondary" icon={LogOut} onClick={() => onAttendance(booking.id, "check-out")}>Check-out</Button>
        )}
        {active && onCancel && (
          <Button variant="danger" icon={XCircle} onClick={() => onCancel(booking.id)}>
            Stornieren
          </Button>
        )}
      </div>
      {(qr.loading || qr.image || qr.error) && (
        <div className="qr-panel">
          {qr.loading && <span>QR-Code wird erstellt…</span>}
          {qr.error && <span className="text-danger">{qr.error}</span>}
          {qr.image && <><img src={qr.image} alt="QR-Code zum Check-in" /><small>Mit dem Smartphone scannen und mit demselben Konto anmelden.</small></>}
          <button type="button" onClick={() => setQr({ loading: false, image: "", error: "" })}>Schließen</button>
        </div>
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
