# PRD: 前端结构重构 + 测试同步

## Problem Statement

前端代码存在结构性问题：页面组件和复用组件混在 `components/` 目录下无法区分；`TripDetail.vue`(251行) 和 `TripList.vue`(244行) 职责过多；WebSocket 生命周期、回收站逻辑、页面布局 wrapper 存在重复代码；所有页面缺少 loading 状态和错误处理。测试层面存在明显缺口：后端 10 个测试文件重复 fixture 样板无 conftest.py；前端 14 个组件只有 4 个有单元测试；E2E 缺少 day 拖拽排序和 activity/packing 级别的回收站操作覆盖。

## Solution

分两阶段进行：第一阶段重构前端代码结构（分层、拆分大文件、提取 composable 和共享组件），同步移动测试文件；第二阶段补齐测试覆盖（后端 fixture 提取、前端单元测试补充、E2E 测试扩展）。

## User Stories

1. As a 开发者, I want 将页面组件和复用组件分开放到 `views/` 和 `components/` 目录, so that 一眼能看出哪些是路由目标、哪些是复用 UI
2. As a 开发者, I want 从 `TripList.vue` 提取独立的 `TripForm.vue` 组件, so that 创建/编辑旅行的表单逻辑可复用且页面更简洁
3. As a 开发者, I want 提取 `PageLayout.vue` 共享布局组件, so that `PackingList`、`Settlement`、`RecycleBin` 三个页面不再重复相同的 wrapper 模板
4. As a 开发者, I want 提取 `useTripData` composable 封装 trip/days/activities 的加载和 CRUD 逻辑, so that `TripDetail.vue` 变成纯模板 + 事件绑定
5. As a 开发者, I want `useTripData` composable 内置 try/catch 错误处理和 loading 状态, so that 所有页面加载数据时有统一的错误反馈和加载指示
6. As a 开发者, I want 提取 `useTripWebSocket` composable 封装 WebSocket 连接生命周期, so that `TripDetail` 和 `PackingList` 不再重复相同的连接/断开/用户切换代码
7. As a 开发者, I want 重构后 router 的 import 路径同步更新, so that 页面路由正常工作
8. As a 开发者, I want 后端测试加 `conftest.py` 提取公共 fixture（db/app/client/auth）, so that 10 个测试文件消除重复样板代码
9. As a 开发者, I want 补充 `useTripData` 和 `useTripWebSocket` 的单元测试, so that 新提取的 composable 有测试覆盖
10. As a 开发者, I want 补充缺失组件（`TripForm`、`PageLayout`、`ConfirmDialog`、`ContextMenu`、`DaySidebar`、`Login`、`Settlement`、`RecycleBin`/`RecycleBinContent`/`RecycleBinDrawer`、`ToastMessage`）的单元测试, so that 组件测试覆盖率从 4/14 提升
11. As a 开发者, I want 新增 E2E 测试覆盖 day 拖拽排序, so that 与后端 test_day_routes 的 reorder 测试对齐
12. As a 开发者, I want 扩展 E2E 回收站测试覆盖 activity 和 packing 级别的恢复和永久删除, so that 与后端 test_recycle_bin 的完整覆盖对齐
13. As a 开发者, I want 每步重构后跑 vitest + playwright 确认无回归, so that 重构过程不引入新 bug
14. As a 开发者, I want 重构完成后跑全量 pytest + vitest + playwright 确认所有测试通过, so that 最终状态可验证

## Implementation Decisions

### 前端目录结构

采用 flat 的 `views/` + `components/` 两层结构，不做 feature-folder 方案（项目规模不需要）。

```
client/src/
├── views/           # 6 个页面组件（路由目标）
│   ├── Login.vue
│   ├── TripList.vue
│   ├── TripDetail.vue
│   ├── PackingList.vue
│   ├── Settlement.vue
│   └── RecycleBin.vue
├── components/      # 复用 UI 组件
│   ├── TripForm.vue       # 新提取
│   ├── PageLayout.vue     # 新提取
│   └── ...（现有组件保留）
├── composables/
│   ├── useTripData.js         # 新提取
│   ├── useTripWebSocket.js    # 新提取
│   └── ...（现有 composable 保留）
```

### TripDetail.vue 拆分

提取两个 composable：
- `useTripData(tripId)` — 加载 trip/days/activities，暴露 `trip`, `days`, `activities`, `selectedDay`, `loadAll()`, `addDay()`, `deleteDay()`, `addActivity()`, `updateActivity()`, `deleteActivity()`，内置 try/catch 和 `loading` ref
- `useTripWebSocket(tripId, onMessage)` — 封装 WebSocket 连接/断开/用户切换的生命周期，`TripDetail` 和 `PackingList` 共用

`addDay()` 中的日期递增 while 循环保留在 composable 内（仅一处调用，无需单独提取为工具函数）。

### TripList.vue 拆分

仅提取 `TripForm.vue`（创建/编辑旅行的表单对话框）。TripList 不需要提取 composable（逻辑量不大），`RecycleBinDrawer` 已是独立组件。

