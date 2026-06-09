# CLAUDE.md — servers/api

> 本文件是 servers/api 子项目的入口。须在阅读根 `CLAUDE.md` 与根 `rules/` 之后阅读。

## 1. 子项目说明

`servers/api` 是后端 API 服务：聚合业务逻辑，对前端提供数据与操作接口；向下游事件生成服务取数。

**契约角色（双向）**：
- 对 `apps/web`：**契约提供方**。
- 对 `servers/generation-service`：**契约消费方**——按其既定契约获取生成的事件，不直连 LLM/网关。

<!-- TODO（项目接入时填写）：本服务的具体职责细化。 -->

## 2. 必读上下文

- [`../../context/domain-glossary.md`](../../context/domain-glossary.md) — 领域术语表
- [`../../context/README.md`](../../context/README.md) — context 类型菜单（其余按需生长）

## 3. 必读规则

- 根规则：[`../../rules/`](../../rules/)
- 本地规则：[`./rules/`](./rules/)（本地优先，但不得违反根 `forbidden.md`）

## 4. 技术栈

- **语言**：TypeScript
- **运行时**：Node.js
<!-- TODO：Web 框架、数据库、ORM、Node 版本等关键依赖在接入时补全。 -->

## 5. 常用命令

在 `servers/api/` 下（依赖经根 `pnpm install` 安装；技术栈 Node + TS + Fastify）：

- 启动（开发）：`pnpm dev`（tsx 热重载，默认 `:3000`，`GET /health` → `{"status":"ok"}`）
- 启动（生产）：`pnpm build && pnpm start`
- 构建：`pnpm build`（`tsc -p tsconfig.build.json` → `dist/`）
- 测试：`pnpm test`（`vitest run`，含 `/health` 用例）
- lint：`pnpm lint`（`eslint .`）
- typecheck：`pnpm typecheck`（`tsc --noEmit`）

四道门一次跑全部 4 子项目：仓库根目录 `make check`。

## 6. 读取顺序

根 `CLAUDE.md` → 根 `rules/` → 本 `CLAUDE.md` → 本 `rules/`

## 7. 边界与契约角色

- 可改范围与跨项目边界见 [`./rules/scope.md`](./rules/scope.md)（专人专项：只在 `servers/api` 内改动）。
- **作为提供方（对 `apps/web`）**：跨子项目契约僵持时本服务（后端提供方）有兜底权；但契约变更须经 feature 层集体定稿，不得单方改动既有对外契约。
- **作为消费方（对 `servers/generation-service`）**：只按其既定契约对接，不得单方改动；需求变更回到 feature 层。
