# Roadmap

What's planned next. Items here are scoped and time-estimated. None of this gates the current release - the launch ships first, the items below land in patches over the following weeks.

If something on this list matters to you, open an issue or email `solutions@arcassystems.com`.

---

## Shipped

- **v1.3.0** - source ingest + read-only wiki lint. Two skills (`ingest`, `lint`), two commands, the `raw/` provenance convention, the `[[wikilink]]` cross-reference syntax.
- **v1.4.0** - wiki graph builder + brain substrate. The `wiki-build` skill (companion to lint), bi-temporal + decay convention for entries (`rules/entry-conventions.md`), `system/quarantine.md` catch-net for silent hook/task failures, approval gate matrix template (`rules/approval-gates.md`), and the first SessionStart brief hook (surfaces flags, stale cadence, decay-due entries, and quarantine ACTIVE entries in one screen at session open).
- **v1.4.1** - patch. Bootloader template (`templates/bootloader-claude-md.md`) was missing the v1.4 substrate sections - new users running `/founder-os:setup` got a stale CLAUDE.md. Fixed. README skill-count drift fixed (22 of 26 -> 23 of 27). Setup wizard now has an explicit hook-copy step so the SessionStart brief actually fires for new installs.
- **v1.4.2** - patch. Windows PowerShell hooks now wired automatically (no git-bash needed for SessionStart brief). Voice fallback unified across all six writing skills. Bash decay scanner regex fixed for Python compatibility. Plugin manifest repository field corrected. README positioning broadened from "solo founder" to "the person running the business".
- **v1.4.3** - patch. Avatar reframed as a user-owned template (was marketing copy). AGENTS.md caught up to the v1.4 surface. Public commit-naming rule shipped (`rules/commit-naming.md`). Brain templates teach the lifecycle by example. GEMINI.md stub removed. CONTRIBUTING, SECURITY, CHANGELOG added. Stale "v1.2" references swept. readiness output reads "high-impact" instead of corporate jargon.
- **v1.5.0** - tailoring + memory release. Six daily skills (sop-writer, meeting-prep, email-drafter, strategic-analysis, decision-framework, your-voice) now actually read the wizard's captured answers. `/rant` and `/dream` ship with `brain/rants/` folder. Auto-memory `MEMORY.md` template + wizard step land cross-session continuity for behavioral guards. Brain example entries seeded with real dates so the SessionStart brief surfaces them on Day 1. README defines substrate / brain / wiki vocabulary in plain English. `docs/first-day.md` adds "A real Tuesday" walkthrough.
- **v1.6.0** - retrieval and ship-safety release. README grouped by Day 1, Week 1, and Month 1+. Eight operating skills added, plus query and audit. `brain/knowledge/` now feeds proposal and strategy work. `/founder-os:query` traverses markdown and `brain/relations.yaml`. `/founder-os:audit` defines one health report across readiness, lint, wiki, brain, and voice.
- **v1.7.0** - retrieval-precision release. Brain entries now carry stable `<channel>-YYYY-MM-DD-NNN` IDs stamped at write time. `scripts/query.py` adds three modes (`--mode index`, `--mode timeline --anchor <slug>`, `--mode full --ids <comma-list>`) so the markdown corpus stays usable past ~500 entries without an index. New opt-in `PostToolUse` hook appends one JSON line per tool call to `brain/observations/<YYYY-MM-DD>.jsonl` when `FOUNDER_OS_OBSERVATIONS=1` is set. `/dream` cites IDs and emits an OBSERVED section. WS4 (install ergonomics sweep) deferred pending tester feedback.
- **v1.8.0** - query test coverage release. Added a stdlib `unittest` suite and synthetic corpus for `scripts/query.py`, covering index, timeline, full, bare invocation, and guard paths.
- **v1.9.0** - hook test coverage release. Added stdlib tests for the opt-in `PostToolUse` hook across bash and PowerShell paths, static parse smoke tests for session hooks, and docs for the query `--root` flag.
- **v1.10.0** - runtime brain context release. New `scripts/brain-snapshot.py` emits a deterministic markdown payload (open flags, must-do, recent decisions, voice and brand fields, staleness) that any skill can consume at task time. Nine output-producing skills (meeting-prep, weekly-review, strategic-analysis, decision-framework, founder-coaching, knowledge-capture, unit-economics, priority-triage, brain-log) now read it. New `brain-pass` skill (`/founder-os:brain-pass "<question>"`) synthesises answers across the brain layer with stable-ID citations, free-tier accessible, no embeddings. `meeting-prep` and `linkedin-post` auto-invoke brain-pass before producing output. 39 skills, 20 commands, 34 tests.
- **v1.11.0** - launch-hardening release. Closes v1.10 install gaps so Path A users actually get the runtime brain context. `scripts/wiki-build.py` mirrored to repo root so `/founder-os:wiki-build` works on a fresh clone. Setup wizard now copies all four runtime helpers (was two), creates `brain/archive/` and `companies/`, and surfaces the per-company business-context template. `/founder-os:update` and `/founder-os:uninstall` now cover `scripts/`, `rules/`, `docs/`, `AGENTS.md`. PowerShell hook fixes for non-English Windows locales (locale-safe ISO-8601 parsing, null path guards). Bash hooks gain `|| exit 0` guards. Revenue-check hooks anchor on hook location, not CWD. New `.gitattributes` enforces LF on `.sh` and `.py` so Windows clones don't break Bash hooks. CLAUDE.md and AGENTS.md catch up to the v1.10 surface (39 skills, 20 commands, brain-pass / brain-snapshot rows). README mobile and kill-criteria claims corrected. AgentOS link replaced with inline summary. Prose semicolons stripped per writing-style rule.

