import { apiRequest } from "./client";

export function getAssets(params) {
  return apiRequest("/assets", { params });
}

export function createAsset(payload) {
  return apiRequest("/assets", { method: "POST", body: payload });
}

export function updateAsset(id, payload) {
  return apiRequest(`/assets/${id}`, { method: "PUT", body: payload });
}

export function deleteAsset(id) {
  return apiRequest(`/assets/${id}`, { method: "DELETE" });
}
