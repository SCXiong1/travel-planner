# Issue 19: 提取 TripForm + PageLayout 组件

## Parent

[PRD: 前端结构重构 + 测试同步](../frontend-refactor-and-tests.md)

## What to build

从 TripList.vue 提取创建/编辑旅行表单为独立的 TripForm.vue 组件。提取 PageLayout.vue 共享布局组件（返回按钮 + 标题 + slot），改造 PackingList、Settlement、RecycleBin 使用它。新增对应单元测试。

Type: AFK
Blocked by: #18

## Acceptance criteria

- [x] TripForm.vue 从 TripList.vue 内联表单提取为独立组件
- [x] TripList.vue 使用 TripForm 组件，功能不变
- [x] PageLayout.vue 提取为共享布局组件
- [x] PackingList.vue、Settlement.vue、RecycleBin.vue 改用 PageLayout
- [x] TripForm.test.js 新增并通过（4 tests）
- [x] PageLayout.test.js 新增并通过（3 tests）
- [x] vitest 全量通过（25/25），playwright Pixel 7 全量通过（22/22）

## User Stories

2, 3
