# F4 评审纪要 —— 首刀 A1 总 spec + 3 契约集体定稿

> feature：`2026-06-10-virtual-persona`｜阶段：F4 集体评审（4 子项目 owner 独立审 spec + 相关契约）。
> 仲裁机制：争议先求共识（**甲**）；僵持 → **提供方（后端）最终建议（乙）**。契约③ 的提供方 = ai-gateway，契约①②的提供方 = api / gen。
> 纪律：每帽须扮出**真实反对**（"我觉得都行"= 纸面过场）。下记**谁提了什么 · 怎么裁 · 落点**。
> 关联：[`spec.md`](spec.md)、[`split.md`](split.md)、契约 schema 见 split.md §1 指针。

---

## 1. web owner（消费 契约① web↔api）

### W-1【硬·阻断】U1 列表无法渲染「地点」——`Event.placeId` 不可解析
- **关切**：spec §2/§8 要 U1 渲染「时间 · **地点** · 在做什么」。但契约① 的 `Event` 只给 `placeId`（opaque），且 `CreatePersonaResponse = {persona, birthEvent}`、`TimelineResponse = {events}` **都不返回 Place**。前端拿到 `placeId` 无处解析 → **渲染不出地点**，验收 §8.3 落空。
- **裁决（甲 共识）**：响应补 `places[]`（该 persona 的 home + 1 休闲 place），前端按 `Event.placeId` 本地解析。Event 仍保持 normalized（`placeId`，合 spec §4），不在 Event 内冗余地点。**采纳 → 改契约①**。

### W-2【硬】请求收 `name`、响应 `Persona` 无 `name` → 设了显示不回来
- **关切**：`CreatePersonaRequest` 有可选 `name`，但 `Persona` schema 无 `name` 字段。前端填了名字却拿不回来显示，是契约内部不一致。
- **裁决（甲 共识）**：A1 三故事（U0/单次生成/U1）不依赖展示名 → **从 A1 契约删 `name`**（YAGNI；待 profile 展示刀再加）。消除不一致。**采纳 → 改契约①**。

### W-3【中·接受】定位被拒 = 无法创建（无手动城市兜底）
- **关切**：`location` 为 required，用户拒授权时 A1 无 fallback → 直接建不了 persona。
- **裁决（甲 共识·接受现状）**：合「真实浏览器定位」设定，A1 **不做**手动选城兜底；前端在授权 UX 里明确告知"需定位方可创建"。**不改契约**，纪要记录、split.md 标注。

### W-4【中·接受】精确坐标透传给后端，前端可接受但要求"用后即焚"对前端可见
- **关切**：前端把原始 GPS 交给 api 透传，需确保链路不留存。这是 PII 收口在 web 的延伸责任边界。
- **裁决（甲 共识）**：接受透传（§6.3 已定，为守高德 key 收口 gen）；要求 spec 明确**透传链上 api 亦不得记录**（见 A-3）。**触发 spec §5.3 澄清**。

---

## 2. api owner（提供 契约① · 消费 契约②）

### A-1【硬】录入审核"注入面首道"——语义注入检测该不该压 api？
- **关切**：api 是聚合/传输层（Fastify）。结构/长度校验认；但"注入特征 denylist"是**安全语义**，与 gen 的复核重复，放 api 是职责外扩。
- **裁决（甲 共识·划线）**：保留纵深防御两道，但**划清深浅**——api 首道 = **结构/长度 + 显式模式 denylist**（如"忽略以上指令"字面量，cheap、入口即拒）；**语义级**复核归 gen（§5.1 已分，确认不改契约，spec §5.1 微澄清深浅边界）。api owner 接受"只背 cheap 首道"。

### A-2【硬】存储归属全压 api：含 `placeRef→placeId` 解析 + 合成 home Place 类型
- **关切**：api 成唯一持久层认了；但 gen 返回 `placeRef=home|place`（逻辑键）、`home` 仅 `Coordinate`（无 type）→ api 要**铸 id + 解析 placeRef + 给 home Place 合成 type="home"**，是业务逻辑渗进"聚合层"。
- **裁决（甲 共识·接受 + 约定常量）**：A1 无并发，解析逻辑轻，api 接受。约定 home Place 的 `type` 取固定常量 `"home"`（api 侧常量，非 api 发明领域语义）。**不改契约②**（保持 gen 无存储不铸 id 的 §6.5 决策）；纪要记录该约定。

### A-3【硬】透传精确坐标 = api 也得 scrub 日志
- **关切**：Fastify 默认请求/错误日志可能落 body → 精确坐标入 access/error log，违 PII"不入日志"。spec 只笼统写"不入日志"未点名 api。
- **裁决（甲 共识）**：**spec §5.3 明确**——透传一手的 api 与取数的 gen **均**不得记录精确坐标（access log / error log / trace 同）。api owner 据此在实现侧关 body 日志 / 脱敏。**触发 spec §5.3 改**。

---

## 3. gen owner（提供 契约② · 消费 契约③）— 关键路径

### G-1【硬】同步 `/generate` 串 3 个慢外部（逆地理 + POI + LLM）→ 时延/超时 + 重试重复烧钱
- **关切**：一次同步调用里串高德逆地理、高德 POI、ai-gateway→DeepSeek，整体可能数秒～十几秒；api 同步阻塞等待。更糟：**无幂等键**，api 超时重试 → gen 重跑高德（耗配额）+ 重跑 LLM（花钱）。
- **裁决（甲 共识·接受 A1 + 记演化）**：A1 无并发/无自调度（§7），同步最简、可接受；**纪要 + split.md 明确**：api↔gen 超时阈值留实现层定，**A1 重试非幂等、会重复消耗高德/LLM 配额**，是已知取舍。**幂等键**列入 [spec §10 契约演化候选](spec.md)（与并发刀一起落）。**触发 spec §10 增行 + split.md 记录**。

