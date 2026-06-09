# CLAUDE.md — servers/ai-gateway

> 本文件是 servers/ai-gateway 子项目的入口。须在阅读根 `CLAUDE.md` 与根 `rules/` 之后阅读。

## 1. 子项目说明

`servers/ai-gateway` 是**薄 LLM 代理层**：统一封装单家 LLM（**DeepSeek**），对内提供稳定的调用入口（鉴权透传、协议适配、超时 / 重试 / 限流、凭证持有）。

**"薄"是硬约束**：只做代理与横切（凭证、协议、稳定性），**不承载事件生成等业务逻辑**（业务在 `servers/generation-service`）。

**契约角色**：对 `servers/generation-service` 是**内部契约提供方**——是其唯一的 LLM 调用入口。

<!-- TODO（项目接入时填写）：代理层模块级职责细化。 -->

## 2. 必读上下文

- [`../../context/domain-glossary.md`](../../context/domain-glossary.md) — 领域术语表
- [`../../context/README.md`](../../context/README.md) — context 类型菜单（其余按需生长）

## 3. 必读规则

- 根规则：[`../../rules/`](../../rules/)
- 本地规则：[`./rules/`](./rules/)（本地优先，但不得违反根 `forbidden.md`）

## 4. 技术栈

- **语言**：Python
- **上游 LLM**：DeepSeek（单家；多家抽象是后续 feature 决策，当前不做）
<!-- TODO：Web 框架、HTTP 客户端、依赖管理、Python 版本在接入时补全。 -->

## 5. 常用命令

<!-- TODO：启动 / 测试 / 构建 / lint / 类型检查（如 ruff / mypy）。 -->

## 6. 读取顺序

根 `CLAUDE.md` → 根 `rules/` → 本 `CLAUDE.md` → 本 `rules/`

## 7. 边界与契约角色

- 可改范围与跨项目边界见 [`./rules/scope.md`](./rules/scope.md)（专人专项：只在 `servers/ai-gateway` 内改动）。
- **作为内部契约提供方（对 `servers/generation-service`）**：契约僵持时本服务（提供方）有兜底权；但契约变更须经 feature 层集体定稿，不得单方改动既有契约。
- **保持薄代理**：越界承载业务逻辑、或擅自扩成多家 LLM 抽象层，均属高影响，须先经评审。
