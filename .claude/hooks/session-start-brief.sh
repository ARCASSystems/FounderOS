#!/usr/bin/env bash
# SessionStart brief: surfaces open flags, stale cadence, pending decisions,
# [FILL] rows, quarantine failures, and entries past their Decay after.
# Fails gracefully. Never blocks session start.

set +e

# Guard path resolution. Without || exit 0, a failed cd silently produces an
# empty REPO and the rest of the script no-ops without explanation.
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || exit 0
REPO="$(cd "$HOOK_DIR/../.." 2>/dev/null && pwd)" || exit 0
[ -z "$REPO" ] && exit 0

# Platform guard. On Windows (Git Bash, MSYS, Cygwin) the PowerShell hook is
# the canonical writer. Without this guard both hooks fire and the brief prints
# twice on every session start.
case "$(uname -s 2>/dev/null)" in
  MINGW*|MSYS*|CYGWIN*) exit 0 ;;
esac

TODAY="$(date +%Y-%m-%d)"

# Resolve python interpreter once. Many Linux/macOS systems ship `python3` only.
if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  PYTHON=""
fi

# Fresh-install welcome. If core/identity.md is missing but other Founder OS
# markers exist (the hooks directory itself, the bootloader template, or a
# Founder OS settings.json), the user has installed the plugin or cloned the
# repo but has not run setup. Surface a one-line nudge so the experience is
# not silence. Without this banner the new-user path is: open Claude Code,
# see nothing, close. Then exit 0 - the brief sections below require
# core/identity.md and would no-op anyway.
if [ ! -f "$REPO/core/identity.md" ]; then
  if [ -f "$REPO/templates/bootloader-claude-md.md" ] || [ -f "$REPO/.claude/settings.json" ] || [ -f "$REPO/CLAUDE.md" ]; then
    echo "Welcome to Founder OS. Say any of these to begin:"
    echo "  - \"set up Founder OS\""
    echo "  - \"help me set up my second brain\""
    echo "  - \"help me onboard\" or \"what do I do\""
    echo ""
    echo "Your personal brain - your files, queryable by you. Not team-shared. Not always-on."
    echo "(15-20 minutes. The wizard asks who you are, what you run, and what is slowing you down.)"
  fi
  exit 0
fi

echo "=== Session brief ($TODAY) ==="

# --- Consolidated Python pass ---
# Previously this script spawned Python up to 8 times (date math, compliance,
# decay scan x3, tip rotation, observations stale count). Each spawn costs
# ~250ms on Windows. Now one Python process emits all sections in a single
# pass; bash parses the @@SECTION markers below.
BRIEF_PY="$HOOK_DIR/session_start_brief.py"
PY_PAYLOAD=""
if [ -n "$PYTHON" ] && [ -f "$BRIEF_PY" ]; then
  PY_PAYLOAD=$("$PYTHON" "$BRIEF_PY" "$REPO" "$TODAY" 2>/dev/null)
fi

# Extract a single section's body from PY_PAYLOAD. Sections are delimited by
# @@SECTION:<name> and @@END. Missing section = empty string (matches the
# quiet-exit semantics of the old heredocs).
get_section() {
  printf '%s\n' "$PY_PAYLOAD" | awk -v name="$1" '
    $0 == "@@SECTION:" name { capture=1; next }
    capture && $0 == "@@END" { capture=0; exit }
    capture { print }
  '
}

# --- Active queue items ---
QUEUE="$REPO/cadence/queue.md"
if [ ! -f "$QUEUE" ]; then
  echo "Active: 0/3 (queue empty - say \"add to queue: <thing>\" to start)"
