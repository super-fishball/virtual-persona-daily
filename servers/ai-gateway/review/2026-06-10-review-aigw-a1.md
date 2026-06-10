# review —— ai-gateway · A1 plan 独立评审（③ 评审讲解）

> 性质：**①–⑦ 的 ③ 评审讲解**，非 PR 前 diff 自检。审阅对象 = [`../plan/2026-06-10-plan-aigw-a1.md`](../plan/2026-06-10-plan-aigw-a1.md)（②）对照 [`../spec/2026-06-10-spec-aigw-a1.md`](../spec/2026-06-10-spec-aigw-a1.md)（①）+ 契约③ [`../contracts/gen-aigw.openapi.yaml`](../contracts/gen-aigw.openapi.yaml)。
> **视角（刻意换帽，不做 owner 自放行）**：戴 **`servers/generation-service`（契约③ 消费方）帽 + 安全镜头**（ai-gateway 是高影响 guardrail/key 服务）。
> 纪律：真写反对，不橡皮图章。**本评审不进 ④**；结论报牵头人裁。

---

## 1. 对照结论（速览）

plan 结构齐（6 文件 / 7 TDD 任务 / 验收对照表），机械映射、block-only、key env、单家 DeepSeek 边界**守住**（§4 逐条正面确认）。但从消费方 + 安全视角发现 **4 条阻断/重要 + 3 条次要**，其中 **C1（请求校验错误体不符契约）** 与 **C2（prompt_leak 规则与测试互相迁就）** 是真实削弱，**建议 ④ 前回炉改 plan**。

| 级别 | 编号 | 一句话 |
|---|---|---|
| 阻断 | C1 | 请求校验 422 体 = FastAPI 默认 `{detail}`，**不符契约③ Error `{code,message}`**，gen 接不住 |
| 阻断 | C2 | `prompt_leak` 只匹配**整条** systemInstruction 逐字回显；spec 要的是**片段**——测试正好回显整条，互相迁就 |
| 重要 | C3 | 日志脱敏靠"没写 log" + 人眼 grep；**意外异常 traceback 会泄漏 prompt/personality** 进日志（违 forbidden #9） |
| 重要 | C4 | 网关最坏时延 ≈ **60s**（2×30s）未透给 gen → gen 超时叠加重试，**G-1 配额烧得更狠**而非更省 |
| 次要 | M1 | 422/502 测试只断言 `code`，未断言错误体 `keys=={code,message}`（对齐 Error `additionalProperties:false`） |
| 次要 | M2 | 非预期异常 → 500，契约③ 无 500（可与 C3 catch-all 一并收口为 502） |
| 次要 | M3 | guardrail 误杀（合法输出偶含 denylist 词）→ 422、整链失败、无兜底（A1 风格可接受，记一笔） |

---

## 2. 关切 / 反对（逐条）

### C1【阻断 · 消费方 + 契约面】请求校验 422 体不符契约③ Error，gen 接不住
- **现象**：契约③ 把 **422 唯一语义 = guardrail 拦截**，体 = `Error{code,message}`。但 plan 的请求模型 `extra="forbid"` + 长度约束触发的是 FastAPI 默认 `RequestValidationError` → **也是 422**，体却是 `{detail:[...]}`。
- **gen 视角影响**：gen 在 422 上若按契约读 `body.code` → **KeyError**；且 guardrail-422 与校验-422 **同码不同体**，gen 无法区分"我请求发错了（personality 超 4000 / 缺字段）"vs"输出被 guardrail 拦"。两种 422 语义混叠 = 消费方真实接不住。
- **plan 现状**：仅在 spec §6.2 注"请求 schema 拒绝非本次契约测试范围"——但这**不只是测试缺口，是契约面真实不一致**。
- **建议**：加 `@app.exception_handler(RequestValidationError)`，统一映射为**符合契约③ Error 的体**（建议 **400** `{code:"invalid_request", message:...}`，与 guardrail 的 422 区分开）；让**所有**对外错误体单一符合 Error。若团队认为校验失败也该 422，则至少错误体必须是 `{code,message}` 且 code≠guardrail_blocked。**此点涉消费方口径，建议拉 gen owner 对齐（契约③ 结构不改，属错误语义描述层澄清，可能回 feature 层点一句）。**

### C2【阻断 · 安全 + 测试】prompt_leak 规则与其测试互相迁就，绿了不证真本事
- **现象**：`guardrail.py` 的 `prompt_leak` = `len(si)>=20 and si in text`——要求**整条 systemInstruction 逐字、连续**出现在输出里才命中。
- **spec 对照**：spec §5.3 写的是"检测输出是否回显 systemInstruction **片段 / 特征**"。plan 实现成"**整条逐字**"，**严格弱于 spec**。
- **测试迁就**：Task5 的 `test_guardrail_blocks_prompt_leak` 输出 = `"我的系统提示是：" + _SYSTEM`（**整条**回显）→ 恰好命中。**测试与实现同形、互相迁就**——真实泄漏多是**片段 / 改写 / 分段**，本实现一概漏，而测试绿得让人误以为"泄漏能拦"。这是"**为适配实现弱化测试**"的典型苗头，也是安全镜头下最该挡的一条。
- **建议**：改片段检测——如 systemInstruction 任一**连续 ≥N 字（如 16）跨度**出现于输出即命中（滑窗 / 按句切分）；测试相应改为**回显片段**断言命中、并加一条"整条不回显但泄漏关键句"用例。N 取值留 plan 定，但**测试必须以片段驱动**，不得回显整条糊弄。

