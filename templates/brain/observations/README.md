# Observations

`brain/observations/` stores a forensic record of every tool call Claude Code makes in a session. Off by default. Turned on by setting an environment variable.

This is the layer that answers "which files did I touch yesterday and why?" without reading through hundreds of log lines. `/dream` rolls the day's observations into the digest when the file exists.

## Opt-in

Set `FOUNDER_OS_OBSERVATIONS=1` in your shell environment.

- Bash / Zsh: add `export FOUNDER_OS_OBSERVATIONS=1` to `~/.bashrc` or `~/.zshrc`.
- PowerShell: add `$env:FOUNDER_OS_OBSERVATIONS = '1'` to your `$PROFILE`.
- Windows (system-wide): `setx FOUNDER_OS_OBSERVATIONS 1` (takes effect in new shells).

When the variable is unset (or set to anything other than `1`), the hook exits silently and writes nothing.

## File format

One file per day: `YYYY-MM-DD.jsonl`. Each line is one JSON object. Append-only. Never edited by the hook.

```json
{"ts":"2026-05-07T15:30:00+04:00","tool":"Edit","file":"skills/audit/SKILL.md","intent":"tightened parallel sub-agent instruction","session":"abc123"}
```

Fields:

- `ts` - ISO 8601 timestamp with timezone offset.
- `tool` - tool name (Read, Edit, Write, Bash, Grep, Glob, others).
- `file` - file touched (relative to repo root) when applicable. Empty string otherwise.
- `intent` - one-line summary, max 120 chars. Generated from the tool's input.
- `session` - Claude Code session ID when available. Empty string otherwise.

## Platform behavior

Both `post-tool-use-observation.sh` and `post-tool-use-observation.ps1` are wired in `.claude/settings.json` so the hook fires regardless of which shell Claude Code launches. To prevent double-writes on Windows, the bash hook exits silently when it detects MINGW, MSYS, or Cygwin and defers to the PowerShell hook. On macOS and Linux only the bash hook runs. Net effect: exactly one append per tool call on every platform.

## Privacy

- The hook logs file paths, command summaries, and a short intent string.
- It does NOT log full diffs, full file content, or full command output.
- The `intent` field is truncated to 120 characters and stripped of control characters.

## How it gets read

`/dream` checks for the day's file. When it exists, the digest gets an extra section:

```
**OBSERVED:** N tool calls today across M files
- Most-touched files: <top 3 by count>
- Notable activity: <up to 3 files where intent suggests something significant>
```

When the file is absent, `/dream` skips the OBSERVED section entirely.

## Cadence

Files accumulate one per day. Archive or prune as needed. The hook never reads back what it wrote, so old files do not affect runtime.
