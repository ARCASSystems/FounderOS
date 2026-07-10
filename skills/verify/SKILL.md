---
name: verify
description: >
  Check that Founder OS is healthy. Say "verify the OS", "health check", "is the OS working",
  "check my setup" (or run /founder-os:verify). Returns a structured report across 8 substrate
  checks, each marked PASS / WARN / FAIL with a one-line reason. Read-only. Never auto-fixes.
why: "Checks that the OS substrate is actually wired up correctly rather than just declaring setup done - hooks, scripts, and counts that disagree silently break skills."
enhance: "Run after every setup or update to catch wiring issues early - a FAIL on scripts or hooks means several skills will behave incorrectly on every subsequent run."
allowed-tools: ["Read", "Glob", "Grep", "Bash"]
mcp_requirements: []
---

# Verify

Runs on: local-exec - runs `python -m py_compile` on the shipped scripts as part of the check; on a cloud or read-only surface I report the checks I can read and mark the exec ones as not run.

Read-only health check across 8 substrate checks. Returns one screen. Never auto-fixes.

## The eight checks

Run all eight checks. Each produces one of: `[PASS]`, `[WARN]`, or `[FAIL]`.

### Check 1 - Plugin surface integrity

First detect the install shape: if the working directory has no `skills/` directory, this is a data-folder install (Path A plugin - the engine lives under `~/.claude/plugins/`, the founder's folder holds only their data). That is a correct state, not a defect:

- Data-folder install -> `[PASS] Plugin surface (engine runs from the plugin; no local engine copy to count)` and skip the counting below.

Otherwise (git-clone, curl, or ZIP install - the engine is in this folder), verify that the skill and command counts are internally consistent:

- Count `skills/<name>/SKILL.md` files on disk.
- Count `.claude/commands/*.md` files on disk.
- Read `skills/index.md` and extract the declared skill count from its header line.
- Read `README.md` and extract the skill and command counts from the "Skills" and
  "Slash commands" sections.
- Read `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` for their
  version fields and any count claims in the description strings.

Outcome:
- All counts agree -> `[PASS] Plugin surface (<N> skills / <M> commands, counts agree)`
- Any count disagrees -> `[WARN] Plugin surface (disk has <N> skills / <M> commands, README claims <X>/<Y>)`

### Check 2 - Hooks installed

- Read `.claude/settings.json` (or the user-level `~/.claude/settings.json`) for
  a `SessionStart` hook entry.
- Check that the file path referenced by the hook actually exists.

Outcome:
- Hook registered and file present -> `[PASS] Hooks installed (SessionStart present)`
- Hook registered but file missing -> `[FAIL] Hooks installed (SessionStart entry found but file missing)`
- No SessionStart hook entry at all -> `[WARN] Hooks installed (no SessionStart hook registered)`

Note: if MCPs are not configured or settings.json is not readable, report `[WARN]` not
`[FAIL]`. Hooks are opt-in by design.

### Check 3 - Scripts present

Check that all seven core Python helper scripts exist and parse cleanly:

- `scripts/query.py`
- `scripts/brain-snapshot.py`
- `scripts/wiki-build.py`
- `scripts/memory-diff.py`
- `scripts/brain-pass-log.py`
- `scripts/menu.py`
- `scripts/observation-rollup.py`

For each, run: `python -m py_compile scripts/<name>.py` (or `python3 -m py_compile`).

Outcome:
- All seven present and compile -> `[PASS] Scripts present (7/7 compile cleanly)`
- Some missing or compile errors -> `[FAIL] Scripts present (<N>/7 - list the failing ones)`

### Check 4 - MCP availability

Read `CLAUDE.md` and `AGENTS.md` for referenced MCP server names (look for server
names listed under "Tools Available" or similar sections).

For each named MCP, check whether it appears in the user's `.claude/settings.json`
under an `mcpServers` or similar key.

Outcome:
- Configured MCPs found -> `[PASS] MCP availability (<N> configured: <names>)`
- No MCPs configured -> `[WARN] MCP availability (0 configured - optional but adds Gmail, Calendar, Notion integrations)`
- MCPs referenced but none configured -> `[WARN] MCP availability (referenced in docs but none configured)`

Do NOT fail if MCPs are unconfigured. MCP setup is optional.

### Check 5 - Free-tier floor preserved

Grep the CORE script set only - the seven scripts in Check 3 - for environment variable references that imply an API key:
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`

Scope matters: do NOT grep the whole tree. Skills, docs, and connector helpers legitimately MENTION key names when documenting optional opt-in upgrades (add-voice's free Google AI Studio key, connect's gitignored `.env` writer, this file). A mention is not a requirement, and flagging it produces a false warning on a perfect install. The floor this check guards is precise: the seven core scripts must RUN without any key.

Outcome:
- No core script references a key -> `[PASS] Free-tier floor preserved (no core script requires an API key)`
- A core script requires a key to run -> `[FAIL] Free-tier floor (core script requires an API key - breaks free-tier users)`

### Check 6 - Wiki integrity

Run the lint check logic inline (do not invoke the lint skill recursively):

- Load `wiki_layer_files` from `scripts/_common.py` and use that exact result as the
  file scope. This is the canonical wiki layer: `core/`, `context/`, `cadence/`,
  `brain/`, `network/`, `companies/`, `roles/`, and `rules/`, with the helper's
  exclusions applied.
- Do not scan `skills/`, `docs/`, `templates/`, `raw/`, or other product surfaces.
- For each `[[target]]` found, verify that a file matching the target exists somewhere
  in the tree.

Approximate issue count:
- 0 unresolvable links -> `[PASS] Wiki integrity (0 issues)`
- 1-3 -> `[WARN] Wiki integrity (<N> unresolvable links)`
- 4+ -> `[FAIL] Wiki integrity (<N> unresolvable links - run /founder-os:lint for detail)`

### Check 7 - Cadence staleness

Compare today's date against the date headers in the cadence files:

`cadence/daily-anchors.md` - looks for `## Today: YYYY-MM-DD`:
- Same day or 1 day stale -> `[PASS]`
- 2-3 days stale -> `[WARN]`
- 4+ days stale or missing -> `[FAIL]`

`cadence/weekly-commitments.md` - looks for `## Week of YYYY-MM-DD`:
- Within 7 days -> `[PASS]`
- 7-10 days -> `[WARN]`
- 10+ days or missing -> `[FAIL]`

Report the worse of the two:
- Both PASS -> `[PASS] Cadence staleness (daily and weekly current)`
- One WARN -> `[WARN] Cadence staleness (daily-anchors <N> days stale)` or similar
- Either FAIL -> `[FAIL] Cadence staleness (<detail> - refresh before planning)`

### Check 8 - Auto-memory presence

Check whether `MEMORY.md` exists in the expected auto-memory location for this project.
The auto-memory path is `~/.claude/projects/<slug>/memory/MEMORY.md` where `<slug>`
is the repo path with separators replaced by hyphens.

- MEMORY.md exists -> count the entries (lines starting with `- [`) and report
  `[PASS] Auto-memory presence (MEMORY.md, <N> entries)`
- MEMORY.md missing -> `[WARN] Auto-memory presence (MEMORY.md not found - run setup wizard to create it)`

## Output format

Plain text. Maximum 30 lines including the header. Exactly this shape:

```
FounderOS v<version> - health check
<YYYY-MM-DD HH:MM>

[PASS] Plugin surface (<N> skills / <M> commands, counts agree)
[WARN] Hooks installed (SessionStart present, PostToolUse not enabled)
[PASS] Scripts present (7/7 compile cleanly)
[PASS] MCP availability (3 configured: Notion, Gmail, Calendar)
[PASS] Free-tier floor preserved (no core script requires an API key)
[PASS] Wiki integrity (0 issues)
[FAIL] Cadence staleness (daily-anchors 4 days stale - refresh before planning)
[PASS] Auto-memory presence (MEMORY.md, 12 entries)

6 PASS - 1 WARN - 1 FAIL - next: refresh cadence/daily-anchors.md
```

Rules for the output:
- No emoji.
- No color codes.
- Brackets + state word + parenthetical for every check line. Exactly this format.
- Summary footer: count each state, name the single highest-priority next action (first
  FAIL, or first WARN if no FAILs, or "all green" if all PASS).
- Read the version from the `VERSION` file in the repo root. On a data-folder install with no `VERSION` file, read the version from the plugin's `.claude-plugin/plugin.json` if reachable; if neither exists, print the header without a version rather than failing.
- Do not exceed 30 lines total.

## Skill reliability

When a user asks how the OS guarantees behavior (or runs `/founder-os:verify` and wants to know which skills are bulletproof vs which depend on the model following markdown), surface this table at the end of the report.

| Skill | Gate type |
|---|---|
| linkedin-post | Python-enforced (check-voice-ready) |
| email-drafter | Python-enforced (check-voice-ready) |
| client-update | Python-enforced (check-voice-ready) |
| proposal-writer | Python-enforced (check-voice-ready) |
| content-repurposer | Python-enforced (check-voice-ready) |
| weekly-review | Python-enforced (check-identity-ready) |
| decision-framework | Python-enforced (check-identity-ready) |
| meeting-prep | Python-enforced (check-identity-ready) |
| strategic-analysis | Python-enforced (check-identity-ready) |
| brain-pass | Python-enforced (check-log-has-history) |
| linkedin-post brain context | Python-enforced (check-log-has-history) |
| brain-log | Instruction-only |
| knowledge-capture | Instruction-only |
| queue | Instruction-only |
| founder-coaching | Instruction-only |
| unit-economics | Instruction-only |
| priority-triage | Instruction-only |

Python-enforced gates exit non-zero and stop the skill in code. Instruction-only skills rely on the model following the SKILL.md body. The distinction is what behavior the OS can guarantee versus what depends on the model. See `docs/calibrating-your-os.md` for how to test instruction-only skills yourself.

## Rules

- **This skill never auto-fixes anything. It only reports.**
- Read-only. Never write to any file, never run any command that modifies state.
- If a check cannot run (missing file, missing Python), report `[WARN]` not `[FAIL]`
  for that check, with a reason in the parenthetical.
- Distinguish `[WARN]` (degraded but functional) from `[FAIL]` (broken or missing).
  The distinction matters so founders can prioritize. A `[FAIL]` means something that
  would produce an error or wrong output in normal use. A `[WARN]` means something
  suboptimal that degrades gracefully.
