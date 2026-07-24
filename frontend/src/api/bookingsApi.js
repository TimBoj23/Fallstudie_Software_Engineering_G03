import { apiRequest } from "./client";

export function getBookings(params) {
  return apiRequest("/bookings", { params });
}

export function getAllBookings(params) {
  return apiRequest("/bookings/all", { params });
}

export function createBooking(payload) {
  return apiRequest("/bookings", { method: "POST", body: payload });
}

export function cancelBooking(id) {
  return apiRequest(`/bookings/${id}`, { method: "DELETE" });
}

export function checkAvailability(params) {
  return apiRequest("/bookings/availability", { params });
}

export function getBookingSchedule(params) {
  return apiRequest("/bookings/schedule", { params });
}
