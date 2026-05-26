import { api } from "./client.js";

export function list(tripId, dayId) {
  return api.get(`/trips/${tripId}/days/${dayId}/activities`);
}

export function create(tripId, dayId, data) {
  return api.post(`/trips/${tripId}/days/${dayId}/activities`, data);
}

export function update(tripId, dayId, actId, data) {
  return api.put(`/trips/${tripId}/days/${dayId}/activities/${actId}`, data);
}

export function remove(tripId, dayId, actId) {
  return api.delete(`/trips/${tripId}/days/${dayId}/activities/${actId}`);
}

export function reorder(tripId, dayId, orders) {
  return api.put(`/trips/${tripId}/days/${dayId}/activities/reorder`, orders);
}
