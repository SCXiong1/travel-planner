const BASE_URL = "/api";

function getUser() {
  return localStorage.getItem("travel-planner-user") || "";
}

export function setUser(user) {
  localStorage.setItem("travel-planner-user", user);
}

export function getCurrentUser() {
  return getUser();
}

export function isLoggedIn() {
  return !!getUser();
}

async function request(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    "X-User": getUser(),
    ...options.headers,
  };

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }

  const text = await res.text();
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export const api = {
  get: (path) => request(path),
  post: (path, body) =>
    request(path, { method: "POST", body: JSON.stringify(body) }),
  put: (path, body) =>
    request(path, { method: "PUT", body: JSON.stringify(body) }),
  delete: (path) => request(path, { method: "DELETE" }),
};
