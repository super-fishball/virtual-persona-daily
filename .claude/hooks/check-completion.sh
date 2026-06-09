#!/usr/bin/env bash
# Stop hook —— 防 Agent 提前结束（development-guard 第 8 类「范围覆盖」的机械兜底）
#   机械·会话内·可绕过；非权威，权威靠 PR 门禁。
# AI 试图结束当前回合时触发：只兜「机械可判」的两件——测试过 + 验收机读覆盖；
#   "需求是否真做对"这类语义判断兜不住，仍归 ① AI 自检 + 人审。
# 输出：exit 0 放行结束 / stdout 输出 {"decision":"block","reason":...} 挡停并把 reason 回喂 AI 续做。
#
# ⚠️ 模板脚手架：两处项目特定值需填——TEST_CMD、验收↔证据机读覆盖判定。
set -uo pipefail

INPUT="$(cat)"

# 防死循环：已因 Stop hook 续过一轮 → 放行（stop_hook_active=true）
ACTIVE="$(printf '%s' "$INPUT" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("stop_hook_active",False))' 2>/dev/null || echo False)"
[ "$ACTIVE" = "True" ] && exit 0

# (1) 测试必须过
TEST_CMD="${TEST_CMD:-}"   # TODO（真实项目填）：如 "npm test" / "pytest -q"
if [ -n "$TEST_CMD" ]; then
  if ! eval "$TEST_CMD" >/tmp/_stop_test.log 2>&1; then
    printf '{"decision":"block","reason":"%s"}\n' "测试未通过，任务未完成，请修复后再结束（日志 /tmp/_stop_test.log）"
    exit 0
  fi
fi

# (2) 验收 ↔ 证据 机读覆盖：每条验收都有过测试才算完成
# TODO（真实项目填）：解析 feature/<…>/acceptance 的机读清单 vs 测试覆盖映射；
#   有验收条无对应过测试 → printf '{"decision":"block","reason":"验收条 X 无测试覆盖，未完成"}' ; exit 0

exit 0
