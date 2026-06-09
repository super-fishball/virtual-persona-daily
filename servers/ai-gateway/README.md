# servers/ai-gateway

薄 LLM 代理层：统一封装单家 LLM（DeepSeek），对内提供稳定的调用入口。

## 职责

- 作为 `servers/generation-service` 唯一的 LLM 调用入口（内部契约提供方）。
- 持有 LLM 凭证，做鉴权透传、协议适配、超时 / 重试 / 限流。
- **保持"薄"**：不承载事件生成等业务逻辑。

## 启动

<!-- TODO：本地启动、依赖（Python 版本、虚拟环境）、环境变量（DeepSeek API Key 等，走密钥管理而非硬编码）。 -->

## AI 协作

入口见 [`CLAUDE.md`](CLAUDE.md)，须先读根 `CLAUDE.md` 与根 `rules/`。
