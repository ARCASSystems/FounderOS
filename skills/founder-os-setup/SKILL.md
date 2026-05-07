---
name: founder-os-setup
description: >
  Interactive setup wizard for Founder OS. Run this after installing the plugin to create your personalized founder operating environment. Creates identity files, brain system, cadence management, role-based operating modes, and project structure. Run /founder-os:setup to start.
argument-hint: "[reset] - run with 'reset' to reconfigure an existing setup"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
mcp_requirements: []
---

# Founder OS Setup Wizard

You are running an interactive setup wizard that builds a complete operating environment for a founder using Claude Code. Follow the phases IN ORDER. Ask ONE question at a time. Wait for the answer before moving on.

## Rules

- Ask ONE question at a time. Wait for the answer.
- When a step requires user input, show what you'll create BEFORE creating it. Get a "yes" or adjustment.
- When creating folders, check what already exists first. Don't overwrite. Don't duplicate.
- Keep CLAUDE.md files LEAN. Global under 80 lines. Company under 60. Project under 40. Bootloader under 120.
- Track everything skipped or deferred in a BACKLOG at the end of the setup.
- After each phase, show a quick status: what's done, what's next.
- If the user says "skip" or "later", log it and move on. Don't push back.

## Handling Real Human Input

Founders don't answer questions like a form. They ramble, go on tangents, answer three questions at once, skip ahead, circle back, and think out loud. This is expected. Handle it:

- **If they answer multiple questions in one response:** Extract all the answers. Mark those questions as answered. Move to the next unanswered question. Don't re-ask what they already told you.
- **If they go on a tangent:** Extract anything useful from the tangent (business context, priorities, pain points, tool preferences). Log it. Gently return to the current question without making them feel corrected.
- **If they skip a question:** Move on. Come back to it later if the answer becomes important for file generation. If it never matters, leave it blank.
- **If they give a partial answer:** Use what you got. Only ask for the specific missing piece, not the whole question again.
- **If they contradict themselves:** Use the most recent answer. Don't flag contradictions unless they materially affect the setup.
- **If they dump everything at once:** Great. Parse it all, map answers to phases, and skip ahead to wherever you have enough info to start building. Show them what you captured and what's still missing.
- **Never ask the user to be more structured.** Adapt to them. That's the whole point of this system.

## Before Starting

Read the templates directory that comes with this plugin. These templates define the structure of every file you'll create. Read each template before generating the personalized version.

Templates location: find the plugin install path, then look in `templates/`.

If the user passed "reset": scan for an existing Founder OS folder, confirm they want to reconfigure, then re-run discovery.

---

## PHASE 0: DISCOVERY

Ask these questions one at a time. Record answers internally.

### 0.1 Who Are You?
Ask: "Let's set up your Founder OS. First - what's your name, and what do you do? Give me the one-sentence version of your business (or businesses if you run more than one)."

### 0.2 Business Map
If they mentioned multiple businesses, ask for each: "For each business, tell me: name, what it does in one sentence, and who else is involved (co-founders, key team members, or just you)."

If they have one business, move to 0.3.

### 0.3 Active Workstreams
For EACH business: "What are you actively working on right now in [business name]? Examples: website, email campaigns, lead generation, content, product development, client delivery, hiring."

Each workstream becomes a potential project folder.

### 0.4 Immediate Priorities
Ask: "Of everything you just listed, what are the top 3 things you need Claude helping with THIS WEEK? Be specific."

These get built first. Everything else is structure for later.

### 0.5 Tool Stack
Ask: "What tools do you use day to day? Go through this list. Skip any you do not use - I will record those as `none`."

- **Knowledge base**: Notion, Obsidian, Google Drive, local-only?
- **Email**: Gmail, Outlook, Apple Mail?
- **Calendar**: Google Calendar, Outlook Calendar?
- **Automation**: n8n, Make, Zapier, none?
- **CRM**: Notion DB, HubSpot, Airtable, none?
- **File storage**: Google Drive, Dropbox, local, none?
- **Meeting notes**: Granola, Otter, Notion, none?
- **Voice input**: Wispr Flow, Whisper local, none?
- **Server / hosting**: Hostinger, DigitalOcean, Render, none?
- **Prospecting database**: Apollo, Sales Navigator, LinkedIn, none?
- **Video tool**: Loom, Zoom, none?
- **Booking**: Cal.com, Calendly, none?

