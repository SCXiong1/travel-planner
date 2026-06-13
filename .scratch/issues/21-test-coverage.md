# Issue 21: 补齐测试覆盖

## Parent

[PRD: 前端结构重构 + 测试同步](../frontend-refactor-and-tests.md)

## What to build

后端：新建 server/tests/conftest.py 提取公共 fixture（db/app/client/auth），清理 10 个测试文件重复样板。前端：补齐缺失组件的单元测试（ConfirmDialog、ContextMenu、DaySidebar、Login、Settlement、RecycleBin/RecycleBinContent/RecycleBinDrawer、ToastMessage）。E2E：新增 day-reorder.spec.js，扩展 recycle-bin.spec.js 覆盖 activity/packing 级别的恢复和永久删除。

Type: AFK
Blocked by: #20

## Acceptance criteria

- [x] server/tests/conftest.py 提取 db/app/client/auth 公共 fixture
- [x] 5 个后端测试文件删除重复样板，统一使用 conftest
- [x] pytest 全量通过（74 个测试）
- [x] ConfirmDialog、ContextMenu、DaySidebar、Login、Settlement、RecycleBin 系列、ToastMessage 各有单元测试（22 新测试）
- [x] vitest 全量通过（56 个测试）
- [ ] e2e/tests/day-reorder.spec.js — 跳过，DaySidebar 无拖拽功能
- [x] e2e/tests/recycle-bin.spec.js 扩展 activity 恢复和永久删除（2 新测试）
- [x] playwright Pixel 7 全量通过（24 个测试）

## User Stories

8, 9, 10, 11, 12, 14
