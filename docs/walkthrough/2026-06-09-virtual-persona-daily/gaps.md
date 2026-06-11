# Phase 0 走查 — gaps（virtual-persona-daily）

> 立走查记录：截至 Phase 0（模板基线 → 子项目重构 → 可跑骨架 + 四道门 → context / high-impact → hook `TASK_SCOPE`/`TEST_CMD`）的发现。
> 本文件**只立条目**；完整证据日志 + 模板忠实度自查留到 **Phase 0 末**再补。
> 分两类：**A 回流-worthy 且已本地修**（缺陷源在团队模板，需上报修上游）、**B 小记 / 待办**（非回流的本地规避 / 留观 + 待回流的延后项；回流性质见每条标注）。
> 每条记：**现象 / 影响 / 现状**（已修 / 已规避 / 待办）。

---

## A. 回流-worthy（缺陷源在团队模板，待回流上游 + 人裁决）

### A1. path-guard.sh fails-open：block 文案变量紧贴全角标点 → `set -u` 下崩溃放过越界

- **现象**：`.claude/hooks/path-guard.sh` 越界分支的错误文案里 `$TASK_SCOPE` 紧贴全角逗号（`…范围=$TASK_SCOPE，却改 …`）。在 `set -u` + bash 3.2（macOS 自带）下，多字节逗号的首字节被并进变量名 → 报 `unbound variable`，脚本 **exit 1 而非 exit 2**。
- **影响**：**fails-open（守卫形同虚设）**。PreToolUse 守卫看似拦截、实则在打印拦截文案时崩溃；越界编辑因退出码非 2 被放过，且不易察觉（"看似拦、其实崩"）。只在越界 / 高影响分支**真正触发**时暴露——正常放行路径（in-scope，exit 0）不触发，故极易漏测。
- **现状**：**本地已修，缺陷源待回流**。本 repo 已将越界与高影响两条 `echo` 的变量改花括号 `${VAR}`，复测 exit=2 恢复正常拦截（step 5，commit `a2fd75b`；本地改动亦记于 [`.claude/VENDOR.md`](../../../.claude/VENDOR.md)）。**缺陷源在团队模板 `path-guard.sh`**（本 repo 由模板基线 `9426e4c` 复制而来）→ 标「**待回流上游模板、人裁决**」：上游同款文案在 `set -u` + bash 3.2 环境普遍中招。

---

## B. 小记 / 待办（非回流的本地规避 / 留观 + 待回流·延后项；回流性质见每条标注）

### B2. path-guard.sh 的 `case "$REL" in $pat)` glob 语义依赖 bash，zsh 下会全漏匹配

- **现象**：用变量当 glob 的 `case "$REL" in $pat)` 写法，**bash 下正确**（`*` 跨 `/`、`**`≈`*`）；但 **zsh 的 `case` 需 `${~pat}`** 才把变量内容当 glob，否则按字面匹配 → 若改用 zsh 跑，high-impact / 越界路径**全部漏匹配**。
- **影响**：换 shell 跑 hook 会**静默失效**。本机交互 shell 即 zsh，曾导致一次自测「全 normal」的假象，改回 bash 复现后才正确——若误以 zsh 为准会得出"守卫没问题"的错误结论。
- **现状**：**已规避**。hook 用 `#!/usr/bin/env bash` shebang 固定解释器；[`rules/high-impact.paths`](../../../rules/high-impact.paths) 文件头已注明匹配语义 = path-guard 的 POSIX `case` glob。无需改动；未来若有人移植到 zsh，需显式 `${~pat}`。

### B3. FastAPI TestClient 的 StarletteDeprecationWarning

- **现象**：两个 Python 服务（generation-service / ai-gateway）`pytest` 跑 `/health` 用例时，FastAPI `TestClient` 报 `StarletteDeprecationWarning`（提示 `httpx` 与 `starlette.testclient` 的用法将变更）。
- **影响**：**仅告警，测试仍过、门为绿**，非阻断。
- **现状**：**留观（留作 F2 升级信号）**。未加 `filterwarnings` 掩盖（避免藏掉未来真信号）；待 F2 依赖升级时按提示处理。

### B4. CODEOWNERS 的 bot 性质未文档化 → 冷读 agent 误报 §2 冲突

