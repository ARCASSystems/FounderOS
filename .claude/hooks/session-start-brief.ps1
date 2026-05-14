# SessionStart brief: surfaces open flags, stale cadence, pending decisions,
# [FILL] rows, quarantine failures, and entries past their Decay after.
# Fails gracefully. Never blocks session start.

$ErrorActionPreference = 'SilentlyContinue'

# Resolve the hook directory safely. $MyInvocation.MyCommand.Path can be null
# in some invocation contexts (dot-sourced, -Command mode, certain CI runners).
# Fall back to PSScriptRoot, then bail quietly if neither resolves.
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

$Today = Get-Date -Format 'yyyy-MM-dd'

# Locale-safe ISO-8601 date parser. [datetime]"2026-05-04" uses thread culture
# and breaks on non-English Windows. ParseExact with InvariantCulture is stable.
function ConvertTo-IsoDate {
  param([string]$value)
  if (-not $value) { return $null }
  try {
    return [datetime]::ParseExact(
      $value,
      'yyyy-MM-dd',
      [System.Globalization.CultureInfo]::InvariantCulture
    )
  } catch {
    return $null
  }
}

# Fresh-install welcome. If core/identity.md is missing but other Founder OS
# markers exist (the templates directory, the bootloader, or a Founder OS
# settings.json), the user has installed the plugin or cloned the repo but
# has not run setup. Surface a one-line nudge so the experience is not
# silence. Without this banner the new-user path is: open Claude Code, see
# nothing, close. Then exit 0 - the brief sections below require
# core/identity.md and would no-op anyway.
if (-not (Test-Path (Join-Path $Repo 'core\identity.md'))) {
  $markers = @(
    (Join-Path $Repo 'templates\bootloader-claude-md.md'),
    (Join-Path $Repo '.claude\settings.json'),
    (Join-Path $Repo 'CLAUDE.md')
  )
  $hasMarker = $false
  foreach ($m in $markers) {
    if (Test-Path $m) { $hasMarker = $true; break }
  }
  if ($hasMarker) {
    Write-Output "Welcome to Founder OS. Run /founder-os:setup to get started."
    Write-Output "(15-20 minutes. The wizard asks who you are, what you run, and what is slowing you down.)"
  }
  exit 0
}

Write-Output "=== Session brief ($Today) ==="

# --- Active queue items ---
$Queue = Join-Path $Repo 'cadence\queue.md'
if (-not (Test-Path $Queue)) {
  Write-Output 'Active: 0/3 (queue empty - say "add to queue: <thing>" to start)'
} else {
  $qLines = Get-Content $Queue
  $inActive = $false
  $activeItems = @()
  foreach ($line in $qLines) {
    if ($line -match '^## ACTIVE') { $inActive = $true; continue }
    if ($line -match '^## ' -and $inActive) { break }
    if ($inActive -and $line -match '^\[') { $activeItems += $line }
  }
  if ($activeItems.Count -eq 0) {
    Write-Output 'Active: 0/3 (queue empty - say "add to queue: <thing>" to start)'
  } else {
    Write-Output "Active: $($activeItems.Count)/3"
    foreach ($item in ($activeItems | Select-Object -First 3)) {
      Write-Output "  - $item"
    }
  }
}

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
    $weekDt = ConvertTo-IsoDate $weekDate
    $todayDtForWeek = ConvertTo-IsoDate $Today
    if ($weekDt -and $todayDtForWeek) {
      $age = (New-TimeSpan -Start $weekDt -End $todayDtForWeek).Days
    } else {
      $age = $null
    }
    if ($null -ne $age -and $age -gt 6) {
      Write-Output "Weekly: STALE (week of $weekDate, $age days old) - run retro before planning"
    } else {
      Write-Output "Weekly: current (week of $weekDate)"
    }
  }
}

