# servers/generation-service

事件生成服务：调用 LLM（经 `servers/ai-gateway`）生成虚拟人物的每日日常事件 / 内容。

## 职责

- 向 `servers/api` 提供生成的事件（契约提供方）。
- 经 `servers/ai-gateway` 消费 LLM 能力（契约消费方，不直连 LLM）。

<!-- TODO：生成管线、输入/输出、关键模块。 -->

## 启动

<!-- TODO：本地启动、依赖（Python 版本、虚拟环境）、环境变量（如网关地址）。 -->

## AI 协作

入口见 [`CLAUDE.md`](CLAUDE.md)，须先读根 `CLAUDE.md` 与根 `rules/`。
