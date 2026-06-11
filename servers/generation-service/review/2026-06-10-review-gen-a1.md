# 独立评审报告 —— A1 generation-service（事后补做的 ⑦）

> ⚠️ **本报告是事后补做的工作流第 ⑦ 步（独立评审）。PR #5（`8bc780a`）已先合并进 `main`，本评审在合并之后冷读复核，非合并门禁。**
> 评审者立场：PR #5 的事后独立评审者，冷读、带怀疑，不参与原实现。
> 评审范围：仅 `servers/generation-service/`（`app/` + `tests/`），不跨子项目。
> 评审基线（git）：`main @ 8bc780a`；评审分支 `review/2026-06-11-gen-a1`。
> 评审方法：逐文件冷读 + 对照三份权威文件 + 实跑测试套件（`41 passed`）+ 对关键缺陷做独立复现（见 F-1）。

## 对照的权威文件

| 角色 | 文件 | 版本 |
|---|---|---|
| spec（gen 视角） | [`../spec/2026-06-10-spec-gen-a1.md`](../spec/2026-06-10-spec-gen-a1.md) | A1 |
| 契约②（我提供，对 api） | [`../contracts/api-gen.openapi.yaml`](../contracts/api-gen.openapi.yaml) | 0.1.0-a1 |
| 契约③（我消费，对 ai-gateway） | [`../../ai-gateway/contracts/gen-aigw.openapi.yaml`](../../ai-gateway/contracts/gen-aigw.openapi.yaml) | 0.1.1-a1 |

评审定的 F1–F4：F1 市级 adcode、F2 catch-all、F3 POI keywords、F4 单一 clock 锚点。

---

## 总体结论

实现整体**忠实于 spec 与契约**，结构清晰、关注点分离到位；**PII / 凭证收口这一最高影响区做得扎实且有真实测试守门**（见专项判断·安全）。错误码映射表逐行落地，对外只吐 400/502，契约②③字段映射严格。

但有 **2 个重要缺陷**未被现有测试覆盖：① 午夜末分钟 `end ≤ start`（负/零时长事件，已实跑复现）；② 直辖市市级 adcode 派生不正确且单测给了假信心。无阻断级（无安全泄漏、无契约破坏）发现。

| 严重度 | 数量 | 编号 |
|---|---|---|
| 阻断 | 0 | —— |
| 重要 | 2 | F-1、F-2 |
| 次要 | 7 | F-3 ~ F-9 |

---

## 阻断（Blocking）

**无。** 明确记录：未发现 PII / 高德 key 泄漏、未发现绕过网关直连、未发现契约②③破坏、未发现对外吐 400/502 之外的响应。PII/凭证一项实现质量高于平均（见安全专项）。

---

## 重要（Important）

### F-1 · 午夜末分钟生成 `end ≤ start`（负时长 / 零时长事件） · `app/assemble.py:21-23`

**现象（已实跑复现）**：`end_of_day = start.replace(hour=23, minute=59, second=0, microsecond=0)` 把秒/微秒抹零，但 `start = now`（`service.py:24` 的 `datetime.now(tz=CN_TZ)`）带真实秒/微秒。当请求落在任意一天的 `[23:59:00, 24:00:00)`（每天 60 秒窗口）：

```
start=2026-06-10T23:59:30+08:00  end=2026-06-10T23:59:00+08:00  dur=-0.50min  end>=start=False
start=2026-06-10T23:59:00+08:00  end=2026-06-10T23:59:00+08:00  dur= 0.00min  end>=start=True
```

即 `end < start`（负时长）或 `end == start`（零时长）的诞生事件。

**为什么是缺陷而非"已接受的罕见场景"**：spec §9·⑤ 的午夜优先级裁决明确接受 `end < 15min`，但其语义前提是 `end ≥ start`（"时长可小于 15 分钟"）。`end < start` 是**语义非法**的事件（结束早于开始），不在裁决接受范围内。契约② `EventPayload` 虽未显式约束 `start < end`，但下游 `api` 落库 / `web` 渲染时间线很可能据此假设，负时长是脆弱点。

**根因**：`end_of_day` 用了抹零后的 23:59:00 作为"当日上界"，当 `start` 本身已在 23:59:xx 区间时上界反而早于 `start`。`assemble_birth_event` 的 `now` 参数可注入，缺陷在函数内部，与高德/LLM 无关。

