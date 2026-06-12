import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e/tests",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: "list",
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "iPhone 14",
      use: { ...devices["iPhone 14"] },
    },
    {
      name: "Pixel 7",
      use: { ...devices["Pixel 7"] },
    },
  ],
  webServer: [
    {
      command: "bash -c 'cd ../server && source .venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 3001'",
      port: 3001,
      reuseExistingServer: false,
    },
    {
      command: "npm run dev -- --host 0.0.0.0",
      port: 5173,
      reuseExistingServer: false,
    },
  ],
});
