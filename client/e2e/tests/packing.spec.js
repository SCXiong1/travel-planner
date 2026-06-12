import { test, expect } from "@playwright/test";
import { setupDatabase } from "../fixtures/db.js";

test.describe("打包清单", () => {
  test.beforeEach(async ({ page }) => {
    await setupDatabase();

    // 登录
    await page.goto("/login");
    await page.getByTestId("login-sd").click();
    await expect(page).toHaveURL("/trips");

    // 创建一个测试旅行
    await page.getByTestId("create-trip-button").click();
    await page.getByTestId("trip-form-title").fill("东京之旅");
    await page.getByTestId("trip-form-destination").fill("东京");
    await page.getByTestId("trip-form-start-date").fill("2026-07-01");
    await page.getByTestId("trip-form-end-date").fill("2026-07-07");
    await page.getByTestId("trip-form-submit").click();
    await expect(page.getByRole("heading", { name: "东京之旅" })).toBeVisible();

    // 进入旅行详情
    await page.getByTestId("trip-card").first().click();
    await expect(page).toHaveURL(/\/trips\/\d+$/);

    // 进入打包清单页
    await page.getByRole("button", { name: "打包" }).click();
    await expect(page.getByRole("heading", { name: "打包清单" })).toBeVisible();
  });

  test("添加物品", async ({ page }) => {
    await page.getByTestId("packing-form-name").fill("护照");
    await page.getByTestId("packing-form-category").fill("证件");
    await page.getByTestId("packing-form-submit").click();

    await expect(page.getByTestId("packing-item")).toHaveCount(1);
    await expect(page.getByTestId("packing-item").first()).toContainText("护照");
  });

  test("勾选物品", async ({ page }) => {
    // 添加物品
    await page.getByTestId("packing-form-name").fill("护照");
    await page.getByTestId("packing-form-category").fill("证件");
    await page.getByTestId("packing-form-submit").click();
    await expect(page.getByTestId("packing-item")).toHaveCount(1);

    // 勾选
    await page.getByTestId("packing-checkbox").first().check();
    await expect(page.getByTestId("packing-checkbox").first()).toBeChecked();
  });

  test("取消勾选", async ({ page }) => {
    // 添加物品
    await page.getByTestId("packing-form-name").fill("护照");
    await page.getByTestId("packing-form-category").fill("证件");
    await page.getByTestId("packing-form-submit").click();
    await expect(page.getByTestId("packing-item")).toHaveCount(1);

    // 勾选再取消
    await page.getByTestId("packing-checkbox").first().check();
    await expect(page.getByTestId("packing-checkbox").first()).toBeChecked();

    await page.getByTestId("packing-checkbox").first().uncheck();
    await expect(page.getByTestId("packing-checkbox").first()).not.toBeChecked();
  });

  test("分配给 sg", async ({ page }) => {
    // 添加物品，分配给 sg
    await page.getByTestId("packing-form-name").fill("护照");
    await page.getByTestId("packing-form-category").fill("证件");
    await page.getByTestId("packing-form-assignee").selectOption("sg");
    await page.getByTestId("packing-form-submit").click();

    await expect(page.getByTestId("packing-item")).toHaveCount(1);
    await expect(page.getByTestId("packing-assignee").first()).toHaveText("sg");
  });
});
