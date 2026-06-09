<!-- 本模板字段为必填，缺项的 PR 不予合并。 -->

## 变更说明

<!-- 这个 PR 做了什么、为什么。 -->

## spec / plan 引用

- spec: <!-- 链接到对应 spec/*.md，简单需求豁免请说明原因 -->
- plan: <!-- 链接到对应 plan/*.md -->
- feature（如跨子项目）: <!-- 链接到 feature 总 spec / 契约 -->

## AI 参与范围

- [ ] 本 PR 有 AI Agent 参与
- AI 参与的部分：<!-- 哪些文件/模块由 AI 起草或修改 -->
- 人工改动 / 复核的部分：<!-- -->

## 影响面

- [ ] 仅限单一子项目（专人专项，未跨边界）
- [ ] 触及高影响区（见 rules/high-impact.md）→ 已申请升级评审
- [ ] 改动跨子项目契约 → 已更新 feature 层契约
- 影响范围说明：<!-- -->

## 自检与测试

- [ ] 已执行 development-guard 自检，无未处理的越界/禁止项
- [ ] 测试真实反映 spec 预期，未为适配实现而弱化测试
- [ ] verification（build/test/lint/typecheck/security）通过
