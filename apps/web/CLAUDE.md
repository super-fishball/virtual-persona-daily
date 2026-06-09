# CLAUDE.md — apps/web

> 本文件是 apps/web 子项目的入口。须在阅读根 `CLAUDE.md` 与根 `rules/` 之后阅读。

## 1. 子项目说明

`apps/web` 是面向最终用户的前端应用：展示虚拟人物的每日日常事件 / 内容，承载用户交互。

**契约角色**：`servers/api` 的**消费方**——只按 feature 层既定契约调用后端，不直连其他服务。

<!-- TODO（项目接入时填写）：页面/模块级职责细化。 -->

## 2. 必读上下文

- [`../../context/domain-glossary.md`](../../context/domain-glossary.md) — 领域术语表
- [`../../context/README.md`](../../context/README.md) — context 类型菜单（其余按需生长）

## 3. 必读规则

- 根规则：[`../../rules/`](../../rules/)
- 本地规则：[`./rules/`](./rules/)（本地优先，但不得违反根 `forbidden.md`）

## 4. 技术栈

- **语言**：TypeScript
- **框架**：React
<!-- TODO：构建工具（如 Vite）、状态管理、UI 库、Node 版本等关键依赖在接入时补全。 -->

## 5. 常用命令

在 `apps/web/` 下（依赖经根 `pnpm install` 安装；技术栈 Vite + React + TS）：

- 启动（开发）：`pnpm dev`（默认 `:5173`，渲染 hello 页面）
- 构建：`pnpm build`（`vite build` → `dist/`）
- 测试：`pnpm test`（`vitest run`）
- lint：`pnpm lint`（`eslint .`）
- typecheck：`pnpm typecheck`（`tsc --noEmit`）

四道门一次跑全部 4 子项目：仓库根目录 `make check`。

## 6. 读取顺序

根 `CLAUDE.md` → 根 `rules/` → 本 `CLAUDE.md` → 本 `rules/`

## 7. 边界

可改范围与跨项目边界见 [`./rules/scope.md`](./rules/scope.md)（专人专项：只在 `apps/web` 内改动，跨子项目走 feature 层契约先行）。
