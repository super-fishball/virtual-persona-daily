# 可修改范围与边界 — servers/generation-service

## 可改

- `servers/generation-service/` 内的源码、生成逻辑 / prompt 模板、测试、本服务文档。

## 不可改（跨边界）

- 任何 `apps/*`、其他 `servers/*`、根 `rules/`、根 `context/`。
- **既有的对外事件契约**（已被 `servers/api` 依赖）——不得单方变更，须经 feature 层集体定稿。
- **与 `servers/ai-gateway` 的消费契约**——只能按网关既定契约对接，需求变更回 feature 层。

## 越界处理

发现任务需要改动 `servers/generation-service` 之外、改动既有对外契约、或绕过网关直连 LLM → **暂停**，走 feature 层或转交对应负责人。

<!-- TODO（项目接入时可细化）。 -->
