# VENDOR.md —— 第三方件出处与刷新

> 本项目按「项目本地 committed（vendor）」落位 AI 工具层（决策见根 [`pending-decisions.md`](../../pending-decisions.md) 「AI 工具层落位」）。
> **只 vendor 已采纳的填洞项，不整套搬。** 每个件记来源 + 版本/commit + 许可 + 抄入日期 + 本地改动，保证可审计、可刷新。
> 许可证原件存于 [`vendor-licenses/`](vendor-licenses/)。

---

## 已 vendor

### superpowers（skills/）

| 项 | 值 |
|---|---|
| 来源 | https://github.com/obra/superpowers |
| 版本 | 5.1.0 |
| commit | `6fd4507659784c351abbd2bc264c7162cfd386dc` |
| 许可 | MIT（Copyright © 2025 Jesse Vincent）→ [`vendor-licenses/superpowers-LICENSE`](vendor-licenses/superpowers-LICENSE) |
| 抄入日期 | 2026-06-08 |
| 来源路径 | 本机插件缓存 `~/.claude/plugins/cache/superpowers-marketplace/superpowers/5.1.0/skills/`（当时 git clone 不通，从本地安装处拷） |
| 本地改动 | 无（原样整目录拷入） |

**拷入的 skills**（仅本套流程用到的 5 个）：

- `brainstorming/` — ① / F1 spec 起草
- `writing-plans/` — ② plan
- `test-driven-development/` — ④ TDD（方法）
- `verification-before-completion/` — ⑤ 完成证据
- `receiving-code-review/` — ⑦ 应对评审

> 未拷（superpowers 里有但本套未用 / 已否决）：`requesting-code-review`（与 ECC code-reviewer 生成器重复，已砍）、`systematic-debugging`、`dispatching-parallel-agents` 等——需要再按本表流程加。

---

### ECC（agents/ + skills/）

| 项 | 值 |
|---|---|
| 来源 | https://github.com/affaan-m/ECC |
| commit | `90dfd9505dc860714cf3cc8216ad7bbb96d93365` |
| 许可 | MIT（Copyright © 2026 Affaan Mustafa）→ [`vendor-licenses/ECC-LICENSE`](vendor-licenses/ECC-LICENSE) |
| 抄入日期 | 2026-06-08 |
| 来源路径 | 本机 marketplace clone `~/.claude/plugins/marketplaces/ecc/`（已 `/plugin marketplace add`；git 直连不通，从此本地副本拷） |
| 本地改动 | 无（原样拷入；自包含检查无外部引用） |

**拷入的 agents**（→ `.claude/agents/`）：

- `code-reviewer.md` — ⑦ 唯一评审生成器 + ⑧ Agent A
- `security-reviewer.md` — ⑦/⑧ 安全镜头
- `typescript-reviewer.md` — 栈特定 review → apps/web
- `database-reviewer.md` — api 的 DB / 迁移域 review（servers/api 高影响区）

> api 的**语言**特定 reviewer（python/go/…）待 api 栈定了再按「刷新流程」加。

**拷入的 skills**（→ `.claude/skills/`）：

- `blueprint/` — F2/F3 契约 + 拆分
- `verification-loop/` — ⑥ PR 前门禁
- `backend-patterns/` / `frontend-patterns/` — conventions 起草来源（人裁剪进 `context/conventions`）
- `security-scan/`（AgentShield）— ⑥ 机械扫描 / ⑦⑧ 红队·审计镜头

---

## 明确不 vendor（装了撞已定决策）

- `continuous-learning` 全家 / `instinct-*` / `learn` / `evolve` / `prune`（隐式漂移、描述当规定）
- `tdd-guide` / `tdd-workflow`（与 superpowers TDD 双装冲突）
- ECC `rules/` 整套（尤其 `common/testing.md` 的 80% 覆盖率，撞"反覆盖率刷分"）
- GitHub App

---

## 本地改动：team-docs 模板 hooks

> 模板基线（commit `9426e4c`「vendor team-docs template baseline」）自带的 hooks 属本地 vendored 件；
> 对其改动逐条记此，便于刷新时对账（呼应下方「刷新流程」末条）。

| 文件 | 本地改动 | 日期 |
|---|---|---|
| `hooks/path-guard.sh` | ①顶部 `source .claude/task.env`（按任务注入 `TASK_SCOPE`）+ 填 `TASK_SCOPE` TODO（空=不查越界）；②修复 block 文案中 `$VAR` 紧跟全角标点在 `set -u` / bash 3.2 下被并入变量名误报 unbound（越界 echo 实测 exit 1 而非 2）→ 越界与高影响两条 echo 均改 `${VAR}`。high-impact 匹配逻辑 / 路径源未动。 | 2026-06-09 |
| `hooks/check-completion.sh` | 顶部加 `ROOT` + `source .claude/task.env`（按任务注入 `TEST_CMD`）；填 `TEST_CMD` TODO；(2) 验收↔证据 TODO 保留并注明「待 F1 acceptance 落地后实现」（不造假解析器）。 | 2026-06-09 |

注入机制见 [`task.env.example`](task.env.example)（committed 模板）；真实 `.claude/task.env` 为 gitignored，改文件即生效。

---

## 刷新流程（vendor 不自动获上游更新，需手动同步）

```
1. clone 上游到临时目录       git clone --depth 1 <repo> /tmp/<x>-vendor
2. 记新 commit/版本           git -C /tmp/<x>-vendor rev-parse HEAD
3. 只重拷已采纳的件            cp -R <临时>/skills/<名> .claude/skills/<名>  …
4. diff 看上游改了什么         git diff（在本仓库内看 .claude/ 的变化）
5. 更新本文件的版本/commit/日期 + 本地改动说明
6. 删临时 clone
```

- **本地改动**：尽量不改 vendored 件；若必须改，**在本表该件「本地改动」栏逐条记**，否则下次刷新会冲突/丢失。
- **冲突优先级**：项目本地 `.claude/` 为唯一真相源；若某人全局也装了同名件，以项目本地为准。
- **评审**：`.claude/` 由 CODEOWNERS 覆盖，改工具（= 改流程）走 PR 审。
