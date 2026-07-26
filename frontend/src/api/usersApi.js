import { apiRequest } from "./client";

export function getUsers(params) {
  return apiRequest("/users", { params });
}

export function getFavorites() {
  return apiRequest("/users/me/favorites");
}

export function getOwnProfile() {
  return apiRequest("/users/me");
}

export function updateOwnProfile(payload) {
  return apiRequest("/users/me", {
    method: "PUT",
    body: payload,
  });
}

export function changeOwnPassword(payload) {
  return apiRequest("/users/me/change-password", {
    method: "POST",
    body: payload,
  });
}

export function deleteOwnAccount(current_password) {
  return apiRequest("/users/me", {
    method: "DELETE",
    body: { current_password },
  });
}

export function setFavorite(target_type, target_id, enabled) {
  return apiRequest("/users/me/favorites", {
    method: "PUT",
    body: { target_type, target_id, enabled },
  });
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

export function updateUser(id, payload) {
  return apiRequest(`/users/${id}`, {
    method: "PUT",
    body: payload,
  });
}
