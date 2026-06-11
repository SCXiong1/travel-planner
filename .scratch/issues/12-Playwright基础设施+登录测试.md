## What to build

搭建 Playwright E2E 测试基础设施，并完成第一个测试模块（登录）。包括：安装 Playwright、配置 webServer 自动启动 uvicorn + vite dev、配置 iPhone 14 和 Pixel 7 两个移动设备 projects、实现 SQLite 文件复制/还原的 fixture 机制、编写 login.spec.js 测试身份选择和跳转、为 Login.vue 添加 data-testid。

## Acceptance criteria

- [ ] Playwright 已安装，playwright.config.js 已配置
- [ ] webServer 配置自动启动 uvicorn（port 3001）和 vite dev server，等待 ready 后开始测试
- [ ] projects 配置包含 iPhone 14 和 Pixel 7 两个设备
- [ ] fixtures 目录包含干净的 db 模板，beforeAll 复制到 data/travel.db，afterAll 还原
- [ ] Login.vue 中选择身份的交互元素添加了 data-testid
- [ ] login.spec.js 覆盖：选择 sd → 进入 /trips、选择 sg → 进入 /trips
- [ ] `npx playwright test` 在两个设备上均通过

## Blocked by

None - can start immediately