**测试为何漏掉**：见 F-7（assemble 测试只用整分钟）。

**严重度 重要**：每天 60 秒窗口（约 0.07%）必现，产出语义非法事件；非阻断仅因 A1 单次低频且仅诞生事件。建议修法方向（不在本评审改）：上界用 `min(end, start_当日23:59:59)` 且兜底 `end = max(end, start)`，或上界取当日真实末刻而非抹零的 23:59:00。

---

### F-2 · 直辖市"市级 adcode"派生为市辖区码，且单测给假信心 · `app/amap.py:56`

**现象**：`city_adcode = adcode[:4] + "00"`。对普通地级市正确（杭州上城区 `330102` → `330100` 杭州市 ✓）。但对 **4 个直辖市**，市级 adcode 形如 `XX0000`（北京 `110000`、上海 `310000`），而 `[:4]+"00"` 得到的是**市辖区伪码** `110100` / `310100`，**不是**直辖市本身的 adcode。

**两个风险**：
1. **可能 502（影响全体直辖市用户）**：`representative_point`（`amap.py:59-68`）拿 `110100`/`310100` 去查 `/v3/config/district`，若高德对该市辖区伪码不返回 `center`，则命中 `amap.py:65-66` → 502 `upstream_unavailable`，**北京/上海/天津/重庆全部用户的 `/generate` 失败**。
2. **代表点偏移**：即便能解析，取到的是"市辖区"质心而非直辖市质心，与"城市代表点"语义略偏。

**单测给了假信心** · `tests/test_amap.py:31-43`：`test_regeo_municipality_fallback` 仅断言**派生出的字符串** `city_adcode == "110100"`，**没有**验证高德真能把 `110100` 解析成可用 `center`（`representative_point` 的 district mock 是另一个用例 `:48-59`，用的是 `310100` + 硬编码 center）。两者拼不出"直辖市端到端可用"的证据。

**严重度 重要（含不确定性）**：能否复现 502 取决于高德 `/v3/config/district` 对 `XX0100` 伪码的真实行为，**本评审无 key、未能实地验证**。诚实标注：这是"高风险但需实测确认"的发现。建议方向：直辖市（province ∈ {11,12,31,50}）特判 `XX0000`，并补一条**真打高德**或更贴真的直辖市端到端用例。

---

## 次要（Minor）

### F-3 · httpx 客户端未复用，每次调用新建 `AsyncClient` · `app/amap.py:30`、`app/aigw.py:25`
单次 `/generate` 内，高德要发 3–5 个请求（regeo 1 + district 1 + POI 1~3），每个 `_get` 都 `async with httpx.AsyncClient(...)` 新建连接池 + 重做 TCP/TLS 握手；aigw 亦每请求新建。无跨调用/跨请求连接复用。A1 低频下功能无碍，但属 httpx 反模式（官方建议复用 client），徒增握手时延。建议：`AmapClient`/`AigwClient` 持有长生命周期 `AsyncClient`（或 app 级共享 + lifespan 关闭）。任务点名"httpx 复用"，据此列出。

### F-4 · 高德错误/空结果分支大面积无测试 · `app/amap.py:40-41,52-53,65-66,89`
仅 HTTP 500 路径有测试（`test_amap.py:85-92` / `test_generate.py:77-92`）。**未覆盖**：① 高德返回 HTTP 200 + `status != "1"`（业务失败，`amap.py:40-41`，任务点名的"高德非 1 status"）；② regeo 不完整 `not city or len(adcode)!=6`（`:52-53`）；③ district 空 `districts==[]`（`:65-66`）；④ POI 全 keyword 落空 `poi not found`（`:89`）。这些分支都汇流到同一个"502 + 无 PII"行为（该行为已被 500 路径测过），故定**次要**；但 spec §8 验收要求错误路径可验，且这些是"下游不可用→502"的契约保证点，建议各补一条 respx 用例。

