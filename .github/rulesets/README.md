# .github/rulesets/

本目录存放本仓 GitHub **repository ruleset 的版本化记录（JSON 快照）**。

> ⚠️ **GitHub 不会自动应用本目录**（不同于 `.github/workflows/`）。**生效源**是 GitHub 仓库设置里的 ruleset；这里只是：
> - 让冷读仓库能看到「合并门禁的真实强制点」（否则只在 GitHub 设置里可见）；
> - 漂移可 diff、配置可重放。

## 文件

- [`main-protection.json`](main-protection.json) — `main` 分支保护 ruleset（`id 17444695`，`refs/heads/main`，`enforcement=active`）的导出快照。语义见 [`../../rules/review-gates.md`](../../rules/review-gates.md) 的「main 分支保护」。

## 重放 / 更新（需有权限的账号 + GitHub 认证）

- 更新现有：`gh api -X PUT repos/super-fishball/virtual-persona-daily/rulesets/17444695 --input main-protection.json`
- 新建（如新仓）：先去掉 `id` / `source` / `source_type` 字段，再 `gh api -X POST repos/<owner>/<repo>/rulesets --input <清理后的.json>`
- 或 GitHub UI：Settings → Rules → Rulesets → Import。

> 改了线上 ruleset 后，记得同步更新本 JSON——否则记录漂移，又回到「配置只在 GitHub 端」的盲区（见 gaps B5）。
