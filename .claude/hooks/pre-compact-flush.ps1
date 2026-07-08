# PreCompact memory-flush hook (PowerShell mirror of pre-compact-flush.sh).
#
# Fires when the session context is about to be compacted (summarized). A
# compaction is where unsaved session facts die: a decision discussed but not
# yet logged, a status change not yet on the client row, a commitment made in
# passing. This hook injects save-before-forget instructions so the load-bearing
# facts survive as brain-file writes, not just as summary prose.
#
# Output goes to the compaction step, not the operator. Exit 0 in all cases.

$ErrorActionPreference = 'SilentlyContinue'

try {
  $HookDir = Split-Path -Parent $MyInvocation.MyCommand.Path
  if (-not $HookDir) { exit 0 }
  $Repo = (Resolve-Path (Join-Path $HookDir '..\..')).Path
  if (-not $Repo) { exit 0 }

  # Only speak inside a set-up Founder OS install.
  if (-not (Test-Path (Join-Path $Repo 'core\identity.md'))) { exit 0 }

  Write-Output '[founder-os pre-compact] Save before you forget. This session is being compacted.'
  Write-Output '1. Preserve in the summary, verbatim where possible: every decision made, commitment given or received, client/prospect status change, deadline, number, and captured fact from this session that has NOT yet been written to a brain file.'
  Write-Output '2. Immediately after compaction, before continuing the task: write those items to their homes - brain/log.md (dated entry), brain/flags.md (open loops), context/clients.md (status changes), brain/decisions-parked.md (deferred calls). Continuity lives in the files, not in the summary.'
  Write-Output '3. If nothing in this session is unwritten, say nothing and carry on.'
} catch {
  # Swallow any error. The hook must never block compaction.
}

exit 0