### G-2【硬】A1 诞生事件落在 home，那 POI 检索的"1 休闲 place"在 A1 是死重
- **关切**：诞生事件（"刚来到这座城市"）`placeRef` 基本是 `home`；可休闲 `place` 由一次高德 POI 检索得来却**无任何 A1 事件用到**——在关键路径上白搭一次高德调用 + 时延。YAGNI 该砍？
- **裁决（乙 提供方兜底）**：gen 是契约②提供方，但此点牵动产品"落在真实城市地图"内核 + 走查目标"穿高德 POI 契约路径"。**共识不全拢**（gen 要砍、产品要留）→ 升**乙**：后端（gen 作为②提供方）最终建议 = **保留**。理由：① 首刀刻意要**穿透**高德 POI 这条线（dogfood 价值，requirement §14 压力源）；② place 是后续刀（自链/移动）立刻要用的最小落点，A1 建好免返工。**代价记录**：A1 该 POI 调用"建而暂不被事件引用"。**不改契约**，纪要 + split.md 记理由。

### G-3【中·接受】高德 key + 逆地理 + 性格复核 + prompt 当数据 全压 gen
- **关切**：gen 一肩挑两道高影响（注入面第二层 + 高德 key）+ 关键路径，资源吃紧。
- **裁决（甲 共识·接受）**：合 spec §3.3/§5 收口设计；split.md §3 已标 gen 为**关键路径、建议优先资源**。压力认下、不改契约。

---

## 4. gateway owner（提供 契约③ gen↔ai-gateway）

### GW-1【硬·F1 跨文档张力落槌】§6.4 输出审核"通用横切"——边界守得住吗？
- **关切**：即便是"通用 guardrail"，"检测泄漏 prompt / 不安全内容"也要**某种内容判断**；今天是 denylist，明天就被要求查"事件是否连贯"——滑向业务，破"薄"。
- **裁决（乙 提供方兜底 = gateway）**：契约③ 提供方 = ai-gateway，僵持由其兜底。gateway owner **认 §6.4 定性**，但加**两条硬约束写进 spec**：
  1. **block-only**：guardrail 命中 → **422 拒绝**，**不做静默改写/脱敏**（改写 = 篡改业务产出 = 向业务滑）；
  2. **固定机械映射**：`systemInstruction→系统角色 / personality→数据消息 / realTime→上下文` 是**写死的槽位映射**，gateway **不按内容做分支判断**。
  越此即非本层、回 §6 暂停。**触发 spec §6.4 增补两条约束**（契约③ 描述同步点一句）。

### GW-2【硬】"性格当数据"分立字段 vs 直接收 messages——谁拼 prompt？
- **关切**：契约③ 收 `{systemInstruction, personality, realTime}` 三分立字段、由 gateway 拼装 → 拼装是 prompt 构建（业务，§5.1 落点本是 gen）。gateway 倾向只收已组装的 `messages[]`、自己只做协议适配 + guardrail（更"薄"）。
- **裁决（甲 共识，乙 确认）**：权衡——
  - 选 messages[]：gateway 最薄，但"性格当数据 vs 指令"的物理分离**移出契约、不可见**，§5.1 的可审计性丢失；
  - 选分立字段（现状）：分离在**契约层可见可审计**，代价是 gateway 做一次**固定槽位映射**。
  **取分立字段**（现状），并由 GW-1 第 2 条把映射钉死为"机械、不按内容判断"→ gateway 不构成业务拼装，"薄"得以守。gateway owner 接受。**不改契约③ 结构**（仅 GW-1 描述补强）。

---

## 5. 裁决汇总与落点

| 编号 | 提出帽 | 裁决 | 落点 |
|---|---|---|---|
| W-1 | web | 甲·采纳 | 改契约①：响应补 `places[]` + 新增 `Place` schema |
| W-2 | web | 甲·采纳 | 改契约①：删 `CreatePersonaRequest.name` |
| W-3 | web | 甲·接受 | 纪要 + split.md（定位拒 = 不可创建，无兜底） |
| W-4/A-3 | web/api | 甲·采纳 | 改 spec §5.3：api 透传亦不得记录精确坐标 |
| A-1 | api | 甲·划线 | spec §5.1 微澄清"api 首道=结构+显式模式；gen=语义" |
| A-2 | api | 甲·接受 | 纪要（home Place type 取常量 `"home"`，不改契约②） |
| G-1 | gen | 甲·接受+记演化 | spec §10 增"同步生成幂等键"演化行 + split.md 记非幂等取舍 |
| G-2 | gen | **乙·保留** | 纪要 + split.md 记理由（穿高德 POI / 免返工；A1 暂不被事件引用） |
| G-3 | gen | 甲·接受 | 已在 split.md §3（关键路径优先资源） |
| GW-1 | gateway | **乙·认定性+加约束** | 改 spec §6.4：block-only + 固定机械映射；契约③ 描述补一句 |
| GW-2 | gateway | 甲·取分立字段 | 不改契约③ 结构（由 GW-1#2 钉死映射） |

**契约改动**：仅契约①（places[] / Place / 删 name）+ 契约③ 描述补强。契约② 不改结构。
**spec 改动**：§5.1（划线）、§5.3（api 不记录）、§6.4（block-only + 机械映射）、§10（幂等键演化行）、§2/§8 渲染口径随 places[] 对齐。

> 定稿状态：4 帽独立审毕，争议均落甲/乙裁决；据此微调 spec + 契约后即为 F4 定稿版（仍 feature 分支，不 PR）。
