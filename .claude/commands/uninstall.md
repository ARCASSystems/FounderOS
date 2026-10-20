---
description: Uninstall Founder OS. Say "uninstall Founder OS" (or run /founder-os:uninstall). Lists what will be removed, asks confirmation, then removes plugin registration and (optionally with --purge) your data files. Default mode preserves your data.
argument-hint: "[--purge]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# Founder OS uninstall

Cleanly removes Founder OS from this machine. Two modes:

- **Default** (no argument): de-registers the plugin and removes the System Layer files (skills, commands, hooks, templates). Preserves your personal data: `core/`, `context/`, `cadence/`, `brain/`, `network/`, `clients/`, `companies/`, `MEMORY.md`, `CLAUDE.md`, and `stack.json` (local tool bindings).
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
- docs/, updates/, notion-package/
- .claude/commands/<list of command files>
- .claude/hooks/<list of hook files>
- .claude/settings.json (if present)
- .claude/skills/<the skill copies the OS generated> and .claude/agents/<the agent files the OS generated> (they point at scripts this removes, so left behind they break the next time Claude Code opens the folder; any skill or agent you added there yourself stays)
- VERSION, AGENTS.md, GEMINI.md, AVATAR.md, README.md, CHANGELOG.md, LICENSE, install.sh, uninstall.sh