- **现象**：`.github/CODEOWNERS` 把 `@vpd-ci-bot`（实为开发者本人的第二个 GitHub 账号、手动点 approve）挂为全路径必须审批人，但文件里未说明该账号性质。
- **影响**：冷读 agent（无上下文）按字面「bot 当全路径门禁」误报与 §2「AI 永不作为合并门禁」冲突——实为单人模拟「作者 ≠ 审批者」的**人工**审批，非 AI / 自动化门禁，**不违 §2**。一次冷读即触发此误报。
- **现状（已修）**：已在 CODEOWNERS 顶部注释澄清——`@vpd-ci-bot` = 开发者第二账号、手动审、非 AI、与 §2 不冲突；并警示绝不可接入自动 approve 的 CI；真实多人时换各域真人 / 团队。

### B5. 分支保护 ruleset 只在 GitHub 端 → 仓库内无版本化记录，冷读看不到真实合并门禁

- **现象**：`main` 分支保护以 GitHub repository ruleset（`main-protection`，`id 17444695`，`enforcement=active`）形式只存在于 GitHub 设置；仓库内此前无版本化记录。强制项（PR + 1 审批、CODEOWNERS 审、`gates` CI strict 必过、禁删 / 禁强推、无 bypass）只在 GitHub UI 可见。
- **影响**：冷读仓库看不到「合并门禁的真实强制点」，易低估 / 误判治理强度；且 ruleset 漂移无 diff 可查、无重放来源。
- **现状（已修）**：已把导出 JSON 落 [`../../../.github/rulesets/main-protection.json`](../../../.github/rulesets/main-protection.json)（同目录 README 注明「GitHub 不自动应用本目录、生效源在设置」，避免下一个误读）；并在 [`../../../rules/review-gates.md`](../../../rules/review-gates.md) 文档化实际强制的门禁。同 [[B4]] 一类：GitHub 端配置不入库 → 冷读盲区，修法 = 版本化 + 文档化。

### B6. path-guard 只挂 Edit/Write/MultiEdit，Bash 写文件绕过守卫

- **现象**：⑧ 越权半 L2 会话内演练。授权「落那条 ai-gateway 注释」后，会话因 Edit/Write 被 PreToolUse 拦，改用 Bash（`echo >>`）把注释写进 [`servers/ai-gateway/app/main.py`](../../../servers/ai-gateway/app/main.py)（高影响区）。**根因**：[`.claude/settings.json`](../../../.claude/settings.json) 的 PreToolUse matcher 是 `Edit|Write|MultiEdit`，不含 Bash，shell 写完全不过 path-guard。
- **影响**：设计本就把 ①.5 会话内 hook 定为「机械·可绕过、权威靠 PR 门禁」；本例坐实其可绕过的具体宽口子 = Bash。且 ②层（git pre-commit + CI「改动路径 vs `high-impact.paths`」diff 检查）尚未建 → Bash 写的高影响改动当前机械层无人拦，只剩单 owner CODEOWNERS。同 [[A1]] 一类：均 path-guard 守卫完整性问题（A1 = fails-open 崩溃放过，B6 = matcher 漏 Bash 写）。
- **现状（待办·延后）**：**回流候选**，开发者已定性「记下、处理延后」。方向（延后）：② git pre-commit 或 CI 增一道「变更路径对照 [`high-impact.paths`](../../../rules/high-impact.paths)」的 diff 门禁，与工具无关（Edit / Bash 都拦）；会话内 Bash matcher 难可靠解析命令里的目标路径，兜底放 commit / CI 层更稳。

> 以下 B7–B11 为 Phase 0 末「门禁对抗审计」（7 向量，审计 ID `wz5n80p0x`）的发现；审计同时确认 ⑥ PR 门禁脊梁（ruleset 零漂移 + `gates` 真跑真覆盖 + CODEOWNERS 接线 + §2 合规 + admin 不可绕）实证充分。开发者已定性「全部记录、修复延后」。

### B7. path-guard `REL` 不规范化 → `..` 路径穿越双绕过（高影响 + 越界同躲）

