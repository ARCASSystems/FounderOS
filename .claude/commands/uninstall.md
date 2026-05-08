---
description: Cleanly remove Founder OS. Lists what will be removed, asks confirmation, then removes plugin registration and (optionally with --purge) your data files. Default mode preserves your data.
argument-hint: "[--purge]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# Founder OS uninstall

Cleanly removes Founder OS from this machine. Two modes:

- **Default** (no argument): de-registers the plugin and removes the System Layer files (skills, commands, hooks, templates). Preserves your personal data: `core/`, `context/`, `cadence/`, `brain/`, `network/`.
- **`--purge`**: also removes your personal data. Irreversible. Asks twice.

Argument: `$ARGUMENTS` - optional. Pass `--purge` (or `purge`) to also delete personal data.

## Procedure

### 1. Detect install state

Check for the following at the repo root:
- `.claude-plugin/plugin.json` (plugin install marker)
- `core/identity.md` (data marker)
- `cadence/`, `brain/`, `context/`, `network/` (data folders)

If none of these exist, reply: `No Founder OS install detected at this location. Nothing to remove.` and stop.

### 2. List what will be removed

Show the founder a single message:

If `$ARGUMENTS` does NOT contain `purge`:

```
Uninstall plan (default mode - preserves your data):

Plugin registration:
- .claude-plugin/plugin.json
- .claude-plugin/marketplace.json

System layer (will be removed):
- skills/<list of skill folders>
- scripts/ (Python helpers: wiki-build.py, query.py, brain-snapshot.py, brain-pass-log.py, memory-diff.py)
- templates/<list of template folders>
- rules/, docs/
- .claude/commands/<list of command files>
- .claude/hooks/<list of hook files>
- .claude/settings.json (if present)

Personal data (will be PRESERVED):
- core/
- context/
- cadence/
- brain/
- network/

If you want to also remove personal data, re-run with: /founder-os:uninstall --purge

Continue with default uninstall? (yes / no)
```

If `$ARGUMENTS` contains `purge`:

```
Uninstall plan (PURGE mode - removes EVERYTHING):

Plugin registration:
- .claude-plugin/

System layer:
- skills/, scripts/, templates/, rules/, .claude/, docs/

Personal data (WILL BE DELETED):
- core/ (identity, voice profile, brand profile, brand assets)
- context/ (priorities, decisions, clients, companies)
- cadence/ (daily anchors, weekly commitments, quarterly sprints, annual targets)
- brain/ (log, flags, patterns, decisions-parked, needs-input)
- network/ (inner circle, mentors, team)

This is IRREVERSIBLE. The data above is unique to this install and is not stored anywhere else.

Type the literal word `PURGE` (uppercase) to confirm.
```

### 3. Wait for reply

Default mode:
- If reply is a clear `yes`, proceed to step 4.
- Anything else, reply: `Uninstall dismissed. Nothing was removed.` and stop.

Purge mode:
- If reply is exactly the word `PURGE` (uppercase), proceed to step 4.
- Anything else, reply: `Purge confirmation not received. Nothing was removed.` and stop.

### 4. Execute removal

Run these in order. After each, report success or failure on a single line.

**Default mode:**

```bash
rm -rf skills/
rm -rf scripts/
rm -rf templates/
rm -rf rules/
rm -rf .claude/commands/
rm -rf .claude/hooks/
rm -rf .claude-plugin/
rm -f .claude/settings.json
rm -rf docs/
rm -f VERSION CLAUDE.md AGENTS.md GEMINI.md AVATAR.md README.md LICENSE stack.json
```

If running in PowerShell on Windows native (no git-bash), use:

```powershell
Remove-Item -Recurse -Force skills, scripts, templates, rules, docs
Remove-Item -Recurse -Force .claude/commands, .claude/hooks, .claude-plugin
Remove-Item -Force .claude/settings.json -ErrorAction SilentlyContinue
Remove-Item -Force VERSION, CLAUDE.md, AGENTS.md, GEMINI.md, AVATAR.md, README.md, LICENSE, stack.json
```

**Purge mode:** all of the above, plus:

```bash
rm -rf core/ context/ cadence/ brain/ network/
```

PowerShell:

```powershell
Remove-Item -Recurse -Force core, context, cadence, brain, network
```

### 5. Final confirmation

After removal:

```
Founder OS removed.

Default mode: your data is preserved at <list remaining folders>. Your data files are yours - you can now archive them, delete them by hand, or move them anywhere.

Plugin path: if you installed via the Claude Code plugin marketplace, also run `/plugin uninstall founder-os` to fully de-register the plugin from your Claude Code session.
```

If purge mode:

```
Founder OS purged. All files removed.

Plugin path: if you installed via the Claude Code plugin marketplace, also run `/plugin uninstall founder-os` to fully de-register the plugin from your Claude Code session.
```

## Rules

- Never run a destructive command before the user has confirmed in step 3.
- In default mode, NEVER touch `core/`, `context/`, `cadence/`, `brain/`, or `network/`.
- In purge mode, require the literal word `PURGE` in uppercase. No softer confirmations.
- If any `rm` step fails (permissions, locked file), report the failure on its own line and continue with the next step. Do not abort halfway.
- This command does not push to any remote. The user is responsible for cleaning up any cloud copies (GitHub forks, Notion mirrors).
- No em dashes or en dashes. Hyphens only.

## Failure modes

- **Plugin install via marketplace**: this command can remove the local files but cannot de-register the plugin from Claude Code. Tell the user to run `/plugin uninstall founder-os` after this command.
- **Files locked by editor**: tell the user which file failed and ask them to close it before re-running.
- **Wrong directory**: if step 1 finds no plugin and no data, refuse to delete anything and explain how to find the install root.
