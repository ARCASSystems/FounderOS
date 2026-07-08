# Setup - Phase 2: Founder OS Root

Load this when identity and the global layer are done. It builds the full folder structure, copies the hooks and scripts byte-for-byte, runs every placeholder substitution, seeds the brain layer, initialises git, and sets the first weekly sprint. This is the heaviest phase. Return to the router (`SKILL.md`) for the phase order.

---

## PHASE 2: FOUNDER OS ROOT

### 2.1 Choose Location

The founder must end up with ONE folder they think of as "my OS." Where it lands depends on how setup was reached. Detect which case you are in before asking anything:

- **Setup is running inside the cloned repo** (the curl or git-clone paths - the current working directory contains both `.claude-plugin/` and `.git/`): set up IN PLACE, right here. This folder becomes the single folder the founder owns - their data, the hooks, and the commands all live together. Do NOT ask for a different location and do NOT create a second folder. Confirm in plain language: "Setting up your OS in this folder: [cwd]. This is yours - a normal git repo you can back up, move, or fork. Nothing phones home." Then build the structure below into the current folder.

- **Setup is running from the installed plugin** (no repo in the current folder - the engine is installed under `~/.claude/plugins/founder-os/`, a tool-managed path that is wiped on plugin update and is NOT where data should live): create the OS folder fresh. Ask: "Where do you want your Founder OS folder? This is your headquarters - priorities, decisions, brain log, weekly planning all live here. Default: ~/founder-os/" Build the tree there. The plugin stays the invisible engine; this new folder is the one the founder owns and opens every day.

Either way, the outcome is the same single owned folder. Never leave the founder with their data in one folder and the hooks wired to another. The plugin (if present) is just the Claude engine that operates on this folder; the folder itself is plain markdown the founder keeps even if they remove the plugin.

### 2.2 Create Structure
Create the full folder structure. Read each template before generating the personalized version:

