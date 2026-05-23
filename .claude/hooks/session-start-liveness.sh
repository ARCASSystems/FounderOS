#!/usr/bin/env bash
# SessionStart liveness: prints one line about how long since the operator
# last ran /since-last-session. Reads brain/.last-session, no other state.
#
# Contract:
#   - DOES NOT update or write brain/.last-session. Only /since-last-session
#     writes the marker. This hook is read-only on that file.
#   - DOES NOT call any LLM. Pure file read + integer math. Free-tier safe.
#   - DOES NOT block session start. Exits within 100ms on a reasonable
#     filesystem. Any error path exits 0 silently so the brief above is
#     never delayed.
#
# Runs after session-start-brief.sh in the SessionStart matcher block so the
# brief prints first and this one-liner appears below it.

set +e

# Guard path resolution. Without || exit 0, a failed cd silently produces an
# empty REPO and the rest of the script no-ops without explanation.
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || exit 0
REPO="$(cd "$HOOK_DIR/../.." 2>/dev/null && pwd)" || exit 0
[ -z "$REPO" ] && exit 0

# Platform guard. On Windows (Git Bash, MSYS, Cygwin) the PowerShell hook is
# the canonical writer. Without this guard both hooks fire and the liveness
# line prints twice on every session start.
case "$(uname -s 2>/dev/null)" in
  MINGW*|MSYS*|CYGWIN*) exit 0 ;;
esac

# Gate on core/identity.md. Matches the brief: that is the canonical signal
# of a FounderOS install that has finished setup. On a fresh pre-setup repo
# the brief already prints the welcome banner; a second liveness line on top
# would be noise.
if [ ! -f "$REPO/core/identity.md" ]; then
  exit 0
fi

MARKER="$REPO/brain/.last-session"

if [ ! -f "$MARKER" ]; then
  echo "No prior synthesis marker found. Run /since-last-session to initialize."
  exit 0
fi

# Resolve Python. The elapsed-hours math + ISO-8601 parse goes through Python
# because portable bash date parsing across Windows / macOS / Linux is brittle.
if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  # No Python available. Silent exit - we cannot parse the marker safely.
  exit 0
fi

# One Python pass: parse marker, compare to now, emit a single line.
"$PYTHON" - "$MARKER" <<'PY' 2>/dev/null
import sys
from datetime import datetime, timezone

marker_path = sys.argv[1]
try:
    with open(marker_path, "r", encoding="utf-8") as f:
        raw = f.read().strip()
except OSError:
    sys.exit(0)

if not raw:
    print("Synthesis marker malformed at brain/.last-session. Run /since-last-session to repair.")
    sys.exit(0)

try:
    marker = datetime.fromisoformat(raw)
except ValueError:
    print("Synthesis marker malformed at brain/.last-session. Run /since-last-session to repair.")
    sys.exit(0)

if marker.tzinfo is None:
    # Spec: marker is ISO-8601 with timezone offset. A naive timestamp is
    # malformed.
    print("Synthesis marker malformed at brain/.last-session. Run /since-last-session to repair.")
    sys.exit(0)

now = datetime.now(timezone.utc)
delta = now - marker
elapsed_seconds = delta.total_seconds()

if elapsed_seconds < 0:
    print("Synthesis marker is in the future; ignoring. Run /since-last-session if you want to repair it.")
    sys.exit(0)

if elapsed_seconds < 3600:
    print("Less than an hour since you last ran /since-last-session.")
    sys.exit(0)

hours = int(elapsed_seconds // 3600)
print(f"{hours} hours since you last ran /since-last-session. Run /since-last-session for the delta, or /strategic-read for a full state-of-OS report.")
PY

exit 0
