# CLAUDE.md

## 语言偏好

- 思考和回答用中文
- 代码标识符、变量名、API 路径保留英文

---

## 项目概述

travel-planner 是一个家庭旅行规划工具，供 sd 和 sg 两人使用。部署在家庭服务器上（Docker 一键启动），通过浏览器访问，支持手机 PWA。核心功能：行程规划 + 打包清单 + 开销结算 + 实时协作。

一句话：travel-planner = 行程规划 + 打包清单 + 开销结算 + 实时同步，跑在家庭服务器上。

---

## 项目目录结构

```
travel-planner/
├── server/       ← FastAPI 后端（Python）
│   ├── app.py    ← 应用工厂 create_app()
│   ├── main.py   ← uvicorn 入口，端口 3001
│   ├── db/       ← 数据库 schema + 连接
│   ├── routes/   ← API 路由
│   ├── services/ ← 业务逻辑
│   ├── middleware/
│   ├── ws/       ← WebSocket 管理
│   └── tests/    ← pytest
├── client/       ← Vue 3 前端（npm run dev → 5173）
│   └── src/
├── data/         ← SQLite 数据库文件（运行时生成）
├── docker/       ← Dockerfile + docker-compose.yml
└── .scratch/     ← Issue 本地草稿
```

---

## 用户模型

无密码登录。前端两个按钮 "sd" / "sg"，选后存 `localStorage`，请求带 `X-User` header。后端读 header 识别用户。

---

## 技术栈

- 后端：Python 3.12+ / FastAPI / SQLite 3
- 前端：Vue 3 + Vite + Tailwind CSS + vitest
- 实时协作：WebSocket（FastAPI 原生支持，最后写入胜出）
- 部署：Docker 单容器
- PWA：vite-plugin-pwa

---

## 数据模型

```
Trip（一次旅行）
  ├── title, destination, start_date, end_date, sort_order
  ├── Day × N
  │     ├── day_number, date
  │     └── Activity × N
  │           ├── type: 吃 / 住 / 行 / 景点
  │           ├── name, location (可选)
  │           ├── start_time, end_time
  │           ├── need_reservation: bool
  │           ├── reservation_detail: text (可选)
  │           ├── sd_review, sg_review: text（每人只能写自己的）
  │           └── deleted_at: soft delete
  │           └── ExpenseItem × N（子表）
  │                 ├── amount, payer (sd/sg), split (equal/assign)
  └── PackingItem × N
        ├── name, category, assignee (sd/sg), checked
        └── deleted_at
```

所有表支持软删除（`deleted_at` 字段）。回收站可查看和恢复已删除项。

---

## API 设计

RESTful 风格，`/api/*` + `/ws`：

```
/api/trips                        — 旅行 CRUD + 拖拽排序
/api/trips/reorder                — Trip 排序（PUT）
/api/trips/:id/days               — 天 CRUD + 排序
/api/trips/:id/days/reorder       — Day 排序（PUT）
/api/trips/:id/days/:dayId/activities — 活动 CRUD + 排序
/api/trips/:id/days/:dayId/activities/reorder — 活动排序（PUT）
/api/trips/:id/packing            — 打包清单 CRUD
/api/trips/:id/settlement         — 结算数据（只读）
/api/trips/:id/recycle-bin        — 回收站列表
/api/recycle-bin/:type/:id/restore — 恢复
/api/recycle-bin/:type/:id        — 永久删除
/ws                               — WebSocket 实时同步
```

---

## UI 布局

主页面（行程规划）：
- 旅行列表：卡片可拖拽排序（⋮ 手柄+蓝色插入线），三点菜单含编辑/删除
- 左侧：天列表（可切换、拖拽排序），底部[+加天]
- 右侧：当天活动时间线（按时间排列，可拖拽排序），底部[+加活动]
- 活动卡片显示：时间、类型标签（吃/住/行/景点）、名称、多笔开销总金额、sd/sg 双评价
- 顶部 Trip 标题栏 + 可点击用户切换 + [打包清单]入口 + [结算]入口 + [回收站]入口

TripList 页面：
- 卡片拖拽排序、右键菜单含编辑/删除
- 新建/编辑弹窗前后端双重校验 start_date <= end_date

结算页面：
- sd/sg 各自支付总额、总开销、每人应承担、最终补差价

回收站：
- 全局抽屉（TripList 入口）+ 单旅行页面，支持 4 种类型恢复 + 永久删除
- parent 链校验：恢复子项前检查父项是否已删除

---

## 约定

- 容器化时单容器搞定
- 项目足够轻量，不引入不必要的抽象
- 项目分层要清晰，要可维护
- 所有表有 `deleted_at` 字段，删除为软删除
- 实时协作采用最后写入胜出，不做冲突合并
- 无密码认证，仅靠 X-User header 区分用户

---

## 当前版本

### v0.4.0 (2026-05-26) — 架构深化：模块提取与消重

4 个 Issue，不改用户可见功能，只改善架构质量：

