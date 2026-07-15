import { apiRequest } from "./client";

export function getSeats(params) {
  return apiRequest("/seats", { params });
}

export function createSeat(payload) {
  return apiRequest("/seats", { method: "POST", body: payload });
}

export function updateSeat(id, payload) {
  return apiRequest(`/seats/${id}`, { method: "PUT", body: payload });
}

export function deleteSeat(id) {
  return apiRequest(`/seats/${id}`, { method: "DELETE" });
}