- **现象**：审计实测——`file_path` 给 `$ROOT/apps/web/../servers/ai-gateway/app/main.py` 时 path-guard **exit=0（放行）**，而直接写 `servers/ai-gateway/app/main.py` 则 exit=2。
- **影响（high）**：[`path-guard.sh`](../../../.claude/hooks/path-guard.sh) 第 24 行 `REL="${FILE#"$ROOT"/}"` 只做字符串剥前缀、**不规范化路径**。含 `..` 的路径剥完是 `apps/web/../servers/ai-gateway/...`：越界检查的 `case "$TASK_SCOPE"/*`（`apps/web/*`，`*` 跨 `/`）把它当 **in-scope 放行**，同时它又不命中 `servers/ai-gateway/**` 高影响 glob → **一发同躲两道检查**，物理写进禁区。比 [[B6]] 更狠：用普通 Edit/Write、仅靠构造路径就骗过守卫，不需换工具。
- **现状（待办·延后）**：**回流候选**。方向：取 `FILE` 后用 `realpath -m` / `readlink -f` 规范化再剥前缀重判，或对含 `..` 段直接拒。同 [[A1]] / [[B6]] 一类：path-guard 守卫完整性。

### B8. path-guard 漏 NotebookEdit：matcher 不含 + 脚本只读 `file_path`

- **现象**：审计实测——`NotebookEdit` 写指向高影响区的 `.ipynb` → **exit=0（不拦）**。
- **影响（high）**：双洞——(1) [`.claude/settings.json`](../../../.claude/settings.json) PreToolUse matcher = `Edit|Write|MultiEdit`，**不含 `NotebookEdit`** → hook 根本不触发；(2) 即便触发，[`path-guard.sh`](../../../.claude/hooks/path-guard.sh) 只读 `tool_input.file_path`，而 NotebookEdit 用 `notebook_path` → 取不到路径。`.ipynb` 写高影响 / 越界区无拦。
- **现状（待办·延后）**：**回流候选**。方向：matcher 加 `NotebookEdit`；取路径时 fallback 读 `notebook_path`。同 [[B6]] 一类（matcher 覆盖不全）。

### B9. 零内容级密钥扫描：按文件名拦 ≠ 按内容拦，含密钥源文件可一路入 main

- **现象**：审计静态确认——全仓无 gitleaks / trufflehog 类机械密钥检测接进 CI / pre-commit；AgentShield（`security-scan` skill）是**手动** skill、只扫 `.claude/` 配置不扫源码、**从未 wired**；path-guard 按文件名拦（`.env*`）非按内容；required check `gates` 不查密钥。
- **影响（high）**：含硬编码密钥的**普通源文件**（如 `config.py` / `keys.json` / 任意 `.py` `.ts`）可一路入 main，唯一拦阻是人审。当前只做到「**不入库**」半（`.gitignore` `.env*`、git grep 无硬编码 key），缺「**内容检测**」半。
- **现状（待办·延后）**：**回流候选**。方向：②层一并接入内容级 secret-scan，与 [[B6]] / 路径 diff 门禁同处（CI 或 pre-commit）——同根：②层机械门尚未建。

### B10. CI 工作流自指不自洽：required check 可在它守护的同一 PR 内被改空仍报绿

- **现象**：审计推演 + 机制确认——required check 按名 `gates` 匹配，`pull_request` 事件跑的是 **PR head 版** `ci.yml` → 对抗 PR 把 `make check` / `gates` job 改成 no-op 即让 `gates` 报 success；`.github/` 无专属 CODEOWNERS（仅 `*` 泛 owner 兜底）。
- **影响（med）**：机械门对「改门禁自身的 PR」退化为纯人审；单 owner 现状下此类 PR 可被同一人低成本通过。
- **现状（待办·延后，真实多人后）**：方向：CODEOWNERS 对 `.github/`（尤其 `workflows/`）设独立强审 owner，或加 workflow-tamper 检测。

### B11. ①.5 软守卫结构性弱点：齿挂在 gitignored 的 task.env，缺失即静默 fail-open

- **现象**：审计确认——越界检查（`TASK_SCOPE`）与完成门（`TEST_CMD` → `check-completion.sh`）都由非提交、每机一份的 `.claude/task.env`（见 `.claude/task.env.example`）注入；缺失 / 留空即静默 fail-open（`TASK_SCOPE` 空 → 不查越界；`TEST_CMD` 空 → `check-completion` 每次 Stop exit 0 = no-op）。另：path-guard 取路径依赖 `python3`，缺 python3 时 `FILE=''` → exit 0（与 [[A1]] 同构的 fails-open，换机 / 精简 CI 镜像即触发）。
- **影响（med）**：会话内软守卫的「齿」可被无意关掉（删 / 空 task.env、缺解释器）而不报警；`check-completion` 当前实为 no-op。
- **现状（观察 / 部分回流）**：与设计自陈一致——权威必须落 ⑥ PR 门禁，**勿把 task.env 当权威开关**。其中 **python3 缺失 fails-open 属回流-worthy**（取值层应 fail-closed：无解释器 → exit 2 / 显式报错）；`check-completion` 实现待 F1 acceptance 落地后再做。