### F-5 · aigw-400"内部告警不可静默"未被断言；aigw 错误路径无泄漏回归测试 · `app/aigw.py:38-41`、`tests/test_aigw.py:46-54`
spec §6.3 规定契约③返回 400（gen 自造请求 bug）时对外 502 **且内部告警（不可静默）**。`test_other_codes_map_502_upstream_unavailable[400]` 只断言 status/code，**没断言 `logger.error` 真被调用**——"不可静默"这条无回归守门（catch-all 的日志在 `test_errors.py:41-47` 测了，但 aigw-400 这条专属告警没测）。另：amap 有两条专门的"错误路径不泄漏 PII/凭证"测试，aigw 错误路径一条都没有（风险更低，见安全专项，但缺少守门）。

### F-6 · `assemble` 的 `_MIN`/`_MAX` 钳制为死代码 · `app/assemble.py:16-19`
`_DEFAULT=60min` 固定，恒在 `[15min, 4h]` 内，故 `if end-start < _MIN` 与 `> _MAX` 两个分支**永不触发**。是为"未来时长可变"预留的脚手架，当前无效、也无测试能触达。非缺陷，记为可读性/覆盖率噪声。

### F-7 · assemble 测试只用整分钟，系统性漏掉 F-1 · `tests/test_assemble.py:6-7`
`_at(h, m)` 构造的 `datetime` 秒/微秒恒为 0，于是三条午夜用例（含 `23:50`）都验不到生产里 `datetime.now()` 必带的秒级精度——正是 F-1 藏身处。属"测试输入迁就了实现的乐观假设"，给出假绿。建议补 `23:59:30` 一类秒级用例。

### F-8 · `prompt.py` 用 `assert` 守安全不变量，`python -O` 下被剥离 · `app/prompt.py:26`
`assert personality not in system_instruction` 是"性格不入指令"的防御性自检（spec §6.1 要求"断言+单测"）。但 `assert` 在 `-O` 优化模式下被剥离。所幸真正的结构保证来自模板只 `format(city, place_type)`、根本不接 personality（`prompt.py:25`），故剥离后分离仍成立，风险低。记一笔：安全不变量长期不宜只靠 `assert`。

### F-9 · 两处无害但易误解的写法
- `app/main.py:24` `response_model_by_alias=True`，但 `schemas.py` 未定义任何 alias（字段名本就是 camelCase），该参数实为 no-op。
- `app/amap.py:50` city 回退只做 `city → province`，spec §9·④ 字面写的是"city 空 → district/province"。代码跳过 district：对直辖市 `province="北京市"` 才是正确市名（district 会得"东城区"，错），故此处**偏离即更正确**，记为良性偏离、无需动作，仅作可追溯标注。

---

## 专项判断（对任务五问的逐条回应）

### 1. 契约符合 —— 通过
- **响应体**：`GenerateResponse{city,home,place,birthEvent}`、`EventPayload{start,end,placeRef(enum home/place),content,statusTag}`、`PlacePayload{type,coordinate}`、`Coordinate{lng,lat}` 全部对齐契约②；`schemas.py` 用 `extra="forbid"` 对齐 `additionalProperties:false`，字段名即 camelCase，序列化无漂移。契约测试 `test_contract.py` 用 jsonschema 拿真 OpenAPI 校验响应，是真正的防漂移。
- **错误体**：`errors.py:24-25` 只产 `{code,message}`，对齐契约② `Error`。
- **对外错误码**：穷举所有抛出点，gen **只对外 400/502**（review→400、校验→400、amap→502、aigw 422→502、aigw 400/500/502/超时→502、catch-all→502），契约②只声明这两类，吻合。
- **对 ai-gateway 调用与字段映射**：`aigw.py:19-23` 发 `{systemInstruction, personality, realTime}` = 契约③ `CompletionRequest` required 三字段；`systemInstruction` 非空（模板）、`personality ≤500 < 4000`、`realTime` 为 `isoformat()` 的 RFC3339 date-time。响应 `resp.json()["text"]` 对齐 `CompletionResponse.text`；200 缺 text → KeyError → catch-all → 502（`errors.py:43` 注释已预期）。错误码映射表（spec §6.3）逐行落地且正确。

