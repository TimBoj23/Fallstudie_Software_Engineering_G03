import { useEffect, useState } from "react";
import QRCode from "qrcode";
import { CalendarArrowDown, Clock3, Copy, LogIn, LogOut, Pencil, QrCode, XCircle } from "lucide-react";
import { mediaUrl } from "../api/client.js";
import { getCheckInCode } from "../api/bookingsApi.js";
import { downloadBookingIcs } from "../utils/calendar.js";
import Button from "./Button.jsx";

const typeLabels = {
  room: "Raum",
  seat: "Arbeitsplatz",
  asset: "Ausstattung",
};

export default function BookingCard({ booking, onCancel, onAttendance, onCopy, onEdit, onExtend }) {
  const [qr, setQr] = useState({ loading: false, image: "", error: "" });
  const [now, setNow] = useState(Date.now());
  const active = booking.status === "active";
  const attendance = attendanceState(booking, now);
  const isCurrent = active && now >= new Date(booking.start_time).getTime() && !attendance.hasEnded;
  const isCheckedIn = attendance.isCheckedIn;
  const isFuture = new Date(booking.start_time).getTime() > now;
  const canExtend = active && !attendance.hasEnded;
  const targetName = booking.target_name || booking.target_id;
  const targetMeta = [typeLabels[booking.target_type] || booking.target_type, booking.target_meta].filter(Boolean).join(" · ");
  const displayedEndTime = effectiveEndTime(booking);
  const endedEarly = Boolean(booking.checked_out_at) && displayedEndTime !== booking.end_time;

  useEffect(() => {
    const remaining = new Date(booking.end_time).getTime() - Date.now();
    if (remaining <= 0) {
      setNow(Date.now());
      return undefined;
    }
    const timer = window.setTimeout(
      () => setNow(Date.now()),
      Math.min(remaining + 100, 2_147_483_647),
    );
    return () => window.clearTimeout(timer);
  }, [booking.end_time]);

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
          <span className={`badge ${active && !attendance.hasEnded ? "success" : "muted"}`}>
            {!active ? "Storniert" : attendance.hasEnded ? "Beendet" : "Aktiv"}
          </span>
          {isCheckedIn && <span className="badge info">Eingecheckt</span>}
          {attendance.isCheckedOut && <span className="badge muted">Ausgecheckt</span>}
        </div>
        <strong>{targetName}</strong>
        <p className="resource-meta">
          {targetMeta}
        </p>
        <p>{formatDate(booking.start_time)} bis {formatDate(displayedEndTime)}</p>
        {endedEarly && (
          <small className="resource-meta">
            Vorzeitig ausgecheckt · ursprünglich geplant bis {formatDate(booking.end_time)}
          </small>
        )}
      </div>
      <div className="booking-card-actions">
        <Button variant="secondary" icon={CalendarArrowDown} onClick={() => downloadBookingIcs(booking)}>Kalender</Button>
        {onCopy && <Button variant="secondary" icon={Copy} onClick={() => onCopy(booking)}>Kopieren</Button>}
        {active && isFuture && onEdit && <Button variant="secondary" icon={Pencil} onClick={() => onEdit(booking)}>Bearbeiten</Button>}
        {canExtend && onExtend && <Button variant="secondary" icon={Clock3} onClick={() => onExtend(booking.id, 30)}>+30 Min.</Button>}
        {active && !attendance.hasEnded && booking.target_type !== "asset" && <Button variant="secondary" icon={QrCode} onClick={showQr}>QR-Code</Button>}
        {booking.target_type !== "asset" && isCurrent && onAttendance && !booking.checked_in_at && (
          <Button icon={LogIn} onClick={() => onAttendance(booking.id, "check-in")}>Check-in</Button>
        )}
        {isCheckedIn && onAttendance && (
          <Button variant="secondary" icon={LogOut} onClick={() => onAttendance(booking.id, "check-out")}>Check-out</Button>
        )}
        {active && !attendance.hasEnded && onCancel && <Button variant="danger" icon={XCircle} onClick={() => onCancel(booking.id, "single")}>{booking.series_id ? "Termin stornieren" : "Stornieren"}</Button>}
        {active && !attendance.hasEnded && booking.series_id && onCancel && <Button variant="danger" icon={XCircle} onClick={() => onCancel(booking.id, "future")}>Serie ab hier stornieren</Button>}
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

export function attendanceState(booking, now = Date.now()) {
  const hasCheckedIn = Boolean(booking.checked_in_at);
  const hasManualCheckout = Boolean(booking.checked_out_at);
  const hasEnded = hasManualCheckout || now >= new Date(booking.end_time).getTime();
  const isCheckedOut = hasManualCheckout || (hasCheckedIn && hasEnded);
  return {
    hasEnded,
    isCheckedIn: hasCheckedIn && !isCheckedOut,
    isCheckedOut,
  };
}

export function effectiveEndTime(booking) {
  if (!booking.checked_out_at) return booking.end_time;
  const checkedOutAt = new Date(booking.checked_out_at).getTime();
  const plannedEnd = new Date(booking.end_time).getTime();
  return Number.isFinite(checkedOutAt) && checkedOutAt < plannedEnd
    ? booking.checked_out_at
    : booking.end_time;
}

function formatDate(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("de-DE", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}
