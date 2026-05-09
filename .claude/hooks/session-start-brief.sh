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
TODAY="$(date +%Y-%m-%d)"

# Resolve python interpreter once. Many Linux/macOS systems ship `python3` only.
if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  PYTHON=""
fi

# Quiet exit if the user's repo is not a Founder OS install.
[ ! -f "$REPO/core/identity.md" ] && exit 0

echo "=== Session brief ($TODAY) ==="

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
DEC="$REPO/context/decisions.md"
if [ -f "$DEC" ]; then
  PENDING=$(grep -cE "^### " "$DEC" 2>/dev/null)
  echo "Decisions: $PENDING tracked"
fi

# --- [FILL] rows in clients ---
CLIENTS="$REPO/context/clients.md"
if [ -f "$CLIENTS" ]; then
  FILL=$(grep -c "\[FILL\]" "$CLIENTS" 2>/dev/null)
  if [ -n "$FILL" ] && [ "$FILL" -gt 0 ] 2>/dev/null; then
    echo "Clients: $FILL [FILL] rows awaiting data"
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
# Scans brain/log.md for the last 30 days of #used or invocation tags. Picks a
# capability not invoked in 14+ days that matches current state. Rotates the
# pick weekly so the same tip does not repeat. If no eligible tip, the line
# is omitted (do NOT print "no tip" or similar).
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
# Build last-used-on map. Walk lines, track current date header, accumulate
# capability mentions. We treat any reference (#used:foo, /founder-os:foo,
# foo skill) as a use.
date_re = re.compile(r'^##\s+(\d{4}-\d{2}-\d{2})')
last_used = {}
cur = None
for ln in text.splitlines():
    m = date_re.match(ln)
    if m:
        cur = date.fromisoformat(m.group(1))
        continue
    if cur is None:
        continue
    for cap, _ in TIPS:
        if cap in ln:
            prev = last_used.get(cap)
            if prev is None or cur > prev:
                last_used[cap] = cur
# Eligible: not used in 14+ days OR never used.
eligible = []
for cap, tip in TIPS:
    last = last_used.get(cap)
    if last is None or (today - last).days >= 14:
        eligible.append((cap, tip))
if not eligible:
    sys.exit(0)
# Weekly rotation: pick the index based on iso-week so the same tip does not
# repeat within a week. Falls back to first eligible if rotation lands on a
# capability that was used in the meantime.
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
else
  echo "Observations: disabled (set FOUNDER_OS_OBSERVATIONS=1 to enable)"
fi

echo "=== end brief ==="

exit 0
