---
description: Uninstall Founder OS. Say "uninstall Founder OS" (or run /founder-os:uninstall). Lists what will be removed, asks confirmation, then removes plugin registration and (optionally with --purge) your data files. Default mode preserves your data.
argument-hint: "[--purge]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# Founder OS uninstall

Cleanly removes Founder OS from this machine. Two modes:

- **Default** (no argument): de-registers the plugin and removes the System Layer files (the skills, commands, scripts and hooks that shipped, templates). Preserves your personal data: `core/`, `context/`, `cadence/`, `brain/`, `network/`, `clients/`, `companies/`, `MEMORY.md`, `CLAUDE.md`, and `stack.json` (local tool bindings), plus any skill, command, script or hook you wrote and your names list `scripts/private-name-patterns.txt`.
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

Show the founder a single message. To fill in the "Yours, kept" lines, first run the lists and the read-only listing block from step 4: they remove nothing.

If `$ARGUMENTS` does NOT contain `purge`:

```
Uninstall plan (default mode - preserves your data):

Plugin registration:
- .claude-plugin/plugin.json
- .claude-plugin/marketplace.json

System layer (will be removed):
- skills/: the <n> skill folders that shipped with Founder OS, plus index.md, discoverable.yaml and the *-pack.md files
- scripts/: the files that shipped with Founder OS (the OS's Python helpers), file by file
- templates/, docs/, updates/, notion-package/, assets/
- .githooks/: the save checks that shipped (pre-commit, commit-msg, pre-push), and the git setting core.hooksPath if it points there and no hook of yours is left in .githooks/
- .claude/commands/: the <n> command files that shipped with Founder OS
- .claude/hooks/: the hook files that shipped with Founder OS
- .claude/settings.json (if present)
- .claude/skills/<the skill copies the OS generated> and .claude/agents/<the agent files the OS generated> (they point at scripts this removes, so left behind they break the next time Claude Code opens the folder; any skill or agent you added there yourself stays)
- VERSION, AGENTS.md, GEMINI.md, AVATAR.md, README.md, CHANGELOG.md, LICENSE, SECURITY.md, CONTRIBUTING.md, llms.txt, .gitattributes, Start Founder OS.bat, Start Founder OS.command, install.sh, uninstall.sh

<only when skills/legal-compliance/references/ exists:> A skill that shipped goes with anything you added inside it. A legal jurisdiction pack or sources you added with /legal-setup or /legal-add-source live in skills/legal-compliance/references/, so copy that folder out first to keep them.

Yours, kept (did not ship with Founder OS):
- <every folder in skills/, file in .claude/commands/, and file in scripts/, .claude/hooks/ and .githooks/ that is not on the shipped lists in step 4, by name; "none" if there are none>
- scripts/private-name-patterns.txt (your list of names to keep out of your files), if present
- <only when core.hooksPath points at .githooks and a hook of yours stays there:> the git setting core.hooksPath, so your own hooks keep running

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
- skills/ (all of it, including skills you wrote), scripts/ (all of it, including scripts you wrote and your names list), templates/, rules/, .claude/ (all of it, including generated skills and agents, commands and hooks you wrote and settings.local.json), docs/, updates/, notion-package/, assets/, .githooks/ (all of it, including hooks you added), and the git setting core.hooksPath if it points there
- VERSION, AGENTS.md, GEMINI.md, AVATAR.md, README.md, CHANGELOG.md, LICENSE, SECURITY.md, CONTRIBUTING.md, llms.txt, .gitattributes, Start Founder OS.bat, Start Founder OS.command, install.sh, uninstall.sh

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

`skills/`, `.claude/commands/`, `scripts/`, `.claude/hooks/` and `.githooks/` are where a founder adds their own skills, commands, scripts and hooks, so none of them is removed whole. Only the entries on these lists go: what shipped with Founder OS, including a few script and hook files retired from older releases that an updated install may still hold. A skill, command, script or hook the founder wrote is not on them and stays, and so does `scripts/private-name-patterns.txt`. The Python caches (`__pycache__` folders) inside those folders go too. `uninstall.sh` carries the same lists, and a test checks all of them against what the releases shipped.

```bash
SHIPPED_SKILLS="add-hands add-mouth add-voice approval-gates audit backup blind-spot-review
bottleneck-diagnostic brain-log brain-pass brain-snapshot brand-interview
brand-voice-interview business-context-loader campaign-from-theme
capture-sweep catch-up client-update connect content-repurposer
content-start context-persistence cross-link data-security
decision-framework decisions-start delivery-start email-drafter
employee-review finance-import forcing-questions founder-coaching
founder-next-move founder-os-setup founder-review founder-scope-challenge
github-ops handoff-protocol hire history housekeeping ingest
knowledge-capture legal-compliance linkedin-brand-direction
linkedin-network-scan linkedin-pack-references linkedin-post
linkedin-power-audit linkedin-start linkedin-warm-revival lint list-pruner
log-archive log-reply meeting-prep memory-pass menu morning-loop
observation-rollup os-evolve own-your-history pipeline-start pitch-deck
pre-send-check priority-triage profile-router proposal-writer prospect-init
query queue readiness-check reconnect-prompt restore review-responder
routines save self-diligence session-handoff ship-deliverable
since-last-session skill-creator sop-writer strategic-analysis
strategic-read today tune unit-economics verify voice-interview
web-fetch-extract weekly-review what-to-change where wiki-build
writing-score your-deliverable-template your-voice"
SHIPPED_SKILL_FILES="index.md discoverable.yaml content-pack.md decisions-pack.md delivery-pack.md
linkedin-pack.md money-pack.md pipeline-pack.md"
SHIPPED_COMMANDS="audit.md brain-pass.md brand-interview.md brand-voice-interview.md
campaign-from-theme.md capture-meeting.md capture-sweep.md catch-up.md
changes.md devil.md dream.md employee-review.md forcing-questions.md
founder-review.md housekeeping.md ingest.md legal-add-source.md
legal-setup.md legal-update.md linkedin-scan.md lint.md log-reply.md
menu.md morning-loop.md next.md observation-rollup.md os-evolve.md
pitch-deck.md pre-meeting.md query.md queue.md rant.md review-responder.md
self-diligence.md setup.md ship-deliverable.md since-last-session.md
status.md strategic-read.md today.md uninstall.md update.md verify.md
voice-interview.md where.md wiki-build.md writing-score.md"
SHIPPED_SCRIPTS="_common.py agent_runs.py agents_sync.py brain-pass-log.py brain-snapshot.py
build_release.py caveman_git.py check-brand-voice-ready.py
check-identity-ready.py check-log-has-history.py check-private-names.py
check-voice-ready.py check_download_links.py claims_check.py connect.py
deliverable_gate.py employee_verdict.py entity_check.py flat_yaml.py
hooks/dispatch.py install-git-hooks.sh list-brands.py log-archive.py
memory-diff.py menu.py observation-rollup.py open_folder.py pitch_deck.py
private-name-patterns.txt.template query.py register_census.py
render-playbook.py render-skills.py scrape.py selfdoc_check.py
session_changes.py set_folder_icon.sh skill_health.py skills_sync.py
unconfirmed_facts.py unit_math.py user-prompt-capture.py verify.py
what-to-change.py where.py wiki-build.py writing_scorecard.py"
SHIPPED_CLAUDE_HOOKS="session_start_brief.py
post-tool-use-observation.ps1 post-tool-use-observation.sh
pre-compact-flush.ps1 pre-compact-flush.sh
pre-tool-use-snapshot.ps1 pre-tool-use-snapshot.sh
session-close-autosave.ps1 session-close-autosave.sh
session-close-changes.ps1 session-close-changes.sh
session-close-revenue-check.ps1 session-close-revenue-check.sh
session-start-brief.ps1 session-start-brief.sh
session-start-liveness.ps1 session-start-liveness.sh
user-prompt-capture.ps1 user-prompt-capture.sh"
SHIPPED_GITHOOKS="pre-commit commit-msg pre-push"
```

Read-only, and the same listing step 2 shows: every entry in the five folders that is not on its list. These are the founder's own.

```bash
on_list() { case " $(echo $2) " in *" $1 "*) return 0 ;; esac; return 1; }
for p in skills/* skills/.[!.]*; do [ -e "$p" ] && ! on_list "${p#skills/}" "$SHIPPED_SKILLS $SHIPPED_SKILL_FILES" && echo "$p"; done
for p in .claude/commands/* .claude/commands/.[!.]*; do [ -e "$p" ] && ! on_list "${p#.claude/commands/}" "$SHIPPED_COMMANDS" && echo "$p"; done
find scripts .claude/hooks .githooks -type f ! -path '*/__pycache__/*' 2>/dev/null | while IFS= read -r p; do
  case "$p" in
    scripts/*) on_list "${p#scripts/}" "$SHIPPED_SCRIPTS" || echo "$p" ;;
    .claude/hooks/*) on_list "${p#.claude/hooks/}" "$SHIPPED_CLAUDE_HOOKS" || echo "$p" ;;
    .githooks/*) on_list "${p#.githooks/}" "$SHIPPED_GITHOOKS" || echo "$p" ;;
  esac
done
```

First, while `skills/` still exists, remove the copies the OS generated inside `.claude/`. Only two kinds qualify, and nothing else in those folders is touched: a `.claude/skills/<name>/` folder whose `<name>` is on `SHIPPED_SKILLS` (the copies `skills_sync.py` writes of the product's skills), and a `.claude/agents/*.md` file containing the line marker `generated by scripts/agents_sync.py` (the agents `agents_sync.py` writes; the registry row in `roles/employees.yaml` that generated it is kept). A skill or agent the founder added by hand matches neither test and stays.

```bash
for s in $SHIPPED_SKILLS; do [ -d ".claude/skills/$s" ] && rm -rf ".claude/skills/$s"; done
for f in .claude/agents/*.md; do [ -f "$f" ] && grep -qF "generated by scripts/agents_sync.py" "$f" && rm -f "$f"; done
rmdir .claude/skills .claude/agents 2>/dev/null
```

Then the shipped entries of `skills/`, `.claude/commands/`, `scripts/`, `.claude/hooks/` and `.githooks/`, and the Python caches inside the last three:

```bash
for s in $SHIPPED_SKILLS $SHIPPED_SKILL_FILES; do rm -rf "skills/$s"; done
for c in $SHIPPED_COMMANDS; do rm -f ".claude/commands/$c"; done
for f in $SHIPPED_SCRIPTS; do rm -f "scripts/$f"; done
for f in $SHIPPED_CLAUDE_HOOKS; do rm -f ".claude/hooks/$f"; done
for f in $SHIPPED_GITHOOKS; do rm -f ".githooks/$f"; done
find scripts .claude/hooks .githooks -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
rmdir scripts/hooks 2>/dev/null
rmdir skills .claude/commands scripts .claude/hooks .githooks 2>/dev/null
```

Then the rest of the system layer:

```bash
rm -rf templates/
rm -rf notion-package/
rm -rf updates/
rm -rf assets/
rm -rf .claude-plugin/
rm -f .claude/settings.json
rm -rf docs/
rm -f VERSION AGENTS.md GEMINI.md AVATAR.md README.md CHANGELOG.md LICENSE SECURITY.md CONTRIBUTING.md llms.txt .gitattributes install.sh uninstall.sh
rm -f "Start Founder OS.bat" "Start Founder OS.command"
```

Last, the git setting that ran the save checks. They call scripts this just removed. Change it only when it points at `.githooks` and `.githooks/` is gone, and say so in one line: `Turned off the git setting core.hooksPath: the save checks it ran are gone, and left on it would stop every commit.` When a hook of the founder's own is still in `.githooks/`, leave the setting on, because it is what runs that hook, and say: `Left the git setting core.hooksPath on: your own hooks in .githooks/ still run.`

```bash
[ -e .git ] && [ ! -d .githooks ] && [ "$(git config --local --get core.hooksPath)" = ".githooks" ] && git config --local --unset core.hooksPath
```

Then list what stays in `skills/`, `.claude/commands/`, `scripts/`, `.claude/hooks/` and `.githooks/`, if those folders still exist, and name each entry in the final message: these are the founder's own.

Do NOT remove `CLAUDE.md`, `stack.json`, or `os-config.yaml` in default mode - all are User Layer per `/founder-os:update`. Setup writes the founder's tool bindings into `stack.json`; deleting it on default uninstall would lose those choices.

If running in PowerShell on Windows native (no git-bash), set the same six lists as PowerShell arrays (`$ShippedSkills = @('add-hands', ...)`, `$ShippedScripts = @('_common.py', ..., 'hooks/dispatch.py', ...)`, every name from the lists above), then:

```powershell
$ShippedSkills | ForEach-Object { Remove-Item -Recurse -Force (Join-Path .claude/skills $_) -ErrorAction SilentlyContinue }
Get-ChildItem .claude/agents -Filter *.md -ErrorAction SilentlyContinue | Where-Object { Select-String -Path $_.FullName -SimpleMatch "generated by scripts/agents_sync.py" -Quiet } | Remove-Item -Force
($ShippedSkills + $ShippedSkillFiles) | ForEach-Object { Remove-Item -Recurse -Force (Join-Path skills $_) -ErrorAction SilentlyContinue }
$ShippedCommands | ForEach-Object { Remove-Item -Force (Join-Path .claude/commands $_) -ErrorAction SilentlyContinue }
$ShippedScripts | ForEach-Object { Remove-Item -Force (Join-Path scripts $_) -ErrorAction SilentlyContinue }
$ShippedClaudeHooks | ForEach-Object { Remove-Item -Force (Join-Path .claude/hooks $_) -ErrorAction SilentlyContinue }
$ShippedGitHooks | ForEach-Object { Remove-Item -Force (Join-Path .githooks $_) -ErrorAction SilentlyContinue }
Get-ChildItem scripts, .claude/hooks, .githooks -Recurse -Directory -Force -Filter __pycache__ -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force templates, notion-package, updates, docs, assets -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .claude-plugin -ErrorAction SilentlyContinue
Remove-Item -Force .claude/settings.json -ErrorAction SilentlyContinue
Remove-Item -Force VERSION, AGENTS.md, GEMINI.md, AVATAR.md, README.md, CHANGELOG.md, LICENSE, SECURITY.md, CONTRIBUTING.md, llms.txt, .gitattributes, install.sh, uninstall.sh, 'Start Founder OS.bat', 'Start Founder OS.command' -ErrorAction SilentlyContinue
foreach ($d in 'scripts/hooks', 'skills', '.claude/commands', 'scripts', '.claude/hooks', '.githooks') { if ((Test-Path $d) -and -not (Get-ChildItem $d -Force)) { Remove-Item $d } }
if ((Test-Path .git) -and -not (Test-Path .githooks) -and ((git config --local --get core.hooksPath) -eq '.githooks')) { git config --local --unset core.hooksPath }
```

PowerShell does not report a failed `Remove-Item` here (`SilentlyContinue`), so check by listing: what is left in those five folders must be only the founder's own entries, and name each one.

**Purge mode:** all of the above, plus `rules/`, every User Layer path, and the runtime and secret files the default mode leaves:

```bash
rm -rf rules/ core/ context/ cadence/ brain/ capture/ brands/ network/ clients/ companies/ roles/ system/ memory/
rm -rf state/ voice/ connectors/ .claude/ skills/ scripts/ .githooks/
rm -f CLAUDE.md MEMORY.md stack.json os-config.yaml .env .env.* .mcp.json
[ -e .git ] && [ "$(git config --local --get core.hooksPath)" = ".githooks" ] && git config --local --unset core.hooksPath
```

PowerShell:

```powershell
Remove-Item -Recurse -Force rules, core, context, cadence, brain, capture, brands, network, clients, companies, roles, system, memory -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force state, voice, connectors, .claude, skills, scripts, .githooks -ErrorAction SilentlyContinue
Remove-Item -Force CLAUDE.md, MEMORY.md, stack.json, os-config.yaml, .env, .env.*, .mcp.json -ErrorAction SilentlyContinue
if ((Test-Path .git) -and ((git config --local --get core.hooksPath) -eq '.githooks')) { git config --local --unset core.hooksPath }
```

`state/` holds the pre-edit snapshot of every file changed in recent sessions, so leaving it keeps a copy of the data purge just removed. `voice/` holds the voice transcripts. `.env` holds the keys. All three are why "everything" has to name them.

Version history, only if the founder typed `DELETE HISTORY` in step 3: `rm -rf .git/` (PowerShell: `Remove-Item -Recurse -Force .git`). Otherwise leave `.git/` and say so in the final message.

Then, purge mode only: list any directory still left at the root. For each one the plan did not name (a company or project folder setup created), ask the operator per folder: delete or keep. Never guess.

### 5. Final confirmation

After removal:

```
Founder OS removed.

Default mode: your data is preserved at <list remaining folders>. Kept because you made them: <each skill folder, command file, script, hook and scripts/private-name-patterns.txt still left in skills/, .claude/commands/, scripts/, .claude/hooks/ and .githooks/, by name; leave the line out if there are none>. Your data files are yours - you can now archive them, delete them by hand, or move them anywhere.

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
