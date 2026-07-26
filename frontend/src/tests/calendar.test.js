import { describe, expect, it } from "vitest";
import { bookingToIcs } from "../utils/calendar.js";

describe("Kalenderexport", () => {
  it("erzeugt einen gültigen UTC-Termin und maskiert Text", () => {
    const ics = bookingToIcs({
      id: "booking-1",
      title: "Planung, Team; A",
      target_name: "Meetingraum Epsilon",
      target_meta: "Gebäude A",
      start_time: "2026-08-01T10:00:00+02:00",
      end_time: "2026-08-01T11:30:00+02:00",
    });

    expect(ics).toContain("BEGIN:VCALENDAR");
    expect(ics).toContain("DTSTART:20260801T080000Z");
    expect(ics).toContain("DTEND:20260801T093000Z");
    expect(ics).toContain("SUMMARY:Planung\\, Team\\; A");
  });
});