These twelve fields populate `stack.json`, which sop-writer, meeting-prep, email-drafter, and other skills read at runtime to tailor output to the user's actual stack. Map answers to the exact lowercase tokens listed in `stack.json`'s `_allowed_values`.

### 0.6 Existing Setup Audit
Before proceeding, scan the filesystem silently:
- Read `~/.claude/CLAUDE.md` if it exists
- Read `~/.claude/settings.json` if it exists
- Check common project folder locations for existing CLAUDE.md files

Report what you found. This prevents duplication.

### 0.7 How You Work
Ask: "A few quick ones about how you work:
- Do you prefer morning or evening deep work?
- How do you make decisions - gut feel, spreadsheets, or talk it through?
- What's your communication style - direct and short, or detailed and thorough?
- What overwhelms you most about running your business?"

These answers personalize the operating rules and identity file.

**Encoding (mandatory).** Map the answers to these structured tokens. Skills downstream read the tokens, not the prose.

- "gut feel" / "instinct" / "feel" → `gut`
- "spreadsheets" / "data" / "numbers" / "math first" → `data`
- "talk it through" / "out loud" / "sounding board" → `dialogue`
- mixed answer or unclear → `mixed`

For communication style:

- "direct" / "short" / "lead with the answer" / "no filler" → `direct`
- "detailed" / "thorough" / "context first" / "build up" → `detailed`

When you write `core/identity.md` in Phase 1.1, populate `**Decision style:**` with the token. When you write `rules/operating-rules.md` in Phase 2.2, populate `**Communication style:**` with the token. Use the prose answer for the descriptive paragraph that follows.

### 0.8 Privacy Layers
Ask: "Last setup question. Some information is private to you, some you'd share with a co-founder or team member. Any businesses where someone else might see the project files? And anything that should ONLY live in your private global config?"

### 0.9 Observation Logging (opt-in)

Ask: "Optional: do you want Claude Code to log every tool call into a daily JSONL? Useful if you want a forensic record of what was touched in each session. Off by default. (yes / no / later)"

This is the `FOUNDER_OS_OBSERVATIONS` opt-in. The PostToolUse hook ships disabled. It only writes when the env var is set to `1`.

- If `no` or `later`: log to backlog as "Observation logging not enabled. Set `FOUNDER_OS_OBSERVATIONS=1` if you want it later." Move on.
- If `yes`:
  1. Create the `brain/observations/` folder at the Founder OS root.
  2. Copy `templates/brain/observations/README.md` to `brain/observations/README.md`. Do not edit the contents.
  3. Tell the user how to set the env var in their shell. Do NOT modify their shell config without explicit approval. Suggested copy:

     > "Add this to your shell config so the hook fires in new sessions:
     > - Bash / Zsh: `export FOUNDER_OS_OBSERVATIONS=1` in `~/.bashrc` or `~/.zshrc`
     > - PowerShell: `$env:FOUNDER_OS_OBSERVATIONS = '1'` in `$PROFILE`
     > - Windows (system-wide): run `setx FOUNDER_OS_OBSERVATIONS 1` once
     >
     > Restart your shell after editing. The hook stays silent until the variable is set."

  4. Append a one-line note to `core/setup-backlog.md` reminding them to set the env var. If the file does not exist, create it with the heading `## Setup Backlog` followed by the note. Example note: `- [ ] Set FOUNDER_OS_OBSERVATIONS=1 in shell env to enable observation logging.`

---

## PHASE 1: IDENTITY + GLOBAL LAYER

### 1.1 Identity File
Using discovery answers, draft `core/identity.md`. Read the template from `templates/identity.md` for structure. Personalize with their actual background, work style, decision style, communication preferences, and overwhelm triggers.

Show the draft. Get approval. Don't write yet.

### 1.2 Global CLAUDE.md
Create or update `~/.claude/CLAUDE.md`. Read `templates/global-claude-md.md` for structure. Keep under 80 lines.

This file should:
- Name the founder and list their businesses
- Set behavioral rules (direct communication, no filler, lead with answers)
- Set context isolation rules (each project loads only its own context)
- Include their communication preferences from 0.7

Show the draft. Get approval. Write it.

### 1.3 Auto-memory layer (cross-session behavioral memory)

Claude Code reads a per-project `MEMORY.md` automatically at every session start. This is the layer that remembers behavioral corrections across sessions. Without it, the same corrections need to be repeated every new session.

Steps:

