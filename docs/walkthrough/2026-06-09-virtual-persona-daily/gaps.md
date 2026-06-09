# Phase 0 走查 — gaps（virtual-persona-daily）

> 立走查记录：截至 Phase 0（模板基线 → 子项目重构 → 可跑骨架 + 四道门 → context / high-impact → hook `TASK_SCOPE`/`TEST_CMD`）的发现。
> 本文件**只立条目**；完整证据日志 + 模板忠实度自查留到 **Phase 0 末**再补。
> 分两类：**A 回流-worthy**（工具 / 流程缺陷，源在团队模板，需上报修上游）、**B tech 小记**（非回流，本地规避 / 留观）。
> 每条记：**现象 / 影响 / 现状**（已修 / 已规避 / 待办）。

---

## A. 回流-worthy（缺陷源在团队模板，待回流上游 + 人裁决）

### A1. path-guard.sh fails-open：block 文案变量紧贴全角标点 → `set -u` 下崩溃放过越界

- **现象**：`.claude/hooks/path-guard.sh` 越界分支的错误文案里 `$TASK_SCOPE` 紧贴全角逗号（`…范围=$TASK_SCOPE，却改 …`）。在 `set -u` + bash 3.2（macOS 自带）下，多字节逗号的首字节被并进变量名 → 报 `unbound variable`，脚本 **exit 1 而非 exit 2**。
- **影响**：**fails-open（守卫形同虚设）**。PreToolUse 守卫看似拦截、实则在打印拦截文案时崩溃；越界编辑因退出码非 2 被放过，且不易察觉（"看似拦、其实崩"）。只在越界 / 高影响分支**真正触发**时暴露——正常放行路径（in-scope，exit 0）不触发，故极易漏测。
- **现状**：**本地已修，缺陷源待回流**。本 repo 已将越界与高影响两条 `echo` 的变量改花括号 `${VAR}`，复测 exit=2 恢复正常拦截（step 5，commit `a2fd75b`；本地改动亦记于 [`.claude/VENDOR.md`](../../../.claude/VENDOR.md)）。**缺陷源在团队模板 `path-guard.sh`**（本 repo 由模板基线 `9426e4c` 复制而来）→ 标「**待回流上游模板、人裁决**」：上游同款文案在 `set -u` + bash 3.2 环境普遍中招。

---

## B. tech 小记（非回流；本地已规避 / 留观）

### B2. path-guard.sh 的 `case "$REL" in $pat)` glob 语义依赖 bash，zsh 下会全漏匹配

- **现象**：用变量当 glob 的 `case "$REL" in $pat)` 写法，**bash 下正确**（`*` 跨 `/`、`**`≈`*`）；但 **zsh 的 `case` 需 `${~pat}`** 才把变量内容当 glob，否则按字面匹配 → 若改用 zsh 跑，high-impact / 越界路径**全部漏匹配**。
- **影响**：换 shell 跑 hook 会**静默失效**。本机交互 shell 即 zsh，曾导致一次自测「全 normal」的假象，改回 bash 复现后才正确——若误以 zsh 为准会得出"守卫没问题"的错误结论。
- **现状**：**已规避**。hook 用 `#!/usr/bin/env bash` shebang 固定解释器；[`rules/high-impact.paths`](../../../rules/high-impact.paths) 文件头已注明匹配语义 = path-guard 的 POSIX `case` glob。无需改动；未来若有人移植到 zsh，需显式 `${~pat}`。

### B3. FastAPI TestClient 的 StarletteDeprecationWarning

- **现象**：两个 Python 服务（generation-service / ai-gateway）`pytest` 跑 `/health` 用例时，FastAPI `TestClient` 报 `StarletteDeprecationWarning`（提示 `httpx` 与 `starlette.testclient` 的用法将变更）。
- **影响**：**仅告警，测试仍过、门为绿**，非阻断。
- **现状**：**留观（留作 F2 升级信号）**。未加 `filterwarnings` 掩盖（避免藏掉未来真信号）；待 F2 依赖升级时按提示处理。

### B4. CODEOWNERS 的 bot 性质未文档化 → 冷读 agent 误报 §2 冲突

- **现象**：`.github/CODEOWNERS` 把 `@vpd-ci-bot`（实为开发者本人的第二个 GitHub 账号、手动点 approve）挂为全路径必须审批人，但文件里未说明该账号性质。
- **影响**：冷读 agent（无上下文）按字面「bot 当全路径门禁」误报与 §2「AI 永不作为合并门禁」冲突——实为单人模拟「作者 ≠ 审批者」的**人工**审批，非 AI / 自动化门禁，**不违 §2**。一次冷读即触发此误报。
- **现状（已修）**：已在 CODEOWNERS 顶部注释澄清——`@vpd-ci-bot` = 开发者第二账号、手动审、非 AI、与 §2 不冲突；并警示绝不可接入自动 approve 的 CI；真实多人时换各域真人 / 团队。

### B5. 分支保护 ruleset 只在 GitHub 端 → 仓库内无版本化记录，冷读看不到真实合并门禁

- **现象**：`main` 分支保护以 GitHub repository ruleset（`main-protection`，`id 17444695`，`enforcement=active`）形式只存在于 GitHub 设置；仓库内此前无版本化记录。强制项（PR + 1 审批、CODEOWNERS 审、`gates` CI strict 必过、禁删 / 禁强推、无 bypass）只在 GitHub UI 可见。
- **影响**：冷读仓库看不到「合并门禁的真实强制点」，易低估 / 误判治理强度；且 ruleset 漂移无 diff 可查、无重放来源。
- **现状（已修）**：已把导出 JSON 落 [`../../../.github/rulesets/main-protection.json`](../../../.github/rulesets/main-protection.json)（同目录 README 注明「GitHub 不自动应用本目录、生效源在设置」，避免下一个误读）；并在 [`../../../rules/review-gates.md`](../../../rules/review-gates.md) 文档化实际强制的门禁。同 [[B4]] 一类：GitHub 端配置不入库 → 冷读盲区，修法 = 版本化 + 文档化。

---

## 备注

- A 类回流流程见 [`.claude/VENDOR.md`](../../../.claude/VENDOR.md) 「刷新流程」末条「本地改动逐条记」；A1 已在 VENDOR.md 记本地改动。
- 走查目录按「日期 + repo」命名：`docs/walkthrough/2026-06-09-virtual-persona-daily/`。