```
[founder-os-root]/
├── CLAUDE.md                    # Bootloader (from templates/bootloader-claude-md.md)
├── core/
│   ├── identity.md              # From Phase 1.1
│   ├── profile.md               # From Phase 1.1.5 (what the OS leads with; read alongside identity by every skill)
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
│   ├── _common.py              # From templates/scripts/_common.py (shared helpers; wiki-build.py + query.py import from it - copy first or they hard-error)
│   ├── wiki-build.py            # From templates/scripts/wiki-build.py (extracts [[wikilinks]] into brain/relations.yaml)
│   ├── query.py                 # From templates/scripts/query.py (plain-file graph query)
│   ├── brain-snapshot.py        # From templates/scripts/brain-snapshot.py (writes brain/.snapshot.md - runtime context for output skills)
│   ├── brain-pass-log.py        # From templates/scripts/brain-pass-log.py (opt-in JSONL telemetry for /founder-os:brain-pass)
│   ├── memory-diff.py           # From templates/scripts/memory-diff.py (SessionStart helper - flags clients/ folders without an auto-memory entry)
│   ├── menu.py                  # From templates/scripts/menu.py (context-aware action surface for /founder-os:menu)
│   ├── observation-rollup.py    # From templates/scripts/observation-rollup.py (daily observation compaction for /founder-os:observation-rollup)
│   ├── check-voice-ready.py     # From templates/scripts/check-voice-ready.py (preflight gate for 5 voice-coupled writing skills)
│   ├── check-brand-voice-ready.py # From templates/scripts/check-brand-voice-ready.py (preflight gate for brand-voice path)
│   ├── check-identity-ready.py  # From templates/scripts/check-identity-ready.py (preflight gate for 4 reasoning skills)
│   ├── check-log-has-history.py # From templates/scripts/check-log-has-history.py (preflight gate for brain-pass + linkedin-post)
│   ├── list-brands.py           # From templates/scripts/list-brands.py (lists brand slugs under brands/)
│   ├── caveman_git.py           # From templates/scripts/caveman_git.py (invisible version control: the save, history, restore, backup verbs)
│   ├── connect.py               # From templates/scripts/connect.py (connector helper: gitignored-only secret writer + Telegram reachability check, for the connect skill)
│   ├── what-to-change.py        # From templates/scripts/what-to-change.py (deterministic candidate gatherer for the what-to-change flagship routine: parked filter + dated gate + resolvable citations)
│   ├── log-archive.py           # From templates/scripts/log-archive.py (ages brain/log.md past its cap into brain/archive/log-YYYY-MM.md - the running-log half of the context discipline)
│   └── session_changes.py       # From templates/scripts/session_changes.py (session-changes tracker: snapshot-before-write, per-session manifest, /changes, one-command restore)
├── cadence/
│   ├── daily-anchors.md         # From templates/cadence/daily-anchors.md
│   ├── weekly-commitments.md    # Personalized with their current priorities
│   ├── quarterly-sprints.md     # Shipped with [NOT SET] placeholders - founder fills in during first quarterly review
│   ├── annual-targets.md        # Shipped with [NOT SET] placeholders - founder fills in during first annual planning session
│   └── queue.md                 # Copied from templates/cadence/queue.md (no personalization needed)
├── context/
│   ├── priorities.md            # Personalized from 0.4
│   ├── decisions.md             # From templates/context/decisions.md
│   ├── companies.md             # Personalized from 0.1/0.2
│   ├── clients.md               # From templates/context/clients.md
│   └── names.md                 # From templates/context/names.md (names glossary - replace {{FOUNDER_NAME}} and {{COMPANY_NAME}}; capture passes read it before writing any name)
├── capture/
│   └── inbox/
│       └── README.md            # From templates/capture/inbox/README.md (drop zone for away-from-laptop captures; swept by catch-up)
├── roles/
│   ├── index.md                 # From templates/roles/index.md
│   ├── coo.md                   # From templates/roles/coo.md
│   ├── cmo.md
│   ├── chief-of-staff.md
│   ├── bd.md
│   ├── cso.md                   # Reference-until-invoked (portfolio strategy lens)
│   └── cto.md                   # Reference-until-invoked (tool-stack + automation lens)
├── rules/
│   ├── operating-rules.md       # Personalized from 0.7
│   ├── writing-style.md         # From templates/rules/writing-style.md
│   ├── commit-naming.md         # From templates/rules/commit-naming.md (plain-language commit subjects, no version-only/AI-attribution; read by github-ops)
│   ├── biases.md                # From templates/rules/biases.md (verbatim - the output bias self-check the OS runs on its own opinions)
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
        ├── session-start-liveness.sh   # Copied from <plugin-root>/.claude/hooks/session-start-liveness.sh
        ├── session-start-liveness.ps1  # Copied from <plugin-root>/.claude/hooks/session-start-liveness.ps1
        ├── user-prompt-capture.sh   # Copied from <plugin-root>/.claude/hooks/user-prompt-capture.sh
        ├── user-prompt-capture.ps1  # Copied from <plugin-root>/.claude/hooks/user-prompt-capture.ps1
        ├── session-close-revenue-check.sh   # Copied from <plugin-root>/.claude/hooks/session-close-revenue-check.sh
        ├── session-close-revenue-check.ps1  # Copied from <plugin-root>/.claude/hooks/session-close-revenue-check.ps1
        ├── session-close-autosave.sh        # Copied from <plugin-root>/.claude/hooks/session-close-autosave.sh (records a local version at session end when the name guard is active)
        ├── session-close-autosave.ps1       # Copied from <plugin-root>/.claude/hooks/session-close-autosave.ps1
        ├── post-tool-use-observation.sh     # Copied from <plugin-root>/.claude/hooks/post-tool-use-observation.sh (opt-in, off until FOUNDER_OS_OBSERVATIONS=1)
        ├── post-tool-use-observation.ps1    # Copied from <plugin-root>/.claude/hooks/post-tool-use-observation.ps1 (opt-in, off until FOUNDER_OS_OBSERVATIONS=1)
        ├── pre-tool-use-snapshot.sh         # Copied from <plugin-root>/.claude/hooks/pre-tool-use-snapshot.sh (session-changes tracker: snapshot before every write)
        ├── pre-tool-use-snapshot.ps1        # Copied from <plugin-root>/.claude/hooks/pre-tool-use-snapshot.ps1
        ├── session-close-changes.sh         # Copied from <plugin-root>/.claude/hooks/session-close-changes.sh (renders the per-session change manifest at Stop)
        ├── session-close-changes.ps1        # Copied from <plugin-root>/.claude/hooks/session-close-changes.ps1
        └── session_start_brief.py           # Copied from <plugin-root>/.claude/hooks/session_start_brief.py (Python helper that session-start-brief.sh calls on Linux/Mac)
```

