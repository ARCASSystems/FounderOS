# UserPromptSubmit hook: capture-aware classifier.
# Reads stdin, hands to scripts/user-prompt-capture.py, prints stdout (a
# capture-suggestion note that Claude reads as added context). Never blocks
# the session - exits 0 even if Python is missing.

$ErrorActionPreference = 'SilentlyContinue'

$HookDir = $null
if ($MyInvocation.MyCommand.Path) {
  $HookDir = Split-Path -Parent $MyInvocation.MyCommand.Path
} elseif ($PSScriptRoot) {
  $HookDir = $PSScriptRoot
}
if (-not $HookDir) { exit 0 }

$Repo = $null
try {
  $Repo = (Resolve-Path (Join-Path $HookDir '..\..') -ErrorAction Stop).Path
} catch {
  exit 0
}
if (-not $Repo) { exit 0 }

$Script = Join-Path $Repo 'scripts\user-prompt-capture.py'
if (-not (Test-Path $Script)) { exit 0 }

# Prefer python3, fall back to python.
$pyExe = $null
$py3 = Get-Command python3 -ErrorAction SilentlyContinue
if ($py3) {
  $pyExe = $py3.Source
} else {
  $py = Get-Command python -ErrorAction SilentlyContinue
  if ($py) { $pyExe = $py.Source }
}
if (-not $pyExe) { exit 0 }

# Pass CLAUDE_PROJECT_DIR through so the python script can resolve the repo.
if (-not $env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR = $Repo }

# Forward stdin to the python script. Get-Content reads stdin in pwsh; the
# script reads it the same way as the bash variant.
$stdin = [Console]::In.ReadToEnd()
$stdin | & $pyExe $Script 2>$null

exit 0
