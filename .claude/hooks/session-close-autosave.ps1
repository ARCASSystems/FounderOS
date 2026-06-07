# Session-close auto-save (PowerShell mirror of session-close-autosave.sh).
#
# At session end, if there are uncommitted changes AND the privacy name guard is
# ACTIVE, record a local version so the founder never loses a session of work.
# If the guard is OFF, it WARNS instead of committing, so unscanned private names
# are never auto-committed. Local only: never pushes. Exits 0 in all cases.

$HookDir = $null
if ($MyInvocation.MyCommand.Path) {
  $HookDir = Split-Path -Parent $MyInvocation.MyCommand.Path
} elseif ($PSScriptRoot) {
  $HookDir = $PSScriptRoot
}
if (-not $HookDir) { exit 0 }

$RepoRoot = $null
try {
  $RepoRoot = (Resolve-Path (Join-Path $HookDir '..\..') -ErrorAction Stop).Path
} catch {
  exit 0
}
if (-not $RepoRoot) { exit 0 }

$Identity = Join-Path $RepoRoot "core\identity.md"
$Script = Join-Path $RepoRoot "scripts\caveman_git.py"
if (-not (Test-Path $Identity)) { exit 0 }
if (-not (Test-Path $Script)) { exit 0 }

# Nothing to save -> stay silent.
$changes = & git -C $RepoRoot status --porcelain 2>$null
if ([string]::IsNullOrEmpty($changes)) { exit 0 }

# Guard-active check: hooksPath wired AND at least one real name pattern.
$hooksPath = & git -C $RepoRoot config core.hooksPath 2>$null
$patterns = Join-Path $RepoRoot "scripts\private-name-patterns.txt"
$guardActive = $false
if (($hooksPath -eq ".githooks") -and (Test-Path $patterns)) {
  $real = Get-Content $patterns -Encoding UTF8 -ErrorAction SilentlyContinue |
    Where-Object { $_ -match '^\s*[^#\s]' }
  if ($real) { $guardActive = $true }
}

$py = $null
foreach ($cand in @("python", "python3")) {
  $cmd = Get-Command $cand -ErrorAction SilentlyContinue
  if ($cmd) { $py = $cmd.Source; break }
}
if (-not $py) { exit 0 }

if ($guardActive) {
  Write-Output ""
  Write-Output "=== AUTO-SAVE ==="
  $env:PYTHONUTF8 = "1"
  & $py $Script save 2>&1 | ForEach-Object { Write-Output $_ }
  Write-Output "(Local only. Say `"undo to ...`" to roll back, `"what changed`" to see versions.)"
  Write-Output "=== END AUTO-SAVE ==="
  Write-Output ""
} else {
  Write-Output ""
  Write-Output "=== AUTO-SAVE PAUSED ==="
  Write-Output "You have unsaved changes this session, but auto-save is paused because the"
  Write-Output "privacy name guard is not active yet (no patterns in"
  Write-Output "scripts/private-name-patterns.txt). The OS will not auto-commit content that"
  Write-Output "has not been name-scanned."
  Write-Output ""
  Write-Output "Say `"save my work`" to save manually now, or add your name to"
  Write-Output "scripts/private-name-patterns.txt (then run scripts/install-git-hooks.sh) to"
  Write-Output "turn on auto-save."
  Write-Output "=== END AUTO-SAVE ==="
  Write-Output ""
}

exit 0
