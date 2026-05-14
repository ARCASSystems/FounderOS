---
title: Codex final-release review brief
target: FounderOS public repo at HEAD (commit 5f45183, tag candidate v1.22.0)
reviewer: Codex (or any independent model with filesystem + shell access)
output: c:/arcas_dev/ARCAS/founder-os/traces/v122-codex-final-review.md
created: 2026-05-14
disposition: FINAL release review. After this, no further feature work from ARCAS Systems.
---

# Codex final-release review - FounderOS v1.22.0

You are reviewing the public FounderOS repo before it is tagged as the final release from ARCAS Systems. After v1.22.0 the repo enters maintenance mode: critical-breakage patches only, no further feature work. Anything wrong with the surface that ships here, the user will hit it - and there will be no v1.23 to fix it.

Your job is to find the things that will hurt a stranger discovering this repo in 2027 and trying to use it without a single ARCAS Systems engineer ever responding. Look at code quality AND user experience. Both load-bearing.

Read this brief end-to-end, then walk the repo, then write your findings to `traces/v122-codex-final-review.md` in the exact format specified at the bottom of this file.

---

## What FounderOS is

A Claude Code plugin. Files-and-skills. Markdown-first. Local-first. The user clones a repo, runs the setup wizard, and gets an operating system they can use from inside Claude Code: identity file, cadence files, decision tracking, knowledge notes, brain log, role modes, voice and brand profiles, snapshot-aware writing skills, queue with a 3-item cap, substrate health check, observation rollup, and a natural-language menu.

No paid API key required for core function. No mandatory external service. No proprietary format. Free-tier accessibility floor is load-bearing - if any path requires a paid Anthropic sub or any commercial product to work end-to-end, that is a critical finding, not a polish item.

Repo: `https://github.com/ARCASSystems/FounderOS`. License: see `LICENSE`.

---

## Why v1.22 exists

v1.21 shipped the operating shell. v1.22 ships the version that someone discovering this repo in 2027 can clone and use without ARCAS Systems doing further development. After v1.22 the only intended work on this repo is user-specific tailoring by the user themselves (their voice profile, brand, skill set, archetype). The baseline is frozen.

v1.22 closed the remaining capability gaps, audited the skill catalogue, rewrote the ROADMAP from "what's next" to "what shipped, what we deliberately did not build, and how to fork from here," and added test coverage for the no-maintenance posture.

---

## What was delivered (seven workstreams, three commits)

### Commit `919a509` - Session 1 - W1 + W3 + W7

- **W1 - Install ergonomics and first-touch.** New `install.sh` (one-line curl), `uninstall.sh` mirror, README install section rewritten in friction order (curl > plugin marketplace > manual git clone > Cowork), `docs/install.md` mirrors it with full step-by-step. `tests/test_install_scripts.py` covers static-content + shell-syntax checks.
- **W3 - ROADMAP rewrite and scope closure.** ROADMAP now has "Shipped," "What we deliberately did not build," "How to fork and extend," "Compatibility commitment." Every former deferred item has a final disposition. Length: 92 lines.
- **W7 - Maintenance handoff documentation.** `CONTRIBUTING.md` has a "Maintenance posture (after v1.22.0)" section with issue-triage policy. New `docs/forking.md` (≤100 lines, 5 sections). README has a final-release stance paragraph near the bottom.

### Commit `cbc66b9` - Session 2 - W2 + W5

- **W2 - Skill audit and archive sweep.** Full audit table at `traces/v122-skill-audit.md`. Dispositions: 42 KEEP, 2 IMPROVE, 0 ARCHIVE. `skills/today/SKILL.md` description rewritten. `skills/approval-gates/SKILL.md` description fixed. `skills/_archive/` directory created.
- **W5 - Setup wizard archetype hardening.** New Phase 0.2.1 role question (founder / operator / team-of-one). Three downstream questions branch phrasing by role. CRM question updated for B2C founders (subscriber list option added per gap M1). New Q5 captures primary marketing channel into `stack.json` (gap M2). `templates/bootloader-claude-md.md` has `{{role_noun}}` placeholders. `scripts/menu.py` now weights the user's declared channel. Tests: `tests/test_skill_catalogue.py` (5 tests), `tests/test_wizard_archetype.py` (9 tests, 2+4+3 across 3 classes).

### Commit `5f45183` - Session 3 - W4 + W6 + version stamp

