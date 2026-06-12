## What to build

旅行列表页的 E2E 测试。覆盖创建、编辑、删除旅行，以及移动端 touch 拖拽排序。编写 trip-list.spec.js，为 TripList.vue 中的旅行卡片、拖拽手柄、创建/编辑/删除按钮添加 data-testid。

## Acceptance criteria

- [x] TripList.vue 中旅行卡片、拖拽手柄、创建按钮、编辑按钮、删除按钮添加了 data-testid
- [x] trip-list.spec.js 覆盖：创建新旅行（填写名称和日期）、编辑旅行名称、删除旅行
- [x] 拖拽排序测试使用 touch 事件模拟（touchstart → touchmove → touchend）
- [x] 每个测试前后数据状态干净（依赖切片 1 的 fixture 机制）
- [x] `npx playwright test tests/trip-list.spec.js` 在两个设备上均通过

## Blocked by

- [12-Playwright基础设施+登录测试](12-Playwright基础设施+登录测试.md)
