# SessionStart brief: surfaces open flags, stale cadence, pending decisions,
# [FILL] rows, quarantine failures, and entries past their Decay after.
# Fails gracefully. Never blocks session start.

$ErrorActionPreference = 'SilentlyContinue'

$HookDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Repo = (Resolve-Path (Join-Path $HookDir '..\..')).Path
$Today = Get-Date -Format 'yyyy-MM-dd'

# Quiet exit if the user's repo is not a Founder OS install.
if (-not (Test-Path (Join-Path $Repo 'core\identity.md'))) {
  exit 0
}

Write-Output "=== Session brief ($Today) ==="

# --- Open flags ---
$Flags = Join-Path $Repo 'brain\flags.md'
if (Test-Path $Flags) {
  $content = Get-Content $Flags
  $openCount = ($content | Select-String -Pattern 'Status:\s*\**OPEN').Count
  $week3Count = ($content | Select-String -Pattern 'Severity (Week 3|at resolution: Week 3)').Count
  Write-Output "Flags: $openCount OPEN, $week3Count Week 3+"
  $lastHeader = $null; $n = 0
  foreach ($line in $content) {
    if ($line -match '^##+\s') { $lastHeader = $line }
    elseif ($line -match 'Status:\s*\**OPEN' -and $lastHeader) {
      Write-Output "  - $lastHeader"
      $lastHeader = $null
      $n++; if ($n -ge 3) { break }
    }
  }
}

# --- Daily cadence staleness ---
$Daily = Join-Path $Repo 'cadence\daily-anchors.md'
if (Test-Path $Daily) {
  $m = (Get-Content $Daily | Select-String -Pattern '^## Today: (\d{4}-\d{2}-\d{2})' | Select-Object -First 1)
  if ($m) {
    $dailyDate = $m.Matches[0].Groups[1].Value
    if ($dailyDate -lt $Today) {
      Write-Output "Daily: STALE (anchor dated $dailyDate, today is $Today) - refresh before planning"
    } else {
      Write-Output "Daily: current ($dailyDate)"
    }
  }
}

# --- Weekly cadence staleness ---
$Weekly = Join-Path $Repo 'cadence\weekly-commitments.md'
if (Test-Path $Weekly) {
  $m = (Get-Content $Weekly | Select-String -Pattern '^## Week of (\d{4}-\d{2}-\d{2})' | Select-Object -First 1)
  if ($m) {
    $weekDate = $m.Matches[0].Groups[1].Value
    $age = (New-TimeSpan -Start ([datetime]$weekDate) -End ([datetime]$Today)).Days
    if ($age -gt 6) {
      Write-Output "Weekly: STALE (week of $weekDate, $age days old) - run retro before planning"
    } else {
      Write-Output "Weekly: current (week of $weekDate)"
    }
  }
}

# --- Pending decisions ---
$Dec = Join-Path $Repo 'context\decisions.md'
if (Test-Path $Dec) {
  $dc = Get-Content $Dec
  $pending = ($dc | Select-String -Pattern '^### ').Count
  Write-Output "Decisions: $pending tracked"
}

# --- Clients [FILL] ---
$Clients = Join-Path $Repo 'context\clients.md'
if (Test-Path $Clients) {
  $fill = (Get-Content $Clients | Select-String -Pattern '\[FILL\]').Count
  if ($fill -gt 0) { Write-Output "Clients: $fill [FILL] rows awaiting data" }
}

# --- Quarantine ---
# Counts entries with "**Status:** ACTIVE" outside of fenced code blocks
# (so the doc's own example snippets don't false-positive).
$Quarantine = Join-Path $Repo 'system\quarantine.md'
if (Test-Path $Quarantine) {
  $activeCount = 0
  $latestHeader = $null
  $inFence = $false
  foreach ($line in (Get-Content $Quarantine)) {
    if ($line -match '^\s*```') { $inFence = -not $inFence; continue }
    if ($inFence) { continue }
    if ($line -match '^##\s+\d{4}-\d{2}-\d{2}') { $latestHeader = $line }
    if ($line -match '^\*\*Status:\*\*\s*ACTIVE\b') { $activeCount++ }
  }
  if ($activeCount -gt 0) {
    Write-Output ""
    Write-Output "Quarantine: $activeCount ACTIVE failure(s) - check system/quarantine.md"
    if ($latestHeader) { Write-Output "  most recent: $latestHeader" }
  }
}

