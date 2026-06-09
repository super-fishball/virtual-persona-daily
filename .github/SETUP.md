# GitHub 仓库设置（必读）

> 本项目的治理依赖若干 **GitHub 仓库设置**（不是代码文件，需在仓库 Settings 里配置）。
> 复制本模板后，**必须**按下面配置，否则合并门禁、发布审批等不会生效。

## 1. Branch Protection Rules（分支保护）

对受保护分支（如 `main`）启用：

- [ ] **Require a pull request before merging**（合并前必须经 PR）
- [ ] **Require approvals**，并勾选 **Require review from Code Owners**（要求 CODEOWNERS 审批）
- [ ] **Require status checks to pass before merging**，把以下设为必需：
  - [ ] verification（build / test / lint / typecheck / security）
  - [ ] Agent Review（启用 agent-review 工作流后）
- [ ] **Require branches to be up to date before merging**
- [ ] 禁止 `force-push` 与删除受保护分支

> 合并门禁 = verification 通过 + Agent Review 通过 + CODEOWNERS 审批，三者齐备方可合并。

## 2. Environment Protection Rules（环境保护 / 发布审批）

对生产环境（如 `production`）：

- [ ] **Required reviewers**：部署到生产前必须人工审批
- [ ] **Deployment branches**：限制只有受保护分支可部署
- [ ] 生产操作由人工执行，AI 不参与（见 [`../rules/forbidden.md`](../rules/forbidden.md)）

## 3. CODEOWNERS 生效

- [ ] 填写 [`CODEOWNERS`](CODEOWNERS)，把 `@TODO-*` 替换为真实账号 / 团队

## 4. Secrets（启用 Agent Review 时需要）

- [ ] `ANTHROPIC_API_KEY` — Claude 审查 Agent
- [ ] `OPENAI_API_KEY` — Codex 审查 Agent

## 5. 启用 Agent Review 工作流

- [ ] [`workflows/agent-review.yml.example`](workflows/agent-review.yml.example) 默认失活（`.example` 后缀，GitHub 不执行）。
- [ ] 补全其中的 SDK 调用逻辑 + 上面的 secrets 后，**去掉 `.example` 后缀**改回 `agent-review.yml` 即启用。
