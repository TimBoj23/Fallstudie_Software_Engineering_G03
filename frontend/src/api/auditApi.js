import { apiRequest } from "./client";

export function getAuditEvents(params) {
  return apiRequest("/audit", { params });
}
