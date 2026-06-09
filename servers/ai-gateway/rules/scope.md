# 可修改范围与边界 — servers/ai-gateway

## 可改

- `servers/ai-gateway/` 内的源码、provider 适配 / 调用配置、测试、本服务文档。

## 不可改（跨边界）

- 任何 `apps/*`、其他 `servers/*`、根 `rules/`、根 `context/`。
- **既有的对内契约**（已被 `servers/generation-service` 依赖）——不得单方变更，须经 feature 层集体定稿。

## 越界处理

发现任务需要改动 `servers/ai-gateway` 之外、改动既有对内契约、在网关层堆叠业务逻辑、或扩成多家 LLM 抽象层 → **暂停**，走 feature 层或转交对应负责人。

<!-- TODO（项目接入时可细化）。 -->
