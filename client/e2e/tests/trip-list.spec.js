import { test, expect } from "@playwright/test";
import { setupDatabase } from "../fixtures/db.js";

test.describe("旅行列表", () => {
  test.beforeEach(async ({ page }) => {
    await setupDatabase();

    await page.goto("/login");
    await page.getByTestId("login-sd").click();
    await expect(page).toHaveURL("/trips");
  });

  test("创建新旅行", async ({ page }) => {
    await page.getByTestId("create-trip-button").click();

    await page.getByTestId("trip-form-title").fill("东京之旅");
    await page.getByTestId("trip-form-destination").fill("东京");
    await page.getByTestId("trip-form-start-date").fill("2026-07-01");
    await page.getByTestId("trip-form-end-date").fill("2026-07-07");
    await page.getByTestId("trip-form-submit").click();

    await expect(page.getByRole("heading", { name: "东京之旅" })).toBeVisible();
    await expect(page.getByTestId("trip-card")).toHaveCount(1);
  });

  test("编辑旅行名称", async ({ page }) => {
    // 先创建一个旅行
    await page.getByTestId("create-trip-button").click();
    await page.getByTestId("trip-form-title").fill("东京之旅");
    await page.getByTestId("trip-form-destination").fill("东京");
    await page.getByTestId("trip-form-start-date").fill("2026-07-01");
    await page.getByTestId("trip-form-end-date").fill("2026-07-07");
    await page.getByTestId("trip-form-submit").click();

    await expect(page.getByRole("heading", { name: "东京之旅" })).toBeVisible();

    // 打开菜单并编辑
    await page.getByTestId("context-menu-button").first().click();
    await page.getByTestId("edit-trip-button").click();

    await page.getByTestId("trip-form-title").fill("大阪之旅");
    await page.getByTestId("trip-form-submit").click();

    await expect(page.getByRole("heading", { name: "大阪之旅" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "东京之旅" })).not.toBeVisible();
  });

  test("删除旅行", async ({ page }) => {
    // 先创建一个旅行
    await page.getByTestId("create-trip-button").click();
    await page.getByTestId("trip-form-title").fill("东京之旅");
    await page.getByTestId("trip-form-destination").fill("东京");
    await page.getByTestId("trip-form-start-date").fill("2026-07-01");
    await page.getByTestId("trip-form-end-date").fill("2026-07-07");
    await page.getByTestId("trip-form-submit").click();

    await expect(page.getByRole("heading", { name: "东京之旅" })).toBeVisible();

    // 打开菜单并删除
    await page.getByTestId("context-menu-button").first().click();
    await page.getByTestId("delete-trip-button").click();

    // 确认删除
    await page.getByTestId("confirm-dialog-confirm").click();

    // 验证卡片消失
    await expect(page.getByTestId("trip-card")).toHaveCount(0);
  });

  test("拖拽排序", async ({ page }) => {
    // 创建两个旅行（新创建的排在前面）
    await page.getByTestId("create-trip-button").click();
    await page.getByTestId("trip-form-title").fill("东京之旅");
    await page.getByTestId("trip-form-destination").fill("东京");
    await page.getByTestId("trip-form-start-date").fill("2026-07-01");
    await page.getByTestId("trip-form-end-date").fill("2026-07-07");
    await page.getByTestId("trip-form-submit").click();

    await expect(page.getByRole("heading", { name: "东京之旅" })).toBeVisible();

    await page.getByTestId("create-trip-button").click();
    await page.getByTestId("trip-form-title").fill("大阪之旅");
    await page.getByTestId("trip-form-destination").fill("大阪");
    await page.getByTestId("trip-form-start-date").fill("2026-08-01");
    await page.getByTestId("trip-form-end-date").fill("2026-08-07");
    await page.getByTestId("trip-form-submit").click();

    await expect(page.getByRole("heading", { name: "大阪之旅" })).toBeVisible();
    await expect(page.getByTestId("trip-card")).toHaveCount(2);

    // 验证初始顺序：大阪在前（新创建），东京在后
    const cards = page.getByTestId("trip-card");
    await expect(cards.first()).toContainText("大阪之旅");
    await expect(cards.last()).toContainText("东京之旅");

    // 拖拽第二个（东京）到第一个位置
    const handles = page.getByTestId("trip-drag-handle");
    const lastHandle = handles.last();

    // 使用鼠标事件模拟拖拽
    const handleBox = await lastHandle.boundingBox();

    // pointerdown on handle - 使用 dispatchEvent 确保事件目标正确
    const pointerId = 1;
    await lastHandle.dispatchEvent("pointerdown", {
      clientX: handleBox.x + handleBox.width / 2,
      clientY: handleBox.y + handleBox.height / 2,
      pointerId,
      pointerType: "mouse",
      bubbles: true,
      cancelable: true,
    });

    // pointermove 到第一个卡片位置
    const firstCardBox = await cards.first().boundingBox();
    await lastHandle.dispatchEvent("pointermove", {
      clientX: firstCardBox.x + firstCardBox.width / 2,
      clientY: firstCardBox.y + firstCardBox.height / 4,
      pointerId,
      pointerType: "mouse",
      bubbles: true,
      cancelable: true,
    });

    // pointerup
    await lastHandle.dispatchEvent("pointerup", {
      clientX: firstCardBox.x + firstCardBox.width / 2,
      clientY: firstCardBox.y + firstCardBox.height / 4,
      pointerId,
      pointerType: "mouse",
      bubbles: true,
      cancelable: true,
    });

    // 等待拖拽完成
    await page.waitForTimeout(1000);

    // 验证顺序变化：东京在前，大阪在后
    await expect(cards.first()).toContainText("东京之旅");
    await expect(cards.last()).toContainText("大阪之旅");
  });
});