1. Resolve the auto-memory path for the founder's working directory.
   - **First, check what already exists.** List the entries under `~/.claude/projects/` (macOS / Linux) or `%USERPROFILE%\.claude\projects\` (Windows). Since this wizard is running inside Claude Code, the slug for the founder's current working directory is already there. Pick the entry that matches the absolute path of the install location (most recently modified is usually it).
   - **If no matching entry exists** (rare - means Claude Code has not registered the project yet), fall back to the computed slug rule:
     - macOS / Linux: take the absolute path, replace `/` with `-`, drop the leading `-` if any. e.g. `/Users/jane/founder-os` -> `Users-jane-founder-os`.
     - Windows: prefix with `c--` (the colon becomes `--`), replace `\` with `-`, lowercase the drive letter. e.g. `C:\Users\Jane\founder-os` -> `c--Users-Jane-founder-os`.
   - Target file: `<claude_projects_dir>/<slug>/memory/MEMORY.md` where `<claude_projects_dir>` is `~/.claude/projects/` on macOS / Linux and `%USERPROFILE%\.claude\projects\` on Windows.
   - **Confirm the path with the user** before writing. Show: "I will write your auto-memory template to: `<full path>`. Proceed? (yes / no / I'll set it up later)" - this catches a wrong slug before the file lands in the wrong place.

2. If the target file already exists, read it. If it has any real content (not just template scaffolding), do not overwrite. Add a note to the setup backlog: "Auto-memory file already exists at <path>. Skipped templating to preserve existing entries."

3. If the target file does not exist or only contains placeholders, copy `templates/memory/MEMORY.md` verbatim to the target path. Create parent directories as needed.

4. Confirm to the user: "Wrote auto-memory template to `<path>`. Add behavioral guards as Claude needs corrections - they persist across every future session in this folder."

This step is optional. If the user opts out (no), log to backlog and continue. Skills do not depend on auto-memory existing; this is a continuity layer, not a hard dependency.

### 1.4 Global Settings (opt-in)

This phase is OPT-IN. Never silently modify the user's global settings file.

First, ASK: "Founder OS works best when project-scoped MCPs are not duplicated globally. I can move duplicates from your global `~/.claude/settings.json` to project-scoped settings. This affects MCP behavior in OTHER Claude Code projects you have. Move them? (yes / no / skip)"

- If the user says "no" or "skip", skip this phase entirely. Move to Phase 2. Log the skip in the backlog.
- If the user says "yes", proceed with the next steps.

Safety backup (required before any edit):
1. Read `~/.claude/settings.json`.
2. Copy it to `~/.claude/settings.json.backup-{timestamp}` where timestamp is `YYYYMMDD-HHMMSS`. Confirm the backup exists on disk before proceeding.
3. Tell the user: "Backup saved to `~/.claude/settings.json.backup-{timestamp}`. You can restore manually if anything breaks."

Then review `~/.claude/settings.json`. Only GitHub should stay global. Propose moving everything else to per-project `.mcp.json` files. Show the exact diff (what moves where). Get approval before writing.

---

## PHASE 2: FOUNDER OS ROOT

### 2.1 Choose Location
Ask: "Where do you want your Founder OS folder? This is your operating headquarters - priorities, decisions, brain log, weekly planning all live here. Default: ~/founder-os/"

### 2.2 Create Structure
Create the full folder structure. Read each template before generating the personalized version:

```
[founder-os-root]/
├── CLAUDE.md                    # Bootloader (from templates/bootloader-claude-md.md)
├── core/
│   ├── identity.md              # From Phase 1.1
│   ├── avatar.md                # From templates/avatar.md (replace {{FOUNDER_NAME}}, leave prompts intact)
│   ├── voice-profile.yml        # Copied from templates/voice-profile.yml.template (placeholders intact - filled later by voice-interview)
│   └── brand-profile.yml        # Copied from templates/brand-profile.yml.template (placeholders intact - filled later by brand-interview)
├── brain/
│   ├── index.md                 # From templates/brain/index.md
│   ├── log.md                   # From templates/brain/log.md
│   ├── patterns.md              # From templates/brain/patterns.md
│   ├── flags.md                 # From templates/brain/flags.md
│   ├── decisions-parked.md      # From templates/brain/decisions-parked.md
│   ├── needs-input.md           # From templates/brain/needs-input.md
│   ├── knowledge/
│   │   └── README.md            # From templates/brain/knowledge/README.md
│   ├── rants/
│   │   └── README.md            # From templates/brain/rants/README.md (kept by /rant + /dream)
│   └── relations.yaml           # From templates/brain/relations.yaml (replace {{TODAY}} with current date)
├── system/
│   └── quarantine.md            # From templates/system/quarantine.md (catch-net for silent hook/task failures)
├── brain/archive/               # Empty dir. /dream and weekly-review move month-old brain entries here.
├── companies/                   # Empty dir. business-context-loader writes per-company files here.
├── scripts/
│   ├── wiki-build.py            # From templates/scripts/wiki-build.py (extracts [[wikilinks]] into brain/relations.yaml)
│   ├── query.py                 # From templates/scripts/query.py (plain-file graph query)
│   ├── brain-snapshot.py        # From templates/scripts/brain-snapshot.py (writes brain/.snapshot.md - runtime context for output skills)
│   └── brain-pass-log.py        # From templates/scripts/brain-pass-log.py (opt-in JSONL telemetry for /founder-os:brain-pass)
├── cadence/
│   ├── daily-anchors.md         # From templates/cadence/daily-anchors.md
│   ├── weekly-commitments.md    # Personalized with their current priorities
│   ├── quarterly-sprints.md     # Personalized with their Q goals
│   └── annual-targets.md        # Personalized with their year goals
├── context/
│   ├── priorities.md            # Personalized from 0.4
│   ├── decisions.md             # From templates/context/decisions.md
│   ├── companies.md             # Personalized from 0.1/0.2
│   └── clients.md               # From templates/context/clients.md
├── roles/
│   ├── index.md                 # From templates/roles/index.md
│   ├── coo.md                   # From templates/roles/coo.md
│   ├── cmo.md
│   ├── chief-of-staff.md
│   └── bd.md
├── rules/
│   ├── operating-rules.md       # Personalized from 0.7
│   ├── writing-style.md         # From templates/rules/writing-style.md
│   ├── entry-conventions.md     # From templates/rules/entry-conventions.md (bi-temporal + decay convention for flags/patterns/decisions)
│   └── approval-gates.md        # From templates/rules/approval-gates.md (what auto-runs vs requires explicit yes)
├── network/
│   ├── inner-circle.md          # Personalized from 0.2 (key people mentioned)
│   ├── mentors.md               # Stub
│   └── team.md                  # Personalized from 0.2 (team members mentioned)
└── .claude/
    ├── settings.json            # Copied from <plugin-root>/.claude/settings.json (wires SessionStart + Stop + PostToolUse hooks)
    └── hooks/
        ├── session-start-brief.sh   # Copied from <plugin-root>/.claude/hooks/session-start-brief.sh
        ├── session-start-brief.ps1  # Copied from <plugin-root>/.claude/hooks/session-start-brief.ps1
        ├── session-close-revenue-check.sh   # Copied from <plugin-root>/.claude/hooks/session-close-revenue-check.sh
        ├── session-close-revenue-check.ps1  # Copied from <plugin-root>/.claude/hooks/session-close-revenue-check.ps1
        ├── post-tool-use-observation.sh     # Copied from <plugin-root>/.claude/hooks/post-tool-use-observation.sh (opt-in, off until FOUNDER_OS_OBSERVATIONS=1)
        └── post-tool-use-observation.ps1    # Copied from <plugin-root>/.claude/hooks/post-tool-use-observation.ps1 (opt-in, off until FOUNDER_OS_OBSERVATIONS=1)
