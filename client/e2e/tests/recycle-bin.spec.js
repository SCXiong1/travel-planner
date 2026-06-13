import { test, expect } from "@playwright/test";
import { setupDatabase } from "../fixtures/db.js";

test.describe("回收站", () => {
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
  });

  test("恢复已删除的旅行", async ({ page }) => {
    // 删除旅行
    await page.getByTestId("context-menu-button").first().click();
    await page.getByTestId("delete-trip-button").click();
    await page.getByTestId("confirm-dialog-confirm").click();
    await expect(page.getByTestId("trip-card")).toHaveCount(0);

    // 打开回收站抽屉
    await page.getByRole("button", { name: "回收站" }).click();

    // 验证已删除的旅行在回收站中
    await expect(page.getByTestId("recycle-bin-item")).toHaveCount(1);
    await expect(page.getByTestId("recycle-bin-item").first()).toContainText("东京之旅");

    // 恢复旅行
    await page.getByTestId("restore-button").first().click();

    // 验证回收站为空
    await expect(page.getByTestId("recycle-bin-item")).toHaveCount(0);

    // 关闭抽屉并刷新页面
    await page.getByTestId("drawer-close-button").click();
    await page.reload();

    // 验证旅行恢复
    await expect(page.getByTestId("trip-card")).toHaveCount(1);
    await expect(page.getByRole("heading", { name: "东京之旅" })).toBeVisible();
  });

  test("永久删除旅行", async ({ page }) => {
    // 删除旅行
    await page.getByTestId("context-menu-button").first().click();
    await page.getByTestId("delete-trip-button").click();
    await page.getByTestId("confirm-dialog-confirm").click();
    await expect(page.getByTestId("trip-card")).toHaveCount(0);

    // 打开回收站抽屉
    await page.getByRole("button", { name: "回收站" }).click();

    // 验证已删除的旅行在回收站中
    await expect(page.getByTestId("recycle-bin-item")).toHaveCount(1);

    // 永久删除
    await page.getByTestId("permanent-delete-button").first().click();
    await page.getByTestId("confirm-dialog-confirm").click();

    // 验证回收站为空
    await expect(page.getByTestId("recycle-bin-item")).toHaveCount(0);
  });

  test("恢复已删除的活动", async ({ page }) => {
    // 进入旅行详情
    await page.getByTestId("trip-card").first().click();
    await expect(page).toHaveURL(/\/trips\/\d+/);

    // 添加天
    await page.getByTestId("add-day-button").click();
    await expect(page.getByTestId("day-item")).toHaveCount(1);

    // 添加活动
    await page.getByTestId("add-activity-button").click();
    await page.getByTestId("activity-form-name").fill("吃拉面");
    await page.getByTestId("activity-form-submit").click();
    await expect(page.getByTestId("activity-card")).toHaveCount(1);

    // 删除活动
    await page.getByTestId("activity-card").first().getByTestId("delete-activity-button").click();
    await expect(page.getByTestId("activity-card")).toHaveCount(0);

    // 打开回收站页面
    await page.getByRole("button", { name: "回收站" }).click();
    await expect(page).toHaveURL(/\/trips\/\d+\/recycle-bin/);

    // 验证活动在回收站中
    await expect(page.getByTestId("recycle-bin-item")).toHaveCount(1);
    await expect(page.getByTestId("recycle-bin-item").first()).toContainText("吃拉面");

    // 恢复活动
    await page.getByTestId("restore-button").first().click();

    // 验证回收站为空
    await expect(page.getByTestId("recycle-bin-item")).toHaveCount(0);
  });

  test("永久删除活动", async ({ page }) => {
    // 进入旅行详情
    await page.getByTestId("trip-card").first().click();

    // 添加天
    await page.getByTestId("add-day-button").click();

    // 添加活动
    await page.getByTestId("add-activity-button").click();
    await page.getByTestId("activity-form-name").fill("吃寿司");
    await page.getByTestId("activity-form-submit").click();
    await expect(page.getByTestId("activity-card")).toHaveCount(1);

    // 删除活动
    await page.getByTestId("activity-card").first().getByTestId("delete-activity-button").click();
    await expect(page.getByTestId("activity-card")).toHaveCount(0);

    // 打开回收站页面
    await page.getByRole("button", { name: "回收站" }).click();

    // 验证活动在回收站中
    await expect(page.getByTestId("recycle-bin-item")).toHaveCount(1);

    // 永久删除
    await page.getByTestId("permanent-delete-button").first().click();
    await page.getByTestId("confirm-dialog-confirm").click();

    // 验证回收站为空
    await expect(page.getByTestId("recycle-bin-item")).toHaveCount(0);
  });
});
