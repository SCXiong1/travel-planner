import { test, expect } from "@playwright/test";
import { setupDatabase } from "../fixtures/db.js";

test.describe("费用结算", () => {
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

    // 添加一天
    await page.getByTestId("add-day-button").click();
    await expect(page.getByTestId("day-item").first()).toContainText("Day 1");
  });

  test("添加 sd 支付的支出并查看结算", async ({ page }) => {
    // 添加活动并带支出
    await page.getByTestId("add-activity-button").click();
    await page.getByTestId("activity-form-type").selectOption("eat");
    await page.getByTestId("activity-form-name").fill("拉面店");

    // 添加一笔开销
    await page.getByRole("button", { name: "+ 添加一笔" }).click();
    await page.getByTestId("expense-amount-0").fill("1000");
    await page.getByTestId("expense-payer-0").selectOption("sd");

    await page.getByTestId("activity-form-submit").click();
    await expect(page.getByTestId("activity-card")).toHaveCount(1);

    // 进入结算页
    await page.getByRole("button", { name: "结算" }).click();
    await expect(page.getByRole("heading", { name: "结算" })).toBeVisible();

    // 验证 sd 支付金额
    await expect(page.getByTestId("sd-paid")).toContainText("1000");
  });

  test("添加 sg 支付的支出并查看结算", async ({ page }) => {
    // 添加活动并带支出
    await page.getByTestId("add-activity-button").click();
    await page.getByTestId("activity-form-type").selectOption("sight");
    await page.getByTestId("activity-form-name").fill("浅草寺门票");

    // 添加一笔开销
    await page.getByRole("button", { name: "+ 添加一笔" }).click();
    await page.getByTestId("expense-amount-0").fill("500");
    await page.getByTestId("expense-payer-0").selectOption("sg");

    await page.getByTestId("activity-form-submit").click();
    await expect(page.getByTestId("activity-card")).toHaveCount(1);

    // 进入结算页
    await page.getByRole("button", { name: "结算" }).click();
    await expect(page.getByRole("heading", { name: "结算" })).toBeVisible();

    // 验证 sg 支付金额
    await expect(page.getByTestId("sg-paid")).toContainText("500");
  });

  test("查看结算结果", async ({ page }) => {
    // 添加活动并带支出（sd 支付 1000）
    await page.getByTestId("add-activity-button").click();
    await page.getByTestId("activity-form-type").selectOption("eat");
    await page.getByTestId("activity-form-name").fill("拉面店");

    await page.getByRole("button", { name: "+ 添加一笔" }).click();
    await page.getByTestId("expense-amount-0").fill("1000");
    await page.getByTestId("expense-payer-0").selectOption("sd");

    await page.getByTestId("activity-form-submit").click();
    await expect(page.getByTestId("activity-card")).toHaveCount(1);

    // 进入结算页
    await page.getByRole("button", { name: "结算" }).click();
    await expect(page.getByRole("heading", { name: "结算" })).toBeVisible();

    // 验证结算结果：sd 支付 1000，总开销 1000，sg 应承担 500
    await expect(page.getByTestId("settlement-result")).toContainText("sg 需支付 sd");
    await expect(page.getByTestId("settlement-result")).toContainText("500");
  });
});
