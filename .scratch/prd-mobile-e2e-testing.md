# PRD: 移动端浏览器端到端测试

## Problem Statement

项目当前没有任何 E2E 测试，仅有 vitest 组件测试和 pytest 后端测试。作为 sd/sg 两人使用的移动端旅行规划工具，核心交互（拖拽排序、touch 操作、多页面链路）无法被单元测试覆盖。需要补充移动端浏览器 E2E 测试，确保核心用户故事在真实浏览器环境中可用。

## Solution

引入 Playwright 作为 E2E 测试框架，针对 iPhone 14 和 Pixel 7 两个内置移动设备，覆盖 6 个核心用户故事。测试运行在本地 dev servers（uvicorn + vite dev）上，通过 SQLite 文件复制/还原实现数据隔离。

## User Stories

1. As sd/sg，我想在 `/login` 页面选择身份后进入旅行列表，以便快速开始使用应用
2. As sd/sg，我想在旅行列表页创建新旅行，以便开始规划新的行程
3. As sd/sg，我想在旅行列表页编辑旅行名称和日期，以便修正信息
4. As sd/sg，我想在旅行列表页删除旅行，以便移除不再需要的行程
5. As sd/sg，我想在旅行列表页通过拖拽改变旅行顺序，以便按优先级排列（移动端 touch 交互）
6. As sd/sg，我想进入旅行详情页查看按天组织的行程，以便了解完整规划
7. As sd/sg，我想在旅行详情页添加新天，以便扩展行程天数
8. As sd/sg，我想在旅行详情页删除某天，以便缩减行程
9. As sd/sg，我想在某天内添加活动（eat/stay/transport/sight），以便规划当天安排
10. As sd/sg，我想编辑已有活动的信息，以便修正细节
11. As sd/sg，我想删除某天内的活动，以便移除不需要的安排
12. As sd/sg，我想通过拖拽改变同一天内活动的顺序，以便调整时间安排（移动端 touch 交互）
13. As sd/sg，我想进入打包清单页查看所有待打包物品，以便准备行李
14. As sd/sg，我想添加新物品到打包清单，以便记录需要携带的东西
15. As sd/sg，我想勾选已打包的物品，以便跟踪打包进度
16. As sd/sg，我想将物品分配给 sd 或 sg，以便明确谁负责带什么
17. As sd/sg，我想进入费用结算页查看两人各自支付的金额，以便了解开支情况
18. As sd/sg，我想在费用结算页添加支出记录，以便追踪旅行花费
19. As sd/sg，我想查看结算结果（谁欠谁多少），以便公平分摊费用
20. As sd/sg，我想进入回收站查看已删除的内容，以便找回误删的旅行/天/活动
21. As sd/sg，我想从回收站恢复已删除的内容，以便撤销删除操作
22. As sd/sg，我想从回收站永久删除内容，以便彻底清理不需要的数据

## Implementation Decisions

### 测试框架选型

- **Playwright** — 选择 Playwright 而非 Cypress，原因：原生多浏览器/多设备支持、内置设备描述符、touch 事件模拟能力更强、测试隔离性更好（并行执行、独立浏览器上下文）

### 测试环境

- **本地 dev servers** — uvicorn（`--host 0.0.0.0 --port 3001`）+ Vite dev server（`--host 0.0.0.0`），通过 Playwright `webServer` 配置自动启动和等待
- Vite 开发服务器已有 `/api` → `localhost:3001` 和 `/ws` → `ws://localhost:3001` 的代理配置，无需额外处理

### 移动端设备模拟

- **内置设备描述符** — 使用 `iPhone 14`（390×844, iOS Safari）和 `Pixel 7`（412×915, Chrome）两个 Playwright 内置设备
- 每个测试文件在两个设备上各跑一次（通过 Playwright projects 配置）

### 测试数据管理

- **SQLite 文件复制/还原** — 每个测试文件 `beforeAll` 阶段复制干净的 db 模板到 `data/travel.db`，测试结束后还原
- uvicorn 使用 SQLite WAL 模式，文件复制安全，下次读取即拿到新数据
- 不通过 API seeding，直接操作文件系统，避免 API 变更导致数据准备失败

### 测试范围（6 个核心用户故事）

| 用户故事 | 覆盖页面 | 移动端特有测试点 |
|---|---|---|
| 登录 | `/login` | 选择身份后正确跳转 |
| 旅行管理 | `/trips` | CRUD + 拖拽排序（touch） |
| 行程规划 | `/trips/:id` | 天管理 + 活动 CRUD + 拖拽排序（touch） |
| 打包清单 | `/trips/:id/packing` | 勾选 + 按人分配 |
| 费用结算 | `/trips/:id/settlement` | 添加支出 + 结算计算 |
| 回收站 | `/trips/:id/recycle-bin` | 恢复 + 永久删除 |

### 拖拽排序测试策略

- **touch 事件模拟** — 使用 `page.touchscreen.tap()` + 移动模拟真实的 `touchstart` → `touchmove` → `touchend` 链路
- 项目 `useDragReorder.js` 基于 pointer 事件实现，touch 和 mouse 均可触发，但测试必须用 touch 以验证移动端实际可用性

### 选择器策略

- 核心交互元素（拖拽手柄、活动卡片、天列表项）使用 `data-testid` 定位
- 文本验证使用 `getByText`（中文文案不受 CSS 框架影响）
- 不依赖 CSS class 选择器，避免样式重构导致测试断裂

### 目录结构

```
client/
  e2e/
    fixtures/          # 干净 db 模板
    tests/
      login.spec.js
      trip-list.spec.js
      trip-detail.spec.js
      packing.spec.js
      settlement.spec.js
      recycle-bin.spec.js
    playwright.config.js
```

## Testing Decisions

### 什么是好的 E2E 测试

- 只测外部可观测行为（页面展示、用户交互、数据持久化），不测实现细节
- 每个测试独立可运行，不依赖其他测试的执行顺序
- 测试稳定：不因非功能性变更（CSS 调整、DOM 结构微调）而断裂
- 移动端特有交互（touch 拖拽）必须用真实 touch 事件模拟

### 测试模块

- `login.spec.js` — 身份选择 + 跳转
- `trip-list.spec.js` — 旅行 CRUD + 拖拽排序
- `trip-detail.spec.js` — 天管理 + 活动 CRUD + 拖拽排序
- `packing.spec.js` — 物品管理 + 勾选 + 分配
- `settlement.spec.js` — 支出记录 + 结算计算
- `recycle-bin.spec.js` — 恢复 + 永久删除

### 现有测试基础

- 后端 pytest 测试覆盖所有 API 路由（10 个测试文件），E2E 不重复测 API 层
- 前端 vitest 组件测试覆盖 TripList、ActivityForm、TripDetail、PackingList，E2E 关注跨页面链路和真实浏览器交互

## Out of Scope

- **WebSocket 实时同步** — E2E 难以稳定测试双人协作场景，留给 vitest 集成测试
- **CSS/Tailwind 升级影响** — 暂不关注样式框架升级对测试的影响
- **Docker 环境测试** — 生产部署用 Docker，但 E2E 测试只跑本地 dev servers
- **CI/CD 集成** — 本次只做本地 E2E，CI 流水线后续单独规划
- **视觉回归测试** — 不做截图对比，只验证功能行为
