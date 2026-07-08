#!/usr/bin/env bash
# PreCompact memory-flush hook (bash variant).
#
# Fires when the session context is about to be compacted (summarized). A
# compaction is where unsaved session facts die: a decision discussed but not
# yet logged, a status change not yet on the client row, a commitment made in
# passing. This hook injects save-before-forget instructions so the load-bearing
# facts survive as brain-file writes, not just as summary prose.
#
# Output goes to the compaction step, not the operator. Exit 0 in all cases.

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
[ -n "$HOOK_DIR" ] || exit 0
REPO="$(cd "$HOOK_DIR/../.." 2>/dev/null && pwd)"
[ -n "$REPO" ] || exit 0

# Only speak inside a set-up Founder OS install.
[ -f "$REPO/core/identity.md" ] || exit 0

cat <<'EOF'
[founder-os pre-compact] Save before you forget. This session is being compacted.
1. Preserve in the summary, verbatim where possible: every decision made, commitment given or received, client/prospect status change, deadline, number, and captured fact from this session that has NOT yet been written to a brain file.
2. Immediately after compaction, before continuing the task: write those items to their homes - brain/log.md (dated entry), brain/flags.md (open loops), context/clients.md (status changes), brain/decisions-parked.md (deferred calls). Continuity lives in the files, not in the summary.
3. If nothing in this session is unwritten, say nothing and carry on.
EOF

exit 0
