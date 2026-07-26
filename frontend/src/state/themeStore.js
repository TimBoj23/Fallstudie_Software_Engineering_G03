const THEME_KEY = "replan_theme";

export function loadTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  const prefersDark = Boolean(window.matchMedia?.("(prefers-color-scheme: dark)").matches);
  return resolveTheme(stored, prefersDark);
}

export function resolveTheme(stored, prefersDark) {
  if (stored === "light" || stored === "dark") return stored;
  return prefersDark ? "dark" : "light";
}

export function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  document.documentElement.style.colorScheme = theme;
  localStorage.setItem(THEME_KEY, theme);
}