Personal data (will be PRESERVED):
- core/
- context/
- cadence/
- brain/
- capture/
- brands/
- network/
- clients/
- companies/
- roles/ (your employee registry - statuses, review stamps, custom rows)
- system/ (this install's quarantine record)
- rules/ (personalized at setup and possibly hand-edited - update treats these as yours, so uninstall does too)
- MEMORY.md
- CLAUDE.md
- stack.json (local tool bindings - if you reinstall, your tool choices come back)
- os-config.yaml (which modules you run, plus your brand values)

If you want to also remove personal data, re-run with: /founder-os:uninstall --purge

Continue with default uninstall? (yes / no)
```

If `$ARGUMENTS` contains `purge`:

```
Uninstall plan (PURGE mode - removes EVERYTHING):

Plugin registration:
- .claude-plugin/

System layer:
- skills/, scripts/, templates/, rules/, .claude/ (all of it, including generated skills and agents and settings.local.json), docs/, updates/, notion-package/
- VERSION, AGENTS.md, GEMINI.md, AVATAR.md, README.md, CHANGELOG.md, LICENSE, install.sh, uninstall.sh

Personal data (WILL BE DELETED):
- core/ (identity, voice profile, brand profile, brand assets)
- context/ (priorities, decisions, clients, companies)
- cadence/ (daily anchors, weekly commitments, quarterly sprints, annual targets)
- brain/ (log, flags, patterns, decisions-parked, needs-input, rants, observations)
- capture/ (your inbox drops), brands/ (per-brand voice)
- network/ (inner circle, mentors, team)
- clients/, companies/, roles/ (your employee registry), system/ (quarantine record)
- memory/ if present
- state/ (the pre-edit copies of your files from recent sessions, change logs, setup markers)
- voice/ (the voice runtime, including runtime-log.jsonl and live-log.md - what you said out loud)
- .env and any .env.* file (your API keys and tokens), connectors/ (connector status), .mcp.json if present
- CLAUDE.md, MEMORY.md, stack.json, os-config.yaml

Asked separately, after this: .git/ (your version history). Every saved
version of everything above lives there too, so deleting the files and
keeping .git keeps your data recoverable. You choose.

Not touched, because they live outside this folder (shown at the end with how
to remove them by hand): the Founder OS block in ~/.claude/CLAUDE.md, and
Claude Code's memory for this folder under ~/.claude/projects/.

One honest limit: if setup created company or project folders at the OS root,
purge cannot guess their names. It lists any root folder it does not recognise
and asks you per folder: delete or keep.

This is IRREVERSIBLE. The data above is unique to this install and is not stored anywhere else.

Type the literal word `PURGE` (uppercase) to confirm.
```

### 3. Wait for reply

Default mode:
- If reply is a clear `yes`, proceed to step 4.
- Anything else, reply: `Uninstall dismissed. Nothing was removed.` and stop.

Purge mode:
- If reply is exactly the word `PURGE` (uppercase), ask the version-history question before removing anything: `Delete your version history too (.git/)? Every saved version of your files is in it. Keeping it means the files can be brought back. Type DELETE HISTORY to delete it, or anything else to keep it.` Record the answer, then proceed to step 4. Only the exact reply `DELETE HISTORY` removes `.git/`; anything else keeps it.
- Anything else, reply: `Purge confirmation not received. Nothing was removed.` and stop.

### 4. Execute removal

Run these in order. After each, report success or failure on a single line.

**Default mode.** Remove ONLY these named system paths. `rules/` is deliberately not on this list: update classifies it as founder-personalized, so uninstall leaves it. Anything not named here survives by construction, including any company or project folders setup created at the root.

First, while `skills/` still exists, remove the copies the OS generated inside `.claude/`. Only two kinds qualify, and nothing else in those folders is touched: a `.claude/skills/<name>/` folder whose `<name>` also exists as `skills/<name>/` (the only kind `skills_sync.py` writes), and a `.claude/agents/*.md` file containing the line marker `generated by scripts/agents_sync.py` (the agents `agents_sync.py` writes; the registry row in `roles/employees.yaml` that generated it is kept). A skill or agent the founder added by hand matches neither test and stays.

```bash
for d in .claude/skills/*/; do [ -d "$d" ] && [ -d "skills/$(basename "$d")" ] && rm -rf "$d"; done
for f in .claude/agents/*.md; do [ -f "$f" ] && grep -qF "generated by scripts/agents_sync.py" "$f" && rm -f "$f"; done
rmdir .claude/skills .claude/agents 2>/dev/null
```

Then the rest of the system layer:

```bash
rm -rf skills/
rm -rf scripts/
rm -rf templates/
rm -rf notion-package/
rm -rf updates/
rm -rf .claude/commands/
rm -rf .claude/hooks/
rm -rf .claude-plugin/
rm -f .claude/settings.json
rm -rf docs/
rm -f VERSION AGENTS.md GEMINI.md AVATAR.md README.md CHANGELOG.md LICENSE install.sh uninstall.sh
```

Do NOT remove `CLAUDE.md`, `stack.json`, or `os-config.yaml` in default mode - all are User Layer per `/founder-os:update`. Setup writes the founder's tool bindings into `stack.json`; deleting it on default uninstall would lose those choices.

If running in PowerShell on Windows native (no git-bash), use:

```powershell
Get-ChildItem .claude/skills -Directory -ErrorAction SilentlyContinue | Where-Object { Test-Path (Join-Path skills $_.Name) } | Remove-Item -Recurse -Force
Get-ChildItem .claude/agents -Filter *.md -ErrorAction SilentlyContinue | Where-Object { Select-String -Path $_.FullName -SimpleMatch "generated by scripts/agents_sync.py" -Quiet } | Remove-Item -Force
Remove-Item -Recurse -Force skills, scripts, templates, notion-package, updates, docs
Remove-Item -Recurse -Force .claude/commands, .claude/hooks, .claude-plugin
Remove-Item -Force .claude/settings.json -ErrorAction SilentlyContinue
Remove-Item -Force VERSION, AGENTS.md, GEMINI.md, AVATAR.md, README.md, CHANGELOG.md, LICENSE, install.sh, uninstall.sh -ErrorAction SilentlyContinue
```

**Purge mode:** all of the above, plus `rules/`, every User Layer path, and the runtime and secret files the default mode leaves:

```bash
rm -rf rules/ core/ context/ cadence/ brain/ capture/ brands/ network/ clients/ companies/ roles/ system/ memory/
rm -rf state/ voice/ connectors/ .claude/
rm -f CLAUDE.md MEMORY.md stack.json os-config.yaml .env .env.* .mcp.json
```

PowerShell:

```powershell
Remove-Item -Recurse -Force rules, core, context, cadence, brain, capture, brands, network, clients, companies, roles, system, memory -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force state, voice, connectors, .claude -ErrorAction SilentlyContinue
Remove-Item -Force CLAUDE.md, MEMORY.md, stack.json, os-config.yaml, .env, .env.*, .mcp.json -ErrorAction SilentlyContinue
```

`state/` holds the pre-edit snapshot of every file changed in recent sessions, so leaving it keeps a copy of the data purge just removed. `voice/` holds the voice transcripts. `.env` holds the keys. All three are why "everything" has to name them.

Version history, only if the founder typed `DELETE HISTORY` in step 3: `rm -rf .git/` (PowerShell: `Remove-Item -Recurse -Force .git`). Otherwise leave `.git/` and say so in the final message.

Then, purge mode only: list any directory still left at the root. For each one the plan did not name (a company or project folder setup created), ask the operator per folder: delete or keep. Never guess.

### 5. Final confirmation

After removal:

```
Founder OS removed.

Default mode: your data is preserved at <list remaining folders>. Your data files are yours - you can now archive them, delete them by hand, or move them anywhere.

Plugin path: if you installed via the Claude Code plugin marketplace, also run `/plugin uninstall founder-os` to fully de-register the plugin from your Claude Code session.
```

If purge mode:

```
Founder OS purged. Everything Founder OS put in this folder is removed, including the session snapshots, voice transcripts, keys and connector files.
<if .git/ was kept:> Your version history (.git/) is still here, and it holds every saved version of the removed files. Delete the .git folder yourself if you want those gone too.

Plugin path: if you installed via the Claude Code plugin marketplace, also run `/plugin uninstall founder-os` to fully de-register the plugin from your Claude Code session.
```

Both modes, last: name the two things outside this folder that uninstall never touches, and how to remove them by hand. Never edit or delete them yourself - the first one is a shared file that holds the founder's own instructions too.

```
Two things outside this folder were not touched. Remove them by hand if you want them gone:

1. ~/.claude/CLAUDE.md (on Windows: %USERPROFILE%\.claude\CLAUDE.md). Setup added a short Founder OS block there. Open the file and delete everything from the line
   <!-- FOUNDER OS START - written by Founder OS setup. Edit or delete this block freely. -->
   down to and including the line
   <!-- FOUNDER OS END -->
   The rest of the file is yours; leave it as it is.

2. Claude Code's memory for this folder: <full path of ~/.claude/projects/<slug>/memory/ for this folder, resolved the same way setup step 1.3 resolves it; if it does not exist, say "no memory folder was created for this folder" instead>. Delete that memory folder.
```

## Rules

- Never run a destructive command before the user has confirmed in step 3.
- In default mode, NEVER touch the User Layer. Authoritative list lives in `/founder-os:update`. Currently: `core/`, `context/`, `cadence/`, `brain/`, `capture/`, `brands/`, `network/`, `clients/`, `companies/`, `roles/`, `system/`, `MEMORY.md`, `CLAUDE.md`, `stack.json`, `os-config.yaml` - plus `rules/`, protected by update as founder-personalized, so default uninstall preserves it too. If `update.md` adds a new User Layer path, mirror it here in the same commit or default uninstall will silently delete it.
- In purge mode, require the literal word `PURGE` in uppercase. No softer confirmations. `.git/` is removed only on a second, separate `DELETE HISTORY`.
- Never touch anything outside this folder. `~/.claude/CLAUDE.md` and `~/.claude/projects/<slug>/memory/` are named for the founder to remove by hand, never removed by this command.
- If any `rm` step fails (permissions, locked file), report the failure on its own line and continue with the next step. Do not abort halfway.
- This command does not push to any remote. The user is responsible for cleaning up any cloud copies (GitHub forks, Notion mirrors).
- No em dashes or en dashes. Hyphens only.

## Failure modes

- **Plugin install via marketplace**: this command can remove the local files but cannot de-register the plugin from Claude Code. Tell the user to run `/plugin uninstall founder-os` after this command.
- **Files locked by editor**: tell the user which file failed and ask them to close it before re-running.
- **Wrong directory**: if step 1 finds no plugin and no data, refuse to delete anything and explain how to find the install root.
