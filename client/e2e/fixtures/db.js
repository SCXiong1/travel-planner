const BASE_URL = process.env.BASE_URL || "http://localhost:3001";

export async function setupDatabase() {
  const res = await fetch(`${BASE_URL}/api/test/reset`, {
    method: "POST",
    headers: { "X-User": "sd" },
  });
  if (!res.ok) {
    throw new Error(`setupDatabase failed: ${res.status} ${res.statusText}`);
  }
}
