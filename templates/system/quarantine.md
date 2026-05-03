# Quarantine

When a hook, scheduled task, or self-healing attempt fails, write the failure here. The SessionStart brief surfaces the count of `Status: ACTIVE` entries so failures are not silent.

## Why this exists

Hooks and scheduled tasks fail silently by design (`set +e` in bash, `$ErrorActionPreference = 'SilentlyContinue'` in PowerShell). That is correct: a broken hook should never block a session. But silent failure compounds: a scheduled task can be dead for weeks before anyone notices.

This file is the catch-net. Anything that fails writes here. SessionStart counts active entries and surfaces them.

## Entry format

```
## YYYY-MM-DD HH:MM - <source> - <one-line summary>

**Source:** <full hook/script/task path>
**Trigger:** <what was attempting to run>
**Error:** <error message or relevant log lines>
**Context:** <what was being processed when it failed>
**Status:** ACTIVE

---
```

When resolved, change `Status: ACTIVE` to `Status: RESOLVED YYYY-MM-DD` and add a one-line resolution note above the `---`. Resolved entries stay in the file for audit; only ACTIVE entries surface in the brief.

## Writing to quarantine from a hook (PowerShell)

```powershell
function Write-Quarantine {
  param([string]$Source, [string]$Trigger, [string]$ErrorMsg, [string]$Context)
  $repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
  $qFile = Join-Path $repo 'system\quarantine.md'
  $ts = Get-Date -Format 'yyyy-MM-dd HH:mm'
  # Defang triple-backticks so an error message containing them cannot open
  # a fenced block that hides every entry below it from the SessionStart scanner.
  $safeErr = ($ErrorMsg -replace '```', "'''")
  $safeCtx = ($Context  -replace '```', "'''")
  $headLine = ($safeErr -split "`n")[0]
  $entry = @"

## $ts - $Source - $headLine

**Source:** $Source
**Trigger:** $Trigger
**Error:** $safeErr
**Context:** $safeCtx
**Status:** ACTIVE

---
"@
  Add-Content -Path $qFile -Value $entry -Encoding UTF8
}
```

## Writing to quarantine from a hook (bash)

```bash
write_quarantine() {
  local source="$1" trigger="$2" error="$3" context="$4"
  local repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
  local qfile="$repo/system/quarantine.md"
  local ts="$(date +'%Y-%m-%d %H:%M')"
  # Defang triple-backticks so an error message containing them cannot open
  # a fenced block that hides every entry below it from the SessionStart scanner.
  local safe_err="${error//\`\`\`/\'\'\'}"
  local safe_ctx="${context//\`\`\`/\'\'\'}"
  local first_line="$(printf '%s\n' "$safe_err" | head -n1)"
  cat >> "$qfile" <<EOF

## $ts - $source - $first_line

**Source:** $source
**Trigger:** $trigger
**Error:** $safe_err
**Context:** $safe_ctx
**Status:** ACTIVE

---
EOF
}
```

## What does NOT go here

- User errors (typo in a command, wrong file path) - those are interactive, not silent.
- Expected failures (e.g. hook gracefully skipping when an MCP is unavailable) - only unexpected ones.
- Per-session debugging output - use `brain/log.md` for that.

This file should stay short. If it grows past 50 ACTIVE entries, the bug is upstream - fix the recurring source, then mark the entries resolved or delete them.

---

<!-- Active entries below. SessionStart counts everything with "Status: ACTIVE". -->
