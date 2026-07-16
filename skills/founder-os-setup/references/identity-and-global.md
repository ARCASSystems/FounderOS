# Setup - Phase 1: Identity and Global Layer

Load this when discovery is done and you are ready to write files. It opens with how to find and read the templates (needed by every file-writing phase), then walks Phase 1. Return to the router (`SKILL.md`) for the phase order.

---

## Before writing any file: read the templates

Read the templates directory that comes with this plugin. These templates define the structure of every file you'll create. Read each template before generating the personalized version.

Templates location by install method:
- **Plugin install** (Claude Code marketplace): `templates/` inside the plugin's installed folder. Confirm by checking for `.claude-plugin/marketplace.json` in the same parent.
- **Git clone** (`git clone https://github.com/ARCASSystems/FounderOS`): `templates/` at the repo root.
- **Curl install**: `templates/` at the install root (the folder named in the curl recipe).

If the exact path is uncertain, run a Glob for `**/templates/identity.md` and use the parent directory. The templates folder always contains: `identity.md`, `profile.md`, `avatar.md`, `bootloader-claude-md.md`, `global-claude-md.md`, `company-claude-md.md`, `project-claude-md.md`, `business-context.template.md`, `voice-profile.yml.template`, `brand-profile.yml.template`, `brand-voice.yml.template`, `brand-positioning.yml.template`, `brand-visual.yml.template`, and the subfolders `brain/`, `cadence/`, `context/`, `roles/`, `rules/`, `scripts/`, `network/`, `memory/`, `raw/`, `system/`. Use that file list to verify you found the right folder before reading.

If the user passed "reset": scan for an existing Founder OS folder, confirm they want to reconfigure, then re-run discovery.

---

## PHASE 1: IDENTITY + GLOBAL LAYER

### 1.1 Identity File
Using discovery answers, draft `core/identity.md`. Read the template from `templates/identity.md` for structure. Personalize with their actual background, positioning, work style, decision style, communication preferences, and overwhelm triggers.

The `## Positioning` section is load-bearing. Populate:

- `**Sells to:**` from 0.2.5 question 1
- `**Sells:**` from 0.2.5 question 2
- `**Buyer pain:**` from 0.2.5 question 3

If any positioning answer was skipped, write `[NOT SET]` for that line. Do not invent a buyer, offer, or pain.

The `## Founder Snapshot` section is the block the OS reads before it proposes a next move. It only exists for the `founder` and `team_of_one` variants - if Phase 0.2.6 was skipped (operator / student / career-mover), omit the whole section. When 0.2.6 ran, populate the four fields from it:

- `**Venture:**` from the 0.2.6 venture one-liner (the confirmed one-line version of 0.1).
- `**Customer:**` from the 0.2.6 customer answer. This is the same source as `## Positioning` `**Sells to:**` for a founder; write it in both places so each block stands alone.
- `**Stage (seed):**` as `<token> - <the founder's own words>`, where the token is the `stage` value mapped in 0.2.6 (pre-idea / idea-validation / building / first-customer / revenue / mrr-scale). Keep the line that says the OS re-infers stage each run - it tells the propose engine this is a seed, not a fixed field.
- `**Biggest blocker:**` from the 0.2.6 `biggest_blocker`, verbatim.

If any of the four was skipped, write `[NOT SET]` for that line. Do not invent a venture, customer, stage, or blocker - a thin-but-honest snapshot is what the propose engine is built to handle.

The `## Basics` section also takes a discovery answer: populate `**Time zone:**` from the Phase 0.5.5 timezone answer. If it was skipped, write `[NOT SET]`. Leave `**Jurisdiction:**` as the shipped `[NOT SET - run /founder-os:legal-setup]` default - `legal-setup` fills it on first run.

Show the draft. Get approval. Don't write yet.

### 1.1.5 Profile (what the OS leads with)

Finalise the variant you read provisionally in Phase 0.2.2, now that you also have their priorities (0.4), tool stack (0.5), and work style (0.7). Re-check against the `profile-router` skill's signal table. If the fuller picture changes the read, say so in one line and confirm.

Draft `core/profile.md` from `templates/profile.md`, filled from the `profile-router` variant map:

- `variant` - the confirmed variant (founder / career-mover / builder / student / team-internal)
- `detected on` - today's date
- `confidence` - high / medium / low, by how clear the signals were
- `signals` - the words, goal, and comfort that pointed here, in one line
- `lead surfaces`, `frame`, `technical comfort` - copied from the variant's row in `profile-router`. Override `technical comfort` when the interview showed otherwise: a founder who says "my nephew put this on here" or reaches for a paper notebook is `low` no matter what the variant row says, and a founder who mentions their own scripts is `high`. The variant row is the default, not the evidence.

If the variant is `team-internal`, set them up as the closest individual variant (founder if they own the company) and append the team-interest note to `core/setup-backlog.md` per the router. Do not block - the individual install is the working product today.

This file is the "meet the human" layer. Every reasoning and writing skill reads it alongside `core/identity.md`, so the OS opens with what this operator's situation needs instead of a generic surface. It locks nothing - every skill stays available to every variant; the variant only changes what leads.

Show the draft. Get approval. Don't write yet - it lands with the rest of `core/` in Phase 2.2.

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
     - On every platform, also replace `_` and `.` with `-` - Claude Code normalizes those in its slugs too (e.g. `my_biz.dev` -> `my-biz-dev`). A slug computed without this writes MEMORY.md to a path Claude Code never reads.
   - Target file: `<claude_projects_dir>/<slug>/memory/MEMORY.md` where `<claude_projects_dir>` is `~/.claude/projects/` on macOS / Linux and `%USERPROFILE%\.claude\projects\` on Windows.
   - **Confirm the path with the user** before writing. Show: "I will write your auto-memory template to: `<full path>`. Proceed? (yes / no / I'll set it up later)" - this catches a wrong slug before the file lands in the wrong place.

2. If the target file already exists, read it. If it has any real content (not just template scaffolding), do not overwrite. Add a note to the setup backlog: "Auto-memory file already exists at <path>. Skipped templating to preserve existing entries."

3. If the target file does not exist or only contains placeholders, copy `templates/memory/MEMORY.md` verbatim to the target path. Create parent directories as needed. Before persisting anything to a file, scan the source text for `<private>...</private>` blocks (case-insensitive). Remove every matched block (including the tags) from the text before writing. If the entire input is wrapped in `<private>`, write nothing and report "skipped - content was tagged private."

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
