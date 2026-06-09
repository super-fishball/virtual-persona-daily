# 审核门禁（review-gates）

> 定义哪些改动**必须人工审核**或**升级评审**，以及 PR 阶段的 Agent Review 机制。命中即触发，AI 不得自行放行。

## 必须升级评审（责任域成员参与）

- 命中 [`high-impact.md`](high-impact.md) 任一区域。
- 改动**跨子项目契约**（API / 数据结构 / 消息格式 / DB schema）。
- 引入新依赖、新外部服务、或调整目录结构。
- **测试阶段缩小范围**：导致某条验收标准失去覆盖，或触及高影响区相关测试（即使验收名义仍覆盖）→ 升级**发布确认人**裁定。AI 只建议、不拍板。

## 必须人工审核（常规 review 即可，但不可省）

- 命中 [`forbidden.md`](forbidden.md) 相关边界的灰区改动。
- 改动量超过阈值。<!-- TODO：定义阈值，如单 PR 变更文件数 / 行数上限。 -->
- 删除或大幅重写测试。
- **文档未同步**：改动命中机读路径源的文档耦合（如改跨子项目 schema 却未同步契约文档 / `context/`），人审**内容够不够**。

> **文档防过时 = 软 + 硬两层**：上面这条是**软门禁**（人审内容，现在就上）；**硬门禁**（CI 机械查路径耦合，确定性、不可绕过）待**单一机读路径源**就位后补——见 [`high-impact.md`](high-impact.md) 与 [`development-guard.md`](development-guard.md) 自检 #7，三层（开发中自检 / pre-commit / CI）复用同一份路径源。

## Agent Review 机制（PR 阶段自动审查）

PR 创建 / 更新时，CI 并行触发多个 Agent（见 [`../.github/workflows/agent-review.yml.example`](../.github/workflows/agent-review.yml.example)，默认失活，启用方式见文件头）：

- **Agent A（Claude）**：Anthropic SDK，读取 PR diff + spec/plan + CLAUDE.md，输出 review → PR comment。
- **Agent B（Codex）**：OpenAI SDK，读取相同上下文，输出 review → PR comment。

每个 Agent 额外输出：结构性影响范围、高影响区标记、对照 spec/plan 的越界文件。

- **changed-files**：基于 PR 的 changed-files 判定影响范围，对照 [`high-impact.md`](high-impact.md) 标记高影响改动。
- **CODEOWNERS**：[`../.github/CODEOWNERS`](../.github/CODEOWNERS) 将对应文件/目录负责人自动加为必须审批人；触及高影响区时升级评审。

**Agent 间无优先级、冲突无需特别协议**：两个 Agent 跨厂商提供独立视角，意见不一致时不裁谁对——**分歧本身就是"此处有争议、人需重点看"的信号**，由 CODEOWNERS 人工权衡裁决。

## 合并门禁

合并门禁 = **verification 通过（机械）+ CODEOWNERS 人工审批（权威裁决）**，两者齐备方可合并。
**Agent Review 不是独立门禁**——它是喂给 CODEOWNERS 人审的**参考输入**，不自动放行、也不自动卡住合并。**AI 永不作为合并门禁，合并与否恒由人裁决。**

## 定位

Agent Review 结果**仅供人工评审参考**，不替代人工评审、测试或上线判断。**AI 永不作为合并门禁**——合并与否恒由人（CODEOWNERS）裁决。

<!-- TODO（项目接入时填写）：本项目特有的门禁触发条件与阈值。 -->
