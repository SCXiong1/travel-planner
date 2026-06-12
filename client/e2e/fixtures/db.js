const BASE_URL = "http://localhost:3001";

export async function setupDatabase() {
  await fetch(`${BASE_URL}/api/test/reset`, {
    method: "POST",
    headers: { "X-User": "sd" },
  });
}
