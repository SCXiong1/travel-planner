## What to build

旅行详情页的 E2E 测试。覆盖天的添加/删除、活动的添加/编辑/删除、以及移动端 touch 拖拽排序活动。编写 trip-detail.spec.js，为 TripDetail.vue、DaySidebar.vue、ActivityCard.vue、ActivityForm.vue 添加 data-testid。

## Acceptance criteria

- [x] DaySidebar.vue 中天列表项、添加天按钮、删除天按钮添加了 data-testid
- [x] ActivityCard.vue 中活动卡片、拖拽手柄、编辑按钮、删除按钮添加了 data-testid
- [x] ActivityForm.vue 中表单字段和提交按钮添加了 data-testid
- [x] trip-detail.spec.js 覆盖：添加天、删除天、添加活动（四种 type）、编辑活动、删除活动
- [x] 活动拖拽排序测试使用 touch 事件模拟
- [x] `npx playwright test tests/trip-detail.spec.js` 在两个设备上均通过

## Blocked by

- [12-Playwright基础设施+登录测试](12-Playwright基础设施+登录测试.md)
