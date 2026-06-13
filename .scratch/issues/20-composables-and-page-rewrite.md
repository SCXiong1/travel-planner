# Issue 20: 提取 composable + 重写页面

## Parent

[PRD: 前端结构重构 + 测试同步](../frontend-refactor-and-tests.md)

## What to build

新建 useTripData.js（封装 trip/days/activities 加载和 CRUD，含 try/catch + loading）和 useTripWebSocket.js（封装 WebSocket 连接生命周期，TripDetail 和 PackingList 共用）。用新 composable 重写 TripDetail.vue 和 PackingList.vue，同步拆分测试文件。新增 composable 单元测试。

Type: AFK
Blocked by: #18

## Acceptance criteria

- [x] useTripData.js 暴露 trip, days, activities, selectedDay, loading, loadAll(), addDay(), deleteDay(), addActivity(), updateActivity(), deleteActivity()
- [x] useTripData 内置 try/catch，失败时 useToast 显示错误
- [x] useTripWebSocket.js 封装连接/断开/用户切换生命周期
- [x] TripDetail.vue 和 PackingList.vue 用新 composable 重写，页面逻辑大幅精简
- [x] 对应测试文件同步更新 import 路径
- [x] useTripData.test.js 新增并通过（7 tests）
- [x] useTripWebSocket.test.js 新增并通过（2 tests）
- [x] vitest 全量通过（34/34），playwright Pixel 7 全量通过（22/22）

## User Stories

4, 5, 6, 13
