import { api } from "./client.js";

export function list(tripId) {
  return api.get(`/trips/${tripId}/days`);
}

export function create(tripId, data) {
  return api.post(`/trips/${tripId}/days`, data);
}

export function remove(tripId, dayId) {
  return api.delete(`/trips/${tripId}/days/${dayId}`);
}

export function reorder(tripId, orders) {
  return api.put(`/trips/${tripId}/days/reorder`, orders);
}
