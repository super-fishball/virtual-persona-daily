# 规则索引与读取规范

本目录定义 AI Agent 在本项目的全局行为规则。

## 文件清单

| 文件 | 作用 |
|---|---|
| [`high-impact.md`](high-impact.md) | 高影响区定义，命中须升级评审 |
| [`forbidden.md`](forbidden.md) | AI Agent 绝对禁止事项 |
| [`review-gates.md`](review-gates.md) | 触发必须人工审核 / 升级评审的条件，及 Agent Review / changed-files / CODEOWNERS 机制 |
| [`development-guard.md`](development-guard.md) | 开发中自检的通用流程（子项目补充栈特有检查） |

## 读取顺序

执行子项目任务时，按以下顺序读取（后读的更具体）：

1. 根 `CLAUDE.md`
2. 根 `rules/`（本目录）
3. 子项目 `CLAUDE.md`
4. 子项目 `rules/`

## 优先级与继承关系（重要）

- **根 `rules/` = 全局基线**，对所有子项目生效。
- **子项目 `rules/` = 本地特例**，只能在基线之上**叠加更严的约束**或补充本子项目特有内容。
- **子项目规则不得放宽或违反根 `forbidden.md`**。局部更严 → 以局部为准；局部试图放宽全局禁止项 → 视为冲突。

## 冲突处理

任何层级规则冲突时，AI **不得自行裁量**，立即暂停并向开发者说明冲突点，等待明确优先级。

## 所有权与维护

本目录规则**无单一主人、集体共有**（团队无协调角色）。所有权统一以 [`../.github/CODEOWNERS`](../.github/CODEOWNERS) 为准——**指针，不在各文件写散文"主责人"**（避免与 CODEOWNERS 两份漂移）。全局 `rules/` 在 CODEOWNERS 指为「组/集体」，子项目 `rules/` 指为各人；变更随 PR 走，由 CODEOWNERS 指定的涉及方共同评审定稿。防过时门禁见 [`review-gates.md`](review-gates.md)。
