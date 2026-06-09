# 高影响区 — servers/generation-service

> 继承根 [`../../../rules/high-impact.md`](../../../rules/high-impact.md) 的判定标准，此处只列 servers/generation-service 本地高影响区。

## 本地高影响类目

- 对外事件契约（被 `servers/api` 依赖）。
- 与 `servers/ai-gateway` 的消费契约（调用协议 / 请求响应结构）。
- 核心生成逻辑与 prompt 模板（直接影响输出质量与成本）。
- LLM 调用的并发 / 重试 / 成本控制（影响费用与上游稳定性）。

## 具体路径

<!-- TODO（项目接入时填写）：
- servers/generation-service/src/contracts/**（对外事件契约定义）
- servers/generation-service/src/prompts/**（prompt 模板）
- servers/generation-service/src/generation/**（核心生成逻辑）
-->
