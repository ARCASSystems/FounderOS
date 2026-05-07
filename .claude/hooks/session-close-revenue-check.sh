#!/bin/bash
# Session-close revenue loop check.
# Warns (does not block) if outreach verbs appear in recent brain/log.md entries
# without a matching context/clients.md modification in the current session.
#
# Trigger: Stop event (register in .claude/settings.local.json under hooks.Stop).
# Exits 0 in all cases - this is a warning, not a blocker.

# Anchor on hook location, not CWD. Claude Code does not guarantee CWD is the
# Founder OS install when the Stop event fires; git rev-parse would return the
# wrong repo if the user is inside a nested checkout.
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || exit 0
REPO_ROOT="$(cd "$HOOK_DIR/../.." 2>/dev/null && pwd)" || exit 0
[ -z "$REPO_ROOT" ] && exit 0

LOG="$REPO_ROOT/brain/log.md"
CLIENTS="$REPO_ROOT/context/clients.md"

# Exit quietly if Founder OS is not installed in this repo
[ ! -f "$LOG" ] && exit 0
[ ! -f "$CLIENTS" ] && exit 0

# Only check if brain/log.md has been modified this session
log_status=$(git -C "$REPO_ROOT" status --porcelain "brain/log.md" 2>/dev/null)
if [ -z "$log_status" ]; then
  exit 0
fi

# Scan the most recent entries (top of file - newest-on-top convention)
recent=$(head -n 120 "$LOG" 2>/dev/null)

# Outreach verbs (case-insensitive) + explicit #acted [S] tag
outreach_pattern="\b(sent|messaged|called|DM'?d|emailed|pitched|reached\s+out|spoke\s+with|outreach|ping(ed)?|texted|whatsapp(ed)?)\b"
acted_s_pattern="#acted\s+\[S\]"

outreach_match=$(echo "$recent" | grep -E -i "$outreach_pattern" | head -5)
acted_match=$(echo "$recent" | grep -E "$acted_s_pattern" | head -3)

if [ -z "$outreach_match" ] && [ -z "$acted_match" ]; then
  exit 0
fi

# Check whether context/clients.md was modified this session
clients_status=$(git -C "$REPO_ROOT" status --porcelain "context/clients.md" 2>/dev/null)

if [ -n "$clients_status" ]; then
  exit 0
fi

# Violation: outreach signal in log, no clients.md update this session
cat <<EOF

=== REVENUE LOOP CHECK ===
Outreach signals detected in recent brain/log.md entries but context/clients.md
has NOT been modified in the current session.

Every outreach action should update context/clients.md AND log to brain/log.md
with #acted [S] in the same session. This keeps your pipeline state honest.

Sample signals matched:
$(echo "$outreach_match" | head -3 | sed 's/^/  /')

Action before closing: update context/clients.md with the outreach touches,
OR add a brain/log.md note explaining why no client row was needed.

=== END CHECK ===

EOF

exit 0
