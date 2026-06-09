# CLAUDE.md — servers/generation-service

> 本文件是 servers/generation-service 子项目的入口。须在阅读根 `CLAUDE.md` 与根 `rules/` 之后阅读。

## 1. 子项目说明

`servers/generation-service` 是事件生成服务：调用 LLM 生成虚拟人物的每日日常事件 / 内容。

**契约角色（双向）**：
- 对 `servers/api`：**契约提供方**——产出事件供后端聚合取用。
- 对 `servers/ai-gateway`：**契约消费方**——所有 LLM 调用一律经内部网关，**禁止直连 DeepSeek 或任何 LLM**。

<!-- TODO（项目接入时填写）：生成管线 / 模块级职责细化。 -->

## 2. 必读上下文

- [`../../context/domain-glossary.md`](../../context/domain-glossary.md) — 领域术语表
- [`../../context/README.md`](../../context/README.md) — context 类型菜单（其余按需生长）

## 3. 必读规则

- 根规则：[`../../rules/`](../../rules/)
- 本地规则：[`./rules/`](./rules/)（本地优先，但不得违反根 `forbidden.md`）

## 4. 技术栈

- **语言**：Python
<!-- TODO：Web/任务框架、依赖管理（如 uv / poetry）、Python 版本、关键库在接入时补全。 -->

## 5. 常用命令

<!-- TODO：启动 / 测试 / 构建 / lint / 类型检查（如 ruff / mypy）。 -->

## 6. 读取顺序

根 `CLAUDE.md` → 根 `rules/` → 本 `CLAUDE.md` → 本 `rules/`

## 7. 边界与契约角色

- 可改范围与跨项目边界见 [`./rules/scope.md`](./rules/scope.md)（专人专项：只在 `servers/generation-service` 内改动）。
- **作为提供方（对 `servers/api`）**：对外事件契约变更须经 feature 层集体定稿，不得单方改动既有契约。
- **作为消费方（对 `servers/ai-gateway`）**：只按网关既定契约对接，不得绕过网关直连 LLM；需求变更回到 feature 层。
