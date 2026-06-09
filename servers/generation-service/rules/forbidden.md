# 额外禁止项 — servers/generation-service

> 继承根 [`../../../rules/forbidden.md`](../../../rules/forbidden.md) 全部条款，以下为 servers/generation-service 额外约束（只增不减）。

- 禁止单方变更**已被 `servers/api` 依赖的既有事件契约**（须经 feature 层集体定稿）。
- 禁止**绕过 `servers/ai-gateway` 直连 DeepSeek 或任何 LLM**（所有模型调用一律经内部网关）。
- 禁止在代码 / 日志 / 仓库中硬编码或泄露任何 LLM 凭证（凭证由网关持有，本服务不应接触）。
- 禁止在日志中输出敏感数据或含隐私的完整 prompt / 生成内容。
- 禁止引入无超时 / 无成本上限的 LLM 调用（避免失控的调用量与费用）。

<!-- TODO（项目接入时可追加）。 -->
