import { test, expect } from "@playwright/test";
import { setupDatabase } from "../fixtures/db.js";

test.describe("行程规划", () => {
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
  });

  test("添加天", async ({ page }) => {
    await page.getByTestId("add-day-button").click();

    // 验证天列表出现 Day 1
    await expect(page.getByTestId("day-item").first()).toContainText("Day 1");
  });

  test("删除天", async ({ page }) => {
    // 先添加一天
    await page.getByTestId("add-day-button").click();
    await expect(page.getByTestId("day-item").first()).toContainText("Day 1");

    // 打开上下文菜单并删除
    await page.getByTestId("day-item").first().getByTestId("context-menu-button").click();
    await page.getByRole("button", { name: "删除" }).click();

    // 确认删除
    await page.getByTestId("confirm-dialog-confirm").click();

    // 验证天列表为空
    await expect(page.getByTestId("day-item")).toHaveCount(0);
  });

  test("添加活动", async ({ page }) => {
    // 先添加一天
    await page.getByTestId("add-day-button").click();
    await expect(page.getByTestId("day-item").first()).toContainText("Day 1");

    // 添加吃类型的活动
    await page.getByTestId("add-activity-button").click();
    await page.getByTestId("activity-form-type").selectOption("eat");
    await page.getByTestId("activity-form-name").fill("拉面店");
    await page.getByTestId("activity-form-submit").click();

    // 验证活动卡片出现
    await expect(page.getByTestId("activity-card")).toHaveCount(1);
    await expect(page.getByTestId("activity-card").first()).toContainText("拉面店");
  });

  test("添加四种类型的活动", async ({ page }) => {
    // 先添加一天
    await page.getByTestId("add-day-button").click();
    await expect(page.getByTestId("day-item").first()).toContainText("Day 1");

    const types = [
      { type: "eat", name: "拉面店" },
      { type: "stay", name: "温泉旅馆" },
      { type: "transport", name: "新干线" },
      { type: "sight", name: "浅草寺" },
    ];

    for (const { type, name } of types) {
      await page.getByTestId("add-activity-button").click();
      await page.getByTestId("activity-form-type").selectOption(type);
      await page.getByTestId("activity-form-name").fill(name);
      await page.getByTestId("activity-form-submit").click();
    }

    // 验证四个活动卡片都出现
    await expect(page.getByTestId("activity-card")).toHaveCount(4);
  });

  test("编辑活动", async ({ page }) => {
    // 先添加一天
    await page.getByTestId("add-day-button").click();
    await expect(page.getByTestId("day-item").first()).toContainText("Day 1");

    // 添加活动
    await page.getByTestId("add-activity-button").click();
    await page.getByTestId("activity-form-type").selectOption("eat");
    await page.getByTestId("activity-form-name").fill("拉面店");
    await page.getByTestId("activity-form-submit").click();
    await expect(page.getByTestId("activity-card")).toHaveCount(1);

    // 点击活动卡片进入编辑
    await page.getByTestId("activity-card").first().click();

    // 修改名称
    await page.getByTestId("activity-form-name").fill("寿司店");
    await page.getByTestId("activity-form-submit").click();

    // 验证名称更新
    await expect(page.getByTestId("activity-card").first()).toContainText("寿司店");
    await expect(page.getByTestId("activity-card").first()).not.toContainText("拉面店");
  });

  test("删除活动", async ({ page }) => {
    // 先添加一天
    await page.getByTestId("add-day-button").click();
    await expect(page.getByTestId("day-item").first()).toContainText("Day 1");

    // 添加活动
    await page.getByTestId("add-activity-button").click();
    await page.getByTestId("activity-form-type").selectOption("eat");
    await page.getByTestId("activity-form-name").fill("拉面店");
    await page.getByTestId("activity-form-submit").click();
    await expect(page.getByTestId("activity-card")).toHaveCount(1);

    // 删除活动
    await page.getByTestId("activity-card").first().getByTestId("delete-activity-button").click();

    // 验证活动消失
    await expect(page.getByTestId("activity-card")).toHaveCount(0);
  });

  test("活动拖拽排序", async ({ page }) => {
    // 先添加一天
    await page.getByTestId("add-day-button").click();
    await expect(page.getByTestId("day-item").first()).toContainText("Day 1");

    // 添加两个活动
    await page.getByTestId("add-activity-button").click();
    await page.getByTestId("activity-form-type").selectOption("eat");
    await page.getByTestId("activity-form-name").fill("拉面店");
    await page.getByTestId("activity-form-submit").click();
    await expect(page.getByTestId("activity-card")).toHaveCount(1);

    await page.getByTestId("add-activity-button").click();
    await page.getByTestId("activity-form-type").selectOption("sight");
    await page.getByTestId("activity-form-name").fill("浅草寺");
    await page.getByTestId("activity-form-submit").click();
    await expect(page.getByTestId("activity-card")).toHaveCount(2);

    // 验证初始顺序：拉面店在前，浅草寺在后
    const cards = page.getByTestId("activity-card");
    await expect(cards.first()).toContainText("拉面店");
    await expect(cards.last()).toContainText("浅草寺");

    // 使用 touch 事件拖拽第二个活动到第一个位置
    const handles = page.getByTestId("activity-drag-handle");
    const lastHandle = handles.last();
    const handleBox = await lastHandle.boundingBox();
    const firstCardBox = await cards.first().boundingBox();

    // touchstart
    await lastHandle.dispatchEvent("pointerdown", {
      clientX: handleBox.x + handleBox.width / 2,
      clientY: handleBox.y + handleBox.height / 2,
      pointerId: 1,
      pointerType: "touch",
      bubbles: true,
      cancelable: true,
    });

    // touchmove 到第一个卡片位置
    await lastHandle.dispatchEvent("pointermove", {
      clientX: firstCardBox.x + firstCardBox.width / 2,
      clientY: firstCardBox.y + firstCardBox.height / 4,
      pointerId: 1,
      pointerType: "touch",
      bubbles: true,
      cancelable: true,
    });

    // pointerup
    await lastHandle.dispatchEvent("pointerup", {
      clientX: firstCardBox.x + firstCardBox.width / 2,
      clientY: firstCardBox.y + firstCardBox.height / 4,
      pointerId: 1,
      pointerType: "touch",
      bubbles: true,
      cancelable: true,
    });

    // 等待拖拽完成
    await page.waitForTimeout(1000);

    // 验证顺序变化：浅草寺在前，拉面店在后
    await expect(cards.first()).toContainText("浅草寺");
    await expect(cards.last()).toContainText("拉面店");
  });
});
