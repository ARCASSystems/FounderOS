# Session-close change manifest hook (PowerShell mirror of session-close-changes.sh).
#
# At session end, render state/session-manifest.md - the list of every file
# this session wrote to, with a one-command restore per file - and print a
# one-line summary. The visibility half of the session-changes tracker.
#
# This hook MUST exit 0 in all cases.

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
  $raw | & $py $Script --manifest 2>$null | ForEach-Object { Write-Output $_ }
} catch {
  # Swallow any error. The hook must never block session close.
}

exit 0