### C3【重要 · 安全 + 运维】日志脱敏未强制，意外异常 traceback 会泄漏 prompt/personality
- **现象**：plan Task6 Step1 用 `grep` + 人眼确认"无 print/log 输出 prompt/personality/text"。但**未处理非预期异常**：service/mapping/guardrail 若抛预期外异常，FastAPI/uvicorn 默认打 traceback，栈帧 local（`messages` / `payload` 含 systemInstruction + personality）**可能落日志** → 违 forbidden #9「日志不输出完整 prompt/响应」。
- **正面**：已知异常（Guardrail/Upstream）handler 不带 body ✓；httpx 异常只存 `type(exc).__name__` 不带 body ✓——**这两处做得好**。缺的是**兜底**。
- **建议**：加 catch-all `@app.exception_handler(Exception)` → 502/500 且**绝不回显 body**；确认 uvicorn access log 不落 body。grep 自检留作辅助、非唯一防线（"靠没写 log"不是强制约束，是约定）。

### C4【重要 · 消费方 + G-1】网关最坏时延 ≈60s 未透给 gen，反放大配额烧钱
- **现象**：`MAX_RETRIES=1` + 每次超时 30s ⇒ 网关单请求最坏 ≈ **2×30 + 0.5 ≈ 60.5s**。
- **gen 视角影响**：gen 在关键**同步**链（还串高德逆地理 + 高德 POI），若 gen/api 自身超时 < 60s，gen 会在**网关第 2 次尝试途中**就超时 → gen 再重试 → DeepSeek 调用翻倍。G-1 的本意是"少重试省配额"，但**网关默默把最坏时延吃到 60s 却没透给消费方**，结果是**放大**而非抑制烧钱。
- **plan 现状**：记了 `MAX_RETRIES` 取值与"非幂等"理由，但**没记最坏时延预算、没给 gen 超时定位建议**。
- **建议**：在 plan / 契约③ 描述里**写明网关最坏时延（≈60s）**，让 gen 把自身超时设 **> 网关**且**不再叠加重试**；或把每次超时压小（如 15–20s）使最坏 ≈30–40s。二选一，但**最坏时延必须对消费方可见**。

### M1〜M3（次要，见 §1 表）
- **M1**：422/502 测试补 `assert set(resp.json())=={"code","message"}`，与 Error `additionalProperties:false` 对齐（现仅断言 `code`，对错误体形状无约束）。
- **M2**：500 不在契约③；与 C3 catch-all 一并收口为 502 更干净。
- **M3**：guardrail 误杀无兜底——与 A1"定位拒=不可创建"同风格，**接受**，记一笔（denylist 起步词表须避高频正常词）。

---

## 3. 正面确认（逐条看过，非橡皮章）

- **block-only 守住** ✓：全链无改写/脱敏路径；guardrail 命中只 `raise GuardrailBlocked`→422，`text` 从不被网关修改。GW-1#1 落实。
- **机械映射可审计** ✓：契约测试断言 `messages[0]=={"role":"system","content":systemInstruction}` 原文、personality 进数据消息且不入指令。GW-1#2 / GW-2 落实。
- **key env** ✓：仅 `os.environ.get` 读取、缺失即 502、无硬编码/提交（forbidden #2）。
- **薄边界** ✓：单家 DeepSeek、无多 provider/fallback/预算限流，守 §3.2、未向业务滑。

---

## 4. 是否需要人工确认

**需要。** 触及高影响（guardrail / key / 对内契约错误语义面）：
- **C1** 涉契约③ 错误体口径 + **消费方 gen** 能否接住 → 建议**拉 gen owner 对齐**（契约③ 结构不改，属错误语义描述层澄清，可能回 feature 层点一句）。
- **C2 / C3** 属安全收口弱化，须 owner + 牵头人确认修订方向后再 ④。

---

## 5. 下一步建议

1. **不进 ④**，先把 C1–C4 回炉改 ② plan（C1/C2 阻断必修；C3/C4 重要建议修；M1 顺手补）。
2. C1 错误体口径与 gen owner 对齐（必要时 feature 层点一句"请求校验错误走 400/`invalid_request`、与 guardrail-422 区分"）。
3. 修订后重跑本 ③ 评审（或牵头人裁定可放行）→ 再启 ④ TDD。
4. **测试不得为适配实现而弱化**（C2）——leak 测试以片段驱动，错误体测试断言形状（M1）。

---

> 评审性质：AI（换 gen 消费方帽 + 安全镜头）独立审，**非 owner 自放行**；仅供评审参考，**不替代人工评审，AI 永不作为合并门禁**。
