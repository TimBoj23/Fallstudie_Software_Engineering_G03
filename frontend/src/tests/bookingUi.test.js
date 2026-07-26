import { describe, expect, it } from "vitest";
import { slotStatus } from "../components/ObjectCalendar.jsx";
import { parseEmails } from "../pages/CreateBooking.jsx";

describe("Buchungsoberfläche", () => {
  it("unterscheidet Ganzraumbelegung und Shared-Desk-Teilbelegung", () => {
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
});
