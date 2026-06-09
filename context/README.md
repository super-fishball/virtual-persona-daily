# context/ —— 项目上下文

> 供 AI Agent 建立项目认知。**原则：按需生长，不摆空架子。** 只有出现真实、且不与别处（PRD/issue/代码）重复的内容时，才建对应文件。

## 当前已建

- [`domain-glossary.md`](domain-glossary.md) — 领域术语表（术语 ↔ 代码映射，防 AI 理解跑偏）

## 可生长的类型（按需建立）

按"对 AI 的价值 / 抗漂移"排，**架构、决策、踩坑三类通常比产品/业务文档更值得先投入**：

| 类型 | 给 AI 什么 | 何时建 |
|---|---|---|
| `architecture.md` | 子项目如何组合、数据流、技术栈总览 | 系统有一定复杂度时 |
| `decisions/`（ADR） | 关键技术选择**为什么**这么定（append-only） | 有需要留痕、防反复的决策时 |
| `gotchas.md` | 非显而易见的陷阱、隐性"部落知识" | 踩过坑、想沉淀时 |
| `integrations.md` | 对接的第三方 / 外部服务 | 有外部依赖时 |
| `non-goals.md` | 项目**故意不做**什么、已知边界 | 需防 AI 越界加戏时 |
| `business-rules.md` | 全局业务规则 | 有不与 PRD 重复的稳定规则时 |
| `product-overview.md` | 产品做什么、给谁、核心价值 | 有稳定、非"正确的废话"的内容时 |
| `conventions/` | 代码规范 / 编码惯例（命名、模式选择、框架惯用法等 **lint 查不了**的写法）；喂 ⑦/⑧ 评审 agent 的项目写法参照 | 有"反复出现、lint 又查不了"的风格分歧时 |

## 注意

- **空文件比没有更糟**——它给人"上下文已就绪"的错觉。需要才建。
- **conventions 的落位与边界**：跨栈通用规范放本目录 `conventions/`；**栈相关**规范放子项目**本地 `conventions.md`**（从子项目 `CLAUDE.md` 引用），**不在子项目建 `context/`**。归 context **不归 rules**（指导非门禁，违背由评审提、不卡合并）；机械可查的格式归 lint、绝对红线归 `rules/forbidden`，**同一条只写一处**。ECC `backend/frontend-patterns` 可作起草来源，人裁剪、不照搬。
- **谁维护 / 如何防过时（✅ 已确定）**：所有权统一收敛到 [`../.github/CODEOWNERS`](../.github/CODEOWNERS)（全局 context = 组/集体共有，子项目 context = 各人），**不在文档里写散文主责人**（避免与 CODEOWNERS 两份漂移）；防过时靠软门禁（人审内容）+ 硬门禁（机械查路径耦合，待路径源就位），见 [`../rules/review-gates.md`](../rules/review-gates.md)。
