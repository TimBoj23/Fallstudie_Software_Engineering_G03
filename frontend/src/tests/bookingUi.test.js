import { describe, expect, it } from "vitest";
import { slotStatus } from "../components/ObjectCalendar.jsx";
import { buildOptions, parseEmails, toApiTargetType } from "../pages/CreateBooking.jsx";
import { filterDismissedNotifications } from "../pages/Notifications.jsx";

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
});
