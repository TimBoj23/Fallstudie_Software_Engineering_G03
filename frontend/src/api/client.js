export const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

function buildUrl(path, params) {
  const url = new URL(`${API_BASE}${path}`);
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, value);
    }
  });
  return url.toString();
}

export async function apiRequest(path, options = {}) {
  const token = localStorage.getItem("replan_token");
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}`, "X-User-Id": token } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(buildUrl(path, options.params), {
    ...options,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const text = await response.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { message: text };
    }
  }

  if (!response.ok) {
    const message = data?.error || data?.message || `Fehler ${response.status}`;
    const error = new Error(message);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}
