import { api } from "./client.js";

export function get(tripId) {
  return api.get(`/trips/${tripId}/settlement`);
}
