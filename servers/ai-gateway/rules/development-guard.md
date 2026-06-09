# 开发中自检 — servers/ai-gateway（栈特有补充）

> 继承根 [`../../../rules/development-guard.md`](../../../rules/development-guard.md) 的通用自检流程（对照物 / 六类清单 / 命中即停 / 输出格式）。
> 本文件**只列 servers/ai-gateway（Python 栈）特有的额外检查步骤**。

## 本服务特有检查

- 凭证（DeepSeek API Key）是否走环境变量 / 密钥管理，代码与日志均无泄露？
- 是否保持"薄"——没有把事件生成等业务逻辑塞进网关？
- 是否擅自扩成多家 LLM 抽象层（当前应为单家 DeepSeek）？
- 是否单方改动了已被 `servers/generation-service` 依赖的既有对内契约？
- LLM 调用是否有超时 / 重试 / 限流，错误是否正确向上游透传？
- 类型注解 / lint（如 ruff / mypy）是否通过？

<!-- TODO（项目接入时可追加 Python 栈特有检查）。 -->