- **W4 - Observation rollup and `<private>` exclusion tag.** `scripts/observation-rollup.py` (stdlib only, groups `brain/observations/*.jsonl` by ISO week, compresses weeks with >=7 days that ended >=3 days ago to `brain/observations/_rollups/YYYY-Wnn.md`, deletes source only after rollup verified written, idempotent). `skills/observation-rollup/SKILL.md` and `.claude/commands/observation-rollup.md` give the natural-language and slash surfaces. SessionStart brief (both `.sh` and `.ps1`) reports rollup count and surfaces a nudge for stale JSONLs. New `rules/operating-rules.md` documents the `<private>` exclusion tag spec (case-insensitive, applies to brain-log, dream, knowledge-capture, rant, auto-memory). All four writing surfaces document the private-tag filter procedure.
- **W6 - End-to-end test coverage.** New `tests/test_e2e_critical_paths.py` with 8 classes (one per critical path): setup wizard, install.sh dry-run, uninstall.sh dry-run, verify healthy state, verify broken state, queue 3-cap gate, brain-pass empty corpus, wiki-build idempotency. `.github/workflows/founderos-audit.yml` added a `test` job that runs `python3 -m unittest discover tests` on every push.
- **Version stamp.** `VERSION`, `plugin.json`, `marketplace.json` (both fields), README Production stamp, README v1.22 status paragraph, ROADMAP Shipped list, CHANGELOG, `skills/index.md` (header count + commands section + status line) all bumped to v1.22.0 / 45 skills / 27 commands / 244 tests.

---

## The critical review dimensions (each must be exercised)

You are NOT writing a generic code review. Each finding must map to one of these dimensions. If it does not, it is a polish observation - and polish belongs in a separate, lower-priority section.

### 1. Functional integrity (highest priority)

- **Does each scriptable path actually do what its docs say?** `install.sh --dry-run`, `uninstall.sh --dry-run`, `scripts/observation-rollup.py`, `scripts/wiki-build.py`, `scripts/brain-snapshot.py`, `scripts/query.py`, `scripts/menu.py`, `scripts/memory-diff.py`, `scripts/brain-pass-log.py`. Run them, read their stderr, check their exit codes. Verify the documentation claims match the actual behavior.
- **Does each skill body's documented procedure terminate?** Pick three high-traffic skills (`founder-os-setup`, `verify`, `weekly-review`) and trace the documented procedure step-by-step against the files it claims to read or write. Find any step that references a file, template, script, or section that does not exist at HEAD.
- **Do the hooks fire correctly?** `.claude/hooks/session-start-brief.sh` and its PowerShell sibling must produce the same brief content on the same inputs. The PostToolUse hook (`post-tool-use-observation.sh` and `.ps1`) must write the same JSONL shape on both surfaces. Run each hook with a synthetic environment and diff the output.
- **Do the four install paths work end-to-end?** Path A (plugin marketplace) requires nothing local. Path B (manual git clone) requires git only. Path E (curl install.sh) requires bash + git + python 3.11+. Path D (Cowork) requires Claude Cowork. For B and E specifically, walk the doc step-by-step in a fresh clone and report whether a non-developer could complete it without external help.

### 2. The free-tier accessibility floor

Every claim in the README, ROADMAP, and CHANGELOG that the OS works without a paid Anthropic sub must be verifiable. Specifically:

- No skill body issues an API call to Anthropic. Skills are markdown that the host model interprets - they should not call back out to a paid endpoint mid-skill.
- No script imports the Anthropic SDK or requires an `ANTHROPIC_API_KEY` env var to function.
- The `brain-pass` skill claims it works on the free tier ("The model running this skill IS the retrieval engine"). Verify the skill body matches that claim. No `requests.post`, no SDK call, no fallback to a paid path.
- `scripts/menu.py`, `scripts/query.py`, `scripts/brain-snapshot.py` must not make network calls.
- The setup wizard must not require any paid integration to complete - all paid integrations should be opt-in.

If you find a path that breaks the floor, that is a critical finding. The floor is the most-cited load-bearing constraint in this repo.

### 3. No leakage of private/personal context

The public repo is forked from a private operator-personal repo. ARCAS Systems is acceptable as repo owner/license. But:

- Run a regex sweep for personal names. Suggested regex: `Aqsa|Afsha|Bilal|Ashrith|Teja|Azeem|Simon Fernandes|Maimuna|Surandar|Keerthana|Aparna|Apeksha|Safa|Tariq|Roula|Alistair|Aranha|alistair@arcas|2547468`.
- Sweep for client domains, internal company names (other than ARCAS Systems / ARCASSystems), or specific revenue figures.
- Sweep for internal Notion IDs, GitHub PAT prefixes, or any URL with `private` or `internal` in the path.
- Check `templates/` files specifically - templates are user-facing and most likely to leak.
- Check `traces/` files - some may be legitimate dev evaluation traces, others may have leaked private context.

Zero matches is the bar. Each match is a critical finding regardless of how minor it looks.

### 4. User-truth verification (not plan-fidelity)

This is the most common failure mode in plan-driven work: the file exists, the test passes, but the documented behavior does not actually work for a user. Specifically check:

- **The setup wizard SKILL.md.** Read the body as if you are running it. Does it actually produce a working `core/identity.md`, `cadence/daily-anchors.md`, `cadence/weekly-commitments.md`, etc.? Are the templates it references at the documented paths? Do the substitutions (`{{role_noun}}`, etc.) have unambiguous source values?
- **The verify skill.** Walk all 8 checks against the live repo. Do the PASS / WARN / FAIL conditions match the actual state of the v1.22 repo? Would a fresh-installed user see at least 6/8 PASS (verify on healthy state expectation)?
- **The four writing surfaces with the `<private>` filter.** The skill bodies document the procedure. Verify the documented procedure is unambiguous - a fresh model reading the body should know exactly what to scan, what to remove, and when to skip writing entirely.
- **The brain-pass skill.** It claims to handle empty corpus gracefully. Walk the documented steps with an empty `brain/` directory in mind. Does the skill produce something useful or does it error out?
- **The README and `docs/install.md` install steps.** Pick the Path B (manual git clone) walkthrough. Read it line-by-line as a non-developer. Does anything assume context the doc has not given? Does any step say "run X" without defining X?

**Persona trace simulation (mandatory).** Static file checks miss things that running-as-a-persona surfaces. The v1.20 / v1.21 traces against Marcus, Maya, and Dev caught gaps the code review had passed. v1.22 changed the wizard meaningfully (new role question, branched downstream questions, `{{role_noun}}` substitution, new B2C subscriber-list and primary-channel paths). Run a simulated trace pass against three personas. For each, do not just check that the file exists - read the wizard SKILL.md body step-by-step and reason about what the persona experiences.

