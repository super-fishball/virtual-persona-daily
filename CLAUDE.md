# CLAUDE.md

> 本文件是 AI Agent 的根入口。执行任何任务前必须完整阅读。

---

## 1. 项目说明

virtual-persona-daily：为虚拟人物（persona）生成每日日常事件 / 内容的产品。

本仓库为 monorepo，包含 4 个子项目：

| 子项目 | 职责 | 栈 | 契约角色 |
|---|---|---|---|
| [`apps/web`](apps/web/) | 面向用户的前端 | React / TypeScript | `servers/api` 的消费方 |
| [`servers/api`](servers/api/) | 后端 API，聚合业务 | Node / TypeScript | 对 web 提供方；对 generation-service 消费方 |
| [`servers/generation-service`](servers/generation-service/) | 事件生成（调 LLM） | Python | 对 api 提供方；对 ai-gateway 消费方 |
| [`servers/ai-gateway`](servers/ai-gateway/) | 薄 LLM 代理（DeepSeek） | Python | 对 generation-service 的内部提供方 |

数据流：`apps/web` → `servers/api` → `servers/generation-service` → `servers/ai-gateway` → DeepSeek。

AI Agent 的行为边界由本文件 + `rules/` + 各子项目的 `CLAUDE.md`/`rules/` 共同约束。

---

## 2. 协作原则

- **任务必须有依据**：无 spec / plan 不得自行决策实现方向。
- **人工保留最终判断权**：AI 产草稿与自检，人做决策。**AI 永不作为合并门禁**——合并与否恒由人裁决。
- **越界立即暂停**：命中高影响区、禁止项或无依据改动时，停止并提示确认。
- **专人专项**：开发动作恒在单一子项目内进行，不跨子项目边界改动。
- **完成要有证据**：声称"完成 / 通过"前必须先验证、摆证据（不谎报成功）；"完成"由 spec/acceptance 定义，未做完的范围不得当完成。
- **透明参与范围**：每个 PR 必须声明 AI 参与了哪些部分。

---

## 3. 产品上下文引用（执行任务前必读）

- [`context/domain-glossary.md`](context/domain-glossary.md) — 领域术语表（当前唯一已建）
- [`context/README.md`](context/README.md) — context 可生长的类型菜单（architecture / ADR / gotchas 等，按需建立）

---

## 4. AI 规则引用（执行任务前必读）

- [`rules/README.md`](rules/README.md) — 规则索引、读取顺序、优先级
- [`rules/high-impact.md`](rules/high-impact.md) — 高影响区定义
- [`rules/forbidden.md`](rules/forbidden.md) — 禁止事项
- [`rules/review-gates.md`](rules/review-gates.md) — 人工审核 / 升级评审触发条件 + Agent Review 机制
- [`rules/development-guard.md`](rules/development-guard.md) — 开发中自检通用流程

---

## 5. 子项目规则读取顺序

在子项目中执行任务时，按以下顺序读取：

1. 根 `CLAUDE.md`（本文件）
2. 根 `rules/`
3. 子项目 `CLAUDE.md`
4. 子项目 `rules/`

**局部规则优先于全局，但不得违反全局 `forbidden.md`。**

---

## 6. 冲突处理规则

多层规则冲突时：**不得自行裁量，立即暂停**，向开发者说明冲突点（哪条规则、哪个层级、具体内容），等待开发者明确优先级后继续。

---

## 7. 任务开始前基本要求

开始写代码前必须确认：

- [ ] 存在对应 `spec/*.md` 与 `plan/*.md`，或已获开发者明确豁免（简单需求可跳过，须在 PR 说明原因）
- [ ] 已阅读本文件及对应子项目 `CLAUDE.md`
- [ ] 已阅读根 `rules/` 及对应子项目 `rules/`

---

## 8. 开发模式（已确定）

- **两层开发**：跨子项目需求先在 **feature 维度**定总 spec + 契约（AI 起草、涉及方集体定稿），再拆到**子项目维度**各自执行。单子项目需求直接在子项目内进行。
- **feature 层无单一主人**：团队无协调角色，总 spec/契约由涉及的子项目开发者集体共有；契约僵持时由提供方（后端）兜底。
- **feature 层落地**：跨子项目需求的总 spec / 契约指针 / 拆分 / 端到端验收，放在根级 [`feature/`](feature/)（每个 feature 一个文件夹，契约用后端机读 schema 指针，见其 README）。
<!-- TODO（时机）：本章暂以原则形式承载开发流程；待流程稳定后，可拆出独立的 workflow.md，本章缩为摘要 + 指针。 -->
