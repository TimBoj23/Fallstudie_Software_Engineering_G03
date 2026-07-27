export function toUtcIso(value) {
  if (!value) return "";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toISOString();
}

export function toDateTimeLocal(value) {
  if (!value) return "";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return String(value).slice(0, 16);
  const localTime = new Date(parsed.getTime() - parsed.getTimezoneOffset() * 60_000);
  return localTime.toISOString().slice(0, 16);
}