### PageLayout.vue

提取共享布局组件，包含返回按钮 + 标题 + slot。适用于 `PackingList`、`Settlement`、`RecycleBin`。`TripList`（无返回按钮）和 `TripDetail`（两栏布局）不用此组件。

### 后端测试 fixture

新建 `server/tests/conftest.py`，提取 `db`（in-memory SQLite + init_db）、`app`（create_test_app）、`client`（httpx AsyncClient）、`auth`（X-User header helper）四个公共 fixture。10 个测试文件删除各自重复的样板，统一使用 conftest。

### 前端测试目录

保持当前的 `__tests__/` 同级模式（与代码紧耦合）。重构后测试文件随代码同步移动：
- 页面组件测试移入 `views/__tests__/`
- 新 composable 测试放在 `composables/__tests__/`
- 新组件测试放在 `components/__tests__/`

### 错误处理

`useTripData` composable 暴露 `loading` ref，所有 API 调用包 try/catch，失败时通过 `useToast` 显示错误。页面组件绑定 loading 状态显示加载指示器。

## Testing Decisions

### 测试原则

- 单元测试只测外部行为（props in → events/emits out），不测实现细节
- E2E 测试只测用户可感知的交互流程，通过 `data-testid` 和 `getByText` 定位
- 后端测试通过 API 契约验证（请求 → 响应），不测 service 内部实现

### 前端单元测试新增

| 被测模块 | 测试文件 | 测试点 |
|---|---|---|
| `useTripData` | `composables/__tests__/useTripData.test.js` | 加载成功/失败、loading 状态切换、CRUD 操作调用正确 API |
| `useTripWebSocket` | `composables/__tests__/useTripWebSocket.test.js` | 连接/断开生命周期、用户切换重连 |
| `TripForm` | `components/__tests__/TripForm.test.js` | 创建/编辑模式渲染、表单提交 emit、取消 emit |
| `PageLayout` | `components/__tests__/PageLayout.test.js` | 标题渲染、slot 内容、返回按钮导航 |
| 缺失组件 | 各自 `__tests__/` 目录 | 基本渲染和交互（ConfirmDialog 确认/取消、ContextMenu 显示/隐藏、DaySidebar 选择、Login 用户切换、Settlement 数据展示、RecycleBin 恢复/删除、ToastMessage 显示/自动消失） |

### 前端单元测试现有

现有的 5 个测试文件（ActivityForm、PackingList、TripDetail、TripList、useDragReorder）在重构后需同步更新 import 路径。

### E2E 测试新增/扩展

| 测试文件 | 变更 | 测试点 |
|---|---|---|
| `e2e/tests/day-reorder.spec.js` | 新增 | 拖拽 day 卡片改变顺序，验证 day_number 更新 |
| `e2e/tests/recycle-bin.spec.js` | 扩展 | 删除 activity 后恢复、永久删除 activity；删除 packing item 后恢复、永久删除 |

### 后端测试

现有 67 个测试不变，仅提取 fixture 到 conftest.py 消除重复。不新增后端测试（覆盖已充分）。

### Prior Art

- 后端测试模式：`server/tests/test_trip_routes.py` 的 fixture 和 auth helper 是所有测试的模板
- 前端单元测试模式：`client/src/components/__tests__/TripDetail.test.js` 的 mock 策略（mock composables、API 模块、vue-router）是页面级组件测试的模板
- E2E 测试模式：`client/e2e/tests/trip-detail.spec.js` 的 beforeEach setup（login → create trip → navigate）是页面级 E2E 的模板
- 拖拽排序 E2E：`client/e2e/tests/trip-list.spec.js` 的 pointer events 模拟是 day reorder 测试的参考

## Out of Scope

- **TypeScript 迁移** — 成本高收益低，当前 JS 可管理
- **引入状态管理库（Pinia/Vuex）** — 当前 composable 单例模式足够
- **WebSocket 实时同步的 E2E 测试** — 成本过高，需模拟多用户并发
- **多用户交互的 E2E 测试** — 所有 E2E 保持单用户（sd）
- **后端新增测试** — 后端 67 个测试覆盖已充分，仅做 fixture 提取
- **两用户硬编码问题** — 不在本次重构范围内

## Further Notes

### 实施顺序（9 步）

1. 创建 `views/`，移动 6 个页面，更新 router import，移动测试文件
2. 提取 `TripForm.vue`，新增测试
3. 提取 `PageLayout.vue`，改造 3 个子页面
4. 提取 `useTripData.js`（含错误处理+loading）和 `useTripWebSocket.js`
5. 重写 `TripDetail.vue` 和 `PackingList.vue` 使用新 composable
6. 移动/拆分前端单元测试，确认全部同步
7. 后端 `conftest.py` 提取公共 fixture
8. 补前端单元测试（新 composable + 缺失组件）
9. 补 E2E 测试（day reorder、recycle bin 深度）

每步跑测试确认无回归。

### 当前分支

`refactor/frontend-structure-and-tests`