### 2. 安全 / PII —— 通过，且独立判断 amap/aigw 的异常链处理**确实安全**
- **精确坐标用后即弃**：`req.location` 仅传入 `amap.regeo_city`（`service.py:20`），之后链路只用 `city/adcode/home`，精确坐标不再出现、不入任何后续入参。POI 围绕 `home`（代表点）检索，绝不用精确坐标（`amap.py:70-89` + `test_amap.py:79-80` 断言）。✓
- **不入日志**：`main.py:13` 把 `httpx` logger 压到 WARNING（httpx 默认 INFO 会打印含坐标的请求 URL）；`test_precise_location_not_logged` 真验。✓
- **高德 key 收口/不泄漏**：key 仅 `config.py` 经环境注入、无硬编码；进每个高德请求的 query（`amap.py:28`）但 URL 不入日志；错误 message 全为静态串（"amap unavailable"等），不回显 key/坐标。✓
- **amap `from None` 修法（`amap.py:34-39`）——正确且必要**：高德请求 URL 内嵌**精确坐标 + key**，httpx 异常的 str/repr 携带该 URL。若用 `from exc` 串入异常链，off-box 捕获（Sentry/APM）或框架 `exc_info` 渲染异常链就会泄漏 PII+凭证。`from None` 断链 + 只记 `type(exc).__name__` 是对的，且有结构级测试 `test_amap_error_does_not_chain_url_bearing_exception` 在异常源头守门（不靠日志回归）——质量很高。✓
- **aigw `from exc` 未修（`aigw.py:29`）——独立判断：安全**。理由：① aigw URL = `http://localhost:8001/v1/complete`，**无 key、无坐标**（网关自持 LLM key，gen 不传任何凭证/鉴权头）；② 敏感的 `personality` 在 **POST body**，而 httpx 异常的 str/repr **不含请求体**（且 aigw 从不 `raise_for_status`，4xx/5xx 走手动 status 分支、不产 `HTTPStatusError`，except 只接住传输层 `RequestError`，其 repr 至多含非敏感的内网 URL）。故 `from exc` 不会泄漏 PII/凭证，反而保留诊断链，**是合理的不对称处理**——amap 因 URL 敏感必须断链，aigw 因 URL 无害可保链。⚠️ 残留前提：此结论依赖 `aigw_base_url` 永不带 URL 凭证（今天成立）；且 aigw 侧缺 amap 那样的"不泄漏"回归测试（见 F-5），安全靠分析非靠测试，建议补一条守门或注释固化。
- **其他泄漏面**：prompt 的 `systemInstruction` 只含 city/place_type（系统派生事实，非用户自由文本），不入日志；catch-all 只记 `type(exc).__name__`（`errors.py:47`），不记 exc 消息；错误响应体全静态。未见 prompt/坐标/key 经响应或日志外泄。
- 残留考量（非缺陷）：catch-all 命中时 Starlette 会在生成 502 后重抛、由 uvicorn 记 traceback；但本服务内"携带精确坐标的异常"只存在于 amap `_get` 的 try 内且恒被 `from None` 收口，不会到达 catch-all，故此路径不泄漏 PII。

### 3. 测试真实性 —— 整体真测行为，非套套逻辑
- respx 真模拟 HTTP、断言解析后的输出 / 请求参数 / 状态码 / 日志内容；PII 测试为结构级（查 `__cause__`、caplog），且刻意规避"测试源码字面坐标"造成的假阳（`test_amap.py:107-113` 注释）——成熟、可信。
- 契约测试用真 OpenAPI schema 校验，防漂移有效。
- 错误映射表（spec §6.3）基本逐行覆盖。
- **真实性短板**：F-7（assemble 测试整分钟、迁就实现的乐观假设，漏 F-1）、F-2（直辖市单测只验派生串、不验高德可解析，假信心）、F-4（高德错误/空结果分支基本无测）、F-5（aigw-400 告警与 aigw 泄漏面无守门）。`test_schemas.py:35-48` 的 `test_response_serializes` 偏 smoke、略套套，但无害。
- **边界覆盖盘点（任务点名项）**：高德非 1 status ✗未覆盖；超时——aigw ✓（`test_timeout`，且断言 `call_count==1` 验不重试）/ amap ✗无显式超时用例（但与 500 同路径，行为等价）；空结果 ✗未覆盖；超长 base64 ✓（`test_review.py:14`）。

