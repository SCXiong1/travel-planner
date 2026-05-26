import { api } from "./client.js";

export function listGlobal() {
  return api.get("/recycle-bin");
}

export function listByTrip(tripId) {
  return api.get(`/trips/${tripId}/recycle-bin`);
}

export function restore(type, id) {
  return api.post(`/recycle-bin/${type}/${id}/restore`);
}

export function permanentDelete(type, id) {
  return api.delete(`/recycle-bin/${type}/${id}`);
}
