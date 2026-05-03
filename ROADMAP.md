# Roadmap

What's planned next. Items here are scoped and time-estimated. None of this gates the current release - the launch ships first, the items below land in patches over the following weeks.

If something on this list matters to you, open an issue or email `solutions@arcassystems.com`.

---

## Shipped

- **v1.3.0** - source ingest + read-only wiki lint. Two skills (`ingest`, `lint`), two commands, the `raw/` provenance convention, the `[[wikilink]]` cross-reference syntax.
- **v1.4.0** - wiki graph builder + brain substrate. The `wiki-build` skill (companion to lint), bi-temporal + decay convention for entries (`rules/entry-conventions.md`), `system/quarantine.md` catch-net for silent hook/task failures, approval gate matrix template (`rules/approval-gates.md`), and the first SessionStart brief hook (surfaces flags, stale cadence, decay-due entries, and quarantine ACTIVE entries in one screen at session open).

---

## v1.3.x - within 2 weeks of v1.3 launch

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

## v1.5 candidate - parallel-agent audit

- **`/founder-os:audit` composite report** (~6 hr). Borrows the parallel-sub-agent pattern: run readiness-check, lint, wiki-build, brain-staleness, voice-completeness in parallel and return one composite OS-health report. Pure addition; readiness-check, lint, and wiki-build stay as standalone commands.

---

## Research-track items (not on a release schedule)

These are open architectural questions. They sit behind explicit triggers - the OS does not start them just because they exist.

- **Continuous research cortex** (Gemini Deep Research v3 prompt). Standalone single-section research pass on the cortex layer pattern: scan surface, relevance filter, quick-win pipeline, reversion register schema, knowledge-layer integration, skill auto-draft loop, three cadence loops (continuous, weekly, monthly), failure modes. Cheap to run. Unblocks any future cortex work.
- **Citation verification on the v2 architecture research.** Five sources to verify (HyperAgents/DGM H, three arXiv IDs, MIND SAFE, MarkTechPost 2026/04/28). Delegate-able to a Codex/Claude background research run.
- **Hybrid temporal knowledge graph (Neo4j + Graphiti + Letta)**. Parked architecture from the lRf9v research branch. Triggers: (a) first paying engagement closed, (b) two consecutive Memory/Retrieval failures the v1.3 lint skill cannot resolve, (c) third multi-entity person enters the OS and the flat-file model produces a material error. Until any trigger fires, no build.

---

## Compatibility commitment

Every roadmap item ships as an addition. Existing skills, commands, hooks, and files keep working unchanged. If a future change would alter behavior for an existing user, it goes through a deprecation cycle: announce in CLAUDE.md, ship as opt-in flag for one minor version, then promote to default in the next minor version. No silent behavior changes.
