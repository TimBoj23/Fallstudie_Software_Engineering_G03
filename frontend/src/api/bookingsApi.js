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

export function checkInBooking(id) {
  return apiRequest(`/bookings/${id}/check-in`, { method: "POST" });
}

export function checkOutBooking(id) {
  return apiRequest(`/bookings/${id}/check-out`, { method: "POST" });
}

export function checkAvailability(params) {
  return apiRequest("/bookings/availability", { params });
}

export function getBookingSchedule(params) {
  return apiRequest("/bookings/schedule", { params });
}

export function getRoomOccupancy() {
  return apiRequest("/bookings/occupancy");
}

export function getBookingAnalytics(days = 30) {
  return apiRequest("/bookings/analytics", { params: { days } });
}

export function getCheckInCode(id) {
  return apiRequest(`/bookings/${id}/check-in-code`);
}

export function qrCheckIn(token) {
  return apiRequest("/bookings/qr-check-in", { method: "POST", body: { token } });
}

export function joinBooking(id, payload) {
  return apiRequest(`/bookings/${id}/join`, { method: "POST", body: payload });
}
