# Issue 18: 前端目录分层 + router 更新

## Parent

[PRD: 前端结构重构 + 测试同步](../frontend-refactor-and-tests.md)

## What to build

将 6 个页面组件从 `components/` 移到 `views/`，更新 router 的 import 路径，同步移动对应的单元测试文件。跑 vitest + playwright 验证无回归。

Type: HITL
Blocked by: None

## Acceptance criteria

- [x] 创建 `client/src/views/` 目录
- [x] Login.vue、TripList.vue、TripDetail.vue、PackingList.vue、Settlement.vue、RecycleBin.vue 移入 views/
- [x] router/index.js 的 import 路径从 `../components/` 改为 `../views/`
- [x] 对应的 `__tests__/` 文件同步移动
- [x] vitest 全量通过（18/18）
- [x] playwright Pixel 7 全量通过（22/22）

## User Stories

1, 7, 13
