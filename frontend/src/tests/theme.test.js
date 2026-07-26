import { describe, expect, it } from "vitest";
import { resolveTheme } from "../state/themeStore.js";

describe("Theme-Auswahl", () => {
  it("bevorzugt eine gespeicherte Auswahl", () => {
    expect(resolveTheme("light", true)).toBe("light");
    expect(resolveTheme("dark", false)).toBe("dark");
  });

  it("verwendet sonst die Systempräferenz", () => {
    expect(resolveTheme(null, true)).toBe("dark");
    expect(resolveTheme(null, false)).toBe("light");
  });
});
