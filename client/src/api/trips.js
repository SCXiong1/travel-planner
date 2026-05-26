import { api } from "./client.js";

export function list() {
  return api.get("/trips");
}

export function get(id) {
  return api.get(`/trips/${id}`);
}

export function create(data) {
  return api.post("/trips", data);
}

export function update(id, data) {
  return api.put(`/trips/${id}`, data);
}

export function remove(id) {
  return api.delete(`/trips/${id}`);
}

export function reorder(orders) {
  return api.put("/trips/reorder", orders);
}
