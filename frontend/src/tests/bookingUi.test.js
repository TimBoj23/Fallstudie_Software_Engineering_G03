import { describe, expect, it } from "vitest";
import { slotStatus } from "../components/ObjectCalendar.jsx";
import { attendanceState, effectiveEndTime } from "../components/BookingCard.jsx";
import { buildOptions, parseEmails, toApiTargetType } from "../pages/CreateBooking.jsx";
import { filterDismissedNotifications } from "../pages/Notifications.jsx";
import { availabilityPresentation } from "../pages/Availability.jsx";
import { resolveFavorites } from "../pages/Favorites.jsx";

describe("Buchungsoberfläche", () => {
  it("unterscheidet Ganzraumbelegung und Shared-Office-Teilbelegung", () => {
    expect(slotStatus({ booked: true, available: false })).toBe("booked-full");
    expect(slotStatus({ booked: true, available: true })).toBe("booked-partial");
    expect(slotStatus({ booked: false, available: true })).toBe("free");
  });

  it("normalisiert und dedupliziert Einladungsadressen", () => {
    expect(parseEmails("Anna@example.de, anna@example.de; max@example.de")).toEqual([
      "anna@example.de",
      "max@example.de",
    ]);
  });

  it("trennt Räume, automatische Shared-Office-Auswahl und konkrete Plätze", () => {
    const resources = {
      rooms: [
        { id: "room-1", name: "Seminar", room_type: "seminarraum" },
        { id: "office-1", name: "Office", room_type: "shared_desk" },
      ],
      seats: [{ id: "seat-1", room_id: "office-1", label: "A1" }],
      assets: [],
    };

    expect(buildOptions("room", resources).map((item) => item.id)).toEqual(["room-1"]);
    expect(buildOptions("shared_office_auto", resources).map((item) => item.id)).toEqual(["office-1"]);
    expect(buildOptions("seat", resources).map((item) => item.id)).toEqual(["seat-1"]);
    expect(toApiTargetType("shared_office_auto")).toBe("room");
  });

  it("blendet gelöschte Benachrichtigungen aus", () => {
    const notifications = [{ id: "one" }, { id: "two" }];
    expect(filterDismissedNotifications(notifications, ["one"])).toEqual([{ id: "two" }]);
  });

  it("zeigt einen abgelaufenen Check-in automatisch als ausgecheckt", () => {
    const booking = {
      checked_in_at: "2026-07-27T14:05:00Z",
      checked_out_at: "",
      end_time: "2026-07-27T15:00:00Z",
    };

    expect(attendanceState(booking, Date.parse("2026-07-27T15:00:00Z"))).toEqual({
      hasEnded: true,
      isCheckedIn: false,
      isCheckedOut: true,
    });
  });

  it("zeigt bei vorzeitigem Check-out den tatsächlichen Endzeitpunkt", () => {
    const booking = {
      checked_in_at: "2026-07-28T08:05:00Z",
      checked_out_at: "2026-07-28T08:30:00Z",
      end_time: "2026-07-28T10:00:00Z",
    };

    expect(attendanceState(booking, Date.parse("2026-07-28T08:31:00Z"))).toEqual({
      hasEnded: true,
      isCheckedIn: false,
      isCheckedOut: true,
    });
    expect(effectiveEndTime(booking)).toBe("2026-07-28T08:30:00Z");
  });

  it("löst gespeicherte Favoriten zu sichtbaren Ressourcen auf", () => {
    const result = resolveFavorites(
      [{ key: "room:room-1", target_type: "room", target_id: "room-1" }],
      { rooms: [{ id: "room-1", name: "Alpha", room_type: "shared_desk", equipment: [] }] },
    );

    expect(result[0]).toMatchObject({
      title: "Alpha",
      favoriteType: "room",
      bookingTargetType: "shared_office_auto",
    });
  });

  it("liefert klare visuelle Texte für freie und belegte Zeiträume", () => {
    expect(availabilityPresentation({ available: true }).title).toBe("Frei und buchbar");
    expect(availabilityPresentation({ available: false }).title).toBe("Bereits belegt");
  });
});
