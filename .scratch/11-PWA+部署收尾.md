# 11 - PWA + 部署收尾

## Type

AFK

## Blocked by

- 01-项目骨架
- 02-身份选择
- 03-旅行计划CRUD
- 04-天管理
- 05-活动基础管理
- 06-活动扩展
- 07-打包清单
- 08-结算页
- 09-软删除+回收站
- 10-实时协作

## What to build

PWA 配置和部署收尾，确保手机可安装、Docker 可一键启动。

**PWA**：`vite-plugin-pwa` 配置，生成 manifest.json 和 Service Worker。图标、离线缓存策略（至少缓存静态资源）、独立应用模式。

**Docker**：完善 Dockerfile（多阶段构建：先构建前端静态文件，再复制到 FastAPI 容器）。`docker-compose.yml` 带 data volume 挂载。确保首次启动时自动建表。

**前端**：响应式适配。手机端：天列表收起到顶部横滑 tab（或下拉选择），活动时间线占满屏宽。

## Acceptance criteria

- [ ] `docker compose up -d` 一条命令启动
- [ ] 浏览器访问 `http://localhost:3000` 正常使用
- [ ] 手机浏览器打开可添加到桌面（PWA 安装提示）
- [ ] 安装后打开像独立 App（无浏览器地址栏）
- [ ] 手机端布局正常：天列表可切换，活动时间线可滚动
- [ ] 数据持久化：重启容器后数据不丢失（data volume）
- [ ] iOS Safari 和 Android Chrome 均可正常使用

---
**Status:** done (2026-05-20)
