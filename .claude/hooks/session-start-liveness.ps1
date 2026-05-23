# SessionStart liveness: prints one line about how long since the operator
# last ran /since-last-session. Reads brain/.last-session, no other state.
#
# Contract:
#   - DOES NOT update or write brain/.last-session. Only /since-last-session
#     writes the marker. This hook is read-only on that file.
#   - DOES NOT call any LLM. Pure file read + integer math. Free-tier safe.
#   - DOES NOT block session start. Exits within 100ms on a reasonable
#     filesystem. Any error path exits 0 silently so the brief above is
#     never delayed.
#
# Runs after session-start-brief.ps1 in the SessionStart matcher block so the
# brief prints first and this one-liner appears below it.

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

# Gate on core/identity.md. Matches the brief: that is the canonical signal
# of a FounderOS install that has finished setup. On a fresh pre-setup repo
# the brief already prints the welcome banner; a second liveness line on top
# would be noise.
if (-not (Test-Path (Join-Path $Repo 'core\identity.md'))) {
  exit 0
}

$Marker = Join-Path $Repo 'brain\.last-session'

if (-not (Test-Path $Marker)) {
  Write-Output 'No prior synthesis marker found. Run /since-last-session to initialize.'
  exit 0
}

$raw = $null
try {
  $raw = (Get-Content -Path $Marker -Raw -Encoding UTF8 -ErrorAction Stop)
} catch {
  exit 0
}

if (-not $raw) {
  Write-Output 'Synthesis marker malformed at brain/.last-session. Run /since-last-session to repair.'
  exit 0
}

$trimmed = $raw.Trim()
if (-not $trimmed) {
  Write-Output 'Synthesis marker malformed at brain/.last-session. Run /since-last-session to repair.'
  exit 0
}

# Parse as ISO-8601 with offset. DateTimeStyles.AssumeUniversal would silently
# accept a naive timestamp; we require an explicit offset per the spec
# (skills/since-last-session/SKILL.md line 31). DateTimeOffset.ParseExact with
# the round-trip "o" formats requires the offset to be present in input.
$markerDt = $null
$styles = [System.Globalization.DateTimeStyles]::AssumeLocal -bor `
          [System.Globalization.DateTimeStyles]::AdjustToUniversal
$culture = [System.Globalization.CultureInfo]::InvariantCulture

# Use DateTimeOffset so we keep the marker's offset rather than coercing to
# local-time silently.
[DateTimeOffset]$parsedMarker = [DateTimeOffset]::MinValue
$parsed = [DateTimeOffset]::TryParse(
  $trimmed,
  $culture,
  [System.Globalization.DateTimeStyles]::AssumeLocal,
  [ref]$parsedMarker
)

if (-not $parsed) {
  Write-Output 'Synthesis marker malformed at brain/.last-session. Run /since-last-session to repair.'
  exit 0
}

# A bare "2026-05-23T03:30:00" with no offset is malformed per spec. TryParse
# accepts it and applies AssumeLocal; detect by checking the input contains an
# explicit offset marker (`Z`, `+HH:MM`, or `-HH:MM` after the `T`).
$hasOffset = $false
if ($trimmed -match 'T[0-9:\.]+(Z|[+\-][0-9]{2}:?[0-9]{2})$') {
  $hasOffset = $true
}

if (-not $hasOffset) {
  Write-Output 'Synthesis marker malformed at brain/.last-session. Run /since-last-session to repair.'
  exit 0
}

$now = [DateTimeOffset]::UtcNow
$elapsedSeconds = ($now - $parsedMarker).TotalSeconds

if ($elapsedSeconds -lt 0) {
  Write-Output 'Synthesis marker is in the future; ignoring. Run /since-last-session if you want to repair it.'
  exit 0
}

if ($elapsedSeconds -lt 3600) {
  Write-Output 'Less than an hour since you last ran /since-last-session.'
  exit 0
}

$hours = [int]([Math]::Floor($elapsedSeconds / 3600))
Write-Output "$hours hours since you last ran /since-last-session. Run /since-last-session for the delta, or /strategic-read for a full state-of-OS report."

exit 0
