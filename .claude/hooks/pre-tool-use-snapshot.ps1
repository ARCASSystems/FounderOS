# PreToolUse snapshot hook (PowerShell mirror of pre-tool-use-snapshot.sh).
#
# Before any Write/Edit/MultiEdit/NotebookEdit lands, hand the hook JSON to
# scripts/session_changes.py --record, which snapshots the file's pre-edit
# bytes and logs the change. Works with or without git - this is the pre-git
# undo floor for ZIP installs, and a second net everywhere else.
#
# This hook MUST exit 0 in all cases. It can never block or slow a write.

$ErrorActionPreference = 'SilentlyContinue'

try {
  $HookDir = Split-Path -Parent $MyInvocation.MyCommand.Path
  if (-not $HookDir) { exit 0 }
  $Repo = (Resolve-Path (Join-Path $HookDir '..\..')).Path
  if (-not $Repo) { exit 0 }

  $Script = Join-Path $Repo 'scripts\session_changes.py'
  if (-not (Test-Path $Script)) { exit 0 }

  $py = $null
  foreach ($cand in @('python', 'python3')) {
    $cmd = Get-Command $cand -ErrorAction SilentlyContinue
    if ($cmd) { $py = $cmd.Source; break }
  }
  if (-not $py) { exit 0 }

  $raw = ''
  try {
    if ([Console]::IsInputRedirected) { $raw = [Console]::In.ReadToEnd() }
  } catch { $raw = '' }

  $env:PYTHONUTF8 = '1'
  $raw | & $py $Script --record 2>$null | Out-Null
} catch {
  # Swallow any error. The hook must never block a tool call.
}

exit 0
