# travel-planner

家庭旅行规划工具 — 行程规划 + 打包清单 + 开销结算 + 实时协作，跑在家庭服务器上。

供 sd 和 sg 两人使用，Docker 一键部署，浏览器访问，支持手机 PWA 安装。

## 功能模块

### 行程规划
- Trip → Day → Activity 三级结构
- 活动分四类：吃 / 住 / 行 / 景点
- 天和活动均支持拖拽排序（pointer 事件 + 蓝色插入线）
- 活动支持多笔开销、双人评价、预约标记

### 打包清单
- 添加物品，分配负责人（sd/sg），勾选进度追踪

### 开销结算
- 每笔开销记录金额、支付人、分摊方式（平分/归集）
- 结算页自动汇总：每人支付额、应承担额、补差价

### 实时协作
- WebSocket 广播，两人同时编辑同个 Trip 即时同步
- 冲突策略：最后写入胜出

### 回收站
- 所有删除为软删除，4 种类型（trip/day/activity/packing）可恢复
- parent 链校验：恢复子项前检查父项未被删除

### 身份认证
- 无密码，前端 sd/sg 两按钮选择，请求带 `X-User` header

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.12 + FastAPI + SQLite 3 |
| 前端 | Vue 3 + Vite + Tailwind CSS |
| 实时同步 | WebSocket（FastAPI 原生） |
| PWA | vite-plugin-pwa |
| 部署 | Docker 单容器 |

## 快速开始

### 开发环境

```bash
# 后端
cd server
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 3001 --reload

# 前端
cd client
npm install
npm run dev -- --host 0.0.0.0
```

- 后端：`http://localhost:3001`
- 前端：`http://localhost:5173`（自动代理 API 到 3001）

### Docker 部署

```bash
docker compose up -d
```

访问 `http://localhost:3000`，单容器同时 serve API 和前端静态文件。数据库文件持久化在 `./data/`。

## 数据模型

```
Trip { id, title, destination, start_date, end_date, sort_order, created_at, deleted_at }
  ├── Day { id, trip_id, day_number, date, title, deleted_at }
  │     └── Activity {
  │           id, day_id, type(eat/stay/transport/sight),
  │           name, location, start_time, end_time,
  │           need_reservation, reservation_detail,
  │           sd_review, sg_review, sort_order, deleted_at
  │         }
  │         └── ExpenseItem { id, activity_id, amount, payer(sd/sg), split(equal/assign) }
  └── PackingItem { id, trip_id, name, category, assignee(sd/sg), checked, sort_order, deleted_at }
```

所有表支持软删除（`deleted_at` 字段）。

## API

```
POST   /api/trips                           — 创建旅行
GET    /api/trips                           — 旅行列表（按 sort_order）
PUT    /api/trips/reorder                   — 拖拽排序旅行
GET    /api/trips/:id                       — 旅行详情
PUT    /api/trips/:id                       — 编辑旅行
DELETE /api/trips/:id                       — 软删除旅行

GET    /api/trips/:id/days                  — 天列表
POST   /api/trips/:id/days                  — 添加天
PUT    /api/trips/:id/days/:dayId           — 编辑天
DELETE /api/trips/:id/days/:dayId           — 软删除天
PUT    /api/trips/:id/days/reorder          — 拖拽排序天

GET    /api/trips/:id/days/:dayId/activities        — 活动列表
POST   /api/trips/:id/days/:dayId/activities        — 添加活动
PUT    /api/trips/:id/days/:dayId/activities/:actId  — 编辑活动
DELETE /api/trips/:id/days/:dayId/activities/:actId  — 软删除活动
PUT    /api/trips/:id/days/:dayId/activities/reorder — 拖拽排序活动

GET    /api/trips/:id/packing               — 打包清单
POST   /api/trips/:id/packing               — 添加物品
PUT    /api/trips/:id/packing/:itemId        — 编辑物品
DELETE /api/trips/:id/packing/:itemId        — 软删除物品
PUT    /api/trips/:id/packing/:itemId/check  — 勾选/取消

GET    /api/trips/:id/settlement             — 结算数据
GET    /api/trips/:id/recycle-bin            — 回收站列表
POST   /api/recycle-bin/:type/:id/restore    — 恢复
DELETE /api/recycle-bin/:type/:id            — 永久删除

WS     /ws?trip_id=1&user=sd                 — 实时同步
```

## UI 布局

### 旅行列表
卡片列表，拖拽排序（⋮ 手柄），三点菜单含编辑/删除

### 行程规划页
```
┌─────────────────────────────────────┐
│  Trip 标题                 [打][结][回]│
├──────────┬──────────────────────────┤
│  Day 1   │  08:00  早餐   吃  ¥20 sd │
│  Day 2   │         sd:"好吃"         │
│          │  10:00  故宫  景点 ¥60 sg  │
│  [+加天] │         sg:"值得去"       │
│          │  [+加活动]                │
└──────────┴──────────────────────────┘
```
手机端：天列表收起到顶部横滑 tab，活动时间线占满宽。

### 结算页
```
┌─────────────────────────────┐
│  sd 支付：¥1,200            │
│  sg 支付：¥800              │
│  总开销：¥2,000             │
│  每人应承担：¥1,000          │
│  sg → sd：¥200              │
└─────────────────────────────┘
```

## 版本历史

### v0.3.1 (2026-05-22) — Trip 编辑 + 拖拽排序 + 时间校验
- Trip 卡片菜单加"编辑"按钮，可修改标题/目的地/日期
- Trip 卡片拖拽排序（⋮ 手柄 + 蓝色插入线），trips 表加 sort_order 列
- 活动时间与行程日期前后端双重校验

### v0.3.0 (2026-05-21) — 天管理修复 + 活动拖拽 + 体验优化
- 天管理：时区偏移修复、日期唯一性校验、天上限检测区分"真满/缺口"
- 活动卡片拖拽排序（pointer 事件 + 蓝色插入线）
- PWA standalone 模式 alert 修复、手机端 ContextMenu 遮挡修复

### v0.2.3 (2026-05-21) — 多笔开销 + 双人评价 + 用户切换
- 一活动多笔开销（expense_items 子表）、sd/sg 双人评价、用户快速切换

### v0.2.0 (2026-05-21) — 软删除 + 统一回收站
- 4 种类型删除入口 + 回收站（恢复 + 永久删除）+ parent 链校验

### v0.1.0 (2026-05-20) — MVP
- 行程规划 + 打包清单 + 开销结算 + 实时协作 + PWA + Docker 部署

## 架构约定

- Route → Service → DB 三层，不引入不必要的抽象
- 所有表 `deleted_at` 字段，删除为软删除
- 实时协作：最后写入胜出，不做冲突合并
- 无密码认证，仅靠 `X-User` header 区分用户
- 数据库文件、日志等持久化在 `./data/`