```

Show the full list of files that will be created. Get approval. Then create them all.

**Hook copy step (mandatory).** The SessionStart brief, session-close revenue check, and post-tool-use observation hook live in the plugin's `.claude/hooks/` and are wired by `.claude/settings.json` via `$CLAUDE_PROJECT_DIR/.claude/hooks/...`. For these to fire in the founder's working directory, the hook scripts AND `settings.json` must exist at the founder's project root. Find the plugin install path (same as where templates live), then copy all six hook files plus `settings.json` from the plugin's `.claude/` to the founder's `.claude/`. Do NOT modify file contents. If a `.claude/settings.json` already exists in the founder's repo (from a prior install), merge by adding the SessionStart, Stop, and PostToolUse hook entries. Do not overwrite the user's other hook customisations. The PostToolUse hook is opt-in - it stays silent until `FOUNDER_OS_OBSERVATIONS=1` is set in the shell env.

**Scripts copy step (mandatory).** Copy all four Python helpers from `templates/scripts/` to the founder's `scripts/`, byte-for-byte:

- `templates/scripts/wiki-build.py` → `scripts/wiki-build.py` (used by `/founder-os:wiki-build`)
- `templates/scripts/query.py` → `scripts/query.py` (used by `/founder-os:query`)
- `templates/scripts/brain-snapshot.py` → `scripts/brain-snapshot.py` (writes `brain/.snapshot.md`, read at task time by nine output-producing skills)
- `templates/scripts/brain-pass-log.py` → `scripts/brain-pass-log.py` (opt-in JSONL telemetry for `/founder-os:brain-pass`)

These are not personalized templates. Copy contents exactly. Do not edit. Verify all four copies exist on disk before continuing. If any are missing the brain-snapshot, brain-pass, and wiki-build skills will fail silently or hard-error.

**{{TODAY}} substitution.** The `templates/brain/relations.yaml` file contains the literal placeholder `{{TODAY}}`. When copying to `brain/relations.yaml`, replace every occurrence of `{{TODAY}}` with today's date in `YYYY-MM-DD` format (use `date -u +%Y-%m-%d` via Bash to get it).

**Avatar template copy.** Copy `templates/avatar.md` to `core/avatar.md` and replace `{{FOUNDER_NAME}}` with the founder name captured in Phase 0.1. Do not auto-populate the bracketed sections. The wizard asks the seed questions, then the founder fills or revises those prompts in their first review session.

### 2.3 Initialize Git

Guard: check if a `.git/` directory already exists in the Founder OS root before running `git init`.

- If `.git/` exists (the common case, because the install folder is already a git clone), SKIP `git init`. Log: "Folder is already a git repository. Skipping git init." Move on.
- If `.git/` does not exist (rare case, user copied files manually instead of cloning), run `git init` and create an initial commit: "Founder OS initialized."

### 2.4 First Weekly Sprint
Ask: "Let's set your first weekly sprint. You mentioned these priorities: [list from 0.4]. Which of these are MUST DO this week (max 3), which are SHOULD DO, and which can wait?"

Write the answers into `cadence/weekly-commitments.md`.

---

## PHASE 3: COMPANY FOLDERS

For each business from Phase 0:

### 3.1 Create Company Folder
Ask where they keep their project folders. Create the company folder if it doesn't exist.

### 3.2 Company CLAUDE.md
Read `templates/company-claude-md.md` for structure. Personalize with:
- Business name and description
- Key people from 0.2
- Active projects (will be filled in Phase 4)
- Business-specific rules or constraints

Under 60 lines. Show draft. Get approval. Write it.

### 3.2.5 Company business-context file (recommended)

Copy `templates/business-context.template.md` to `companies/<slug>-business.md` (where `<slug>` is the company folder name from 3.1). Replace the obvious placeholders ({{COMPANY_NAME}}, {{TAGLINE}}, {{YEAR}}) with what the founder gave in Phase 0.1 / 0.2. Leave the `[FILL]` markers intact - the `business-context-loader` skill walks them on first run with the founder.

This file is the input that `business-context-loader`, `proposal-writer`, `client-update`, and `strategic-analysis` read for ICP, pricing tier, positioning, and offer structure. Without it those skills produce generic output. The wizard surfaces it once; the founder fills it the first time they need a company-specific deliverable.

If the founder skips it, log a backlog item: `- [ ] Fill companies/<slug>-business.md before next proposal or strategic analysis`.

### 3.3 Company .mcp.json
Based on tool stack from 0.5, create a `.mcp.json` with only the MCPs this business needs.

Show proposed config. Get approval. Write it.

---

## PHASE 4: FIRST PROJECT

Take the top priority from 0.4. Build it properly as the reference project.

### 4.1 Create Project Folder
Inside the correct company folder. Choose the right template based on project type:

- **Email/Campaigns**: templates/, active/, data/, archive/
- **Website**: src/, content/, assets/, reference/
- **Lead Pipeline**: prospects/, outreach/, templates/
- **Data/Dashboards**: exports/, reports/, queries/
- **General**: docs/

### 4.2 Project CLAUDE.md
Read `templates/project-claude-md.md` for structure. Under 40 lines. Include:
- What this project does
- Current task
- Tools used
- Project-specific rules

### 4.3 Project .mcp.json
Subset of company MCPs relevant to this project.

### 4.4 Live Test
Ask: "Do you have a real task in this project we can try right now - even a small one? A draft, a note, a decision to log?"

If they have something, execute it. Confirm only project context loaded, MCPs work, output quality is good.

If they don't have a task yet (no active clients, pre-revenue, just starting), skip the live test. Tell them: "You can run `/founder-os:status` anytime to check readiness, and test a real task once one comes up."

---

## PHASE 5: REMAINING PROJECTS + CROSS-REFERENCES

### 5.0 Write Tool Stack to stack.json

Take the tool-stack answers captured in Phase 0.5 (knowledge base, email, calendar, automation, CRM, file storage, meeting notes, voice input, server, prospecting DB, video tool, booking) and write them to `stack.json` at the Founder OS root.

Steps:
1. Read the existing `stack.json`. Preserve the `_description`, `_wizard_version`, `_allowed_values`, and `_notes` fields.
2. Set `_generated` to today's date in `YYYY-MM-DD` format.
3. For each field the user answered in 0.5, set the value to the exact lowercase token from `_allowed_values` (e.g. `notion`, `gmail`, `google_calendar`, `n8n`). If the user named a tool not in `_allowed_values`, ask them to pick the closest match or set the value to `null` and log the actual tool name in the backlog.
4. For fields the user did not answer, leave the value as `null`.
5. Validate the file is parseable JSON before writing. If parse fails, stop and surface the error.
6. Confirm to the user: "Wrote your tool stack to `stack.json`. Skills that adapt to your tools now read from here."

### 5.1 Skeleton Projects
For each remaining workstream from 0.3 that wasn't built in Phase 4:
- Create the folder with a stub CLAUDE.md and .mcp.json
- Don't spend time on full setup - just the skeleton

### 5.2 Update Company Files
Go back to each company CLAUDE.md and update the "Active Projects" section.

### 5.3 Verify Isolation
Open two different project folders (ideally different businesses). Confirm:
- No context from Business A appears in Business B
- MCPs are scoped correctly
- Global identity is accessible when needed but not pre-loaded

---

## PHASE 6: VALIDATE + ORIENT

### 6.1 Final Commit
Commit all company and project folders: "Add company folders and first project setup."

### 6.2 Orient the User
Show the user what they have AND the next two profile steps. The wizard creates the operating layer, but the writing skills are gated on the voice and brand profiles - tell them this directly.

"Your Founder OS is set up. The operating layer is live. Two more 10-minute steps activate the writing skills:

**Step 1 - Voice profile.** Run `/founder-os:voice-interview`. The interview captures how you write. After this, linkedin-post, client-update, proposal-writer, email-drafter, content-repurposer, sop-writer, and your-voice all write as you instead of as Claude. ~10 minutes.

**Step 2 - Brand profile.** Run `/founder-os:brand-interview`. Captures your visual brand (colors, fonts, logo). After this, your-deliverable-template, branded proposals, and branded client updates render in your visual identity. ~10 minutes.

**Step 3 - Check readiness.** Run `/founder-os:status`. Returns a 0-100% score across Core, Voice and Brand, Cadence, Business Context, and Brain Layer. Names the next 3 high-impact moves.

Then start using it:

**Daily:** Open Claude Code in your Founder OS folder. Run `/today` for a one-screen view, or `/next` for one recommended action.

**Weekly:** Run your weekly review. Claude rolls the sprint, does the retro, and sets the next week.

**When overwhelmed:** Say 'I'm overwhelmed' or 'what should I focus on' - Claude triages your priorities.

**When you learn something:** Say 'capture this' or 'log this' - goes into your brain system.

**Before meetings:** Say 'prep me for my call with [name]' - Claude builds a brief.

**When you have a post / email / proposal to write:** Just ask. After the voice profile is filled, every output is in your voice.

**When making decisions:** Say 'help me decide' - Claude walks you through a structured framework.

**End of every session:** Claude commits changes. Your repo is your memory.

**To audit anytime:** `/founder-os:status` shows the OS state in one screen.

**To remove cleanly:** `/founder-os:uninstall` (default mode preserves your data; --purge wipes everything).

**Your folder structure:**
- Open `[founder-os-root]/` for strategic work
- Open `[company]/[project]/` for execution work
- Claude loads the right context based on where you are."

### 6.3 Backlog
Show any skipped or deferred items from the setup. Save them to `core/setup-backlog.md` as a simple markdown list under the heading `## Setup Backlog`. Create the file if it does not exist. Do not scatter deferred items across other files.

---

## Personalization Approach

Templates are structural guides, not copy-paste sources. When you read a template, understand its structure and sections, then generate a personalized version using the founder's discovery answers.

Adapt phrasing to match the founder's communication style from 0.7. Skip sections that don't apply (e.g., if they have no team, skip team-related sections in operating rules). Add context-specific content where the template has placeholders.

The goal: every file should feel like it was written FOR this specific founder, not generated from a form.