# --- Pending decisions ---
# Count only ### headings under the ## Pending section to exclude Resolved/Parked.
$Dec = Join-Path $Repo 'context\decisions.md'
if (Test-Path $Dec) {
  $dc = Get-Content $Dec
  $pending = 0
  $inPending = $false
  foreach ($line in $dc) {
    if ($line -match '^## Pending') { $inPending = $true; continue }
    if ($line -match '^## ' -and $inPending) { break }
    if ($inPending -and $line -match '^### ') { $pending++ }
  }
  Write-Output "Decisions: $pending pending"
}

# --- Clients [FILL] ---
$Clients = Join-Path $Repo 'context\clients.md'
if (Test-Path $Clients) {
  $fill = (Get-Content $Clients | Select-String -Pattern '\[FILL\]').Count
  if ($fill -gt 0) { Write-Output "Clients: $fill [FILL] rows awaiting data" }
}

# --- Unprocessed rants ---
# Surfaces the rant-to-action gap. Without this line, rants captured via
# /rant sit in brain/rants/ until the user remembers /dream exists (15-25%
# of users, per pre-v1.23 review). Count rant entries (not files) where
# the frontmatter line `processed: false` is present.
$RantsDir = Join-Path $Repo 'brain\rants'
if (Test-Path $RantsDir) {
  $unproc = 0
  foreach ($file in (Get-ChildItem -Path $RantsDir -Filter '*.md' -ErrorAction SilentlyContinue)) {
    $matches = (Get-Content $file.FullName -ErrorAction SilentlyContinue) | Select-String -Pattern '^processed:\s*false\s*$'
    if ($matches) { $unproc += $matches.Count }
  }
  if ($unproc -gt 0) {
    if ($unproc -ge 3) {
      Write-Output "Unprocessed rants: $unproc - say `"process my rants`" or run /founder-os:dream. They go stale at 30 days."
    } else {
      Write-Output "Unprocessed rants: $unproc (say `"process my rants`" or run /founder-os:dream to distil them)"
    }
  }
}

# $todayDt must be initialized here so the compliance block below can compare
# deadline dates. Defined after ConvertTo-IsoDate (above) and before first use.
$todayDt = ConvertTo-IsoDate $Today
if (-not $todayDt) { $todayDt = Get-Date }

