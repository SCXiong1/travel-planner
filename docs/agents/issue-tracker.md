# Issue tracker: GitHub

Issues 和 PRD 记录在 GitHub Issues 中。仓库：`SCXiong1/travel-planner`。

Issue 由用户手动维护，skills（如 `to-issues`、`triage`、`to-prd`）不直接调用 `gh` CLI。如需操作 issue，使用 `gh` CLI：

## 约定

- **创建 issue**：`gh issue create --title "..." --body "..."`。多行 body 用 heredoc。
- **查看 issue**：`gh issue view <number> --comments`
- **列出 issue**：`gh issue list --state open --json number,title,body,labels,comments`
- **评论 issue**：`gh issue comment <number> --body "..."`
- **管理标签**：`gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **关闭 issue**：`gh issue close <number> --comment "..."`

仓库信息通过 `git remote -v` 推断，`gh` 在 clone 目录内会自动识别。
