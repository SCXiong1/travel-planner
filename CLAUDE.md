# CLAUDE.md

## 语言偏好

- 思考和回答用中文
- 代码标识符、变量名、API 路径保留英文

---

## 项目概述

travel-planner 是一个家庭旅行规划工具，供 sd 和 sg 两人使用。部署在家庭服务器上（Docker 一键启动），通过浏览器访问，支持手机 PWA。核心功能：行程规划 + 打包清单 + 开销结算 + 实时协作。

一句话：travel-planner = 行程规划 + 打包清单 + 开销结算 + 实时同步，跑在家庭服务器上。

---

## 用户模型

无密码登录。前端两个按钮 "sd" / "sg"，选后存 `localStorage`，请求带 `X-User` header。后端读 header 识别用户。

---

## 技术栈

- 后端：Python 3.12+ / FastAPI / SQLite 3
- 前端：Vue 3 + Vite + Tailwind CSS
- 实时协作：WebSocket（FastAPI 原生支持，最后写入胜出）
- 部署：Docker 单容器
- PWA：vite-plugin-pwa

---

## 数据模型

```
Trip（一次旅行）
  ├── title, destination, start_date, end_date
  ├── Day × N
  │     ├── day_number, date
  │     └── Activity × N
  │           ├── type: 吃 / 住 / 行 / 景点
  │           ├── name, location (可选)
  │           ├── start_time, end_time
  │           ├── need_reservation: bool
  │           ├── reservation_detail: text (可选)
  │           ├── expense_amount, expense_payer (sd/sg), expense_split (equal/assign)
  │           ├── review: text
  │           └── deleted_at: soft delete
  └── PackingItem × N
        ├── name, category, assignee (sd/sg), checked
        └── deleted_at
```

所有表支持软删除（`deleted_at` 字段）。回收站可查看和恢复已删除项。

---

## API 设计

RESTful 风格，`/api/*` + `/ws`：

```
/api/trips                        — 旅行 CRUD
/api/trips/:id/days               — 天 CRUD + 排序
/api/trips/:id/days/:dayId/activities — 活动 CRUD + 排序
/api/trips/:id/packing            — 打包清单 CRUD
/api/trips/:id/settlement         — 结算数据（只读）
/api/trips/:id/recycle-bin        — 回收站列表
/api/recycle-bin/:type/:id/restore — 恢复
/ws                               — WebSocket 实时同步
```

---

## UI 布局

主页面（行程规划）：
- 左侧：天列表（可切换、拖拽排序），底部[+加天]
- 右侧：当天活动时间线（按时间排列，可拖拽排序），底部[+加活动]
- 活动卡片显示：时间、类型标签（吃/住/行/景点）、名称、开销、评价
- 顶部 Trip 标题栏 + [打包清单]入口 + [结算]入口

结算页面：
- sd/sg 各自支付总额、总开销、每人应承担、最终补差价

---

## 约定

- 容器化时单容器搞定
- 项目足够轻量，不引入不必要的抽象
- 项目分层要清晰，要可维护
- 所有表有 `deleted_at` 字段，删除为软删除
- 实时协作采用最后写入胜出，不做冲突合并
- 无密码认证，仅靠 X-User header 区分用户

---

## 当前版本 (v0.1.0 MVP)

2026-05-20 完成。11 个 Issue 全部合入 master。

已实现：
- 行程规划（Trip → Day → Activity，含开销/评价/预约）
- 打包清单（勾选、进度条、sd/sg 分配）
- 开销结算（平分/归集、自动算差价）
- 实时协作（WebSocket 广播，最后写入胜出）
- 软删除 + 回收站（恢复）
- 简单身份选择（sd/sg 按钮）
- PWA（可安装到手机桌面）
- Docker 单容器部署

待做（下一轮）：
- 代码 review 中列出的 7 个改进项
- 拖拽排序的前端交互（目前只有 API 支持）
- 更好的错误提示和日志
- 暗黑模式 / 多语言

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
