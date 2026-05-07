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

## v1.7 candidates

- **Stronger retrieval path** (~6 hr). Add richer ranking and optional cached indexes only if plain-file query misses real user questions twice.
- **Company OS layer 2 sketch** (~6 hr). Draft the multi-user state model once a real team handoff needs shared operating context.
- **Install ergonomics sweep** (~4 hr). Re-check plugin install, script copy, and first-run docs after v1.6 reaches fresh users.

---

## Research-track items (not on a release schedule)

These are open architectural questions. They sit behind explicit triggers - the OS does not start them just because they exist.

- **Continuous research cortex** (Gemini Deep Research v3 prompt). Standalone single-section research pass on the cortex layer pattern: scan surface, relevance filter, quick-win pipeline, reversion register schema, knowledge-layer integration, skill auto-draft loop, three cadence loops (continuous, weekly, monthly), failure modes. Cheap to run. Unblocks any future cortex work.
- **Citation verification on the v2 architecture research.** Five sources to verify (HyperAgents/DGM H, three arXiv IDs, MIND SAFE, MarkTechPost 2026/04/28). Delegate-able to a Codex/Claude background research run.
- **Hybrid temporal knowledge graph (Neo4j + Graphiti + Letta)**. Parked architecture from the lRf9v research branch. Triggers: (a) first paying engagement closed, (b) two consecutive Memory/Retrieval failures the v1.3 lint skill cannot resolve, (c) third multi-entity person enters the OS and the flat-file model produces a material error. Until any trigger fires, no build.

---

## Compatibility commitment

Every roadmap item ships as an addition. Existing skills, commands, hooks, and files keep working unchanged. If a future change would alter behavior for an existing user, it goes through a deprecation cycle: announce in CLAUDE.md, ship as opt-in flag for one minor version, then promote to default in the next minor version. No silent behavior changes.
