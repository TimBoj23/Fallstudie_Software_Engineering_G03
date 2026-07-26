import { apiRequest } from "./client";

export function loginUser(credentials) {
  return apiRequest("/auth/login", {
    method: "POST",
    body: credentials,
  });
}

export function registerUser(payload) {
  return apiRequest("/auth/register", {
    method: "POST",
    body: payload,
  });
}

export function logoutUser() {
  return apiRequest("/auth/logout", {
    method: "POST",
    body: {},
  });
}

export function requestPasswordReset(payload) {
  return apiRequest("/auth/password-reset-request", {
    method: "POST",
    body: payload,
  });
}

export function resetPassword(payload) {
  return apiRequest("/auth/password-reset", {
    method: "POST",
    body: payload,
  });
}
