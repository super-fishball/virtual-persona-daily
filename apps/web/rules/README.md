# apps/web 本地规则索引

本目录只描述 `apps/web` **特有**的约束；通用规则继承自根 [`../../../rules/`](../../../rules/)。

## 文件清单

| 文件 | 作用 |
|---|---|
| [`scope.md`](scope.md) | 可修改范围、跨项目边界 |
| [`high-impact.md`](high-impact.md) | 本子项目需升级评审的高影响区 |
| [`forbidden.md`](forbidden.md) | 本子项目额外禁止项 |
| [`development-guard.md`](development-guard.md) | 前端栈特有的额外自检步骤（通用流程继承自根 `rules/`） |

> review-gates 无本地增量，直接继承根 [`../../../rules/review-gates.md`](../../../rules/review-gates.md)；如出现前端特有的门禁触发，再建本地 `review-gates.md`。

## 与根规则的关系

本地规则**只能更严或补充**，不得放宽或违反根 `forbidden.md`。冲突时暂停并请开发者裁定。