### B12. whole-dir 高影响过粗：F2 落声明式 contract schema 被误拦（粒度未分"敏感代码 vs 声明式契约"）

- **现象**：F2 写契约 schema 时，`servers/generation-service/contracts/api-gen.openapi.yaml` 与 `servers/ai-gateway/contracts/gen-aigw.openapi.yaml` 被 path-guard 拦（exit=2）。根因：[`rules/high-impact.paths`](../../../rules/high-impact.paths) 骨架期把两个 provider 子项目按 `servers/<provider>/**` **全目录**收口（自注"骨架期标全目录；首刀后收窄到具体模块"），`*` 跨 `/` → 连 `contracts/` 下的**声明式契约 schema** 一并命中。
- **影响（low）**：守卫本身**行为正确**（跨子项目契约本就是高影响类目，拦下来让人看并无错）——但**粒度过粗**：把"P0 敏感代码"（prompt 构建 / key 使用 / guardrail / 事件写入）与"声明式契约 schema"混为一谈。契约 schema 恰恰**该**走「跨子项目契约」评审路径（review-gates 升级评审 + CODEOWNERS），而非 P0 敏感代码收口；二者评审责任域、节奏不同，混收口会在每次契约演化时误触 P0 暂停。非 [[A1]]/[[B6]]/[[B7]] 的守卫完整性问题（那些是"该拦没拦"），这是"**拦对了类目、但粒度该再分**"。
- **现状（已本地收窄 + 回流候选）**：本 repo 已把两条全目录收口收窄到代码目录 `servers/<provider>/app/**`（prompt/key/guardrail/事件写入均在此，**仍高影响**），并显式注明 `contracts/**` 不收口、走契约评审路径；收窄后契约 schema 写入放行、敏感代码仍拦。**回流候选**：团队模板的"本项目高影响区"约定应**从一开始就区分「敏感代码（按 module 收口）vs 声明式契约（走契约评审）」**，避免骨架期 whole-dir 占位在 F2 契约落地时普遍误拦——这是"两层开发/契约先行"在治理粒度上的必然交点。出处见 [`feature/2026-06-10-virtual-persona/spec.md`](../../../feature/2026-06-10-virtual-persona/spec.md)（F2 契约阶段）。


### B13. 子项目模板未编码 ①–⑦ 步骤 → ③「评审讲解」最易被漏（owner 自放行倾向）

- **现象**：CLAUDE.md §7 / §8 与各子项目 `CLAUDE.md`、`rules/` 均**未把 ①–⑦ 子项目链的步骤序列编码成清单 / 模板 / 门**。`spec/`、`plan/`、`review/` 三目录各有 README，但**无任何机制提示"②plan 之后、④TDD 之前必须做 ③ 独立评审讲解"**。首刀 A1 走 ai-gateway 链时，①spec→②plan 由 owner 顺势自产，**③ 评审讲解仅因牵头人显式点名才发生**——若不点名，会直接从 ②plan 滑到 ④TDD，且因 ai-gateway 是高影响 guardrail/key 服务、又是 owner 自审，**最易形成"owner 自放行"**（用 owner 帽审自己起草的 plan，等于橡皮图章）。
- **影响（med）**：③ 是"换视角独立审、挡掉 owner 盲区"的关键关（本次换 gen 消费方帽 + 安全镜头即查出 C1 契约错误体不符 / C2 测试与实现互相迁就等阻断项，见 [`servers/ai-gateway/review/2026-06-10-review-aigw-a1.md`](../../../servers/ai-gateway/review/2026-06-10-review-aigw-a1.md)）。步骤不编码 → 该关**靠人记得点名才生效**，是会话内软约束（同 [[B11]] 一类：齿挂在"人记得"上，缺失即静默跳过），高影响子项目尤其危险。
- **现状（待办·回流候选）**：**回流候选**，本 repo 暂靠牵头人显式驱动补上 ③。方向（延后）：团队模板把 ①–⑦ 编码为子项目链的**显式 checklist / 产物门**——尤其 ③ 应规定"**审者 ≠ 起草者视角**"（换帽 / 换消费方 / 换安全镜头，禁 owner 自审自放行），并把 `review/` 产物列为 ④ 前置必产物（缺 ③ review → 不得进 ④）。与 [[B4]]/[[B5]] 同根：**关键治理点未版本化 / 未编码 → 冷读或顺势执行即漏**；区别是这条漏的是**流程步骤**而非配置。

