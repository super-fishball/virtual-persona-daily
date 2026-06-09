# CLAUDE.md — servers/api

> 本文件是 servers/api 子项目的入口。须在阅读根 `CLAUDE.md` 与根 `rules/` 之后阅读。

## 1. 子项目说明

`servers/api` 是后端 API 服务，**跨子项目契约的提供方**（对接 `apps/*`）。

<!-- TODO（项目接入时填写）：本服务的具体职责。 -->

## 2. 必读上下文

- [`../../context/domain-glossary.md`](../../context/domain-glossary.md) — 领域术语表
- [`../../context/README.md`](../../context/README.md) — context 类型菜单（其余按需生长）

## 3. 必读规则

- 根规则：[`../../rules/`](../../rules/)
- 本地规则：[`./rules/`](./rules/)（本地优先，但不得违反根 `forbidden.md`）

## 4. 技术栈

<!-- TODO：框架、数据库、关键依赖、语言/运行时版本。 -->

## 5. 常用命令

<!-- TODO：启动 / 测试 / 构建 / lint / 迁移。 -->

## 6. 读取顺序

根 `CLAUDE.md` → 根 `rules/` → 本 `CLAUDE.md` → 本 `rules/`

## 7. 边界与契约角色

- 可改范围与跨项目边界见 [`./rules/scope.md`](./rules/scope.md)（专人专项：只在 `servers/api` 内改动）。
- **契约提供方角色**：跨子项目契约僵持时本服务有最终建议权（根 workflow 甲+乙仲裁）；但契约变更须经 feature 层集体定稿，不得单方改动既有契约。
