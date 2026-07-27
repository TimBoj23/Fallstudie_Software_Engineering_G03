import { apiRequest } from "./client";
import { toUtcIso } from "../utils/dateTime.js";

export function getBookings(params) {
  return apiRequest("/bookings", { params: normalizeFilterTimes(params) });
}

export function getAllBookings(params) {
  return apiRequest("/bookings/all", { params: normalizeFilterTimes(params) });
}

export function createBooking(payload) {
  return apiRequest("/bookings", { method: "POST", body: normalizeBookingTimes(payload) });
}

export function cancelBooking(id, scope = "single") {
  return apiRequest(`/bookings/${id}`, { method: "DELETE", params: { scope } });
}

export function updateBooking(id, payload) {
  return apiRequest(`/bookings/${id}`, { method: "PUT", body: normalizeBookingTimes(payload) });
}

export function extendBooking(id, minutes = 30) {
  return apiRequest(`/bookings/${id}/extend`, { method: "POST", body: { minutes } });
}

export function checkInBooking(id) {
  return apiRequest(`/bookings/${id}/check-in`, { method: "POST" });
}

export function checkOutBooking(id) {
  return apiRequest(`/bookings/${id}/check-out`, { method: "POST" });
}

export function checkAvailability(params) {
  return apiRequest("/bookings/availability", { params: normalizeFilterTimes(params) });
}

export function getBookingSchedule(params) {
  return apiRequest("/bookings/schedule", { params: normalizeFilterTimes(params) });
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

export function joinBookingByCode(payload) {
  return apiRequest("/bookings/join", { method: "POST", body: payload });
}

export function getNotifications(limit = 30) {
  return apiRequest("/bookings/notifications", { params: { limit } });
}

function normalizeBookingTimes(payload = {}) {
  return {
    ...payload,
    ...(payload.start_time ? { start_time: toUtcIso(payload.start_time) } : {}),
    ...(payload.end_time ? { end_time: toUtcIso(payload.end_time) } : {}),
  };
}

function normalizeFilterTimes(params = {}) {
  return {
    ...params,
    ...(params.start ? { start: toUtcIso(params.start) } : {}),
    ...(params.end ? { end: toUtcIso(params.end) } : {}),
  };
}
