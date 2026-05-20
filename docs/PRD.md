# PRD: travel-planner MVP

## Problem Statement

sd 和 sg 每次出去旅行，行程规划靠聊天记录、开销算账靠脑子记、打包靠临时想。需要一个简单、私有、两个人能同时编辑的旅行规划工具，不需要注册，不需要 App Store，打开浏览器就能用。

## Solution

一个自部署的家庭旅行规划工具（Docker 一键启动），两人通过浏览器和手机 PWA 访问。核心能力：规划每天的行程活动、记录开销并自动算账、制作打包清单、两个人实时同步编辑。

## User Stories

1. 作为 sd，我能创建一个新旅行计划，填写目的地和日期，这样所有行程信息有地方放
2. 作为 sd，我能给旅行添加多天，每天有日期，这样按天规划行程
3. 作为 sd，我能在某天下添加活动（吃/住/行/景点），填写名称、地点、开始和结束时间，这样我知道每天的具体安排
4. 作为 sg，我能看到 sd 创建的旅行计划，并在里面添加和编辑活动，这样我们共同规划
5. 作为 sd，我能拖拽调整活动和天的顺序，这样行程可以灵活调整
6. 作为 sd，我能在活动上标记是否需要预约，并填写预约详情（确认号、电话等），这样不会漏掉预订
7. 作为 sd，我能在活动上记录花了多少钱、谁付的、分摊方式（平分还是归集），这样每笔开销都有迹可循
8. 作为 sg，我能看到"结算"页面，显示每人付了多少、每人该承担多少、谁该补给谁多少钱，这样算账不用自己算
9. 作为 sd，我能创建打包清单，添加物品、分类、分配给谁带，并勾选已打包，这样不会漏带东西
10. 作为 sg，我能看到并勾选自己负责的物品，这样知道自己的打包进度
11. 作为 sd，我删除一个活动或打包项后，它进入回收站而不是永久消失，这样误删了能恢复
12. 作为 sd，我能在回收站里看到之前删的东西并恢复它们
13. 作为 sd，我在编辑行程时，sg 打开同一个行程能即时看到我的改动，反之亦然，这样不需要刷新页面
14. 作为使用者，我打开浏览器选 sd 或 sg 就能用，不需要注册、不需要记密码
15. 作为使用者，我能在手机上把这个工具装到桌面（PWA），打开就像 App 一样
16. 作为 sd，我能看到所有旅行计划的列表，点进去就是行程详情
17. 作为 sd，我能编辑已有的活动信息（改时间、改评价、改开销等）
18. 作为 sg，我能在旅行结束后给每个活动写一段文字评价，这样以后回顾能想起来

## Implementation Decisions

### 技术栈
- 后端：Python 3.12 + FastAPI + SQLite 3
- 前端：Vue 3 + Vite + Tailwind CSS
- 实时同步：WebSocket（FastAPI 原生支持）
- PWA：vite-plugin-pwa
- 部署：Docker 单容器（FastAPI 同时 serve API 和前端静态文件）

### 用户认证
- 无密码。前端两按钮 sd/sg，选后存 localStorage
- 请求带 `X-User` header，后端中间件解析
- WebSocket 通过查询参数传 user

### 数据模型
```
Trip { id, title, destination, start_date, end_date, created_at }
  └── Day { id, trip_id, day_number, date, title }
        └── Activity {
              id, day_id, type(eat/stay/transport/sight),
              name, location, start_time, end_time,
              need_reservation, reservation_detail,
              expense_amount, expense_payer(sd/sg), expense_split(equal/assign),
              review, sort_order, deleted_at
            }
  └── PackingItem {
        id, trip_id, name, category, assignee(sd/sg),
        checked, sort_order, deleted_at
      }
```
所有表支持软删除（deleted_at 字段）。

