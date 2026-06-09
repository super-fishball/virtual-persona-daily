# 开发中自检（development-guard）—— 通用流程

> 开发过程中，AI Agent 每轮代码修改后执行本自检。这是**与技术栈无关的通用流程**；各子项目在其 `rules/development-guard.md` 中补充本栈特有的检查步骤（只增不减）。
> **触发**：主触发 = **AI 自驱动**——每轮代码修改后在 AI 循环内自动执行本自检。
> 机械规则（路径越界 / 禁止文件 / 高影响路径）有两道补充机械层（均可绕过、非权威；建时用**单一机读路径源**，见 [`high-impact.md`](high-impact.md)）：**①.5 Claude Code hook**（`.claude/settings.json` 的 PreToolUse / PostToolUse / Stop，**会话内**执行——PreToolUse 能**直接拦**越界/禁止文件调用、Stop 拦"未完成就结束"）+ **② git pre-commit hook**（提交时、覆盖人改）。权威执行仍靠 ③ PR 门禁（Agent Review + 分支保护）。两道都延后实现。

## 自检对照物

- 需求 / Bug 描述
- 对应 `spec/*.md`、`plan/*.md`（含 AI 参与范围、禁改范围）
- 适用规则：根 `rules/` + 当前子项目 `rules/`（scope / high-impact / forbidden / review-gates）
- 当前 `git diff`

## 自检清单（通用八类）

逐项检查本轮改动是否：

1. **越界**：改了当前子项目之外、或 plan 禁改范围内的内容？（目录结构即机读源：本任务归属 `apps/web` 却碰了 `servers/api/**` = 越界）
2. **高影响**：命中 high-impact（根 + 子项目）？
3. **禁止项**：触碰 forbidden（根 + 子项目）？
4. **门禁**：触发 review-gates 的升级评审 / 人工审核条件？
5. **跨项目影响**：改动是否隐含影响其他子项目（尤其契约）？
6. **无依据改动**：存在 spec/plan 未覆盖的自行发挥？
7. **文档同步**：对照**机读路径源**，diff 命中耦合路径（如 schema ↔ 契约文档 / `context/`）→ 提示对应文档可能需同步更新。<!-- TODO：路径耦合映射表待真实项目路径就位后建，与硬门禁共用同一份机读源。 -->
8. **范围覆盖 / 防提前结束**：spec/plan/acceptance 的全部范围是否做完？有没有**未完成项被当成完成**？**"完成"由 spec/acceptance + 证据定义，不由 AI 自判。**<!-- 机械兜底：Claude Code Stop hook（配 .claude/settings.json；AI 试图结束时跑，输出 {"decision":"block","reason":...} 则挡回去续做；只兜机械可判的"测试过 / 验收机读覆盖"，判断归本自检 + 人审）。延后，参考 ECC hooks/。 -->

> #1（越界）与 #7（文档同步）的机械判定都靠**单一机读路径源**（见 [`high-impact.md`](high-impact.md)）；同一份源在 ② pre-commit hook、③ CI 硬门禁复用。本层（①）是最早、最便宜的一道，**命中即停但可被绕过，非权威**，权威靠 ③。

## 自检输出

- 已改文件清单
- 风险点（对应上面哪一类）
- 是否需要人工确认
- 下一步建议

## 命中即停

命中**越界 / 高影响 / 禁止项 / 无依据改动**任一 → **暂停继续修改**，提示开发者确认后再继续。

## 声称完成前：verification-before-completion[superpowers]

每轮宣称"好了 / 修好了 / 测试过了"**之前**，先跑验证命令、确认输出，**用证据再下结论**（evidence before assertions）。这是 [`forbidden.md`](forbidden.md)「结果完整性」的正向执行程序，与上面第 8 项（范围覆盖）共同防"提前结束 / 谎报完成"。
- 落点：开发循环末（本自检同处）+ PR 前。
- PR 那一刻的权威验证由 [`review-gates.md`](review-gates.md) 的 verification 门禁承担，本条不与之重复。
