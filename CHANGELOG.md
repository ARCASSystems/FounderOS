# Changelog

All notable releases. Format follows the user-value-first commit naming rule (`rules/commit-naming.md`).

## v1.12.0 - 2026-05-08

Cross-session memory gap now surfaces in the session brief. When a cloud Claude session, a parallel local session, or a teammate creates a new `clients/<slug>/` folder with intel and prep, the next local session boots blind to it because `MEMORY.md` does not auto-populate from filesystem changes. v1.12 ships a small read-only helper that runs from the SessionStart hook and flags any client folder with no matching auto-memory entry, so the operator knows to write one before the work goes cold.

### Added

- **`tests/test_memory_diff.py`** (nine stdlib tests). Covers the silent-exit branches (no clients folder, no memory dir), the three slug-match strategies (MEMORY.md text, project filename, project first-token), an empty-clients-folder edge case, and both the hyphenated (`c--Users-jane-founder-os`) and unhyphenated (`Users-jane-founderos`) shapes of the public-OS slug.
- **`scripts/memory-diff.py`** (with byte-identical mirror at `templates/scripts/memory-diff.py`). Walks `clients/<slug>/`, checks each slug against `~/.claude/projects/<slug>/memory/MEMORY.md` plus per-file `project_*.md` entries, and prints up to five uncovered slugs with the line `(write project_<slug>.md in your auto-memory dir so the next session boots aware)`. Stdlib only. No new runtime dependency. Fails silent when the auto-memory dir is missing, the clients folder is missing, or no slugs are uncovered. Free-tier accessible.
- **SessionStart hook wiring.** `.claude/hooks/session-start-brief.sh` and `.claude/hooks/session-start-brief.ps1` invoke the helper near the end of the brief. Bash uses the resolved `$PYTHON` (python3 or python). PowerShell guards on `Get-Command python` so the hook stays silent when Python is not installed.

### Changed

- **`founder-os-setup` skill copy step now covers five helpers** (was four). PHASE 2.2 file map adds `scripts/memory-diff.py`. Mandatory scripts copy step lists the same five files. New installs get the helper out of the box.
- **`/founder-os:update` and `/founder-os:uninstall` script lists** add `memory-diff.py` so existing users get the helper on the next update and the uninstaller cleans it up.
- **CLAUDE.md and AGENTS.md** gain a one-line note describing the helper under the v1.10 substrate paragraph. Skill count stays 39. Slash command count stays 20.
- **Release metadata bumped.** `VERSION`, `plugin.json`, `marketplace.json`, README status header, and ROADMAP all point at v1.12.0.

### Notes

- Dogfood validated in the upstream private OS first. The gap surfaced on 2026-05-08 when a cloud session created a fresh `clients/<slug>/` for a same-day call and the next local session had no idea it existed. Fix shipped privately first, then ported to the public repo this same week.
- Skill count and command count unchanged. Test count rose from 34 to 43 (added nine memory-diff tests covering silent-exit branches, slug-match strategies, hyphenated and unhyphenated public-OS slugs, and edge cases like empty clients folders). Hook-only feature.
- Cross-platform path handling works on Windows (PowerShell) and Linux/macOS (bash). `os.path.expanduser` and `pathlib` cover all three. Helper exits 0 in every fail-soft branch.

## v1.11.0 - 2026-05-08

The launch-hardening release. v1.10 shipped the runtime brain context but left several install-time gaps that broke the marquee feature for fresh users. v1.11 closes those gaps and fixes a string of cross-platform hook bugs that would silently no-op on non-English Windows. End-to-end audit pass across leaks, code, docs, install flow, and skill integrity.

### Fixed

