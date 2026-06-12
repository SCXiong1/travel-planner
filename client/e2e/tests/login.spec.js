import { test, expect } from "@playwright/test";
import { setupDatabase, teardownDatabase } from "../fixtures/db.js";

test.beforeAll(() => {
  setupDatabase();
});

test.afterAll(() => {
  teardownDatabase();
});

test.describe("登录页", () => {
  test("选择 sd 后跳转到旅行列表", async ({ page }) => {
    await page.goto("/login");

    const sdButton = page.getByTestId("login-sd");
    await expect(sdButton).toBeVisible();
    await sdButton.click();

    await expect(page).toHaveURL("/trips");
  });

  test("选择 sg 后跳转到旅行列表", async ({ page }) => {
    await page.goto("/login");

    const sgButton = page.getByTestId("login-sg");
    await expect(sgButton).toBeVisible();
    await sgButton.click();

    await expect(page).toHaveURL("/trips");
  });
});
