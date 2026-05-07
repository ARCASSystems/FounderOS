#!/usr/bin/env bash
# PostToolUse observation hook (opt-in).
#
# Appends a one-line JSON observation to brain/observations/<YYYY-MM-DD>.jsonl
# every time a tool call completes. Off by default. Enable by setting
# FOUNDER_OS_OBSERVATIONS=1 in your shell environment.
#
# Privacy: logs file paths, command summaries, and a short intent string.
# Never logs full diffs, full file content, or full command output.
#
# This hook MUST exit 0 in all cases. A failing hook cannot block a tool call.

# Hard guard: any internal error must not block tool execution.
{
  # Opt-in gate.
  if [ "${FOUNDER_OS_OBSERVATIONS:-0}" != "1" ]; then
    exit 0
  fi

  # Platform guard. On Windows (Git Bash, MSYS, Cygwin) the PowerShell hook is
  # the canonical writer. Both hooks are wired in settings.json, so without
  # this guard each tool call would append twice on Windows.
  case "$(uname -s 2>/dev/null)" in
    MINGW*|MSYS*|CYGWIN*)
      exit 0
      ;;
  esac

  HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || exit 0
  REPO="$(cd "$HOOK_DIR/../.." 2>/dev/null && pwd)" || exit 0

  # Read hook input from stdin. Tolerate missing or malformed JSON.
  INPUT=""
  if [ ! -t 0 ]; then
    INPUT="$(cat 2>/dev/null || true)"
  fi

  # Extract fields with jq if available, otherwise fall back to a tolerant
  # python parse, otherwise empty strings.
  TOOL_NAME=""
  SESSION_ID=""
  FILE_PATH=""
  NEW_STRING=""
  CONTENT=""
  COMMAND=""
  PATTERN=""
  SEARCH_PATH=""

  # Resolve python interpreter once. Used by both the python-fallback parse and
  # the json_escape helper below.
  if command -v python3 >/dev/null 2>&1; then
    PYBIN=python3
  elif command -v python >/dev/null 2>&1; then
    PYBIN=python
  else
    PYBIN=""
  fi

  if [ -n "$INPUT" ] && command -v jq >/dev/null 2>&1; then
    TOOL_NAME=$(printf '%s' "$INPUT" | jq -r '.tool_name // ""' 2>/dev/null || echo "")
    SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // ""' 2>/dev/null || echo "")
    FILE_PATH=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // ""' 2>/dev/null || echo "")
    NEW_STRING=$(printf '%s' "$INPUT" | jq -r '.tool_input.new_string // ""' 2>/dev/null || echo "")
    CONTENT=$(printf '%s' "$INPUT" | jq -r '.tool_input.content // ""' 2>/dev/null || echo "")
    COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null || echo "")
    PATTERN=$(printf '%s' "$INPUT" | jq -r '.tool_input.pattern // ""' 2>/dev/null || echo "")
    SEARCH_PATH=$(printf '%s' "$INPUT" | jq -r '.tool_input.path // ""' 2>/dev/null || echo "")
  elif [ -n "$INPUT" ]; then
    if [ -n "$PYBIN" ]; then
      PY_SCRIPT='import json, sys
try:
    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}
except Exception:
    data = {}
if not isinstance(data, dict):
    data = {}
ti = data.get("tool_input") or {}
if not isinstance(ti, dict):
    ti = {}
def g(d, k):
    v = d.get(k, "")
    return "" if v is None else str(v)