### 4. spec 符合 / F1–F4 —— 未发现偷偷偏离，唯 F1 直辖市处理有缺陷
- **F1 市级 adcode**：思路落地（`amap.py:54-56` 区级→市级），但直辖市派生错误，见 **F-2**。
- **F2 catch-all**：`errors.py:41-51` 兜底 Exception→502，`test_errors.py:41-47` 验，✓。
- **F3 POI keywords**：`amap.py:12,72-78` 用 `keywords`（咖啡馆/公园/书店）而非类目码，label 兼作对外 type，对齐 F3 决策（注释亦标 F3），✓。
- **F4 单一 clock 锚点**：`service.py:24` 一次取 `now`，同时喂 `realTime`（`:27`）与 `assemble`（`:33`），realTime/start 同锚点，✓。
- 性格当数据/不拼指令（spec §6.1/§9·②）：`prompt.py` 模板只 `format(city, place_type)`，personality 只走数据槽，✓（`test_prompt.py` 双向验）。realTime 走专属字段、不入 systemInstruction，✓。
- 录入审核第二道（§9·③）：`review.py` 结构化启发式（角色标记/分隔符/base64 blob/控制字符），命中即 400，非 denylist 非 ML，对齐裁决，✓。
- 无状态/不铸 id、placeRef=home(G-2)、statusTag 固定、start=此刻 UTC+8、LLM 只产 content：均符合 §9·⑤，✓。
- 超时>30s 不重试（§6.2）：`config.py:16` aigw 35s，`aigw.py` 无重试，`test_config.py:11`/`test_aigw.py:66` 守门，✓。

### 5. 健壮性
- 输入校验：pydantic 严格（`extra=forbid` + 范围 + 长度），对齐契约②，✓。
- 502 映射：齐全，✓。
- 异常处理：catch-all 兜底防吐契约外响应，✓；但高德响应形状解析有硬索引 `data["regeocode"]["addressComponent"]`（`amap.py:49`），异常形状靠 catch-all 兜成 502（设计如此，可接受，但不如显式）。
- httpx 复用：未复用，见 **F-3**。
- 时间钳制：`end ≤ start` 缺陷，见 **F-1**；死钳制见 F-6。

---

## 是否需要人工确认

**需要。** 命中本子项目高影响区：
- **对 api 的对外事件契约**：F-1 产出语义非法（`end ≤ start`）的 `birthEvent`，影响契约②消费方 `servers/api` 的落库/渲染假设——需人裁定修复优先级。
- **网关消费契约 / 直连**：未发现绕过网关、未发现直连 DeepSeek（唯一 LLM 入口 = `aigw.py` 经契约③）。✓
- **核心 prompt / 注入面**：性格当数据分离成立（F-8 的 `assert` 提醒为次要）。
- 本评审**未改动任何代码与契约**，仅新增本报告。

---

## 下一步建议（按优先级，均待人工裁决，本评审不改码）

1. **F-1**：修午夜上界算法（`min(end, 当日真实末刻)` 且兜底 `end ≥ start`），补秒级午夜用例。
2. **F-2**：直辖市特判市级 adcode（`XX0000`）；补"真打高德"或更贴真的直辖市端到端用例，确认 `/v3/config/district` 对直辖市的真实返回。
3. **F-4 / F-5**：补高德错误/空结果分支（非 1 status、regeo 不完整、district 空、POI 落空）与 aigw-400 告警/泄漏面的回归用例。
4. **F-3**：复用 httpx client。
5. F-6 / F-8 / F-9：可读性与防御性收尾，低优先。

---

## 已查文件清单（评审证据，无任何改动）

- `app/`：`main.py`、`service.py`、`amap.py`、`aigw.py`、`prompt.py`、`review.py`、`assemble.py`、`errors.py`、`schemas.py`、`config.py`
- `tests/`：`test_amap.py`、`test_aigw.py`、`test_generate.py`、`test_assemble.py`、`test_contract.py`、`test_errors.py`、`test_prompt.py`、`test_review.py`、`test_schemas.py`、`test_config.py`、`test_health.py`
- 权威对照：spec、契约②、契约③（见顶部表）
- 实跑：`AMAP_KEY=dummy uv run pytest -q` → **41 passed**；`assemble_birth_event` 午夜秒级复现（F-1 证据）

---

> **AI 参与声明**：本报告由 AI（本会话）作为 PR #5 的事后独立评审者，冷读 `servers/generation-service/` 代码与测试、对照三份权威文件、实跑测试与复现关键缺陷后撰写。**全程只评审、只写本报告，未改动任何代码 / 测试 / 契约。** AI 永不作为合并门禁；findings 的处置与优先级由人裁决。
