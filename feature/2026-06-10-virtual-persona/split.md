# 拆分索引 + 契约指针 —— F1 首刀 A1

> feature：`2026-06-10-virtual-persona`｜本文件 = **F3 拆分索引**（A1 拆成哪些子项目任务）+ **指向权威契约的指针**。
> 总 spec 与设计理由见 [`spec.md`](spec.md)。**契约「是什么」不在 feature/**——只有一份机读权威源 = 各**提供方子项目**持有的 schema，本文件只放指针。
> 状态：F2 契约 schema 已落（见下）；F3 各子项目 spec/plan 待建（①–⑦ 在各子项目内进行）。本包 F4 集体定稿后整包 PR 进 main。

---

## 1. 契约指针（F2 产物，权威源在提供方子项目）

> 3 条契约均为 OpenAPI 3.1 YAML，**只含 A1 首刀字段**，与 spec §2 主链 / §4 数据模型一致。
> 防漂移靠**契约测试**：提供方验证实现符合 schema、消费方验证按 schema 调用（契约测试在各子项目 ①–⑦ 落）。

| 契约 | 方向 | 提供方（持 schema） | 消费方 | 权威 schema 路径 | validate |
|---|---|---|---|---|---|
| ① web↔api | 对外 REST | `servers/api` | `apps/web` | [`servers/api/contracts/web-api.openapi.yaml`](../../servers/api/contracts/web-api.openapi.yaml) | ✅ openapi-spec-validator OK |
| ② api↔gen | 内部 HTTP | `servers/generation-service` | `servers/api` | [`servers/generation-service/contracts/api-gen.openapi.yaml`](../../servers/generation-service/contracts/api-gen.openapi.yaml) | ✅ openapi-spec-validator OK |
| ③ gen↔ai-gateway | 内部 HTTP | `servers/ai-gateway` | `servers/generation-service` | [`servers/ai-gateway/contracts/gen-aigw.openapi.yaml`](../../servers/ai-gateway/contracts/gen-aigw.openapi.yaml) | ✅ openapi-spec-validator OK |

- **schema 归提供方子项目，不放 feature/**（本表只放指针，不复述路径以外的接口细节）。
- **已知 A1 契约空缺（非缺陷，刻意）**：契约未声明鉴权（spec §3.2「鉴权聚合的完整化 A1 不做」）。redocly recommended 的 `security-defined` 会就此报警——属预期，待鉴权刀落地时在契约①补 `security`。是否采用 redocly 作为项目 lint 工具留团队定（本期 validate 门 = openapi-spec-validator）。

---

## 2. 子项目 A1 任务拆分（①–⑦ 在各子项目内进行）

> 每个子项目只做 A1 必需的最小切片（spec §3）；专人专项、不跨边界。各自的 spec/plan/guard/review 在子项目内建（下方"子项目产物"为待建指针）。

### 2.1 `apps/web`（前端 · TS/React）
- **任务**：U0 创建表单（性格输入）；`navigator.geolocation` 取精确坐标 + **显式授权 UI**；U1 当天时间线列表渲染。
- **契约角色**：契约① **消费方**——按 schema 调 api，不直连 gen/高德/LLM。
- **高影响收口**：定位 PII → [`apps/web/src/*location*` / `*geo*`](../../rules/high-impact.paths)（落地自动生效）。
- **子项目产物（待建）**：`apps/web/spec/`、`apps/web/plan/`。

### 2.2 `servers/api`（对外服务 · Node/TS）
- **任务**：`POST /personas`（录入审核**首道** + 转交 gen + 落库 Persona/Place/Event + placeRef→placeId 解析）；`GET /personas/{id}/timeline`（当天有序事件）。**本期唯一持久层**。
- **契约角色**：契约① **提供方**；契约② **消费方**。
- **高影响收口**：性格录入审核 → [`servers/api/src/*persona*`](../../rules/high-impact.paths)（落地自动生效）。
- **子项目产物（待建）**：`servers/api/spec/`、`servers/api/plan/`。

### 2.3 `servers/generation-service`（生成引擎 · Python）
- **任务**：`POST /generate`（无状态）——性格复核（录入审核**第二道**）；高德逆地理取城市（精确坐标用后即丢）；home=城市代表点 + 高德 POI 落 1 place；**性格当数据**构建 prompt（不拼指令）；经 ai-gateway 生成诞生事件；返回 payload（**无存储、不铸 id**）。
- **契约角色**：契约② **提供方**；契约③ **消费方**（禁直连 DeepSeek）。
- **高影响收口**：prompt 构建 / 高德 key / 事件相关 → [`servers/generation-service/app/**`](../../rules/high-impact.paths)（`contracts/**` 已豁免，见 [gaps B12](../../docs/walkthrough/2026-06-09-virtual-persona-daily/gaps.md)）。
- **子项目产物（待建）**：`servers/generation-service/spec/`、`servers/generation-service/plan/`。

### 2.4 `servers/ai-gateway`（薄 LLM 代理 · Python）
- **任务**：`POST /v1/complete`——映射 systemInstruction/personality(数据槽)/realTime → 调 DeepSeek；**输出横切 guardrail**（第三层，注入回显/泄漏 prompt/不安全内容过滤，不解析业务字段）；持 LLM key。
- **契约角色**：契约③ **提供方**（gen 唯一 LLM 入口）。保持薄代理。
- **高影响收口**：provider 适配 / guardrails / LLM key / 限流 → [`servers/ai-gateway/app/**`](../../rules/high-impact.paths)（`contracts/**` 已豁免）。
- **子项目产物（待建）**：`servers/ai-gateway/spec/`、`servers/ai-gateway/plan/`。

---

## 3. 依赖顺序与并行（实施排程）

> 契约先行（F2）已完成，解耦了子项目实现——各子项目可按 schema **并行**起步，契约测试是各自防漂移的锚。

```
F2 契约①②③（已落，validate 绿）
        │  （三条 schema 已就位，下游解耦）
        ▼
┌──────────────── 可并行（按 schema 各自实现 + 契约测试）────────────────┐
│  web（消费①）   api（提供①/消费②）   gen（提供②/消费③）   ai-gateway（提供③）│
└────────────────────────────────────────────────────────────────────┘
        │  端到端联调按主链方向收敛：ai-gateway → gen → api → web
        ▼
端到端验收（spec §8；可执行细化见 acceptance.md，待建）
```

- **并行**：4 子项目实现无共享代码、各自契约测试对 schema → 可并行推进。
- **串行收敛点**：端到端联调按主链 `ai-gateway→gen→api→web` 自底向上拼（提供方先可用，消费方再联），但**不阻塞**各自单元 + 契约测试的并行开发。
- **关键路径**：gen（一肩挑契约②提供 + 契约③消费 + 高德 + prompt 当数据，含两道高影响），建议优先资源。

---

## 4. F4 评审落地（接受 / 记录项，不改契约结构）

> 完整纪要见 [`f4-review.md`](f4-review.md)。下列为裁决"接受现状 / 仅记录"的项，实施时须照此：

- **W-3（web）**：`location` 为 required，**定位被拒 = 无法创建**，A1 无手动选城兜底（合"真实浏览器定位"）；前端授权 UX 须明确告知"需定位方可创建"。
- **A-2（api）**：home Place 的 `type` 取**固定常量 `"home"`**（api 侧常量，非发明领域语义）；api 落库时把 gen 返回的 `home: Coordinate` 建成 home-type Place、`placeRef` 解析为真实 `placeId`。
- **G-1（gen，关键路径）**：api↔gen 同步 `/generate` 串高德逆地理 + 高德 POI + LLM，**时延偏高**；超时阈值留实现层定。**A1 重试非幂等、会重复消耗高德/LLM 配额**——已知取舍，幂等键见 [`spec.md` §10](spec.md)。
- **G-2（gen，乙·保留）**：A1 诞生事件落 home，高德 POI 检索的"1 休闲 place"**A1 暂不被事件引用**；**仍保留**——理由：穿透高德 POI 契约路径（dogfood 价值）+ 后续刀立即要用、免返工。

## 5. 关联

- F4 评审纪要：[`f4-review.md`](f4-review.md)
- 总 spec + 设计理由：[`spec.md`](spec.md)
- 需求定稿：[`requirement.md`](requirement.md)
- 端到端验收细化：`acceptance.md`（待建，随各子项目 ①–⑦ 落地）
- 契约演化候选：[`spec.md` §10](spec.md)（Event 存储归属：A1 api 落库 → 后续或转 gen 写共享存储）
- 治理回流：[gaps B12](../../docs/walkthrough/2026-06-09-virtual-persona-daily/gaps.md)（whole-dir 高影响收窄到 `app/**`、`contracts/**` 豁免）
