import { describe, expect, it } from "vitest";

import { toDateTimeLocal, toUtcIso } from "../utils/dateTime.js";

describe("Zeitzonen-Helfer", () => {
  it("sendet datetime-local-Werte als eindeutigen UTC-Zeitpunkt", () => {
    const localValue = "2026-07-27T16:00";
    expect(new Date(toUtcIso(localValue)).getTime()).toBe(new Date(localValue).getTime());
    expect(toUtcIso(localValue)).toMatch(/Z$/);
  });

  it("wandelt API-Zeitstempel für datetime-local zurück", () => {
    const instant = new Date("2026-07-27T14:00:00Z");
    const expectedLocal = new Date(instant.getTime() - instant.getTimezoneOffset() * 60_000)
      .toISOString()
      .slice(0, 16);

    expect(toDateTimeLocal(instant.toISOString())).toBe(expectedLocal);
  });
});
