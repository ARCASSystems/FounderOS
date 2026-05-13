---
name: verify
description: >
  Check that Founder OS is healthy. Say "verify the OS", "health check", "is the OS working",
  "check my setup" (or run /founder-os:verify). Returns a structured report across 8 substrate
  checks, each marked PASS / WARN / FAIL with a one-line reason. Read-only. Never auto-fixes.
allowed-tools: ["Read", "Glob", "Grep", "Bash"]
mcp_requirements: []
---

# Verify

Read-only health check across 8 substrate checks. Returns one screen. Never auto-fixes.

**This skill never auto-fixes anything. It only reports.**

## Natural-language phrases that invoke this skill

- "verify the OS"
- "health check"
- "is the OS working"
- "check my setup"
- "run a health check"

Say any of these and the verify skill fires. The slash command `/founder-os:verify`
is a shortcut.

## The eight checks

Run all eight checks. Each produces one of: `[PASS]`, `[WARN]`, or `[FAIL]`.

### Check 1 - Plugin surface integrity

Verify that the skill and command counts are internally consistent:

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

Check that all five core Python helper scripts exist and parse cleanly:

- `scripts/query.py`
- `scripts/brain-snapshot.py`
- `scripts/wiki-build.py`
- `scripts/memory-diff.py`
- `scripts/brain-pass-log.py`

For each, run: `python -m py_compile scripts/<name>.py` (or `python3 -m py_compile`).

Outcome:
- All five present and compile -> `[PASS] Scripts present (5/5 compile cleanly)`
- Some missing or compile errors -> `[FAIL] Scripts present (<N>/5 - list the failing ones)`

### Check 4 - MCP availability

Read `CLAUDE.md` and `AGENTS.md` for referenced MCP server names (look for server
names listed under "Tools Available" or similar sections).

For each named MCP, check whether it appears in the user's `.claude/settings.json`
under an `mcpServers` or similar key.

Outcome:
- Configured MCPs found -> `[PASS] MCP availability (<N> configured: <names>)`
- No MCPs configured -> `[WARN] MCP availability (0 configured - optional but unlocks Gmail, Calendar, Notion integrations)`
- MCPs referenced but none configured -> `[WARN] MCP availability (referenced in docs but none configured)`

Do NOT fail if MCPs are unconfigured. MCP setup is optional.

### Check 5 - Free-tier floor preserved

Grep the working tree for environment variable references that imply a paid API key:
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`

The CORE script set (the five scripts in Check 3) must not require any paid key.
Optional skills that call paid APIs are allowed.

Outcome:
- Core scripts have no paid key references -> `[PASS] Free-tier floor preserved (no core script requires paid keys)`
- A core script references a paid key -> `[FAIL] Free-tier floor (core script requires paid key - breaks free-tier users)`
- Only non-core files reference paid keys -> `[WARN] Free-tier floor (optional skill requires paid key: <skill-name>)`

### Check 6 - Wiki integrity

Run the lint check logic inline (do not invoke the lint skill recursively):

- Count files in `skills/`, `core/`, `context/`, `cadence/`, `brain/`, `rules/`,
  `roles/` that contain `[[` wikilink syntax.
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

[PASS] Plugin surface (44 skills / 26 commands, counts agree)
[WARN] Hooks installed (SessionStart present, PostToolUse not enabled)
[PASS] Scripts present (5/5 compile cleanly)
[PASS] MCP availability (3 configured: Notion, Gmail, Calendar)
[PASS] Free-tier floor preserved (no core script requires paid keys)
[PASS] Wiki integrity (0 issues)
[FAIL] Cadence staleness (daily-anchors 4 days stale - refresh before planning)
[PASS] Auto-memory presence (MEMORY.md, 12 entries)

3 PASS - 4 WARN/PASS - 1 FAIL - next: refresh cadence/daily-anchors.md
```

Rules for the output:
- No emoji.
- No color codes.
- Brackets + state word + parenthetical for every check line. Exactly this format.
- Summary footer: count each state, name the single highest-priority next action (first
  FAIL, or first WARN if no FAILs, or "all green" if all PASS).
- Read the version from the `VERSION` file in the repo root.
- Do not exceed 30 lines total.

## Rules

- **This skill never auto-fixes anything. It only reports.**
- Read-only. Never write to any file, never run any command that modifies state.
- If a check cannot run (missing file, missing Python), report `[WARN]` not `[FAIL]`
  for that check, with a reason in the parenthetical.
- Distinguish `[WARN]` (degraded but functional) from `[FAIL]` (broken or missing).
  The distinction matters so founders can prioritize. A `[FAIL]` means something that
  would produce an error or wrong output in normal use. A `[WARN]` means something
  suboptimal that degrades gracefully.
- No em dashes or en dashes. Hyphens only.