---

## Patch candidates (deferred from earlier releases, still valid)

### Install ergonomics

- **`install.sh` for one-line curl install** (~2 hr). Path D: `curl -fsSL https://.../install.sh | bash`. Drops skills into `~/.claude/skills/` for users who don't want to think about plugin marketplace mechanics. Manual git-clone (Path B) stays the recommended baseline.
- **`uninstall.sh` script mirror of `/founder-os:uninstall`** (~1 hr). Lists everything by name before removing, same as the slash command.

### Skill ergonomics

- **`/founder-os` orchestrator skill** (~4 hr). Optional unified entry: `/founder-os <subcommand>` routes to the existing skill files. The namespaced commands (`/founder-os:setup`, `/founder-os:status`, etc.) keep working unchanged.
- **Visual bar formatting in `/founder-os:status` and `/founder-os:lint`** (~1 hr). Add ASCII bars to the bucket scores for legibility.
- **Output file naming convention doc** (~30 min). Document which skills produce new artifacts (e.g. `WEEKLY-RETRO-2026-W18.md`) versus update existing files.

### Surface polish

- **README banner.svg + status badges** (~1 hr). Visual entry. Skill count, command count, MIT badge, install-paths shortcut.
- **HTML playbook** (~4 hr, post-launch nice-to-have). Single self-contained HTML file users can email to others or open offline. README plus first-day docs cover the launch case; the playbook is for sharing.

---

## v1.12 candidates

- **Company OS layer 2 sketch** (~6 hr). Draft the multi-user state model once a real team handoff needs shared operating context.
- **Observation rollup polish** (~3 hr). After v1.7's opt-in observation log gets used in real sessions, tune the `/dream` OBSERVED section format. Add a per-tool summary, dedupe noisy file reads, and surface unusual tool patterns.
- **Query layer caching** (~4 hr). Once entry counts cross ~500 per channel, cache parsed frontmatter in `brain/.query-cache.json` so `query.py` does not re-parse every file on every run. Cache invalidates on file mtime change.
- **Semantic memory layer with embeddings** (~8 hr). Natural next step if v1.10's brain-pass proves slow or shallow at scale. Build a small vector index in `brain/.embeddings.jsonl` keyed on entry IDs, refresh on a write hook, and have brain-pass consult it as a candidate filter before reading. Stays opt-in. The markdown corpus remains canonical.
- **Snapshot consumers across the rest of the skill catalogue** (~2 hr). v1.10 wired nine output-producing skills. After tester feedback, audit the remaining writers (email-drafter, sop-writer, content-repurposer, client-update, proposal-writer) and decide which benefit from the snapshot.

## v1.12+ surface expansion

- **"Works with: Cowork" tag** when Anthropic ships hook + `.claude/commands/` parity in Claude Cowork. Until then, FounderOS is Claude-Code-only on the active surface; Cowork pairs as read-only execution surface against the same folder.
- **Notion Starter Kit** for Cloud Claude users who do not have Claude Code. Shipping path is a public Notion duplicate template plus a Claude Project system prompt. Tracked separately from this roadmap.

---

## Research-track items (not on a release schedule)

These are open architectural questions. They sit behind explicit triggers - the OS does not start them just because they exist.

- **Continuous research cortex** (Gemini Deep Research v3 prompt). Standalone single-section research pass on the cortex layer pattern: scan surface, relevance filter, quick-win pipeline, reversion register schema, knowledge-layer integration, skill auto-draft loop, three cadence loops (continuous, weekly, monthly), failure modes. Cheap to run. Unblocks any future cortex work.
- **Citation verification on the v2 architecture research.** Five sources to verify (HyperAgents/DGM H, three arXiv IDs, MIND SAFE, MarkTechPost 2026/04/28). Delegate-able to a Codex/Claude background research run.
- **Hybrid temporal knowledge graph (Neo4j + Graphiti + Letta)**. Parked architecture from the lRf9v research branch. Triggers: (a) first paying engagement closed, (b) two consecutive Memory/Retrieval failures the v1.3 lint skill cannot resolve, (c) third multi-entity person enters the OS and the flat-file model produces a material error. Until any trigger fires, no build.

---

## Compatibility commitment

Every roadmap item ships as an addition. Existing skills, commands, hooks, and files keep working unchanged. If a future change would alter behavior for an existing user, it goes through a deprecation cycle: announce in CLAUDE.md, ship as opt-in flag for one minor version, then promote to default in the next minor version. No silent behavior changes.
