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
    echo "Welcome to Founder OS. Say \"set up Founder OS\" to get started."
    echo "(15-20 minutes. The wizard asks who you are, what you run, and what is slowing you down.)"
  fi
  exit 0
fi

echo "=== Session brief ($TODAY) ==="

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
  WEEK3_COUNT=$(grep -cE "Severity (Week 3|at resolution: Week 3)" "$FLAGS" 2>/dev/null)
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
DAILY="$REPO/cadence/daily-anchors.md"
if [ -f "$DAILY" ]; then
  DAILY_DATE=$(grep -m1 -oE '^## Today: [0-9]{4}-[0-9]{2}-[0-9]{2}' "$DAILY" | awk '{print $3}')
  if [ -n "$DAILY_DATE" ]; then
    if [ -n "$PYTHON" ]; then
      # Delegate the comparison to Python so collation order is locale-stable.
      DAILY_DELTA=$($PYTHON -c "from datetime import date; a=date.fromisoformat('$DAILY_DATE'); b=date.fromisoformat('$TODAY'); print((b-a).days)" 2>/dev/null)
      if [ -n "$DAILY_DELTA" ] && [ "$DAILY_DELTA" -gt 0 ] 2>/dev/null; then
        echo "Daily: STALE (anchor dated $DAILY_DATE, today is $TODAY) - refresh before planning"
      else
        echo "Daily: current ($DAILY_DATE)"
      fi
    else
      # Python absent. ISO-8601 string compare under LC_ALL=C is byte-stable.
      if LC_ALL=C [ "$DAILY_DATE" \< "$TODAY" ]; then
        echo "Daily: STALE (anchor dated $DAILY_DATE, today is $TODAY) - refresh before planning"
      else
        echo "Daily: current ($DAILY_DATE)"
      fi
    fi
  fi
fi

# --- Weekly cadence staleness ---
WEEKLY="$REPO/cadence/weekly-commitments.md"
if [ -f "$WEEKLY" ]; then
  WEEK_DATE=$(grep -m1 -oE '^## Week of [0-9]{4}-[0-9]{2}-[0-9]{2}' "$WEEKLY" | awk '{print $4}')
  if [ -n "$WEEK_DATE" ] && [ -n "$PYTHON" ]; then
    AGE=$($PYTHON -c "from datetime import date; a=date.fromisoformat('$WEEK_DATE'); b=date.fromisoformat('$TODAY'); print((b-a).days)" 2>/dev/null)
    if [ -n "$AGE" ] && [ "$AGE" -gt 6 ] 2>/dev/null; then
      echo "Weekly: STALE (week of $WEEK_DATE, $AGE days old) - run retro before planning"
    else
      echo "Weekly: current (week of $WEEK_DATE)"
    fi
  fi
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
# OR overdue. Format expected: "## YYYY-MM-DD - <description>" headings.
# Quiet exit if file missing - skill is opt-in via /founder-os:legal-setup.
COMPLIANCE="$REPO/context/compliance.md"
if [ -f "$COMPLIANCE" ] && [ -n "$PYTHON" ]; then
  COMPLIANCE_HITS=$($PYTHON - "$COMPLIANCE" "$TODAY" <<'PYEOF' 2>/dev/null
import sys, re
from datetime import date
path, today_str = sys.argv[1], sys.argv[2]
today = date.fromisoformat(today_str)
upcoming = []
overdue = []
try:
    with open(path, encoding='utf-8') as f:
        lines = f.read().splitlines()
except Exception:
    sys.exit(0)
heading_re = re.compile(r'^##\s+(\d{4}-\d{2}-\d{2})\s*[-:]\s*(.+?)\s*$')
status_re = re.compile(r'^\s*-\s*Status:\s*(\w+)', re.IGNORECASE)
i = 0
while i < len(lines):
    m = heading_re.match(lines[i])
    if not m:
        i += 1
        continue
    deadline = date.fromisoformat(m.group(1))
    desc = m.group(2)
    status = 'OPEN'
    j = i + 1
    while j < len(lines) and not lines[j].startswith('## '):
        sm = status_re.match(lines[j])
        if sm:
            status = sm.group(1).upper()
            break
        j += 1
    if status == 'DONE':
        i = j
        continue
    delta = (deadline - today).days
    if delta < 0:
        overdue.append((deadline, desc, abs(delta)))
    elif delta <= 30:
        upcoming.append((deadline, desc, delta))
    i = j
if overdue:
    print(f'OVERDUE|{len(overdue)}')
    for d, desc, days_past in sorted(overdue)[:3]:
        print(f'  {d} - {desc} (overdue {days_past}d)')
if upcoming:
    print(f'UPCOMING|{len(upcoming)}')
    for d, desc, days_to in sorted(upcoming)[:3]:
        print(f'  {d} - {desc} (in {days_to}d)')
PYEOF
  )
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
# Convention: rules/entry-conventions.md.
scan_decay() {
  local file="$1" heading_re="$2"
  [ ! -f "$file" ] && return
  [ -z "$PYTHON" ] && return
  $PYTHON - "$file" "$heading_re" "$TODAY" <<'PYEOF' 2>/dev/null
import sys, re
from datetime import date, timedelta
path, heading_re, today_str = sys.argv[1], sys.argv[2], sys.argv[3]
today = date.fromisoformat(today_str)
with open(path, encoding='utf-8') as f:
    lines = f.read().splitlines()
hpat = re.compile(heading_re)
def anchor_date(entry, file):
    h = entry[0]
    if 'flags.md' in file:
        m = re.search(r'(\d{4}-\d{2}-\d{2})', h)
        if m: return date.fromisoformat(m.group(1))
    for l in entry:
        m = re.match(r'\s*-?\s*Date parked:\s*(\d{4}-\d{2}-\d{2})', l)
        if m: return date.fromisoformat(m.group(1))
        m = re.match(r'\s*-?\s*First observed:\s*(\d{4}-\d{2}-\d{2})', l)
        if m: return date.fromisoformat(m.group(1))
    return None
def process(entry):
    if not entry: return
    head = entry[0].strip()
    decay = None
    missing_anchor = False
    for l in entry:
        m = re.match(r'\s*-?\s*Decay after:\s*(.+?)\s*$', l)
        if m:
            val = m.group(1).strip()
            if re.match(r'^\d{4}-\d{2}-\d{2}$', val):
                decay = date.fromisoformat(val)
            else:
                m2 = re.match(r'^(\d+)d$', val)
                if m2:
                    a = anchor_date(entry, path)
                    if a: decay = a + timedelta(days=int(m2.group(1)))
                    else: missing_anchor = True
            break
    if decay and decay < today:
        age = (today - decay).days
        print(f"DECAY|{head}|{age}")
    elif missing_anchor:
        print(f"NOANCHOR|{head}|0")
entry = []
for ln in lines:
    if hpat.match(ln):
        process(entry); entry = [ln]
    else:
        entry.append(ln)
process(entry)
PYEOF
}

