export function bookingToIcs(booking) {
  const escapeText = (value) => String(value || "")
    .replace(/\\/g, "\\\\")
    .replace(/\n/g, "\\n")
    .replace(/,/g, "\\,")
    .replace(/;/g, "\\;");
  const utcStamp = (value) => new Date(value).toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z");
  const summary = booking.title || "RePlan Buchung";
  const location = booking.target_name || booking.target_meta || "";
  const description = [booking.target_name, booking.target_meta].filter(Boolean).join(" · ");

  return [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//RePlan//Buchung//DE",
    "CALSCALE:GREGORIAN",
    "BEGIN:VEVENT",
    `UID:${escapeText(booking.id)}@replan.local`,
    `DTSTAMP:${utcStamp(new Date())}`,
    `DTSTART:${utcStamp(booking.start_time)}`,
    `DTEND:${utcStamp(booking.end_time)}`,
    `SUMMARY:${escapeText(summary)}`,
    `LOCATION:${escapeText(location)}`,
    `DESCRIPTION:${escapeText(description)}`,
    "END:VEVENT",
    "END:VCALENDAR",
    "",
  ].join("\r\n");
}

export function downloadBookingIcs(booking) {
  const blob = new Blob([bookingToIcs(booking)], { type: "text/calendar;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `replan-${String(booking.title || booking.id || "buchung").replace(/[^a-z0-9_-]+/gi, "-").toLowerCase()}.ics`;
  link.click();
  URL.revokeObjectURL(url);
}