Personas (use these exact ones - they map to the wizard's three role options):

1. **B2B founder.** Owns a 3-person SaaS company. Sells to mid-market enterprises. Has a CRM. Picks the "founder" role.
2. **B2C team-of-one creator.** Solo creator. Mailing list of 8000. Sells digital courses. No employees, no investors, no B2B context. Picks the "team-of-one" role.
3. **Operator-not-founder.** Runs operations for someone else's business. Reports to a founder. Has no ownership authority. Picks the "operator" role.

For each persona, report:

- Would this person finish setup without confusion? Name any wizard phrase that does not fit their context.
- Does the bootloader CLAUDE.md the wizard writes match their role and framing? Specifically: does `{{role_noun}}` produce the right noun for them in every place it substitutes? Are there any hardcoded "founder" references left in role-context sentences?
- Does any downstream skill assume context they did not provide? Pick the three skills they are most likely to use first (linkedin-post, today, weekly-review for B2C; client-update, meeting-prep, queue for operator; proposal-writer, brain-log, deal-scoping equivalent for B2B founder) and walk those skill bodies the same way.
- Does the OS produce output this persona would actually want? Or does it produce output shaped for the operator's original archetype (B2B founder)?

Treat each persona as a separate trace. Each gap surfaced is a finding with file path + the exact line that fails for that persona.

### 5. Documentation drift

The repo has ~7000 lines of docs. With v1.22 being the final, drift between docs and code matters more than ever (no one will fix it later).

- README `### Slash commands (27)` must list exactly 27 commands. Count the rows.
- README `### Skills` section (or equivalent) must show 45 skills.
- `skills/index.md` table must list 45 skills. The Commands section must list 27.
- `plugin.json` and `marketplace.json` description counts must match.
- `docs/skills.md` and `docs/commands.md` must match the live `.claude/commands/` and `skills/` directories. Any orphan in one not in the other.
- CHANGELOG should not name any skill or command that does not exist at HEAD.
- ROADMAP "Shipped" list must not promise a feature that is not in the repo.
- `CLAUDE.md` and `AGENTS.md` must not name a script that does not exist.

**Forward-pointing language sweep (mandatory).** Doc-contradicts-doc drift is invisible without a grep. Run a case-insensitive sweep across `README.md`, `ROADMAP.md`, `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/*.md`, `skills/index.md`, `skills/*/SKILL.md`, and `templates/*.md` for these patterns:

- `planned`
- `coming soon`
- `coming in`
- `next quarter`
- `next release`
- `will ship`
- `will add`
- `will support`
- `future release`
- `not yet shipped`
- `roadmap` (lowercase, as a noun referencing a future plan rather than the ROADMAP.md file)
- `TBD`
- `tracking for v1.2[3-9]` or `v1.[3-9]`
- `we plan to`

Each match must point either to ROADMAP's "What we deliberately did not build" section (with clear reasoning) or to "How to fork and extend" (with a starting prompt). Any match that implies ARCAS Systems will ship something later is a critical finding - fix the doc, do NOT undeclare the not-built decision. The historical failure mode this catches: README:290 saying "Company OS layer (planned, not shipped)" seven days after ROADMAP said "declined." Cheap to grep, invisible without it.

### 6. Test substance (not vacuous coverage)

244 tests is a lot for a markdown-and-scripts repo. The risk: tests that pass plan rows while shipping broken behavior.

- For each W4 / W5 / W6 test class, verify the assertions actually exercise the documented behavior, not just "the file exists."
- The E2E `test_e2e_critical_paths.py` mostly does static-content checks. That is fine for skill-bodies-as-markdown - but flag any test where the assertion is so weak that a future refactor could break the user-visible behavior while the test still passes.
- The install.sh smoke tests run `bash install.sh --dry-run` - do they verify the dry-run output actually names the operations the script would perform, or just that it exits?
- The wiki-build idempotency test runs the script twice and diffs the result - does the test scaffold a realistic input or a trivial one that hides bugs?
- Are there hooks tests (`test_session_hooks.py`) that exercise both bash and PowerShell paths, or only one?

### 7. Cross-platform parity

The repo claims to work on macOS, Linux, and Windows (Git Bash). The hooks ship in two implementations (`.sh` + `.ps1`). The install.sh ships bash-only.

- Do the `.sh` and `.ps1` hooks produce equivalent output? Specifically check the new W4 rollup section.
- Does `install.sh` actually work in Git Bash on Windows (the most common Windows path)? Read for bash 4 features that Git Bash 4.x may or may not support.
- Does any test or script assume forward-slash paths in a way that breaks on Windows?

### 8. Maintenance posture realism

`CONTRIBUTING.md` declares what kinds of issues will and will not get responses. `docs/forking.md` teaches users to fork. These are commitments to the community. They must be:

- Honest about what will happen when a critical-breakage issue lands.
- Clear about what extension points exist and how to use them.
- Consistent with the "no further feature work" stance.

If `CONTRIBUTING.md` says "we will respond to critical breakage" but there is no triage mechanism, that is a finding. If `docs/forking.md` lists extension points that have been deprecated or do not work, that is a finding.

---

## Known concerns to specifically address

These came up during execution. State your position on each.

1. **Row 32 - test suite timing.** The plan's verification row says "Full suite runs in < 30 seconds" on Wall time. On the operator's Windows machine the full suite runs in ~42 seconds. The new W4 + W6 tests run in <1 second; the cost is in existing tests (test_session_hooks subprocess overhead, voice-interview content scans). Linux CI should hit <30s easily. Decision needed: is this a finding (drop slow existing tests or fix subprocess overhead) or accept-as-is for the Windows reality?
2. **One amend on the session-3 commit.** I amended `e566e5a` to `5f45183` once to add the "45 skills, 27 commands, 244 tests." summary line to the CHANGELOG. The plan says "do not amend." The commit was unpushed at the time, so no remote impact. Surface or accept?
3. **Untracked files left in working tree.** `.agents/` directory (origin unknown) and 5 `traces/v1202-*.md` / `v1203-*.md` files from earlier sessions are in the working tree but not staged or committed. Are these dev artifacts that should be deleted, kept untracked, or committed under a `traces/` retention policy?
4. **The W4 observation-rollup `aggregates correctly` test.** The current assertion checks for presence of specific tool/skill/session strings in the rollup. Is that strong enough, or should the test verify the actual counts (e.g., "21 total" appears)? The current test does check "21" but it is a substring search, not a structural assertion.
5. **The `<private>` tag spec for case-insensitive closing tag.** The spec says "the closing tag must match the opening tag case-insensitively." Is the implementation guidance in the four writing-surface bodies clear enough that two model implementations would behave identically? Or is there enough ambiguity that case-mismatched tags (`<PRIVATE>...</private>`) might be silently dropped from filtering?
6. **The setup wizard's three-archetype claim.** v1.22 W5 added founder / operator / team-of-one. Was the team-of-one path actually exercised, or is it inferred from the founder path? A B2C solo creator should be able to run setup without B2B context creeping in.
7. **The legal-compliance skill scope.** It loads UAE references by default and lets other jurisdictions add their own. Is the framing in the skill body honest about that limitation, or does it imply broader coverage than is shipped?
8. **The `notes/` and `notion-package/` directories.** Do they belong in a public final-release repo, or are they leftovers? If they belong, are they self-explanatory to a fresh user?

---

## Out of scope (do NOT review these)

- Whether v1.23 should exist. It will not. The final disposition is final.
- Whether the Plan A / Plan B split should be different. Already decided.
- Whether the skill catalogue should have more / fewer skills. W2 audited; ship what's in `skills/`.
- Anything in the operator's private repo at `c:/arcas_dev/ARCAS/ARCASFounderOS/`. You are reviewing only the public repo at `c:/arcas_dev/ARCAS/founder-os/`.
- The Personal OS sibling repo at `c:/arcas_dev/ARCAS/personal-os/`.

---

## Output format

Write your findings to `traces/v122-codex-final-review.md` in the public repo (`c:/arcas_dev/ARCAS/founder-os/traces/v122-codex-final-review.md`). Use exactly this structure:

```markdown
---
title: FounderOS v1.22.0 final-release review
reviewer: Codex (or named model)
target_commit: 5f45183
date: 2026-MM-DD
recommendation: SHIP / SHIP WITH PATCHES / DO NOT SHIP
---

# FounderOS v1.22.0 - Codex final-release review

## Headline

One sentence: ship as-is, ship after N specific patches, or do not ship.

## Critical findings (must fix before tag)

Each finding gets a heading, a one-line claim, evidence (file path + line number or exact command + output), and a proposed fix.

### Finding 1 - <short title>

- **Claim:** <one line>
- **Evidence:** <file:line or command output>
- **Impact:** <which review dimension + who hits it>
- **Fix:** <one to three lines of specific instruction>

## Quality concerns (should fix, can ship without)

Same structure as critical. These are things that will degrade user experience or future maintenance but do not break the release.

## Polish observations (optional)

Same structure. Anything below the quality bar.

## Positions on the eight known concerns

For each of the eight known concerns from the brief, state your position in one paragraph. No equivocation.

1. Test timing - <position>
2. Amend on session-3 commit - <position>
3. Untracked files - <position>
4. Aggregates test strength - <position>
5. Private-tag case-insensitivity - <position>
6. Team-of-one archetype coverage - <position>
7. Legal-compliance scope honesty - <position>
8. notes/ and notion-package/ presence - <position>

## Confidence

How confident are you in the review? What did you NOT have time or context to verify? Be explicit about gaps.

## Final recommendation

SHIP / SHIP WITH PATCHES / DO NOT SHIP. If patches, list the exact ones (cross-reference your critical findings).
```

---

## What "good" looks like

A good review is one where the operator reads it and can act on every finding without going back to ask "where?" or "what specifically?" Cite file paths, line numbers, and exact command output. Do not editorialize - the operator can interpret a finding faster than they can parse opinion.

A good review also takes a clear stance on the eight known concerns. The operator already has the context to decide; what they need is your independent judgment, not a menu.

---

## Constraints on your review file

- No em dashes or en dashes. Simple hyphens only.
- No banned phrases (delve, robust, seamless, leverage as verb, comprehensive, holistic, transformative, streamline, optimize, utilize, facilitate, unlock, navigate, ecosystem, landscape, proactively).
- No AI attribution footer. No "Generated with Codex" or similar.
- Markdown only. No code blocks beyond what is necessary to cite evidence.
- One file. Do not split into multiple review documents.

Write the review. The operator will read it and decide whether v1.22.0 ships as-is or with patches.