### API 设计
```
GET    /api/trips                           — 旅行列表
POST   /api/trips                           — 创建旅行
GET    /api/trips/:id                       — 旅行详情
PUT    /api/trips/:id                       — 编辑旅行
DELETE /api/trips/:id                       — 软删除旅行

GET    /api/trips/:id/days                  — 天列表
POST   /api/trips/:id/days                  — 添加天
PUT    /api/trips/:id/days/:dayId           — 编辑天
DELETE /api/trips/:id/days/:dayId           — 软删除天
PUT    /api/trips/:id/days/reorder          — 拖拽排序天

GET    /api/trips/:id/days/:dayId/activities       — 活动列表
POST   /api/trips/:id/days/:dayId/activities       — 添加活动
PUT    /api/trips/:id/days/:dayId/activities/:actId — 编辑活动
DELETE /api/trips/:id/days/:dayId/activities/:actId — 软删除活动
PUT    /api/trips/:id/days/:dayId/activities/reorder — 拖拽排序活动

GET    /api/trips/:id/packing               — 打包清单
POST   /api/trips/:id/packing               — 添加物品
PUT    /api/trips/:id/packing/:itemId        — 编辑物品
DELETE /api/trips/:id/packing/:itemId        — 软删除物品
PUT    /api/trips/:id/packing/:itemId/check  — 勾选/取消

GET    /api/trips/:id/settlement             — 结算数据

GET    /api/trips/:id/recycle-bin            — 回收站列表
POST   /api/recycle-bin/:type/:id/restore    — 恢复

WS     /ws?trip_id=1&user=sd                 — 实时同步
```

### 实时协作
- 用户进入 Trip 后连接 WebSocket
- 服务端维护 trip_id → [连接] 映射
- 增删改操作后广播事件给同 trip 的其他连接
- 冲突：最后写入胜出，不做合并

### 结算算法
- 平分（equal）：金额 ÷ 2，各承担一半
- 归集（assign）：金额全部由支付人承担
- 汇总：每人支付总额 − 应承担额 = 正数则对方欠你，负数则你欠对方

### 软删除
- 所有删除操作 SET deleted_at = 当前时间
- 列表查询过滤 WHERE deleted_at IS NULL
- 回收站查 WHERE deleted_at IS NOT NULL
- 恢复 SET deleted_at = NULL

### 架构分层
- Route → Service → DB 三层
- 路由层处理 HTTP 细节 + Pydantic 校验
- 服务层处理业务逻辑 + 数据库操作
- WebSocket 连接管理独立模块

### 前端模块
- 登录页 → 旅行列表 → 行程规划（核心页） → 打包清单 / 结算 / 回收站
- 共享状态用 Vue composables，不引入状态管理库
- API 客户端封装所有请求，自动带 X-User header
- WebSocket 客户端处理连接生命周期和事件回调

### UI 布局
- 行程规划页：左侧天列表 + 右侧活动时间线（两栏布局）
- 活动卡片展示：时间、类型标签（颜色区分吃/住/行/景点）、名称、开销、评价
- 点击活动卡片展开编辑弹窗
- 手机端：天列表收起到顶部 tab，活动时间线占满宽

### 打包顺序
1. 数据库建表 + 基础连接
2. 后端路由 + 服务层（按 Trip → Day → Activity → Packing → Settlement → RecycleBin）
3. WebSocket 实时同步
4. 前端页面（登录 → 旅行列表 → 行程规划 → 打包 → 结算 → 回收站）
5. Docker 化 + PWA 配置

## Out of Scope

- 用户注册/登录/密码（sd/sg 按钮即可）
- OIDC/SSO 登录
- MFA 两步验证
- 多用户权限系统（只有 sd 和 sg）
- 照片上传和管理（仅文字评价）
- 文件附件
- 地图集成（后续可加）
- 地点搜索（后续可加）
- PDF 导出
- 多语言（仅中文）
- 暗黑模式（后续可加）
- 群聊/评论/投票
- MCP 协议 / AI 集成
- 年假规划 / 世界足迹
- 预订管理模块（仅活动上的预约标记）
- 离线支持（后续可加）

## Further Notes

- 本 PRD 基于 TREK 项目（全功能旅行协作工具）做减法，保留最核心的四个模块：行程规划、打包清单、开销结算、实时协作
- 参考文档：项目说明书.md、工程说明书.md（TREK 的原版设计和工程指南）
- MVP 目标：能在家庭服务器上 Docker 一键部署，sd 和 sg 打开浏览器就能规划下一次旅行
