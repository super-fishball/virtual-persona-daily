# 额外禁止项 — servers/ai-gateway

> 继承根 [`../../../rules/forbidden.md`](../../../rules/forbidden.md) 全部条款，以下为 servers/ai-gateway 额外约束（只增不减）。

- 禁止单方变更**已被 `servers/generation-service` 依赖的既有对内契约**（须经 feature 层集体定稿）。
- 禁止在代码 / 日志 / 仓库中硬编码或泄露 **DeepSeek API Key** 等凭证（走环境变量 / 密钥管理）。
- 禁止在网关层堆叠**业务逻辑**（保持"薄"——只做鉴权透传 / 协议适配 / 限流 / 凭证，不做事件生成业务）。
- 禁止擅自扩成**多家 LLM 抽象层**（当前单家 DeepSeek；多家是后续 feature 决策）。
- 禁止在日志中输出完整 prompt / 响应等可能含隐私或敏感数据的内容。

<!-- TODO（项目接入时可追加）。 -->
