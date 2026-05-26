import { api } from "./client.js";

export function list(tripId) {
  return api.get(`/trips/${tripId}/packing`);
}

export function create(tripId, data) {
  return api.post(`/trips/${tripId}/packing`, data);
}

export function toggleCheck(tripId, itemId) {
  return api.put(`/trips/${tripId}/packing/${itemId}/check`);
}

export function remove(tripId, itemId) {
  return api.delete(`/trips/${tripId}/packing/${itemId}`);
}
