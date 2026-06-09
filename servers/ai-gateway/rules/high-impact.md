# 高影响区 — servers/ai-gateway

> 继承根 [`../../../rules/high-impact.md`](../../../rules/high-impact.md) 的判定标准，此处只列 servers/ai-gateway 本地高影响区。

## 本地高影响类目

- 对内契约（被 `servers/generation-service` 依赖的调用入口）。
- LLM provider 凭证的持有与使用（DeepSeek API Key）。
- 超时 / 重试 / 限流 / 熔断（直接影响上游稳定性与成本）。
- "薄代理"边界：任何向网关引入业务逻辑、或扩成多家 LLM 抽象的改动。

## 具体路径

<!-- TODO（项目接入时填写）：
- servers/ai-gateway/src/contracts/**（对内契约定义）
- servers/ai-gateway/src/provider/**（DeepSeek 适配与凭证使用）
- servers/ai-gateway/src/ratelimit/**（限流 / 熔断）
-->
