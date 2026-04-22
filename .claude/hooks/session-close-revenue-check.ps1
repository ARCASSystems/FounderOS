# Session-close revenue loop check (PowerShell mirror of session-close-revenue-check.sh).
# Warns if outreach verbs appear in recent brain/log.md without a matching context/clients.md update.
# Trigger: Stop event. Exits 0 in all cases.

$RepoRoot = & git rev-parse --show-toplevel 2>$null
if (-not $RepoRoot) { $RepoRoot = Get-Location }

$LogFile = Join-Path $RepoRoot "brain\log.md"
$ClientsFile = Join-Path $RepoRoot "context\clients.md"

if (-not (Test-Path $LogFile)) { exit 0 }
if (-not (Test-Path $ClientsFile)) { exit 0 }

$logStatus = & git -C $RepoRoot status --porcelain "brain/log.md" 2>$null
if ([string]::IsNullOrEmpty($logStatus)) { exit 0 }

$recent = Get-Content $LogFile -TotalCount 120 -ErrorAction SilentlyContinue

$outreachPattern = "\b(sent|messaged|called|DM'?d|emailed|pitched|reached\s+out|spoke\s+with|outreach|ping(ed)?|texted|whatsapp(ed)?)\b"
$actedSPattern = "#acted\s+\[S\]"

$outreachMatches = $recent | Select-String -Pattern $outreachPattern -CaseSensitive:$false | Select-Object -First 5
$actedMatches = $recent | Select-String -Pattern $actedSPattern | Select-Object -First 3

if (-not $outreachMatches -and -not $actedMatches) { exit 0 }

$clientsStatus = & git -C $RepoRoot status --porcelain "context/clients.md" 2>$null
if (-not [string]::IsNullOrEmpty($clientsStatus)) { exit 0 }

Write-Output ""
Write-Output "=== REVENUE LOOP CHECK ==="
Write-Output "Outreach signals detected in recent brain/log.md entries but context/clients.md"
Write-Output "has NOT been modified in the current session."
Write-Output ""
Write-Output "Every outreach action should update context/clients.md AND log to brain/log.md"
Write-Output "with #acted [S] in the same session. This keeps your pipeline state honest."
Write-Output ""
Write-Output "Sample signals matched:"
$outreachMatches | Select-Object -First 3 | ForEach-Object { Write-Output ("  " + $_.Line) }
Write-Output ""
Write-Output "Action before closing: update context/clients.md with the outreach touches,"
Write-Output "OR add a brain/log.md note explaining why no client row was needed."
Write-Output ""
Write-Output "=== END CHECK ==="
Write-Output ""

exit 0