print(g(data, "tool_name"))
print(g(data, "session_id"))
print(g(ti, "file_path"))
print(g(ti, "new_string"))
print(g(ti, "content"))
print(g(ti, "command"))
print(g(ti, "pattern"))
print(g(ti, "path"))
'
      PARSED=$(printf '%s' "$INPUT" | "$PYBIN" -c "$PY_SCRIPT" 2>/dev/null) || PARSED=""
      if [ -n "$PARSED" ]; then
        # Read parsed lines into variables.
        TOOL_NAME=$(printf '%s\n' "$PARSED" | sed -n '1p')
        SESSION_ID=$(printf '%s\n' "$PARSED" | sed -n '2p')
        FILE_PATH=$(printf '%s\n' "$PARSED" | sed -n '3p')
        NEW_STRING=$(printf '%s\n' "$PARSED" | sed -n '4p')
        CONTENT=$(printf '%s\n' "$PARSED" | sed -n '5p')
        COMMAND=$(printf '%s\n' "$PARSED" | sed -n '6p')
        PATTERN=$(printf '%s\n' "$PARSED" | sed -n '7p')
        SEARCH_PATH=$(printf '%s\n' "$PARSED" | sed -n '8p')
      fi
    fi
  fi

  # Build the intent string from the tool's purpose.
  case "$TOOL_NAME" in
    Read)
      INTENT="read ${FILE_PATH}"
      ;;
    Edit|Write)
      SNIPPET=""
      if [ -n "$NEW_STRING" ]; then
        SNIPPET="$NEW_STRING"
      else
        SNIPPET="$CONTENT"
      fi
      # Strip newlines and tabs from snippet, then truncate to 80 chars.
      SNIPPET=$(printf '%s' "$SNIPPET" | tr '\n\r\t' '   ')
      SNIPPET="${SNIPPET:0:80}"
      INTENT="edit ${FILE_PATH} - ${SNIPPET}"
      ;;
    Bash)
      CMD_SNIP=$(printf '%s' "$COMMAND" | tr '\n\r\t' '   ')
      CMD_SNIP="${CMD_SNIP:0:80}"
      INTENT="bash - ${CMD_SNIP}"
      ;;
    Grep)
      INTENT="grep ${PATTERN} in ${SEARCH_PATH}"
      ;;
    Glob)
      INTENT="glob ${PATTERN}"
      ;;
    "")
      INTENT="unknown"
      ;;
    *)
      INTENT="$TOOL_NAME"
      ;;
  esac

  # Strip any control characters and newlines from intent, then truncate to 120.
  INTENT=$(printf '%s' "$INTENT" | tr -d '\000-\010\013\014\016-\037\177' | tr '\n\r\t' '   ')
  INTENT="${INTENT:0:120}"

  # Resolve "file" field. Empty string when no file was touched.
  FILE_FIELD="$FILE_PATH"

  # Compose ISO 8601 timestamp with timezone offset.
  TS=""
  if date --version >/dev/null 2>&1; then
    # GNU date
    TS=$(date +"%Y-%m-%dT%H:%M:%S%:z")
  else
    # BSD/macOS date or other; fallback to %z (no colon).
    TS=$(date +"%Y-%m-%dT%H:%M:%S%z")
  fi
  TODAY=$(date +"%Y-%m-%d")

  OBS_DIR="$REPO/brain/observations"
  OBS_FILE="$OBS_DIR/${TODAY}.jsonl"

  mkdir -p "$OBS_DIR" 2>/dev/null || exit 0

  # JSON-escape helper. Prefer jq if available, otherwise python, otherwise
  # a minimal manual escape.
  json_escape() {
    local input="$1"
    if command -v jq >/dev/null 2>&1; then
      printf '%s' "$input" | jq -Rs '.' 2>/dev/null
      return
    fi
    if [ -n "${PYBIN:-}" ]; then
      printf '%s' "$input" | "$PYBIN" -c 'import json,sys; print(json.dumps(sys.stdin.read()))' 2>/dev/null
      return
    fi
    # Manual escape fallback. Strip control chars (including DEL) first so the
    # final line cannot contain raw tab/newline/etc. Then escape backslash and
    # double quote, then wrap in quotes.
    local stripped esc
    stripped=$(printf '%s' "$input" | tr -d '\000-\037\177')
    esc=$(printf '%s' "$stripped" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g')
    printf '"%s"' "$esc"
  }

  TS_J=$(json_escape "$TS")
  TOOL_J=$(json_escape "$TOOL_NAME")
  FILE_J=$(json_escape "$FILE_FIELD")
  INTENT_J=$(json_escape "$INTENT")
  SESSION_J=$(json_escape "$SESSION_ID")

  # Single-line JSON. Each value is already wrapped in quotes by json_escape.
  printf '{"ts":%s,"tool":%s,"file":%s,"intent":%s,"session":%s}\n' \
    "$TS_J" "$TOOL_J" "$FILE_J" "$INTENT_J" "$SESSION_J" >> "$OBS_FILE" 2>/dev/null || exit 0
} 2>/dev/null

exit 0
