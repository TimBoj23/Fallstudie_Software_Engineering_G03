import { apiRequest } from "./client";

export function getUsers() {
  return apiRequest("/users");
}

export function createUser(payload) {
  return apiRequest("/users", {
    method: "POST",
    body: payload,
  });
}

export function resetUserPassword(id, payload) {
  return apiRequest(`/users/${id}/reset-password`, {
    method: "POST",
    body: payload,
  });
}