- **Issue 18 (P0) — 客户端 API 服务层**：新增 6 个领域 API 模块（trips/days/activities/packing/settlement/recycleBin），组件不再直接调 api/client.js，22 处调用归位
- **Issue 19 (P1) — 拖拽 composable + TripDetail 组件拆分**：提取 useDragReorder composable（6 测试），TripDetail 拆分为 ActivityCard/ActivityForm（4 测试）/DaySidebar，TripDetail 515→251 行。新增 10 个前端 vitest 测试
- **Issue 20 (P1) — 回收站消重**：提取 constants.js + RecycleBinContent.vue，RecycleBin (113→47 行) 和 RecycleBinDrawer (130→51 行) 各瘦身 ~60%
- **Issue 21 (P2) — 服务端 recycle_service 注册表化**：TABLE_MAP → ENTITY_REGISTRY，新增实体类型只需加注册条目不改函数体

### v0.3.1 (2026-05-22) — Trip 编辑 + 拖拽排序 + 时间校验

在 v0.3.0 基础上完成 3 个增强：

- Trip 编辑：卡片菜单增加"编辑"按钮，可修改标题/目的地/日期，复用已有弹窗和后端 PUT 接口
- Trip 拖拽排序：复用活动 pointer 事件拖拽模式，trips 表加 sort_order 列，新建排最前
- 时间校验：活动 start_time > end_time 和行程 start_date > end_date 前后端双重拦截

### v0.3.0 (2026-05-21) — 天管理修复 + 拖拽排序 + 用户切换体验

11 个 commits 合入 master：

- 天管理修复：时区偏移、日期唯一性校验、软删日期复用、天上限检测区分"真满/缺口"
- 活动卡片拖拽排序：pointer 事件 + 蓝色插入线
- PWA standalone 模式 alert 静默屏蔽修复
- 手机端 ContextMenu 删除按钮被遮挡修复
- 用户切换 toast 提示

### v0.2.3 (2026-05-21) — 多笔开销 + 双人评价 + 用户切换

在 v0.2.0 基础上完成 3 个增强 + 4 个 review 修复：

- 一活动多笔开销：新增 expense_items 子表，活动表单动态增删开销行，结算从子表聚合
- sd/sg 双人评价：activities.review 拆为 sd_review + sg_review，后端按 X-User 校验写权限
- 用户快速切换：右上角用户标签可点击 toggle，自动 WebSocket 重连
- 4 个 review 修复：replace_items 事务原子化、list_activities N+1 优化、前端细节修复、混合结算测试

### v0.2.0 (2026-05-21) — 删除功能 + 统一回收站

- 4 种类型（trip/day/activity/packing）删除入口 + 软删除
- 统一回收站（全局抽屉 + 单旅行页面），支持恢复 + 永久删除
- parent 链校验（恢复子项前检查父项是否已删除）
- 新增 ConfirmDialog、ContextMenu、RecycleBinDrawer 组件

### v0.1.0 MVP (2026-05-20)

11 个 Issue 全部合入 master：
- 行程规划（Trip → Day → Activity，含开销/评价/预约）
- 打包清单（勾选、进度条、sd/sg 分配）
- 开销结算（平分/归集、自动算差价）
- 实时协作（WebSocket 广播，最后写入胜出）
- 软删除 + 回收站（恢复）
- 简单身份选择（sd/sg 按钮）
- PWA（可安装到手机桌面）
- Docker 单容器部署

---

## 开发环境

### 每次会话必须激活

```bash
# Node.js（fnm 管理）
eval "$(/d/document/fnm/fnm.exe env)"

# Python（myaccounting conda 环境，conda activate 在 bash 不可用）
export PYTHON=/d/document/Anaconda/envs/myaccounting/python.exe
```

所有 Python 命令用 `$PYTHON` 替代 `python`，pip 用 `$PYTHON -m pip`。uvicorn 和 pytest 在 myaccounting 环境的 Scripts 下，可直接用。

### 关键注意事项

- **Bash 工作目录持久化**：`cd xxx` 的效果会持续到后续所有 bash 命令。务必总是在同一命令中用 `cd /d/document/personal_tools/travel-planner/server && ...` 或 `cd /d/document/personal_tools/travel-planner/client && ...` 显式切换，不要假设之前已经在目标目录。
- **不要 `cd server` 再 `cd client` 分散到两条命令**——第二条会从第一条的目录继续。
- 后端入口是 `server/app.py`（不是 `app/main.py`），导入用 `from app import create_app`。

### 当前环境版本

| 组件 | 版本 |
|------|------|
| Python | 3.12.13 (myaccounting) |
| FastAPI | 0.136.1 |
| Node.js | v22.22.2 (fnm) |
| npm | 10.9.7 |
| Docker | 29.4.1 |

### Issue 工作流

Issue 本地维护在 `.scratch/` 目录，由用户手动管理。开发时按 Issue 编号顺序推进。测试完成后用户自行推送至 GitHub。

---

## Agent skills

### Issue tracker

Issues 记录在 GitHub Issues（仓库 `SCXiong1/travel-planner`）。由用户手动维护，skills 不直接操作 issue。详见 `docs/agents/issue-tracker.md`。

### Triage labels

使用标准五标签词汇表：`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。详见 `docs/agents/triage-labels.md`。

### Domain docs

单上下文结构：根目录 `CONTEXT.md` + `docs/adr/`。详见 `docs/agents/domain.md`。