else
  ACTIVE_LINES=$(awk '
    /^## ACTIVE/ { in_section=1; next }
    /^## / { if (in_section) exit }
    in_section && /^\(none yet\)/ { next }
    in_section && /^\[/ { print }
  ' "$QUEUE" 2>/dev/null)
  ACTIVE_COUNT=$(printf '%s\n' "$ACTIVE_LINES" | grep -c '^\[' 2>/dev/null || echo 0)
  if [ -z "$ACTIVE_LINES" ] || [ "${ACTIVE_COUNT:-0}" -eq 0 ] 2>/dev/null; then
    echo "Active: 0/3 (queue empty - say \"add to queue: <thing>\" to start)"
  else
    echo "Active: ${ACTIVE_COUNT}/3"
    printf '%s\n' "$ACTIVE_LINES" | head -3 | while IFS= read -r line; do
      echo "  - $line"
    done
  fi
fi

# --- Open flags ---
FLAGS="$REPO/brain/flags.md"
if [ -f "$FLAGS" ]; then
  OPEN_COUNT=$(grep -cE "Status:[[:space:]]*\**OPEN" "$FLAGS" 2>/dev/null)
  # Match any line that has both Severity context AND a Week number >= 3.
  # Covers "Severity Week 3", "Severity: Week 3", "Severity at resolution:
  # Week 3", "Severity frozen at Week 3", "Severity bumped... Week 3", and
  # Week 10+. The .* is line-bounded so won't false-positive across lines.
  WEEK3_COUNT=$(grep -cE "Severity.*Week ([3-9]|[1-9][0-9]+)" "$FLAGS" 2>/dev/null)
  echo "Flags: ${OPEN_COUNT:-0} OPEN, ${WEEK3_COUNT:-0} Week 3+"
  awk '
    /^##+[[:space:]]/ { last_header=$0 }
    /Status:[[:space:]]*\**OPEN/ && last_header != "" {
      print "  - " last_header
      last_header=""
      n++
      if (n>=3) exit
    }
  ' "$FLAGS"
fi

# --- Daily cadence staleness ---
# Backed by the consolidated Python pass above; falls back to a locale-safe
# string comparison when Python is unavailable.
DAILY_LINE=$(get_section daily)
if [ -n "$DAILY_LINE" ]; then
  case "$DAILY_LINE" in
    STALE\|*)
      DAILY_DATE=$(printf '%s' "$DAILY_LINE" | awk -F'|' '{print $2}')
      echo "Daily: STALE (anchor dated $DAILY_DATE, today is $TODAY) - refresh before planning"
      ;;
    CURRENT\|*)
      DAILY_DATE=$(printf '%s' "$DAILY_LINE" | awk -F'|' '{print $2}')
      echo "Daily: current ($DAILY_DATE)"
      ;;
  esac
elif [ -f "$REPO/cadence/daily-anchors.md" ]; then
  # Python-absent fallback. ISO-8601 string compare under LC_ALL=C is byte-stable.
  DAILY_DATE=$(grep -m1 -oE '^## Today: [0-9]{4}-[0-9]{2}-[0-9]{2}' "$REPO/cadence/daily-anchors.md" | awk '{print $3}')
  if [ -n "$DAILY_DATE" ]; then
    if LC_ALL=C [ "$DAILY_DATE" \< "$TODAY" ]; then
      echo "Daily: STALE (anchor dated $DAILY_DATE, today is $TODAY) - refresh before planning"
    else
      echo "Daily: current ($DAILY_DATE)"
    fi
  fi
fi

# --- Weekly cadence staleness ---
WEEKLY_LINE=$(get_section weekly)
if [ -n "$WEEKLY_LINE" ]; then
  case "$WEEKLY_LINE" in
    STALE\|*)
      WEEK_DATE=$(printf '%s' "$WEEKLY_LINE" | awk -F'|' '{print $2}')
      AGE=$(printf '%s' "$WEEKLY_LINE" | awk -F'|' '{print $3}')
      echo "Weekly: STALE (week of $WEEK_DATE, $AGE days old) - run retro before planning"
      ;;
    CURRENT\|*)
      WEEK_DATE=$(printf '%s' "$WEEKLY_LINE" | awk -F'|' '{print $2}')
      echo "Weekly: current (week of $WEEK_DATE)"
      ;;
  esac
fi

