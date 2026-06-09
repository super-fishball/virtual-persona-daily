#!/usr/bin/env bash
# PreToolUse hook —— development-guard 的「①.5 Claude Code hook 层」
#   机械·会话内·可绕过；非权威，权威靠 PR 门禁（Agent Review + 分支保护）。
# 作用：编辑/写文件前，对照「单一机读路径源」拦"高影响/禁止路径"与"跨子项目越界"。
# 输入：stdin JSON（含 tool_input.file_path）。
# 输出：exit 0 放行 / exit 2 拦截（stderr 文案回喂给 AI，命中即停提示人工确认）。
#
# ⚠️ 模板脚手架：机制写实，但两处项目特定值需填——
#   (1) TASK_SCOPE：本任务允许的子项目（建议由分支名/环境变量/plan 注入）；
#   (2) rules/high-impact.paths：高影响/禁止路径清单（单一机读源，见该文件）。
set -uo pipefail

INPUT="$(cat)"
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

# 按任务注入：source 本地 .claude/task.env（gitignored）→ TASK_SCOPE / TEST_CMD。
# 见 .claude/task.env.example；改文件即生效；不存在则按空处理（不查越界）。
[ -f "$ROOT/.claude/task.env" ] && . "$ROOT/.claude/task.env"

# 取目标文件路径（无 python3 时可换 jq / node）
FILE="$(printf '%s' "$INPUT" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null || true)"
[ -z "$FILE" ] && exit 0   # 非文件类工具 → 放行

REL="${FILE#"$ROOT"/}"     # 转相对仓库根

# (1) 高影响 / 禁止路径：单一机读源
PATHS_FILE="$ROOT/rules/high-impact.paths"
if [ -f "$PATHS_FILE" ]; then
  while IFS= read -r pat; do
    case "$pat" in ''|\#*) continue ;; esac
    # shellcheck disable=SC2254
    case "$REL" in $pat)
      echo "development-guard｜命中高影响/禁止路径 [${pat}]：${REL} → 暂停，需人工确认（见 rules/high-impact.paths / high-impact.md）" >&2
      exit 2 ;;
    esac
  done < "$PATHS_FILE"
fi

# (2) 跨子项目越界（目录结构即机读源）
TASK_SCOPE="${TASK_SCOPE:-}"   # 由 .claude/task.env 注入（见顶部 source）；空=不查越界。例：servers/api
if [ -n "$TASK_SCOPE" ]; then
  case "$REL" in
    "$TASK_SCOPE"/*) : ;;                       # 在本任务范围内 → 放行
    apps/*|servers/*)
      echo "development-guard｜越界：本任务范围=${TASK_SCOPE}，却改 ${REL} → 跨子项目须走 feature 层契约先行再拆分，暂停" >&2
      exit 2 ;;
  esac
fi

exit 0
