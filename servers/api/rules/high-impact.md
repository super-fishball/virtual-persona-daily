# 高影响区 — servers/api

> 继承根 [`../../../rules/high-impact.md`](../../../rules/high-impact.md) 的判定标准，此处只列 servers/api 本地高影响区。

## 本地高影响类目

- 认证授权、token 签发与校验。
- 支付 / 计费 / 对账逻辑。
- 数据库 schema 与迁移（难回滚）。
- 对外 API 契约（被 apps/* 依赖）。
- 事务边界、并发控制、限流熔断。

## 具体路径

<!-- TODO（项目接入时填写）：
- servers/api/src/auth/**
- servers/api/src/billing/**
- servers/api/migrations/**
- servers/api/src/api/**（对外契约定义）
-->