- **`/founder-os:wiki-build` no longer fails on a fresh clone.** `scripts/wiki-build.py` was missing from the repo even though the command and skill existed. The script lived only in `templates/scripts/`. Now mirrored to `scripts/` so the command works without running setup first.
- **Setup wizard now copies all four runtime helpers** (`wiki-build.py`, `query.py`, `brain-snapshot.py`, `brain-pass-log.py`). v1.10 wired nine skills to read `brain/.snapshot.md` but the wizard only copied two scripts, so brain-snapshot and brain-pass silently degraded for every Path A install. Marquee feature now actually ships.
- **`/founder-os:update` now refreshes `scripts/`, `rules/`, `docs/`, and `AGENTS.md`.** System Layer was missing those paths, so existing users running update would never receive new Python helpers, doc updates, or the cross-agent file. Stash backup now covers the same paths.
- **`/founder-os:uninstall` removes `scripts/` and `rules/`.** Same omission, mirror fix.
- **Windows hooks no longer silently break on non-English locales.** `session-start-brief.ps1` used `[datetime]"2026-05-04"` which parses against thread culture and throws on non-English Windows. Replaced with `ParseExact` + `InvariantCulture`. Weekly staleness and decay scan now work on Arabic, German, French, etc.
- **Hook path resolution hardened.** `session-start-brief.ps1` and `session-close-revenue-check.ps1` now guard `$MyInvocation.MyCommand.Path` (can be null in some invocation contexts) and fall back to `$PSScriptRoot`. Bash counterparts gained `|| exit 0` guards on `cd` so a failed path resolution exits cleanly instead of silently no-opping against the wrong directory.
- **`session-close-revenue-check.{sh,ps1}` now anchor on hook location, not CWD.** Previous version used `git rev-parse --show-toplevel` which returns the wrong repo if the user is inside a nested checkout when the Stop event fires.
- **Cross-platform line endings.** New `.gitattributes` enforces LF for `.sh` and `.py` so Windows clones (default `core.autocrlf=true`) don't break Bash hooks with `'bash\r'` errors. PowerShell scripts stay CRLF.
- **`scripts/query.py --mode full` now ignores malformed `id:` lines outside frontmatter blocks.** Previously a bare `id: <slug>` line in prose would return raw YAML / metadata as the entry body. Now requires the canonical fence pattern (`---`, frontmatter, closing `---`).

### Changed

- **CLAUDE.md, AGENTS.md, and `docs/tools-and-mcps.md` now reflect the v1.10 surface.** Skill count 37 -> 39, command count 19 -> 20. Added rows for `brain-snapshot`, `brain-pass`, and `your-voice` to the bootloader skill table. Added v1.10 substrate paragraph to both bootloader files. The bootloader is what gets copied to user repos by setup, so users see the right surface from Day 1.
- **Bootloader template references corrected.** `core/infrastructure.json` reference replaced with `stack.json` (which actually exists). Operating-rules reference updated to match.
- **Setup wizard now creates `brain/archive/` and `companies/` directories** so the bootloader's references to those paths resolve out of the box.
- **PHASE 3.2.5 added to setup wizard** to surface `templates/business-context.template.md` for each company. Without it, `business-context-loader`, `proposal-writer`, `client-update`, and `strategic-analysis` had no per-company input file to read.
- **README mobile claim corrected.** "On mobile, skills work via typed input" was misleading. Claude Code is desktop-only today. There is no mobile execution surface. Reworded to say so.
- **README "Kill criteria in the product" reworded** to match what the OS actually does. The decay convention surfaces entries for keep/kill review. The OS does not auto-kill.
- **README AgentOS link replaced** with an inline architecture summary. The external `three-layer-architecture.md` doc was cited as authoritative but the AgentOS public repo is still in development.
- **Scheduled-tasks framing in CLAUDE.md softened.** The previous wording read like the OS shipped Monday-morning briefs out of the box. Founder OS does not ship any scheduled tasks. The MCP integration is bring-your-own.
- **Prose semicolons removed** from README, CLAUDE.md, AGENTS.md, and docs per the writing-style rule.
- **Release metadata bumped.** `VERSION`, `plugin.json`, `marketplace.json`, README status, ROADMAP shipped line all point at v1.11.0.

### Notes

- No new runtime dependencies. No new skills. v1.11 is hardening, not surface expansion.
- The 34 v1.7-v1.10 tests still pass unchanged after every fix in this release.
- Free-tier accessibility floor preserved. Nothing in the install path requires a paid AI subscription or API key.

## v1.10.0 - 2026-05-08