# --- Pending decisions ---
# Count only ### headings under the ## Pending section to exclude Resolved/Parked.
DEC="$REPO/context/decisions.md"
if [ -f "$DEC" ]; then
  PENDING=$(awk '
    /^## Pending/ { in_pending=1; next }
    /^## /        { if (in_pending) exit }
    in_pending && /^### / { count++ }
    END { print count+0 }
  ' "$DEC" 2>/dev/null)
  echo "Decisions: ${PENDING:-0} pending"
fi

# --- [FILL] rows in clients ---
CLIENTS="$REPO/context/clients.md"
if [ -f "$CLIENTS" ]; then
  FILL=$(grep -c "\[FILL\]" "$CLIENTS" 2>/dev/null)
  if [ -n "$FILL" ] && [ "$FILL" -gt 0 ] 2>/dev/null; then
    echo "Clients: $FILL [FILL] rows awaiting data"
  fi
fi

# --- Connector status ---
# Surfaces tools the user has not connected yet so a skipped connector does not
# stay silent. Written by the `connect` skill to connectors/status.md (no
# secrets; gitignored per-user state). Quiet exit when the file is absent.
CONNECTORS="$REPO/connectors/status.md"
if [ -f "$CONNECTORS" ]; then
  NOT_CONNECTED=$(grep -E '^- .*:[[:space:]]*not connected' "$CONNECTORS" 2>/dev/null)
  if [ -n "$NOT_CONNECTED" ]; then
    echo ""
    echo "Connectors not set up:"
    printf '%s\n' "$NOT_CONNECTED" | sed -E 's/^- ([^:]+):.*/  - \1 - say "connect \1"/' | head -5
  fi
fi

# --- Unprocessed rants ---
# Surfaces the rant-to-action gap. Without this line, rants captured via
# /rant sit in brain/rants/ until the user remembers /dream exists (15-25%
# of users, per pre-v1.23 review). Count rant entries (not files) where
# the frontmatter line `processed: false` is present.
RANTS_DIR="$REPO/brain/rants"
if [ -d "$RANTS_DIR" ]; then
  UNPROC=$(grep -h "^processed:[[:space:]]*false" "$RANTS_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
  if [ -n "$UNPROC" ] && [ "$UNPROC" -gt 0 ] 2>/dev/null; then
    if [ "$UNPROC" -ge 3 ] 2>/dev/null; then
      echo "Unprocessed rants: $UNPROC - say \"process my rants\" or run /founder-os:dream. They go stale at 30 days."
    else
      echo "Unprocessed rants: $UNPROC (say \"process my rants\" or run /founder-os:dream to distil them)"
    fi
  fi
fi

# --- Compliance deadlines (legal-compliance skill) ---
# Surfaces entries in context/compliance.md with a date within the next 30 days
# OR overdue. Quiet exit if file missing - skill is opt-in via
# /founder-os:legal-setup. Backed by the consolidated Python pass above.
COMPLIANCE_HITS=$(get_section compliance)
if [ -n "$COMPLIANCE_HITS" ]; then
  echo ""
  OVERDUE_LINE=$(printf '%s\n' "$COMPLIANCE_HITS" | grep '^OVERDUE|' || true)
  UPCOMING_LINE=$(printf '%s\n' "$COMPLIANCE_HITS" | grep '^UPCOMING|' || true)
  if [ -n "$OVERDUE_LINE" ]; then
    OVERDUE_COUNT=$(printf '%s' "$OVERDUE_LINE" | cut -d'|' -f2)
    echo "Compliance: $OVERDUE_COUNT OVERDUE deadline(s) - file or escalate today"
    printf '%s\n' "$COMPLIANCE_HITS" | grep -A100 '^OVERDUE|' | grep -v '^OVERDUE|' | grep -v '^UPCOMING|' | head -3
  fi
  if [ -n "$UPCOMING_LINE" ]; then
    UPCOMING_COUNT=$(printf '%s' "$UPCOMING_LINE" | cut -d'|' -f2)
    echo "Compliance: $UPCOMING_COUNT deadline(s) within 30 days"
    printf '%s\n' "$COMPLIANCE_HITS" | grep -A100 '^UPCOMING|' | grep -v '^UPCOMING|' | grep -v '^OVERDUE|' | head -3
  fi
fi

# --- Quarantine ---
QUARANTINE="$REPO/system/quarantine.md"
if [ -f "$QUARANTINE" ]; then
  Q_ACTIVE=$(awk '
    /^[[:space:]]*```/ { fence = !fence; next }
    fence { next }
    /^\*\*Status:\*\*[[:space:]]*ACTIVE/ { n++ }
    END { print n+0 }
  ' "$QUARANTINE")
  if [ -n "$Q_ACTIVE" ] && [ "$Q_ACTIVE" -gt 0 ] 2>/dev/null; then
    Q_LATEST=$(awk '
      /^[[:space:]]*```/ { fence = !fence; next }
      fence { next }
      /^## [0-9]{4}-[0-9]{2}-[0-9]{2}/ { print; exit }
    ' "$QUARANTINE")
    echo ""
    echo "Quarantine: $Q_ACTIVE ACTIVE failure(s) - check system/quarantine.md"
    [ -n "$Q_LATEST" ] && echo "  most recent: $Q_LATEST"
  fi
fi

# --- Review Due (decay scan) ---
# Convention: rules/entry-conventions.md. Backed by the consolidated Python
# pass above which scans brain/flags.md, brain/patterns.md, and
# brain/decisions-parked.md in one process.
HITS=$(get_section decay)
if [ -n "$HITS" ]; then
  DECAY_HITS=$(printf '%s\n' "$HITS" | grep '^DECAY|' || true)
  NOANCHOR_HITS=$(printf '%s\n' "$HITS" | grep '^NOANCHOR|' || true)
  if [ -n "$DECAY_HITS" ]; then
    COUNT=$(printf '%s\n' "$DECAY_HITS" | wc -l | tr -d ' ')
    echo ""
    echo "Review Due ($COUNT past decay):"
    printf '%s\n' "$DECAY_HITS" | head -5 | while IFS='|' read -r tag head age; do
      echo "  - $head (decayed ${age}d ago)"
    done
  fi
  if [ -n "$NOANCHOR_HITS" ]; then
    COUNT=$(printf '%s\n' "$NOANCHOR_HITS" | wc -l | tr -d ' ')
    echo ""
    echo "Decay anchor missing ($COUNT entries with relative Decay after but no First observed / Date parked):"
    printf '%s\n' "$NOANCHOR_HITS" | head -5 | while IFS='|' read -r tag head age; do
      echo "  - $head"
    done
  fi
fi

# --- Memory/Retrieval diff (clients folders without memory entries) ---
# Closes the cross-session gap where cloud or parallel sessions create
# clients/<slug>/ folders that the next local session boots blind to.
MEMORY_DIFF="$REPO/scripts/memory-diff.py"
if [ -f "$MEMORY_DIFF" ] && [ -n "$PYTHON" ]; then
  $PYTHON "$MEMORY_DIFF" "$REPO" 2>/dev/null
fi

# --- Founder next move (propose-engine nudge) ---
# Fires only when core/identity.md carries a ## Founder Snapshot (founder /
# team_of_one installs). READY means the brain can propose a real move; THIN
# names the field still needed. Keeps the propose engine discoverable daily.
FOUNDER_MOVE=$(get_section founder_move)
if [ -n "$FOUNDER_MOVE" ]; then
  case "$FOUNDER_MOVE" in
    READY)
      echo ""
      echo "Your brain is ready - say \"what should I focus on next?\" for your move toward a paying customer."
      ;;
    THIN\|*)
      MISSING=$(printf '%s' "$FOUNDER_MOVE" | cut -d'|' -f2)
      echo ""
      echo "Almost ready to propose - tell me your $MISSING in one line and I can name your next move."
      ;;
  esac
fi

# --- Tip (rotates weekly, surfaces one underused capability) ---
# Backed by the consolidated Python pass above. Fresh-install gate, last-used
# tracking, and weekly rotation logic all live in session_start_brief.py.
TIP=$(get_section tip)
if [ -n "$TIP" ]; then
  echo ""
  echo "Tip: $TIP"
fi

# --- Observations (opt-in telemetry, FOUNDER_OS_OBSERVATIONS=1 to enable) ---
# Printed inside the brief so the visual closure (=== end brief ===) is the
# last line.
if [ -n "$FOUNDER_OS_OBSERVATIONS" ] && [ "$FOUNDER_OS_OBSERVATIONS" = "1" ]; then
  echo "Observations: enabled (writing to brain/observations/<date>.jsonl)"
  # --- Observation rollup state ---
  OBS_DIR="$REPO/brain/observations"
  ROLLUP_DIR="$OBS_DIR/_rollups"
  ROLLUP_COUNT=0
  if [ -d "$ROLLUP_DIR" ]; then
    ROLLUP_COUNT=$(ls -1 "$ROLLUP_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ' || echo 0)
  fi
  echo "  Rollups: ${ROLLUP_COUNT} weekly summaries in brain/observations/_rollups/"
  # Stale-jsonl count comes from the consolidated Python pass above (emitted
  # only when FOUNDER_OS_OBSERVATIONS=1, so no extra process spawned here).
  STALE=$(get_section observations)
  if [ -n "$STALE" ] && [ "${STALE:-0}" -gt 0 ] 2>/dev/null; then
    echo "  ${STALE} JSONL files older than 10 days - say 'roll up observations' to compress old logs."
  fi
else
  echo "Observations: disabled (set FOUNDER_OS_OBSERVATIONS=1 to enable)"
fi

echo "=== end brief ==="

exit 0
