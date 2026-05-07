# PostToolUse observation hook (opt-in).
#
# Appends a one-line JSON observation to brain/observations/<YYYY-MM-DD>.jsonl
# every time a tool call completes. Off by default. Enable by setting
# FOUNDER_OS_OBSERVATIONS=1 in your shell environment.
#
# Privacy: logs file paths, command summaries, and a short intent string.
# Never logs full diffs, full file content, or full command output.
#
# This hook MUST exit 0 in all cases. A failing hook cannot block a tool call.

$ErrorActionPreference = 'SilentlyContinue'

try {
  # Opt-in gate.
  if ($env:FOUNDER_OS_OBSERVATIONS -ne '1') {
    exit 0
  }

  $HookDir = Split-Path -Parent $MyInvocation.MyCommand.Path
  $Repo = (Resolve-Path (Join-Path $HookDir '..\..')).Path

  # Read hook input from stdin. Tolerate missing or malformed JSON.
  $rawInput = ''
  try {
    if (-not [Console]::IsInputRedirected) {
      $rawInput = ''
    } else {
      $rawInput = [Console]::In.ReadToEnd()
    }
  } catch {
    $rawInput = ''
  }

  $data = $null
  if ($rawInput -and $rawInput.Trim().Length -gt 0) {
    try {
      $data = $rawInput | ConvertFrom-Json -ErrorAction Stop
    } catch {
      $data = $null
    }
  }

  function Get-Field {
    param($obj, [string]$name)
    if ($null -eq $obj) { return '' }
    try {
      $v = $obj.PSObject.Properties[$name]
      if ($null -eq $v) { return '' }
      $val = $v.Value
      if ($null -eq $val) { return '' }
      return [string]$val
    } catch {
      return ''
    }
  }

  $toolName  = Get-Field $data 'tool_name'
  $sessionId = Get-Field $data 'session_id'

  $toolInput = $null
  if ($data) {
    try {
      $tiProp = $data.PSObject.Properties['tool_input']
      if ($tiProp) { $toolInput = $tiProp.Value }
    } catch {
      $toolInput = $null
    }
  }

  $filePath  = Get-Field $toolInput 'file_path'
  $newString = Get-Field $toolInput 'new_string'
  $content   = Get-Field $toolInput 'content'
  $command   = Get-Field $toolInput 'command'
  $pattern   = Get-Field $toolInput 'pattern'
  $searchPath = Get-Field $toolInput 'path'

  function Truncate-Snippet {
    param([string]$text, [int]$max)
    if (-not $text) { return '' }
    $cleaned = $text -replace "[`r`n`t]", ' '
    if ($cleaned.Length -gt $max) {
      return $cleaned.Substring(0, $max)
    }
    return $cleaned
  }

  switch ($toolName) {
    'Read'  { $intent = "read $filePath" }
    'Edit'  {
      $snippet = if ($newString) { $newString } else { $content }
      $snippet = Truncate-Snippet $snippet 80
      $intent = "edit $filePath - $snippet"
    }
    'Write' {
      $snippet = if ($newString) { $newString } else { $content }
      $snippet = Truncate-Snippet $snippet 80
      $intent = "edit $filePath - $snippet"
    }
    'Bash'  {
      $cmdSnip = Truncate-Snippet $command 80
      $intent = "bash - $cmdSnip"
    }
    'Grep'  { $intent = "grep $pattern in $searchPath" }
    'Glob'  { $intent = "glob $pattern" }
    ''      { $intent = 'unknown' }
    default { $intent = $toolName }
  }

  # Strip control characters and newlines (including DEL = 0x7F), then
  # truncate to 120.
  $intent = $intent -replace "[`r`n`t]", ' '
  $intent = ($intent.ToCharArray() | Where-Object { ([int]$_ -ge 32 -and [int]$_ -ne 127) -or $_ -eq ' ' }) -join ''
  if ($intent.Length -gt 120) {
    $intent = $intent.Substring(0, 120)
  }

  # ISO 8601 timestamp with timezone offset.
  $now = Get-Date
  $tz = [System.TimeZoneInfo]::Local.GetUtcOffset($now)
  $sign = if ($tz.Ticks -lt 0) { '-' } else { '+' }
  $tzStr = '{0}{1:D2}:{2:D2}' -f $sign, [Math]::Abs($tz.Hours), [Math]::Abs($tz.Minutes)
  $ts = $now.ToString('yyyy-MM-ddTHH:mm:ss') + $tzStr
  $today = $now.ToString('yyyy-MM-dd')

  $obsDir = Join-Path $Repo 'brain\observations'
  if (-not (Test-Path $obsDir)) {
    New-Item -ItemType Directory -Path $obsDir -Force | Out-Null
  }
  $obsFile = Join-Path $obsDir ("{0}.jsonl" -f $today)

  $entry = [ordered]@{
    ts      = $ts
    tool    = $toolName
    file    = $filePath
    intent  = $intent
    session = $sessionId
  }

  # Compress to single line.
  $jsonLine = $entry | ConvertTo-Json -Compress

  # Append as UTF-8 without BOM. Add-Content -Encoding UTF8 on Windows
  # PowerShell 5.1 writes a BOM on first write, which corrupts line 1 of every
  # new day's JSONL. AppendAllText with UTF8Encoding($false) avoids the BOM on
  # both 5.1 and 7+.
  [System.IO.File]::AppendAllText($obsFile, $jsonLine + "`n", (New-Object System.Text.UTF8Encoding $false))
} catch {
  # Swallow any error. The hook must never block a tool call.
}

exit 0