# --- Compliance deadlines (legal-compliance skill) ---
# Surfaces entries in context/compliance.md within next 30 days or overdue.
# Quiet exit if file missing - skill is opt-in via /founder-os:legal-setup.
$Compliance = Join-Path $Repo 'context\compliance.md'
if (Test-Path $Compliance) {
  $complianceLines = Get-Content $Compliance
  $overdue = @()
  $upcoming = @()
  $i = 0
  while ($i -lt $complianceLines.Count) {
    $line = $complianceLines[$i]
    if ($line -match '^##\s+(\d{4}-\d{2}-\d{2})\s*[-:]\s*(.+?)\s*$') {
      $deadlineStr = $matches[1]
      $desc = $matches[2]
      $deadlineDt = ConvertTo-IsoDate $deadlineStr
      $status = 'OPEN'
      $j = $i + 1
      while ($j -lt $complianceLines.Count -and -not ($complianceLines[$j] -match '^##\s')) {
        if ($complianceLines[$j] -match '^\s*-\s*Status:\s*(\w+)') {
          $status = $matches[1].ToUpper()
          break
        }
        $j++
      }
      if ($status -ne 'DONE' -and $deadlineDt -and $todayDt) {
        $delta = [int]($deadlineDt - $todayDt).TotalDays
        if ($delta -lt 0) {
          $overdue += [PSCustomObject]@{ date = $deadlineStr; desc = $desc; daysPast = [Math]::Abs($delta) }
        } elseif ($delta -le 30) {
          $upcoming += [PSCustomObject]@{ date = $deadlineStr; desc = $desc; daysTo = $delta }
        }
      }
      $i = $j
    } else {
      $i++
    }
  }
  if ($overdue.Count -gt 0 -or $upcoming.Count -gt 0) {
    Write-Output ""
    if ($overdue.Count -gt 0) {
      Write-Output "Compliance: $($overdue.Count) OVERDUE deadline(s) - file or escalate today"
      foreach ($o in ($overdue | Sort-Object date | Select-Object -First 3)) {
        Write-Output ("  " + $o.date + " - " + $o.desc + " (overdue " + $o.daysPast + "d)")
      }
    }
    if ($upcoming.Count -gt 0) {
      Write-Output "Compliance: $($upcoming.Count) deadline(s) within 30 days"
      foreach ($u in ($upcoming | Sort-Object date | Select-Object -First 3)) {
        Write-Output ("  " + $u.date + " - " + $u.desc + " (in " + $u.daysTo + "d)")
      }
    }
  }
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
            $decayDate = ConvertTo-IsoDate $val
          } elseif ($val -match '^(\d+)d$') {
            $days = [int]$matches[1]
            $anchor = Resolve-EntryAnchorDate -entryLines $entry -file $path
            $anchorDt = if ($anchor) { ConvertTo-IsoDate $anchor } else { $null }
            if ($anchorDt) { $decayDate = $anchorDt.AddDays($days) }
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

# --- Memory/Retrieval diff (clients folders without memory entries) ---
# Closes the cross-session gap where cloud or parallel sessions create
# clients/<slug>/ folders that the next local session boots blind to.
$MemoryDiff = Join-Path $Repo 'scripts\memory-diff.py'
if (Test-Path $MemoryDiff) {
  # Prefer python3 (macOS / Linux pwsh ships only python3) and fall back to python (Windows / older systems).
  $pyExe = $null
  $py3 = Get-Command python3 -ErrorAction SilentlyContinue
  if ($py3) {
    $pyExe = $py3.Source
  } else {
    $py = Get-Command python -ErrorAction SilentlyContinue
    if ($py) { $pyExe = $py.Source }
  }
  if ($pyExe) {
    & $pyExe $MemoryDiff $Repo 2>$null
  }
}

# --- Tip (rotates weekly, surfaces one underused capability) ---
# Scans brain/log.md for explicit action tags only. Counts `#used-<capability>`
# or `#acted` lines that name the capability. Picks a capability not
# invoked in 14+ days. Rotates the pick weekly so the same tip does not
# repeat. Fresh-install gate: the log must have at least 10 entries
# (### date headings) AND span at least 30 days from the earliest entry to
# today. Below that floor the Tip is omitted entirely so new users don't see
# capability pitches before they have any state. If no eligible tip, the
# line is omitted (do NOT print "no tip" or similar).
$Log = Join-Path $Repo 'brain\log.md'
if (Test-Path $Log) {
  $tips = @(
    @{cap='decision-framework'; tip='Try saying "help me decide" next time you''re stuck on a choice - the decision-framework skill walks you through it.'},
    @{cap='priority-triage'; tip='Say "what should I focus on next" when the open list grows past five - priority-triage cuts it down to one thing.'},
    @{cap='forcing-questions'; tip='Try "force me to think this through" before starting something new - forcing-questions runs six tests on the idea before you commit.'},
    @{cap='weekly-review'; tip='Say "run my weekly review" on Friday or Monday - weekly-review rolls the sprint and forces a verdict on every open flag.'},
    @{cap='audit'; tip='Say "audit the OS" when things feel drifty - one composite report on health, voice, and wiki state.'},
    @{cap='brain-pass'; tip='Try "ask the brain about <topic>" - brain-pass synthesises across log, knowledge, and decisions instead of one keyword match.'},
    @{cap='knowledge-capture'; tip='Say "capture this" after a book or podcast worth keeping - knowledge-capture files it with a stable ID.'},
    @{cap='ingest'; tip='Say "ingest this" on a URL or transcript - ingest preserves the source with provenance and proposes wiki updates.'},
    @{cap='bottleneck-diagnostic'; tip='Try "what''s blocking me" once a quarter - bottleneck-diagnostic scores founder dependency across five dimensions.'},
    @{cap='strategic-analysis'; tip='Say "analyze this market" or "competitor map" - strategic-analysis grounds the scan in your knowledge notes.'}
  )
  $logLines = Get-Content $Log
  # Fresh-install gate. An entry is a line starting with "### " followed by
  # an ISO date. Require >= 10 entries AND earliest-entry-to-today >= 30 days.
  $entryDates = @()
  foreach ($line in $logLines) {
    if ($line -match '^###\s+(\d{4}-\d{2}-\d{2})') {
      $d = ConvertTo-IsoDate $matches[1]
      if ($d) { $entryDates += $d }
    }
  }
  $gatePassed = $false
  if ($entryDates.Count -ge 10) {
    $earliest = ($entryDates | Sort-Object)[0]
    $span = (New-TimeSpan -Start $earliest -End $todayDt).Days
    if ($span -ge 30) { $gatePassed = $true }
  }
  if ($gatePassed) {
    $lastUsed = @{}
    $curDate = $null
    foreach ($line in $logLines) {
      if ($line -match '^#{2,3}\s+(\d{4}-\d{2}-\d{2})') {
        $curDate = ConvertTo-IsoDate $matches[1]
        continue
      }
      if (-not $curDate) { continue }
      foreach ($t in $tips) {
        $capPattern = [regex]::Escape($t.cap)
        $usedPattern = "(^|\s)#used-$capPattern\b"
        $actedPattern = "(^|\s)#acted\b"
        if (($line -match $usedPattern) -or (($line -match $actedPattern) -and ($line -match $capPattern))) {
          $prev = $lastUsed[$t.cap]
          if ($null -eq $prev -or $curDate -gt $prev) {
            $lastUsed[$t.cap] = $curDate
          }
        }
      }
    }
    $eligible = @()
    foreach ($t in $tips) {
      $last = $lastUsed[$t.cap]
      if ($null -eq $last) {
        $eligible += $t
      } else {
        $age = (New-TimeSpan -Start $last -End $todayDt).Days
        if ($age -ge 14) { $eligible += $t }
      }
    }
    if ($eligible.Count -gt 0) {
      # Weekly rotation: index by ISO week so the same tip does not repeat
      # within a week.
      $cal = [System.Globalization.CultureInfo]::InvariantCulture.Calendar
      $weekRule = [System.Globalization.CalendarWeekRule]::FirstFourDayWeek
      $week = $cal.GetWeekOfYear($todayDt, $weekRule, [System.DayOfWeek]::Monday)
      $idx = $week % $eligible.Count
      Write-Output ""
      Write-Output ("Tip: " + $eligible[$idx].tip)
    }
  }
}

# --- Observations (opt-in telemetry, FOUNDER_OS_OBSERVATIONS=1 to enable) ---
# Printed inside the brief so the visual closure (=== end brief ===) is the
# last line.
if ($env:FOUNDER_OS_OBSERVATIONS -eq "1") {
    Write-Output "Observations: enabled (writing to brain/observations/<date>.jsonl)"
    # --- Observation rollup state ---
    $obsDir = Join-Path $Repo "brain\observations"
    $rollupDir = Join-Path $obsDir "_rollups"
    $rollupCount = 0
    if (Test-Path $rollupDir) {
        $rollupCount = @(Get-ChildItem -Path $rollupDir -Filter "*.md" -ErrorAction SilentlyContinue).Count
    }
    Write-Output "  Rollups: $rollupCount weekly summaries in brain/observations/_rollups/"
    if (Test-Path $obsDir) {
        $cutoff = (Get-Date).AddDays(-10).Date
        try {
            $stale = @(Get-ChildItem -Path $obsDir -Filter "*.jsonl" -ErrorAction SilentlyContinue |
                Where-Object {
                    try { [datetime]::ParseExact($_.BaseName, "yyyy-MM-dd", $null) -lt $cutoff }
                    catch { $false }
                }).Count
            if ($stale -gt 0) {
                Write-Output "  $stale JSONL files older than 10 days - say 'roll up observations' to compress old logs."
            }
        } catch {}
    }
} else {
    Write-Output "Observations: disabled (set FOUNDER_OS_OBSERVATIONS=1 to enable)"
}

Write-Output "=== end brief ==="

exit 0
