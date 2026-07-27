import { apiRequest } from "./client.js";

export function resetDemoActivity(payload) {
  return apiRequest("/admin/reset-demo", { method: "POST", body: payload });
}