Show the full list of files that will be created. Get approval. Then create them all.

**Hook copy step (mandatory).** The SessionStart brief, session-close revenue check, session-close autosave, user-prompt capture, and post-tool-use observation hooks live in the plugin's `.claude/hooks/` and are wired by `.claude/settings.json` via `$CLAUDE_PROJECT_DIR/.claude/hooks/...`. For these to fire in the founder's working directory, the hook scripts AND `settings.json` must exist at the founder's project root. Resolve the plugin source path the same way Phase 2.2 already does (one of the named install methods: Plugin, Git clone, Curl, or ZIP), then copy all seventeen hook files plus `settings.json` from the plugin's `.claude/` to the founder's `.claude/`. The seventeen hook files are: `session-start-brief.sh`, `session-start-brief.ps1`, `session-start-liveness.sh`, `session-start-liveness.ps1`, `user-prompt-capture.sh`, `user-prompt-capture.ps1`, `session-close-revenue-check.sh`, `session-close-revenue-check.ps1`, `session-close-autosave.sh`, `session-close-autosave.ps1`, `session-close-changes.sh`, `session-close-changes.ps1`, `pre-tool-use-snapshot.sh`, `pre-tool-use-snapshot.ps1`, `post-tool-use-observation.sh`, `post-tool-use-observation.ps1`, and `session_start_brief.py` (the Python helper that `session-start-brief.sh` calls on Linux/Mac to compute the staleness, decay, and tip sections of the brief; the `.ps1` inlines this logic so Windows does not strictly need it, but copy it so cross-platform installs get the full brief). This must match every script referenced by `settings.json` across all hook events (PreToolUse, SessionStart, UserPromptSubmit, Stop, PostToolUse); if any are missing from the founder's `.claude/hooks/`, the SessionStart brief, capture hooks, snapshot tracker, or Stop hooks fail silently. Do NOT modify file contents. If a `.claude/settings.json` already exists in the founder's repo (from a prior install), merge by adding the SessionStart, Stop, UserPromptSubmit, and PostToolUse hook entries. Do not overwrite the user's other hook customisations. The PostToolUse hook is opt-in - it stays silent until `FOUNDER_OS_OBSERVATIONS=1` is set in the shell env.

**Scripts copy step (mandatory).** Copy all twenty Python helpers (plus the private-name patterns template) from `templates/scripts/` to the founder's `scripts/`, byte-for-byte:

- `templates/scripts/_common.py` → `scripts/_common.py` (shared helper module - `wiki-build.py` and `query.py` both `import` from it; if it is missing, `/founder-os:wiki-build` and `/founder-os:query` hard-error with `ModuleNotFoundError` on first run)
- `templates/scripts/wiki-build.py` → `scripts/wiki-build.py` (used by `/founder-os:wiki-build`)
- `templates/scripts/query.py` → `scripts/query.py` (used by `/founder-os:query`)
- `templates/scripts/brain-snapshot.py` → `scripts/brain-snapshot.py` (writes `brain/.snapshot.md`, read at task time by nine output-producing skills)
- `templates/scripts/brain-pass-log.py` → `scripts/brain-pass-log.py` (opt-in JSONL telemetry for `/founder-os:brain-pass`)
- `templates/scripts/memory-diff.py` → `scripts/memory-diff.py` (SessionStart helper that flags `clients/<slug>/` folders without an auto-memory entry)
- `templates/scripts/menu.py` → `scripts/menu.py` (used by `/founder-os:menu` to surface context-aware actions)
- `templates/scripts/observation-rollup.py` → `scripts/observation-rollup.py` (used by `/founder-os:observation-rollup` to compact daily observations)
- `templates/scripts/check-voice-ready.py` → `scripts/check-voice-ready.py` (preflight gate for voice-coupled writing skills: linkedin-post, email-drafter, client-update, content-repurposer, proposal-writer)
- `templates/scripts/check-brand-voice-ready.py` → `scripts/check-brand-voice-ready.py` (preflight gate when brand voice is selected)
- `templates/scripts/check-identity-ready.py` → `scripts/check-identity-ready.py` (preflight gate for reasoning skills: meeting-prep, decision-framework, strategic-analysis, weekly-review)
- `templates/scripts/check-log-has-history.py` → `scripts/check-log-has-history.py` (preflight gate for brain-pass and linkedin-post when prior context is required)
- `templates/scripts/list-brands.py` → `scripts/list-brands.py` (lists brand slugs under `brands/`, used by your-voice, campaign-from-theme, review-responder)
- `templates/scripts/user-prompt-capture.py` → `scripts/user-prompt-capture.py` (writes user prompts to `brain/observations/` when `FOUNDER_OS_OBSERVATIONS=1`)
- `templates/scripts/check-private-names.py` → `scripts/check-private-names.py` (called by `.githooks/pre-commit` and `.githooks/commit-msg` to block leaked private names, em-dashes / en-dashes, AI-attribution trailers, and committed secrets)
- `templates/scripts/caveman_git.py` → `scripts/caveman_git.py` (the invisible version-control engine behind the save, history, restore, and backup verbs; also used by the session-close-autosave hook)
- `templates/scripts/connect.py` → `scripts/connect.py` (connector helper behind the `connect` skill: the gitignored-only secret writer and the Telegram reachability check; without it `connect` cannot store a key or run its test send)
- `templates/scripts/what-to-change.py` → `scripts/what-to-change.py` (deterministic candidate gatherer behind the `what-to-change` flagship routine: it excludes parked items, gates on dated signal, and returns resolvable citations; without it the routine cannot filter false urgency mechanically)
- `templates/scripts/log-archive.py` → `scripts/log-archive.py` (the engine behind the `log-archive` skill: ages `brain/log.md` past its 300-line cap into `brain/archive/log-YYYY-MM.md` and leaves a pointer, so the running log every skill reads stays small as the install ages)
- `templates/scripts/session_changes.py` → `scripts/session_changes.py` (the session-changes tracker behind the PreToolUse snapshot hook, the session-close manifest, and the `/changes` command; the pre-git undo floor on ZIP installs and a second net everywhere else)