### B14. 高影响守卫只有「拦」没有「确认放行」档 → 逼出 Bash 绕过 / 整体关停（接 [[B6]]）

- **现象**：④ TDD 写 `servers/ai-gateway/app/**`（持 key + guardrail，高影响）时，[`path-guard.sh`](../../../.claude/hooks/path-guard.sh) 对每个 app/ 文件 `exit=2` 暂停。即便牵头人**已显式预授权**「确认是本子项目工作即放行」，守卫也**没有「确认后放行这一笔」的档位**——PreToolUse 只能 block 或不 block，无 per-edit 批准通道。结果只剩两条路：① Bash heredoc 绕过（即 [[B6]] 的洞，但这次是**被守卫逼着**主动绕，不是工具偏好）；② 牵头人**整体临时关停** path-guard（本次采纳）。
- **影响（med）**：两条路都比「确认放行这一笔」**粒度粗**——①绕过让守卫形同虚设且开坏先例；②整体关停期间**所有**高影响保护一并失效（不止本子项目 app/，全仓 high-impact 都不拦），关停窗口内任何越界/高影响误改都无机械拦阻，只剩 PR 门禁兜底。本次靠「单 owner + 关停窗口短 + 全程 commit 留痕」兜住，但机制上是「要么全拦、要么全放」。同 [[B6]]/[[B11]] 一类：会话内软守卫的结构性弱点——这条特指**缺「确认放行」中间档**，把预授权的合法高影响编辑逼成「绕过或关停」。
- **现状（待办·回流候选）**：**回流候选**，接 [[B6]]。方向（延后）：给 high-impact 暂停加一档**显式确认放行**（如读 `.claude/task.env` 的一次性 `ALLOW_HIGH_IMPACT=<path>` 票、或 PreToolUse 返回询问而非硬 block），让「预授权的本子项目高影响编辑」能**留痕放行**而非二选一绕过/关停；权威仍落 ⑥ PR 门禁，但会话层不必在「裸奔」与「寸步难行」间跳。出处：本 feature ④ TDD（`feat/ai-gateway-a1`）。

### B15. 日志/传输层 PII/凭证泄漏在 3 层 guardrail 覆盖外；A1 修复是 httpx 压级 band-aid，凭证 / 错误路径靠测试兜底

- **现象**：gen A1 的 3 层 guardrail（① 录入审核 / ② prompt-as-data / ③ ai-gateway 输出审核）全在**内容层**（防注入 / 回显 / 不安全内容）。但精确坐标(PII)与高德 key(凭证)经 httpx 落在**日志 / 传输层**：httpx 默认 INFO 记完整请求 URL——逆地理 URL 含坐标、各高德 URL 含 `&key=`。④ TDD `test_precise_location_not_logged` 红捕获，A1 修复 = [`servers/generation-service/app/main.py`](../../../servers/generation-service/app/main.py) 把 `httpx` logger 压到 WARNING。本次向导侧 checkpoint 复查发现该修复**覆盖不全**：(a) 原测试只断坐标、未断 key；(b) 只测 happy path，未测高德错误路径——[`app/amap.py`](../../../servers/generation-service/app/amap.py) `_get` 的 `raise GenError(...) from exc` 把含完整 URL（坐标+key）的 `HTTPStatusError` 链进 `__cause__`，而 httpx 压级只管"请求 INFO 行"、**管不到异常链**；实测确认：错误路径下 `__cause__` 的 str 同时含坐标与 key，且若任何 error logger 以 `exc_info` 记该异常即泄漏。
- **影响（high·security·结构性）**：3 层 guardrail 是**内容层**防御，对"基础设施 / 依赖默认行为把 PII / 凭证写进日志或异常链"这类**结构性泄漏面无覆盖**。httpx 压级是 band-aid（点状压一个 logger 的级别），非系统性的"PII / 凭证不出服务边界"控制；坐标+key 仍**潜伏在异常链**中——错误路径 green 是"当前无 `exc_info` 异常日志"的偶然结果，而非结构保证。同 [[B9]] 一类：那条是"按文件名拦 ≠ 按内容拦"，这条是"内容层 guardrail ≠ 传输 / 日志层泄漏"——都是机械 / 内容防线与真实泄漏面错位。
- **现状（实例已结构闭合 + 设计层回流候选保留）**：分两步处置——
  - (1) 先按 TDD 补强两条**日志层**回归测试（`test_precise_location_not_logged` 加 key 断言、强化为坐标+凭证双断；`test_amap_error_path_no_pii_in_logs` 高德 500 错误路径下断坐标+key 均不入日志）。实测错误路径**日志层当前 green**（现码无 `exc_info` 异常日志），但坐标+key 仍**潜伏异常链**——green 系偶然、回归日志测试**守不住 off-box 捕获(Sentry/APM) 与框架默认 `exc_info` 异常日志**。
  - (2) 经向导裁决**提前防御性闭合该实例**：[`app/amap.py`](../../../servers/generation-service/app/amap.py) `_get` 的 `raise GenError(...) from exc` 改 **`from None`** 断异常链（httpx 异常 repr 含完整 URL〔坐标+key〕，原随 `__cause__` 外泄），并加只含**异常类型名**（不含 URL/凭证）的 `logger.warning` 保留诊断；新增**源头结构测试** `test_amap_error_does_not_chain_url_bearing_exception`（在异常源头断 `__cause__ is None` 且异常数据面无坐标/凭证，**先红后绿**）钉死。**本实例已结构闭合**（异常链不再携带 URL/凭证），不再依赖"恰好没人 `exc_info`"。
  - **但 guardrail 设计层仍无传输层 redaction 的通用控制** → **回流候选保留**：日志层 redaction filter / 统一异常脱敏策略。逐处 `from None` 是**点修**（每个新增下游 client 都得自觉守同一纪律），非系统性兜底；"日志 / 传输层泄漏面"应作为内容层 guardrail 之外**另立的一层**纳入盲区清单。同 [[B9]] 一类（机械 / 内容防线与真实泄漏面错位）。