# --- Review Due (decay scan) ---
# Scans brain/flags.md, brain/patterns.md, brain/decisions-parked.md for
# entries with explicit "Decay after:" field that has passed. Supports
# YYYY-MM-DD or Nd. Convention defined in rules/entry-conventions.md.
$todayDt = [datetime]$Today

function Resolve-EntryAnchorDate {
  param([string[]]$entryLines, [string]$file)
  $heading = $entryLines[0]
  if ($file -like '*flags.md' -and $heading -match '##\s+(\d{4}-\d{2}-\d{2})') {
    return $matches[1]
  }
  foreach ($l in $entryLines) {
    if ($l -match '^\s*-?\s*Date parked:\s*(\d{4}-\d{2}-\d{2})') { return $matches[1] }
    if ($l -match '^\s*-?\s*First observed:\s*(\d{4}-\d{2}-\d{2})') { return $matches[1] }
  }
  return $null
}

function Get-DecayHits {
  param([string]$path, [string]$headingPattern)
  if (-not (Test-Path $path)) { return @() }
  $hits = @()
  $lines = Get-Content $path
  $entry = @()
  $entryHeading = $null
  for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    $isHeading = $line -match $headingPattern
    $isNextHeading = $isHeading -and $entry.Count -gt 0
    if ($isNextHeading -or $i -eq ($lines.Count - 1)) {
      if ($i -eq ($lines.Count - 1) -and -not $isNextHeading) { $entry += $line }
      if ($entry.Count -gt 0 -and $entryHeading) {
        $decayLine = $entry | Where-Object { $_ -match '^\s*-?\s*Decay after:\s*(.+?)\s*$' } | Select-Object -First 1
        if ($decayLine) {
          $val = ($decayLine -replace '^\s*-?\s*Decay after:\s*', '').Trim()
          $decayDate = $null
          $missingAnchor = $false
          if ($val -match '^\d{4}-\d{2}-\d{2}$') {
            $decayDate = [datetime]$val
          } elseif ($val -match '^(\d+)d$') {
            $days = [int]$matches[1]
            $anchor = Resolve-EntryAnchorDate -entryLines $entry -file $path
            if ($anchor) { $decayDate = ([datetime]$anchor).AddDays($days) }
            else { $missingAnchor = $true }
          }
          if ($decayDate -and $decayDate -lt $todayDt) {
            $age = [int]($todayDt - $decayDate).TotalDays
            $hits += [PSCustomObject]@{ heading = $entryHeading; daysAgo = $age; missingAnchor = $false }
          } elseif ($missingAnchor) {
            $hits += [PSCustomObject]@{ heading = $entryHeading; daysAgo = -1; missingAnchor = $true }
          }
        }
      }
      $entry = @($line)
      if ($isHeading) { $entryHeading = $line.Trim() } else { $entryHeading = $null }
    } else {
      if ($isHeading) { $entryHeading = $line.Trim(); $entry = @($line) }
      else { $entry += $line }
    }
  }
  return $hits
}

$flagHits    = Get-DecayHits -path (Join-Path $Repo 'brain\flags.md')             -headingPattern '^##\s'
$patternHits = Get-DecayHits -path (Join-Path $Repo 'brain\patterns.md')          -headingPattern '^###\s'
$parkedHits  = Get-DecayHits -path (Join-Path $Repo 'brain\decisions-parked.md')  -headingPattern '^###\s'
$allHits = @($flagHits) + @($patternHits) + @($parkedHits)
$decayedHits = @($allHits | Where-Object { -not $_.missingAnchor })
$missingAnchorHits = @($allHits | Where-Object { $_.missingAnchor })
if ($decayedHits.Count -gt 0) {
  Write-Output ""
  Write-Output "Review Due ($($decayedHits.Count) past decay):"
  foreach ($h in ($decayedHits | Select-Object -First 5)) {
    Write-Output ("  - " + $h.heading + " (decayed " + $h.daysAgo + "d ago)")
  }
}
if ($missingAnchorHits.Count -gt 0) {
  Write-Output ""
  Write-Output "Decay anchor missing ($($missingAnchorHits.Count) entries with relative Decay after but no First observed / Date parked):"
  foreach ($h in ($missingAnchorHits | Select-Object -First 5)) {
    Write-Output ("  - " + $h.heading)
  }
}

Write-Output "=== end brief ==="
exit 0
