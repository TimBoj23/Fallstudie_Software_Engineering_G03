import { apiRequest } from "./client";

export function getRooms(params) {
  return apiRequest("/rooms", { params });
}

export function createRoom(payload) {
  return apiRequest("/rooms", { method: "POST", body: payload });
}

export function updateRoom(id, payload) {
  return apiRequest(`/rooms/${id}`, { method: "PUT", body: payload });
}

export function deleteRoom(id) {
  return apiRequest(`/rooms/${id}`, { method: "DELETE" });
}
