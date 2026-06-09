# 高影响区 — apps/web

> 继承根 [`../../../rules/high-impact.md`](../../../rules/high-impact.md) 的判定标准，此处只列 apps/web 本地的高影响区。

## 本地高影响类目

- 认证 / 会话相关的前端逻辑（登录态、token 存储、路由守卫）。
- 与支付 / 金额展示相关的组件。
- 全局状态管理、底层请求封装（影响面广）。
- 构建配置、路由表、权限控制组件。

## 具体路径

<!-- TODO（项目接入时填写）：
- apps/web/src/auth/**
- apps/web/src/router/**
- apps/web/src/api/**（请求封装）
-->