Also copy `templates/scripts/private-name-patterns.txt.template` → `scripts/private-name-patterns.txt` (NOTE: drop the `.template` suffix on the destination filename). The pre-commit hook and `install-git-hooks.sh` both look for `scripts/private-name-patterns.txt` exactly. The `.template` suffix marks the source-of-truth example, not the runtime file.

Offer to auto-write the captured founder name as the first uncommented pattern in `scripts/private-name-patterns.txt`: `\b<FOUNDER_NAME>\b`. This gives the new install one working guard out of the box without forcing the founder to learn regex syntax on day one.

Write `\b` as a literal two-character backslash-b, not an escape. A shell `printf`/`echo -e` path turns `\b` into a backspace byte (0x08) and ships a dead privacy guard that looks installed but matches nothing. Use `printf '%s\n' '\b<FOUNDER_NAME>\b'` or a single-quoted heredoc, then verify with a throwaway commit that the guard actually blocks the name before continuing. On Windows or PowerShell, write the pattern with the file-write tool or `Set-Content` (PowerShell has no `echo -e`, so the backspace trap does not arise there) - never a shell echo.

These are not personalized templates. Copy contents exactly. Do not edit. Verify all nineteen `.py` copies plus `scripts/private-name-patterns.txt` exist on disk before continuing. If `templates/scripts/` ever holds a `.py` helper not named above, copy it too - the founder's `scripts/` set must equal the `templates/scripts/` set, since helpers import each other. If any are missing, the brain-snapshot, brain-pass, wiki-build, query, menu, observation-rollup, preflight-gate, observation-capture, or private-name guard helpers will fail silently or hard-error.

**{{role_noun}} substitution.** The `templates/bootloader-claude-md.md` file contains `{{role_noun}}` placeholders in two places. When writing the bootloader CLAUDE.md, substitute based on the role captured in Phase 0.2.1:

- `founder` → replace `{{role_noun}}` with `founder`
- `operator` → replace `{{role_noun}}` with `operator`
- `team_of_one` → replace `{{role_noun}}` with `operator` (operator is the generic term for non-owners)

If role was not captured or defaulted, use `founder`.

**{{FOUNDER_NAME}} substitution.** Before the universal placeholder pass below runs, substitute `{{FOUNDER_NAME}}` with the founder name captured in Phase 0.1 in every template that contains it. At minimum:

- `templates/bootloader-claude-md.md` → bootloader CLAUDE.md (lines 1 and 5 must end up with the founder's actual name, NOT `[NOT SET]`).
- `templates/global-claude-md.md` → `~/.claude/CLAUDE.md` or equivalent global location.
- `templates/identity.md` → `core/identity.md`.
- `templates/avatar.md` → `core/avatar.md` (already covered above; do not double-substitute).
- `templates/business-context.template.md` → `companies/<slug>-business.md` (substitutes `{{COMPANY_NAME}}` with the company name from Phase 0.1).
- `templates/context/names.md` → `context/names.md` (substitutes both `{{FOUNDER_NAME}}` and `{{COMPANY_NAME}}` - the glossary's first two seed rows).

If no founder name was captured, fall through to the universal pass and write `[NOT SET]`. Do NOT leave literal `{{FOUNDER_NAME}}` on disk.

**{{CONTENT_CHANNELS}} and {{CONTENT_CADENCE}} substitution (roles/cmo.md).** `templates/roles/cmo.md` carries two tokens the rest of the role tree does not feed. Substitute them like every other token, before the universal pass, so they never reach the founder's disk as literal `{{...}}`:

- `{{CONTENT_CHANNELS}}` - if the founder named a primary channel in Phase 0.5 Q5 (`primary_channel` in `stack.json`), seed it here, e.g. `LinkedIn (add any other channels you use)`. If `primary_channel` is `null` or was skipped, substitute the graceful default `your main channels (fill these in)`.
- `{{CONTENT_CADENCE}}` - no discovery question captures posting cadence this phase, so substitute the graceful default `your posting rhythm (fill this in)`.

Do NOT write `[NOT SET]` for these two, and do NOT hardcode the default into `cmo.md` itself. Keeping the tokens in the template and the value in this substitution layer means a future wizard pass can personalize them the moment a real content-channels question exists. A natural-language default reads better to a founder than `[NOT SET]` for a section they are meant to fill in themselves.

**Universal placeholder pass (always run last).** After every template copy completes in Phase 2.2 (and any later phase that copies a template), grep the destination file for any remaining `{{...}}` placeholder. Replace every match with `[NOT SET]`. This is the same rule already applied to `cadence/weekly-commitments.md`. It must apply universally: `rules/operating-rules.md`, `rules/writing-style.md`, `roles/*.md`, `global-claude-md.md`, `context/priorities.md`, and any future template all go through this pass. The named substitutions above MUST run before the universal pass so they don't get overwritten with `[NOT SET]`.

**{{TODAY}} substitution.** The `templates/brain/relations.yaml` file contains the literal placeholder `{{TODAY}}`. When copying to `brain/relations.yaml`, replace every occurrence of `{{TODAY}}` with today's date in `YYYY-MM-DD` format (use `date -u +%Y-%m-%d` via Bash to get it).

**{{DATE}} substitution.** The `templates/cadence/daily-anchors.md` file contains the literal placeholder `{{DATE}}` on the `## Today: {{DATE}}` heading. When copying to `cadence/daily-anchors.md`, replace `{{DATE}}` with today's date in `YYYY-MM-DD` format (same source as `{{TODAY}}` above). The SessionStart brief and `/today` command both grep this heading - leaving the placeholder in place would make the very first session report STALE before the founder has done anything.

**{{WEEK_START_DATE}} substitution.** The `templates/cadence/weekly-commitments.md` file contains the literal placeholder `{{WEEK_START_DATE}}` on the `## Week of {{WEEK_START_DATE}}` heading. When copying to `cadence/weekly-commitments.md`, replace `{{WEEK_START_DATE}}` with today's date in `YYYY-MM-DD` format (same source as `{{TODAY}}` and `{{DATE}}` above). The SessionStart brief greps this heading to compute weekly staleness, and `/founder-os:verify` Check 7 will fail if the placeholder is left in place. Replace every remaining `{{...}}` placeholder in the file with `[NOT SET]` so the wizard never ships a half-substituted template - Phase 2.4 walks the founder through filling MUST/SHOULD/COULD entries, but the file must be valid on disk before Phase 2.4 even runs.

**Queue template copy.** Copy `templates/cadence/queue.md` to `cadence/queue.md`. No substitutions needed - the template has no placeholders. If `cadence/queue.md` already exists at setup time, do not overwrite it. Log: "queue.md already present, leaving untouched."

**Avatar template copy.** Copy `templates/avatar.md` to `core/avatar.md` and replace `{{FOUNDER_NAME}}` with the founder name captured in Phase 0.1. Do not auto-populate the bracketed sections. The wizard asks the seed questions, then the founder fills or revises those prompts in their first review session.

**Profile file write.** Write `core/profile.md` from the Phase 1.1.5 draft - the confirmed variant, signals, lead surfaces, frame, and technical comfort, all real values. Do not copy `templates/profile.md` verbatim; the template ships `[NOT SET]` defaults and Phase 1.1.5 already resolved them. The universal placeholder pass leaves the resolved file alone because it has no `{{...}}` tokens left.

**Seed brain content (so the first brief is not a blank screen).** The brain templates ship one worked example each so a brand-new install has something to look at on day one. Empty states kill the first run. Date-stamp the seeds to the install so they read as current, not as two-year-old samples:

- `brain/flags.md` ships one example flag dated `2024-01-01`. Replace that date with a date about 20 days before today, so it surfaces as Review Due on the first SessionStart brief - that surfacing is the demo. Give it a real ID per `rules/entry-conventions.md` (channel `flag`).
- `brain/patterns.md` ships one example pattern with `First observed:` and `Last seen:` dated `2024-01-01`. Replace both with a date about 100 days before today, so it passes the 90d default decay and surfaces as Review Due on the first SessionStart brief - that surfacing is the demo. Give it a real ID per `rules/entry-conventions.md` (channel `pattern`).
- `brain/decisions-parked.md` ships one example parked decision dated `2024-01-01`. Replace `Date parked:` with today's date and give it a real `parked-` ID.
- `brain/log.md` ships its worked examples inside an HTML comment. Plant ONE live worked entry dated today so the brief's "last 3 log entries" is not empty. Use a neutral entry: `### [<today>] #context Installed Founder OS and ran setup. First real entry. (log-<today>-001)`. Leave the commented examples in place as a format reference.

Keep all three generic. Do not invent business facts. They are labelled as examples for the operator to replace once their own first entries land.

### 2.3 Initialize Git

First check whether git exists at all: run `git --version`.

**If git is NOT installed (the normal state of a ZIP-download install):** do not error, do not send the founder to a download page, and do not make setup wait on it. Say plainly: "Version history is off for now - git is not on this machine, and you do not need it today. Every file the OS touches is still snapshotted each session with a one-command restore. When you want the full timeline, say 'own my history' and I will install and wire git for you - one yes, nothing for you to type." Skip the rest of 2.3 (including the privacy-guard wiring - it is a git hook and has nothing to attach to yet; the own-your-history skill wires it before the first commit). Continue to 2.4.

**If git IS installed,** guard: check if a `.git/` directory already exists in the Founder OS root before running `git init`.

- If `.git/` exists (the common case, because the install folder is already a git clone), SKIP `git init`. Log: "Folder is already a git repository. Skipping git init." Move on.
- If `.git/` does not exist (ZIP or manual-copy install on a machine that happens to have git), run `git init` and create an initial commit: "Founder OS initialized."

**Wire the privacy guard (so it is active, not just installed).** The private-name guard only fires if `git config core.hooksPath` points at `.githooks`. A fresh `git clone` does not inherit that setting, so without this step the guard is copied but dormant. After the git guard above:

1. Make sure `.githooks/pre-commit`, `.githooks/commit-msg`, and `scripts/install-git-hooks.sh` exist in the founder's OS root. If the install method scaffolded into a fresh directory (Plugin or Curl paths) rather than a clone, copy these three from the plugin source resolved in Phase 2.2.
2. Activate the guard. On Linux/Mac (or Windows with Bash): run `bash scripts/install-git-hooks.sh`. On Windows without Bash: run `git config core.hooksPath .githooks`. Either way the pre-commit and commit-msg hooks now fire on every commit.
3. Confirm with the founder that the guard is live. Out of the box it already blocks committed secrets (API keys, tokens, bot tokens, PEM private keys), em/en dashes, and AI-attribution trailers. The NAME check stays inactive until `scripts/private-name-patterns.txt` has at least one pattern (their own name was offered in the scripts copy step above), so adding their name turns on name-leak blocking too. The file is gitignored, so their names never leave the machine.

### 2.4 First Weekly Sprint
Ask: "Let's set your first weekly sprint. You mentioned these priorities: [list from 0.4]. Which of these are MUST DO this week (max 3), which are SHOULD DO, and which can wait?"

Write the answers into `cadence/weekly-commitments.md`.