if [ -n "$PYTHON" ]; then
  HITS=""
  HITS="$HITS$(scan_decay "$REPO/brain/flags.md" '^##\s')"$'\n'
  HITS="$HITS$(scan_decay "$REPO/brain/patterns.md" '^###\s')"$'\n'
  HITS="$HITS$(scan_decay "$REPO/brain/decisions-parked.md" '^###\s')"
  HITS=$(printf '%s\n' "$HITS" | grep -v '^$' || true)
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

# --- Tip (rotates weekly, surfaces one underused capability) ---
# Scans brain/log.md for explicit action tags only. Counts #used-<capability>
# or #acted lines that name the capability. Picks a capability not
# invoked in 14+ days that matches current state. Rotates the pick weekly so
# the same tip does not repeat. Fresh-install gate: the log must have at
# least 10 entries (### date headings) AND span at least 30 days from the
# earliest entry to today. Below that floor the Tip is omitted entirely so
# new users don't see capability pitches before they have any state. If no
# eligible tip, the line is omitted (do NOT print "no tip" or similar).
LOG="$REPO/brain/log.md"
if [ -f "$LOG" ] && [ -n "$PYTHON" ]; then
  TIP=$($PYTHON - "$LOG" "$TODAY" <<'PYEOF' 2>/dev/null
import sys, re
from datetime import date, timedelta
log_path, today_str = sys.argv[1], sys.argv[2]
today = date.fromisoformat(today_str)
# Capabilities with their natural-language tip lines. Order matters for the
# weekly rotation tie-break.
TIPS = [
    ("decision-framework", "Try saying \"help me decide\" next time you're stuck on a choice - the decision-framework skill walks you through it."),
    ("priority-triage", "Say \"what should I focus on next\" when the open list grows past five - priority-triage cuts it down to one thing."),
    ("forcing-questions", "Try \"force me to think this through\" before starting something new - forcing-questions runs six tests on the idea before you commit."),
    ("weekly-review", "Say \"run my weekly review\" on Friday or Monday - weekly-review rolls the sprint and forces a verdict on every open flag."),
    ("audit", "Say \"audit the OS\" when things feel drifty - one composite report on health, voice, and wiki state."),
    ("brain-pass", "Try \"ask the brain about <topic>\" - brain-pass synthesises across log, knowledge, and decisions instead of one keyword match."),
    ("knowledge-capture", "Say \"capture this\" after a book or podcast worth keeping - knowledge-capture files it with a stable ID."),
    ("ingest", "Say \"ingest this\" on a URL or transcript - ingest preserves the source with provenance and proposes wiki updates."),
    ("bottleneck-diagnostic", "Try \"what's blocking me\" once a quarter - bottleneck-diagnostic scores founder dependency across five dimensions."),
    ("strategic-analysis", "Say \"analyze this market\" or \"competitor map\" - strategic-analysis grounds the scan in your knowledge notes."),
]
try:
    text = open(log_path, encoding='utf-8').read()
except Exception:
    sys.exit(0)
# Fresh-install gate. An entry is a line starting with "### " followed by an
# ISO date. Require >= 10 entries AND earliest-entry-to-today >= 30 days.
entry_re = re.compile(r'^###\s+(\d{4}-\d{2}-\d{2})')
entry_dates = []
for ln in text.splitlines():
    m = entry_re.match(ln)
    if m:
        try:
            entry_dates.append(date.fromisoformat(m.group(1)))
        except ValueError:
            continue
if len(entry_dates) < 10:
    sys.exit(0)
earliest = min(entry_dates)
if (today - earliest).days < 30:
    sys.exit(0)
# Build last-used-on map. Walk lines, track current date header (## or ###),
# accumulate explicit action tags. A planning line like "run audit later" is
# not a use. Count #used-<capability>, or #acted lines that name a capability.
date_re = re.compile(r'^#{2,3}\s+(\d{4}-\d{2}-\d{2})')
last_used = {}
cur = None
for ln in text.splitlines():
    m = date_re.match(ln)
    if m:
        try:
            cur = date.fromisoformat(m.group(1))
        except ValueError:
            cur = None
        continue
    if cur is None:
        continue
    for cap, _ in TIPS:
        if f"#used-{cap}" in ln or ("#acted" in ln and cap in ln):
            prev = last_used.get(cap)
            if prev is None or cur > prev:
                last_used[cap] = cur
# Eligible: not used in 14+ days OR never used. "Never used" only counts
# here because the fresh-install gate above already enforced enough log
# history for the pitch to make sense.
eligible = []
for cap, tip in TIPS:
    last = last_used.get(cap)
    if last is None or (today - last).days >= 14:
        eligible.append((cap, tip))
if not eligible:
    sys.exit(0)
# Weekly rotation: pick the index based on iso-week so the same tip does not
# repeat within a week.
week = today.isocalendar()[1]
idx = week % len(eligible)
print(eligible[idx][1])
PYEOF
  )
  if [ -n "$TIP" ]; then
    echo ""
    echo "Tip: $TIP"
  fi
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
  if [ -n "$PYTHON" ] && [ -d "$OBS_DIR" ]; then
    # On Git Bash/Cygwin/WSL, Python is the Windows binary and does not parse
    # POSIX paths like /c/Users/...; cygpath converts to Windows form so
    # pathlib's glob actually finds the files.
    if command -v cygpath >/dev/null 2>&1; then
      OBS_PY=$(cygpath -w "$OBS_DIR" 2>/dev/null || echo "$OBS_DIR")
    else
      OBS_PY="$OBS_DIR"
    fi
    STALE=$($PYTHON -c "
from datetime import date, timedelta
from pathlib import Path
obs = Path(r'''$OBS_PY''')
cut = date.today() - timedelta(days=10)
try:
    n = sum(1 for f in obs.glob('*.jsonl') if date.fromisoformat(f.stem) < cut)
    print(n)
except Exception:
    print(0)
" 2>/dev/null || echo 0)
    if [ "${STALE:-0}" -gt 0 ] 2>/dev/null; then
      echo "  ${STALE} JSONL files older than 10 days - say 'roll up observations' to compress old logs."
    fi
  fi
else
  echo "Observations: disabled (set FOUNDER_OS_OBSERVATIONS=1 to enable)"
fi

echo "=== end brief ==="

exit 0
