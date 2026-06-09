# 开发中自检 — servers/generation-service（栈特有补充）

> 继承根 [`../../../rules/development-guard.md`](../../../rules/development-guard.md) 的通用自检流程（对照物 / 六类清单 / 命中即停 / 输出格式）。
> 本文件**只列 servers/generation-service（Python 栈）特有的额外检查步骤**。

## 本服务特有检查

- LLM 调用是否一律经 `servers/ai-gateway`，没有任何直连 DeepSeek/其它 LLM 的旁路？
- 是否单方改动了已被 `servers/api` 依赖的既有事件契约？
- LLM 调用是否有超时 / 重试 / 成本上限？
- prompt 模板与日志是否泄露隐私或敏感数据？
- 类型注解 / lint（如 ruff / mypy）是否通过？

<!-- TODO（项目接入时可追加 Python 栈特有检查）。 -->