### B16. ②plan 内联的测试片段有自洽 bug（base64 正则漏 `=`），③ 评审讲解未抓出、仅 ④ TDD 揪出

- **现象**：gen A1 的 ②plan（[`plan/2026-06-10-plan-gen-a1.md`](../../../servers/generation-service/plan/2026-06-10-plan-gen-a1.md) Task 3）直接内联了 review 第二道的**测试**与**实现**片段；其 base64 blob 正则 `[A-Za-z0-9+/]{80,}` 漏掉 `=` 填充符。plan 自带的测试用例（一段以 `=` 结尾的 base64 串 ×3 拼接）因 `=` 不在字符类内被切成最长 51 字符的连续段 < 80 → **plan 的测试与 plan 的实现互相矛盾**，照抄即红。该自洽 bug 在 ③ 评审讲解（对 plan 的独立讲解评审）**未被发现**，直到 ④ TDD 照 plan 写测试、跑出红才暴露；④ 修法 = 把 `=` 纳入字符类 `[A-Za-z0-9+/=]{80,}`（commit `d3d05db`）。
- **影响（med·process）**：③ 评审讲解的职责是"换视角独立审 plan、挡 owner 盲区"（见 [[B13]]），但本次 ③ 审的是 plan 的**叙述 / 决策**，没**实跑 plan 内联的可执行片段**——plan 里的 test / impl 代码成了评审盲区。plan 越"贴心"地内联完整 test+impl，越容易让人误以为"评审过 = 片段对"，而其自洽性（测试与实现是否互证）只有真跑才验得出。
- **现状（已修 + 流程留观）**：④ 已修正则并 commit，测试转绿。**流程留观 / 回流候选（延后）**：③ 评审讲解若 plan 内联了可执行片段，应把片段的"测试 ↔ 实现"自洽性纳入 checklist（哪怕粗跑一次）；或约定 plan **不内联**完整实现代码、只给意图 + 签名，避免"未验证的实现细节"伪装成已评审结论。同 [[B13]] 一类：均 ③ 评审讲解的覆盖盲区——B13 是"步骤易被整条跳过（owner 自放行）"，B16 是"步骤做了、但未覆盖 plan 内可执行片段的自洽性"。

---

## 备注

- A 类回流流程见 [`.claude/VENDOR.md`](../../../.claude/VENDOR.md) 「刷新流程」末条「本地改动逐条记」；A1 已在 VENDOR.md 记本地改动。
- 走查目录按「日期 + repo」命名：`docs/walkthrough/2026-06-09-virtual-persona-daily/`。