The runtime brain context release. Skills no longer start cold. A small deterministic snapshot now captures what is true right now (open flags, this week's must-do, recent decisions, voice and brand fields, staleness). Nine output-producing skills read it at task time. A new brain-pass skill lets Claude reason across the brain layer and return a synthesised answer with citations, on free-tier accessibility (no embeddings, no API call). Two skills (meeting-prep, linkedin-post) auto-invoke brain-pass to prove the composition pattern.

### Added

- **Brain snapshot generator.** `scripts/brain-snapshot.py` (with `templates/scripts/brain-snapshot.py` mirror) reads voice, brand, flags, weekly commitments, and decisions, then emits a small markdown payload (~200 tokens). Output goes to stdout by default or to `brain/.snapshot.md` with `--write`. Pure stdlib. Fail-soft on missing files. Deterministic for test stability.
- **Brain snapshot test suite.** `tests/test_brain_snapshot.py` covers happy path, missing voice profile, template defaults, no-flags-file, stale cadence days-past math, top-three flag cap, --write file behaviour, and determinism. Synthetic public-safe fixture under `tests/fixtures/snapshot-corpus/`.
- **`brain-snapshot` skill.** `skills/brain-snapshot/SKILL.md` documents the contract for skill authors and users.
- **`brain-pass` skill.** `skills/brain-pass/SKILL.md` defines a semantic-retrieval contract: pick relevant brain files, scan with intent, synthesise an answer, cite entry IDs, return a structured Answer / Evidence / Confidence / Gaps block. Free-tier accessible. No embeddings.
- **`/founder-os:brain-pass` slash command.** `.claude/commands/brain-pass.md` runs the brain-pass skill end to end with a question argument.

### Changed

- **Nine skills now read the brain snapshot.** `meeting-prep`, `weekly-review`, `strategic-analysis`, `decision-framework`, `founder-coaching`, `knowledge-capture`, `unit-economics`, `priority-triage`, and `brain-log` each gained a "Brain context (default)" section describing how to consume `brain/.snapshot.md`. Snapshot is opt-in via the file existing. Skills proceed with profile-only context if it is missing.
- **`meeting-prep` and `linkedin-post` auto-invoke brain-pass.** Meeting briefs now compose past interactions, open commitments, and unresolved threads via brain-pass before drafting. LinkedIn posts now compose recent themes and recent decisions via brain-pass to flag repetition risk and tie posts to current thinking. Both fall back to `scripts/query.py` if brain-pass is unavailable.
- **Skill index and command index bumped.** 37 -> 39 skills. 19 -> 20 slash commands.
- **`.gitignore` ignores `brain/.snapshot.md`.** Per-user state, regenerated locally on each machine.
- **Release metadata bumped.** `VERSION`, plugin manifest, marketplace manifest, README status, roadmap, and skill index now point at v1.10.0.

### Notes

- No runtime dependencies were added.
- Twenty-one v1.8/v1.9 tests still pass unchanged. Eight new brain-snapshot tests plus five brain-pass-log tests bring the suite to 34 tests.
- Snapshot generation is the only new code path. brain-pass and the WS4 wire-ins are doc-only changes that depend on the model running the skill.
- Snapshot consumers are opt-in. Older installs without the snapshot script keep working with profile-only context. v1.7 features (stable IDs, three-mode query, opt-in observation log) remain unchanged.
- The brain snapshot is regenerated on demand. Cheap to refresh after `/dream`, after rolling the daily anchor, or at session start.

## v1.9.0 - 2026-05-08

The hook test coverage release. The opt-in observation hook now has stdlib tests for bash and PowerShell paths: gates, JSONL writes, BOM safety, intent shaping, privacy truncation, malformed input, and fail-open write failures. Session hooks get static parse smoke tests. Query docs now name the existing `--root` flag.

### Added

- **PostToolUse hook tests.** `tests/test_post_tool_use_hook.py` runs the observation hook in temp repos and checks opt-in gates, platform guard behavior, JSONL output, PowerShell BOM safety, append behavior, intent shaping, malformed input, privacy truncation, and fail-open write failures.
- **Hook input fixtures.** `tests/fixtures/hook-input/` holds public-safe Edit, Read, Bash, Grep, Glob, unknown-tool, and malformed inputs.
- **Session hook smoke tests.** `tests/test_session_hooks.py` parses the SessionStart and Stop hooks without running a live Founder OS install.

### Changed

- **Query docs name `--root`.** `skills/query/SKILL.md` and `.claude/commands/query.md` now document the existing script flag for querying a non-default folder.
- **Test docs widened.** `tests/README.md` now lists query tests, hook tests, fixtures, and the pattern for adding another stdlib test.
- **Release metadata bumped.** `VERSION`, plugin manifest, marketplace manifest, README status, roadmap, and skill index now point at v1.9.0.

### Notes

- No runtime dependencies were added.
- Existing v1.8 query tests still pass unchanged.
- Bash fake-uname tests use a PATH shim with LF newlines so WSL and git-bash can execute it.

## v1.8.0 - 2026-05-07

The query test coverage release. `scripts/query.py` now has a stdlib `unittest` suite covering index, timeline, full, bare invocation, and guard paths against a small synthetic corpus.

### Added

- **Query CLI tests.** `tests/test_query.py` runs the public CLI through subprocess calls and checks output shape, IDs, timeline ordering, full ID lookup, and exit code guards.
- **Synthetic query corpus.** `tests/fixtures/query-corpus/` provides public-safe markdown and YAML fixtures for the three query modes.
- **Test docs.** `tests/README.md` documents the local command: `python -m unittest discover tests/`.
- **`.gitignore` for Python bytecode.** Added `__pycache__/`, `*.py[cod]`, `*$py.class` so test runs do not dirty the working tree.

### Changed

- **`scripts/query.py` excludes `tests/`.** Added `tests` to `EXCLUDED_PARTS` so test fixtures never appear in real query results. If you keep a `tests/` folder under your FounderOS root for unrelated reasons and want it indexed, rename or move it.

### Notes

- No runtime dependencies were added.
- No CI integration was added. The solo-founder workflow stays local-first.
- `tests/` ships with the plugin. Plugin users who do not run tests can ignore the folder.

## v1.7.0 - 2026-05-07

The retrieval-precision release. Brain entries now carry stable IDs so downstream skills cite instead of restate. Query gains three modes so the markdown corpus stays usable as it grows. An opt-in observation log captures tool calls without changing default behavior.

### Added

- **Stable entry IDs (citations-by-ID).** Every new brain entry gets a stable `<channel>-YYYY-MM-DD-NNN` ID stamped at write time. Skills like `/dream` now cite IDs instead of restating content. ID convention documented in `templates/rules/entry-conventions.md`.
- **Token-aware progressive query.** `scripts/query.py` gains three modes: `--mode index` (default, ~50 tokens per hit, hard cap 10), `--mode timeline --anchor <slug>` (7-day window either side, hard cap 20), `--mode full --ids <comma-list>` (full body of specified IDs). Bare invocation `python scripts/query.py "<question>"` still works and produces index output (backwards compat preserved).
- **Observation log auto-tail (opt-in).** New `PostToolUse` hook (`post-tool-use-observation.sh` + `.ps1`) appends one JSON line per tool call to `brain/observations/<YYYY-MM-DD>.jsonl`. Off by default. Activate with `FOUNDER_OS_OBSERVATIONS=1`. `/dream` rolls up the day's observations into an OBSERVED section. Setup wizard adds an opt-in question (Phase 0.9).

### Changed

- `/dream` digest format now cites entry IDs and emits an OBSERVED section when an observations file is present.
- `scripts/query.py` output format adds `(id: <id>)` per result when an entry ID is found.

### Notes

- v1.6 users pulling v1.7 see no behavior change unless they set `FOUNDER_OS_OBSERVATIONS=1`. Observation logging is fully opt-in.
- WS4 (install ergonomics sweep) deferred pending tester feedback. See `notes/v1.7-codex-findings.md`.

## v1.6.0 - 2026-05-07

The retrieval and ship-safety release. FounderOS now has a clearer first-week path and a working way to ask the OS what connects to what.

- README skills are now grouped by real usage cadence: Day 1, Week 1, and Month 1+. Install stays above the fold, and substrate details move below the user-facing ship list.
- Eight public-safe operating skills land: forcing-questions, blind-spot-review, ship-deliverable, approval-gates, handoff-protocol, context-persistence, data-security, and bottleneck-diagnostic.
- Four commands land: `/founder-os:forcing-questions`, `/founder-os:ship-deliverable`, `/founder-os:query`, and `/founder-os:audit`.
- `brain/knowledge/` becomes the durable note layer. knowledge-capture writes topic files, and proposal-writer plus strategic-analysis read matching notes back before drafting.
- `/founder-os:query` adds plain markdown and YAML traversal through `brain/relations.yaml`, boot files, patterns, flags, and knowledge notes. No embeddings, no external database.
- `/founder-os:audit` defines one health report across readiness, lint, wiki state, brain staleness, and voice completeness.
- Setup now creates `brain/knowledge/` and copies both `wiki-build.py` and `query.py` helper scripts for fresh installs.
- Version, manifests, README, CLAUDE.md, and AGENTS.md now reflect the v1.6 surface: 37 skills and 19 commands.

## v1.5.0 - 2026-05-07

The tailoring + memory release. The wizard's answers now reach the skills they should reach.

- Setup wizard answers (decision style, communication style, tool stack) are now structured fields the skills actually read. Previously the wizard captured rich answers and only voice/brand profiles flowed downstream. Six daily skills (sop-writer, meeting-prep, email-drafter, strategic-analysis, decision-framework, your-voice) now read identity, operating-rules, and `stack.json` so output is specific instead of generic
- `/rant` and `/dream` commands ship - capture the volume that is the thinking, then distil unprocessed rants into patterns, flags, parked decisions, needs-input, and client signals with a 5-line digest written to brain/log.md
- `brain/rants/` folder convention with frontmatter (`captured`, `processed: false|true`)
- `brain/needs-input.md` joins the brain layer as the "what is blocked on you" channel
- Auto-memory layer documented and seeded - `templates/memory/MEMORY.md` is a four-section index (Behavioral Guards, Active Project Context, Review Due, Expired) the wizard now writes into Claude Code's per-project memory location so behavioral corrections persist across sessions
- Setup wizard hardened: mandatory script copy step (so `/founder-os:wiki-build` does not fail post-install) and mandatory rants folder creation
- Brain example entries seeded with real dates so the SessionStart brief actually surfaces them on Day 1, demonstrating the decay convention by example
- `brain/relations.yaml` ships with three seeded curated edges so users see the format by example rather than spec
- README defines substrate / brain / wiki vocabulary in one block at the top of "What you actually get" - the existing audit's biggest jargon-density bounce point closed
- README setup line restructured as a four-step ladder (Install -> Setup -> Voice -> Brand) so users do not see `/founder-os:setup` before they have an install path
- `docs/first-day.md` adds "A real Tuesday" walkthrough and a [FILL] placeholder explanation - the missing "what does it actually feel like" content the audit flagged

## v1.4.3 - 2026-05-06

- Avatar moves from marketing artifact to user-owned template, populated from your real patterns over time
- AGENTS.md catches up to the v1.4 surface so non-Claude agents see the same commands and substrate
- Public commits now follow a user-readable naming rule (`rules/commit-naming.md`)
- Brain templates teach the v1.4 lifecycle by example so fresh installs see the convention modelled, not just claimed
- GEMINI.md removed. It was a 7-line stub. AGENTS.md covers the cross-agent contract.
- Notion package gets a louder in-development banner so visitors do not assume it installs today
- `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md` added (public-repo standards)
- Stale "v1.2" references in `docs/tools-and-mcps.md` swept to current state
- Readiness output now reads "high-impact" instead of corporate jargon across all surfaces

## v1.4.2 - 2026-05-03

- Windows users now get the SessionStart brief without git-bash (PowerShell hooks wired automatically)
- Voice fallback unified across all six writing skills so a missing voice profile warns and falls back instead of stopping
- Setup wizard and readiness-check now read and write the same backlog file (`core/setup-backlog.md`)
- Bash decay scanner regex fixed for Python compatibility
- Plugin manifest repository field corrected to spec
- Currency rule in proposal-writer made geography-neutral
- README positioning rewritten to broaden audience from "solo founder" to "the person running the business"

## v1.4.1 - 2026-05-02

- Bootloader template now ships the v1.4 substrate so fresh installs see the same CLAUDE.md as upgraded installs
- Setup wizard explicitly copies hooks to the user repo so the SessionStart brief actually fires after install
- README skill count drift fixed (22-of-26 to 23-of-27)

## v1.4.0 - 2026-05-02

- Wiki graph builder skill (`/founder-os:wiki-build`) walks markdown, extracts `[[wikilinks]]`, and writes the graph to `brain/relations.yaml`
- Brain entries can now declare `Decay after: 14d`. Past the date, the SessionStart brief surfaces them for keep / kill review.
- New `system/quarantine.md` catch-net for silent hook and scheduled-task failures
- New `rules/approval-gates.md` matrix listing what auto-runs, what requires explicit yes, and what is blocked outright
- SessionStart brief hook surfaces flags, stale cadence, decay-due entries, and quarantine ACTIVE failures in one screen at session open

## v1.3.0 - 2026-04-30

- Source ingest skill (`/founder-os:ingest`) files external sources into `raw/` with provenance frontmatter, then proposes wiki updates the operator approves
- Read-only wiki lint (`/founder-os:lint`) audits cross-references, orphans, stale time-sensitive content, provenance gaps, and possible contradictions
- `[[wikilink]]` cross-reference convention introduced (forward-only; existing files not retrofitted)

## v1.2.0 - 2026-04-28

- Three voice-coupled writing skills shipped: `linkedin-post`, `client-update`, `proposal-writer`
- `readiness-check` skill and `/founder-os:status` command return a weighted readiness score and the next 3 high-impact moves
- `/founder-os:uninstall` ships with a default mode that preserves user data and a `--purge` mode that wipes everything
- Plugin marketplace install path fixed (schema bug that was silently failing)

## Earlier versions

Earlier work happened on a feature branch and merged into main as v1.0.0. See `git log` for the history.
