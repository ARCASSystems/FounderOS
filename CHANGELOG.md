# Changelog

All notable releases. Format follows the user-value-first commit naming rule (`rules/commit-naming.md`).

## v1.36.1 - 2026-06-06

### Fix - CI gate, CMO role token, setup fields, install steer, and provider honesty

A patch release that clears a red CI gate and tightens five rough edges an audit surfaced. No new skills or commands.

- **CI gate fixed so contributors can push.** `check_install_completeness.py` read only `skills/founder-os-setup/SKILL.md`, but a docs refactor had moved the wizard's script and hook copy lists into `references/root-structure.md`. The guard then reported every runtime script and wired hook as named nowhere and failed every push to main. It now reads the whole setup-skill surface (`SKILL.md` plus `references/*.md`), so it sees what the wizard actually names. A new local test (`tests/test_ci_guards_pass_on_clean_tree.py`) runs every `.github/scripts/check_*.py` guard on the clean tree and asserts each exits 0, so a future doc move cannot silently break a guard while the test suite stays green.
- **CMO role no longer ships an unfilled token.** `templates/roles/cmo.md` carried `{{CONTENT_CHANNELS}}` and `{{CONTENT_CADENCE}}` with no entry in the wizard's substitution map, so they were the only tokens that could land on a founder's disk as literal `{{...}}`. The wizard now substitutes both like every other token: it seeds channels from the primary channel captured in discovery when present, and otherwise fills a plain-language default a founder can edit, instead of a bare `[NOT SET]`.
- **Setup captures timezone.** `meeting-prep` reads a timezone from `core/identity.md`, but discovery never asked for one, so it shipped blank. Discovery now asks a single skip-able timezone question and writes it into the identity file. Jurisdiction stays opt-in and is collected by `legal-setup` on first run, which discovery now states so the unset field reads as intentional.
- **Non-technical founders are steered to the no-terminal install.** The install section led with the one-line curl labelled simplest, which actually needs git, Python, and bash. It now leads with the plugin install, which runs entirely inside Claude Code with no terminal step, and every path states its real prerequisites. `docs/install.md` mirrors the new order.
- **Provider claim now matches what actually runs.** The README said the AI subscription could be Claude, OpenAI, or Google, but the wizard, the slash commands, and the hooks are Claude Code only. The cost section now leads with built for Claude Code and keeps the honest portability note: the files are plain markdown you can read in any AI, but the product runs in Claude Code. `llms.txt` command count corrected from 33 to 34.

### Cross-cutting

VERSION bumped to 1.36.1. Both manifest version fields and the README status line updated to match. Test count updated to 643 (the new CI-guard self-test). Skill count unchanged at 62, command count unchanged at 34.

## v1.36.0 - 2026-06-04

### Add - output bias self-check (`rules/biases.md` + `/founder-os:devil`)

The OS now runs a check on its OWN reasoning before it gives an opinion of consequence, so advice ships named-and-countered instead of confidently biased. There is no bias-free advice - the model running the OS is itself a bias engine - so the honest target is to name the most likely bias and argue the other side, not to claim none exists.

- `rules/biases.md` - the six output biases (sycophancy/confirmation, authority, recency, action bias, absence blindness, narrative coherence) and the output contract: a counter-case, a confidence level, what evidence is absent, and the do-nothing option, attached to any recommendation, go/no-go, pick between options, or yes/no on a send or spend. Carries the anti-theater rule: a check that always says "no bias found" launders confidence, so an empty counter means "low confidence, thin evidence", never "all clear". Ships in `templates/rules/` too, so a fresh setup gets it.
- `/founder-os:devil <claim>` - runs the self-check on demand against any claim or decision. Names the one most-likely bias, builds the counter-case, and gives an honest read on whether the position survives. Read-only.
- Boot rule plus a plain-language "Why your OS pushes back" section in `CLAUDE.md` (and the generated bootloader), mirrored into `AGENTS.md` and `GEMINI.md` for non-Claude agents. The frame is the human analogue: you cannot see your own bias because from the inside it looks like normal thinking, so a good advisor names it for you. The setup wizard tells new users this during onboarding.
- A one-line `[bias-check]` decision-prompt nudge folded into the existing `UserPromptSubmit` capture hook (`scripts/user-prompt-capture.py`): when a prompt asks for a decision or opinion, it reminds the model to run the self-check before answering, and stays silent on plain tasks. It matches phrasing not intent, so it misses some decision-asks by design.

### Cross-cutting

VERSION bumped to 1.36.0. Both manifest version fields and the README status line updated to match. Command count 33 to 34 (the new `/founder-os:devil`); count statements updated across README, AGENTS.md, skills/index.md, plugin.json, marketplace.json, the verify example, and docs/commands.md. Skill count unchanged at 62. Test count updated to 641.

## v1.35.0 - 2026-06-02

### Add - three generic operating skills (`reconnect-prompt`, `list-pruner`, `finance-import`)

Three skills ported from the private source and made vendor-neutral. They bring the public set to 62 skills; command count stays at 33.

- `reconnect-prompt` - turns an expired-token or 401 failure into one copy-paste reconnect prompt and logs the failed call to the `system/quarantine.md` catch-net so a dead connector does not stay silent until the next session notices missing data. It stops the failing action, never retries, and never asks for credentials. Resolves the `stack.json` placeholder that broke (`{calendar}`, `{email_platform}`, `{knowledge_base}`, etc.) and degrades to a one-line `brain/log.md` note on installs without the catch-net. Called by any integration-touching skill on auth failure.
- `list-pruner` - cleans a contact list before outreach: normalizes and de-duplicates emails, flags missing fields, and scores each row High / Medium / Low. Accepts a CSV path or a pasted table and returns a clean markdown table; writes a CSV only on request. Composes with `linkedin-network-scan` (which builds the list) and surfaces High-scored rows as candidates for `context/leads.md`. Free-tier safe - paste the CSV, get the table back.
- `finance-import` - parses a finance CSV export into a normalized markdown summary at `finance/<period>/summary.md`, totalled by category with warnings for missing fields. Read-only at the source: it never writes back to your accounting tool. Detects amount, date, account, category, and memo columns and stops to ask for redaction if it finds confidential identifiers. Feeds `unit-economics`. PDF input is a documented manual path until a per-format parser is tested.

### Cross-cutting

VERSION bumped to 1.35.0. Both manifest version fields, the README status line, and every canonical skill-count statement (README, CLAUDE.md, AGENTS.md, skills/index.md, plugin.json, marketplace.json, docs/skills.md) updated from 59 to 62. Command count unchanged at 33.

## v1.34.1 - 2026-05-31

### Add - career / talent ICP example for `linkedin-network-scan`

The scanner shipped with one example ICP aimed at sales and partnership targeting. This release adds a second example, `icp.career.example.yaml`, for the people axis: the recruiters, talent leaders, and hiring managers in your network who can refer you, hire you, or help you hire, plus the decision-makers at the companies you are targeting. The engine is unchanged - the career lens is pure config. `min_seniority: ic` so a junior recruiter or sourcer at a target company is not dropped, a lower threshold (18) so role-matched recruiter and talent titles clear the bar on their own, and a roles list seeded with recruiter, talent acquisition, sourcer, hiring manager, head of people, plus the senior titles that own the hiring decision. Same privacy contract: ZIP-gated, raw CSVs never enter context, message content never read, nothing sent. The SKILL body now offers both examples and asks which goal you are on (selling / partnering, or hiring / job search) when both fit.

### Cross-cutting

VERSION bumped to 1.34.1. Both manifest version fields and the README status line updated to match. Skill count (59) and command count (33) unchanged - this adds an example config to an existing skill, not a new skill.

## v1.34.0 - 2026-05-31

### Add - `linkedin-network-scan` (rank your own network against your ICP, without burning context)

A new skill that turns your own LinkedIn data export into a ranked outreach worklist scored against an ICP you define. The point is token efficiency: a LinkedIn connections export is thousands of rows and tens of thousands of tokens, so a deterministic local script (`scan.py`, Python standard library only - no `pip install`) does the scoring and collapses the export to a compact ranked digest. The assistant reads only that small digest, never the raw `Connections.csv` or `messages.csv`.

- ZIP-gated: the skill's first move is to confirm you have your LinkedIn export, and walk you through requesting it if not. It reads straight from the ZIP - no need to unzip.
- ICP is yours: roles, industries, company keywords, a named seniority floor, an optional region filter, and an exclusion list, all from a config file you edit (`icp.example.yaml` ships as the template; JSON also accepted). Omit it for a permissive default, which the output states plainly.
- Scoring carries the hard-won fixes from the private engine: UTF-8 throughout (emoji and accented names do not crash on Windows), direction-aware warmth (a real incoming reply counts as warm, a one-way send does not), recency-aware warmth (a year-stale thread is dormant, not hot), title demotions (analysts, front-line "advisors", and property agents do not inflate to decision-maker), and a separate pending-invitations list.
- Free plan only. No scrapers, no paid tools, no API calls. Message content is never read - metadata only. Output files (HTML, CSV, JSON, compact digest) are written outside any repo, each with a "keep this local, do not commit" header. Nothing is sent; the outreach is manual by design.

### Fix - `scrape.py` imports fail clearly on a clean machine

`scripts/scrape.py` imported `httpx`, `selectolax`, and `tenacity` at module level, so a fresh machine without them threw a raw `ModuleNotFoundError` while the `web-fetch-extract` skill documents that it "errors clearly" and falls back to `WebFetch`. The three imports are now guarded with a one-line install hint and a clean exit, matching what the skill promises.

## v1.33.0 - 2026-05-29

v1.33 is the completeness and clean-release pass over the public product. No new skills. The work makes the existing 58 self-contained, installable from a clean clone with nothing missing, and consistent across every surface a reader checks. It also adds two CI guards so the kinds of drift this pass fixed cannot return silently.

### Fix - install completeness (a fresh clone now scaffolds a working brain)

Two source files the setup wizard relied on were never named in its copy steps, so a fresh install was quietly missing them:

- `scripts/_common.py` - the shared helper that `wiki-build.py` and `query.py` both import. Without it, `/wiki-build` and `/query` failed with `ModuleNotFoundError` on first run. It is now first in the scripts copy list, and the scaffold tree names it.
- `.claude/hooks/session_start_brief.py` - the Python helper that `session-start-brief.sh` calls on Linux and Mac to compute the staleness, decay, and tip sections of the brief. It is now in the hook copy list. The PowerShell hook already inlined this logic, so Windows installs were unaffected.

The wizard also wires the privacy guard now instead of only copying it. A fresh `git clone` does not inherit `core.hooksPath`, so the pre-commit private-name blocker sat dormant until the operator wired it by hand. The wizard now runs `scripts/install-git-hooks.sh` (or sets `core.hooksPath` on Windows) so the guard is live on install, and reminds the operator it stays inactive until they add at least their own name to the pattern file.

### Fix - count truth across every surface

The skill count had drifted to "52" in four current-state statements (`README.md`, `skills/index.md`, `CLAUDE.md`, `docs/tools-and-mcps.md`) while the real count is 58. All four now say 58. Historical counts in the changelog and the recent-versions block are release records and stay as written.

### Feature - the menu leads with your profile variant

`scripts/menu.py` now reads `core/profile.md` and, when a variant is set, surfaces that variant's lead capabilities ahead of their peers within the same tier. A state-urgent suggestion still wins; the variant only orders the rest. The engine stays deterministic with no model call, and the weighting is a no-op on installs without a profile, so behaviour is unchanged where no variant is set.

### Docs and cross-agent

- `GEMINI.md` added at the repo root as a thin bridge for Gemini CLI, pointing back to `CLAUDE.md` as canonical and `AGENTS.md` as the full cross-agent reference.
- The profile layer is now narrated where a new reader meets it: the README setup ladder, `docs/first-day.md`, and the `CLAUDE.md` "How It Works" section all describe variant detection and the seeded day-one brain.

### Guards - CI doc-parity and install-completeness

Two stdlib-only checks now run in CI on every push and pull request (`.github/workflows/doc-parity.yml`):

- `check_doc_parity.py` fails the build when a skill or command count drifts out of sync across the shipped surfaces. This is what would have caught the "52 skills" drift.
- `check_install_completeness.py` fails when the wizard references a missing source or omits a script or hook a fresh install needs. This is what would have caught the `_common.py` gap.

The test suite is gitignored and maintainer-local, so it is not in a CI checkout; these guards check only what ships, and the local `test_readme_invariants.py` still owns the test-count claim.

### Writing style

Em dashes removed from `CHANGELOG.md`, `CONTRIBUTING.md`, and `docs/forking.md`. Two banned-verb usages and one banned-noun usage replaced across `brand-voice-interview`, `verify`, and `skills/index.md`.

### Cross-cutting

VERSION bumped to `1.33.0`. Skill count (58) and command count (33) unchanged. Test count `596 -> 611`: a variant-map test for `profile-router` and profile-weighting tests for the menu. `founder-os-playbook.html` re-rendered via renderer-flow (the drift check returned no drift before the version bump) and a version-tagged `founder-os-playbook-v1.33.0.html` emitted.

### Post-release correction (2026-05-30)

- **Manifest version fields corrected from 1.32.0 to 1.33.0** in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (both `metadata.version` and `plugins[0].version`). The count-truth pass reconciled the manifest description strings but not the version fields, so a plugin install reported 1.32.0 while running 1.33.0 content. The doc-parity guard checks counts, not the version field, which is why it did not catch this.
- **Install-completeness note reworded** in `check_install_completeness.py`: `scrape.py` (web-fetch-extract) is fallback-only by policy - a plugin-repo-only deterministic helper whose skill ships an inline keyless fallback - not an install gap. It stays out of `templates/scripts/` so no founder is forced to install httpx or selectolax to run a fresh scaffold.

### Hardening (2026-05-30)

More post-release corrections on 1.33.0. No version bump, no playbook re-render.

- **Decisions phantom-count fixed.** `templates/context/decisions.md` shipped a `### Format` heading and a fenced `### [Decision Name]` example under `## Pending`, and the line-based pending-decisions counter in the SessionStart brief read both as live entries, so a brand-new install's first brief reported `Decisions: 2 pending` off the template. The format reference is now bullet fields with no `###` heading lines, so a fresh install reports zero pending decisions. Real decisions still use a `###` heading and still count. This is the same class commit `8d65990` fixed in `flags.md` and `patterns.md` but missed here.
- **Brief-cleanliness guard added** (`.github/scripts/check_brief_cleanliness.py`, wired into `doc-parity.yml`). It mirrors each brief counter against all three template families - `decisions.md`, `flags.md`, and `patterns.md` - and fails the build if any format-spec or example block would be miscounted as a live flag, decision, or past-decay entry. The intentional dated demo entries stay allowed. This stops a fourth instance of the class.
- **Version-parity guard added** (`.github/scripts/check_version_parity.py`, wired into `doc-parity.yml`). It asserts the `VERSION` file, both manifest version fields in `plugin.json` and `marketplace.json`, and the README status-line version are identical. This is what would have caught the 1.32.0 / 1.33.0 manifest drift the earlier hotfix corrected; the doc-parity guard checks counts, not the version field. The playbook sidebar version is deliberately out of scope, so a patch never forces a playbook re-render.
- **PowerShell note** added to the `founder-os-setup` privacy-guard write step: on Windows or PowerShell, write the `\b<FOUNDER_NAME>\b` pattern with the file-write tool or `Set-Content`, never a shell echo.
- Test count `611 -> 616`: the brief-cleanliness maintainer test (`tests/test_brief_cleanliness.py`). README status line updated to match.

## v1.32.0 - 2026-05-29

v1.32 makes the OS meet the human on first contact, and reconciles the skill registry so every surface tells the same truth. The headline is the out-of-box brain: the OS now reads who is operating it and what it should lead with, instead of assuming everyone is a founder.

### Feature - profile-router and the out-of-box brain (WS-G)

A new `profile-router` skill reads who is operating the OS and maps them to one of five variants - founder, career-mover, builder, student, or team-internal - then writes `core/profile.md` with the surfaces the OS should open with and the frame it speaks in. The setup wizard calls it: a new Phase 0.2.2 ("meet you where you are") states a provisional read in one line and asks for a yes, and Phase 1.1.5 finalises it once priorities and work style are known. The bootloader reads `core/profile.md` alongside `core/identity.md` at every session start, so reasoning and writing skills open with what this operator's situation needs. Nothing is locked: every skill stays available to every variant; the variant only changes what leads. The scaffold is identical for everyone; only the task differs, which is why one setup serves a founder, a job-seeker, a builder, and a student without forking into four products.

Seed brain content is now dated to the install so the first SessionStart brief is not a blank screen: the wizard date-stamps the starter flag and parked decision and plants one worked log entry, so day one shows a real Review-Due flag and a real log line.

Positioning guards applied to all new copy: the brain is the durable asset and it travels (mouth and hands swap around it), capability is explained through human analogues, and the words "governance" and "diagnostics" stay out of operator-facing copy.

### Fix - skill registry reconciled to 58 skills (WS-C / WS-E3)

The skill count was wrong and contradictory across surfaces. v1.32 reconciles it. The real count is 58 skill folders. `README.md`, `skills/index.md`, `AGENTS.md`, `docs/skills.md`, and the playbook manifest now all say 58. `skills/index.md` gains the rows it was missing for the five generic tooling skills that shipped to disk and docs earlier without registry entries (`skill-creator`, `web-fetch-extract`, `memory-pass`, `cross-link`, `github-ops`) plus the new `profile-router`. `docs/skills.md` gains the 11 entries it was missing (the five generic skills, `profile-router`, and `brand-voice-interview`, `campaign-from-theme`, `review-responder`, `log-reply`, `since-last-session`, `strategic-read`). `docs/commands.md` gains the 3 it was missing (`log-reply`, `since-last-session`, `strategic-read`). `AGENTS.md` scripts line adds `scrape`.

### Docs - playbook re-rendered at version-tagged filename

`founder-os-playbook.html` re-rendered via the renderer-flow (drift check returned A-bucket only). The render now also emits `founder-os-playbook-v1.32.0.html`, the version-tagged copy, so a shared link signals which release the reader is seeing. Skill count on the playbook updated to 58.

### Cross-cutting

VERSION bumped to `1.32.0`. README Version line and Status narrative updated. Command count (33) and test count (596) unchanged - this release adds a skill and reconciles docs; it does not add tests.

## v1.31.0 - 2026-05-26

v1.31 closes the wikilink resolver gap that v1.30 Workstream B surfaced through an `@expectedFailure` test. The fix lands one place, `scripts/query.py:find_anchor_file`. The `widget-co` test flips from `expectedFailure` to a normal pass and the operator-first contract now holds for every slug regardless of where it sorts relative to `prospects/`.

### Fix - wikilink resolver operator-first preference

When `[[<slug>]]` matches both `companies/<slug>.md` (operator) and `companies/prospects/<slug>.md` (prospect), the resolver now prefers the operator file. Before this fix, `find_anchor_file` returned the first match in sorted path order. Inside `companies/`, the `prospects/` directory sorts after slug names starting with a-o ('a'-'o' < 'p') and before slug names starting with q-z ('p' < 'q'-'z'). So the de-facto operator-first behavior from the v1.28 backlog claim held only for the first half of the alphabet; slugs starting with q, r, s, t, u, v, w, x, y, z silently routed to the prospect file. The v1.30 `widget-co` test marked the gap as `@unittest.expectedFailure` with a docstring naming the fix as v1.31 scope.

The fix replaces the early-return loop with a collect-all-matches pattern, then prefers any match that is NOT under a `prospects/` subdirectory. When no operator-side file exists, the resolver falls back to the prospect file as before. The behavior for slugs that match exactly one file is unchanged.

Lands in both `scripts/query.py` and `templates/scripts/query.py` (F38 parity guard requires byte-identical copies). The `tests/test_wikilink_operator_first.py::test_operator_first_for_widget_co` test loses its `@unittest.expectedFailure` decorator and now asserts the operator-first contract directly. 577 passed, 19 skipped, 0 failed (596 total, unchanged from v1.30 - the widget-co test simply flipped from xfail to pass).

### Cross-cutting

`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` versions bumped from `1.30.0` to `1.31.0`. `README.md` Version line and `Status` narrative updated. Skill count (52), command count (33), and test count (596) unchanged.

## v1.30.0 - 2026-05-23

v1.30 closes the deferred SessionStart hook from v1.29 and adds one polish on `/strategic-read`. The on-demand liveness reads from v1.29 now feel ambient: every Claude Code session start surfaces a one-line summary of how long since the last `/since-last-session` run, below the existing session brief. No LLM call in the hook, no marker write, no block on session start. Free-tier accessibility preserved end-to-end.

### Feature - SessionStart liveness hook

A new `session-start-liveness` hook fires on every Claude Code session start in a FounderOS install. It reads `brain/.last-session` (the marker file owned by the v1.29 `/since-last-session` skill), computes elapsed time, and prints one line below the existing session brief. Marker missing: `No prior synthesis marker found. Run /since-last-session to initialize.` Under one hour: `Less than an hour since you last ran /since-last-session.` One hour or more: `X hours since you last ran /since-last-session. Run /since-last-session for the delta, or /strategic-read for a full state-of-OS report.` Malformed marker (not parseable ISO-8601 with timezone offset): `Synthesis marker malformed at brain/.last-session. Run /since-last-session to repair.` Marker dated in the future: `Synthesis marker is in the future; ignoring. Run /since-last-session if you want to repair it.` The hook does NOT update or write the marker (only `/since-last-session` writes it). The hook does NOT call any LLM (pure file read plus integer math). The hook does NOT block session start (exits within 100ms on a reasonable filesystem). Gates on `core/identity.md` matching the existing brief, so a fresh pre-setup repo stays silent. Bash variant (`.sh`) and PowerShell variant (`.ps1`) follow the same Windows platform-guard convention as the existing brief hook. Registered as the second command pair inside the existing `SessionStart` matcher block in `.claude/settings.json`, after the brief, so the brief prints first and the liveness one-liner appears below it.

### Feature - /strategic-read section argument

`/strategic-read` now accepts an optional section key so you can scope the report to one of the five sections instead of generating all five. Valid keys: `identity`, `commitments`, `decisions`, `flags`, `next-moves`. The keys map one-to-one to the v1.29 section headers via a contract table in the SKILL body; the mapping stays coupled if the headers ever reword. Example: `/strategic-read flags` renders only the Active flags section. `/strategic-read next-moves` renders only the recommended moves. Invalid section keys print the valid list and exit; the command does NOT fall back to the full report, so a typo cannot silently broaden the surface. No-arg behavior unchanged: the full 5-section report still renders.

### Test - wikilink resolver operator-first behavior contract

A local test at `tests/test_wikilink_operator_first.py` locks the F27 CTO-review MAJOR-2 router behavior: when both `companies/<slug>.md` (operator-facing) and `companies/prospects/<slug>.md` exist for the same bare slug, `[[<slug>]]` is supposed to resolve to the operator file. The three `acme` cases pass cleanly. The test also surfaced a plan-fidelity gap: the v1.28 backlog claim that the router is "de-facto operator-first via alphabetical-within-directory sort" is only true for slugs that sort before `prospects/` lexicographically. Slugs starting with q-z (e.g. `widget-co`) hit the prospect file first. The `widget-co` case ships as `@unittest.expectedFailure` to document the gap honestly; the resolver fix is queued for v1.31 (test-only scope in v1.30 per plan). `tests/` is `.gitignore`d per v1.28; this file lives in the maintainer's local working tree and runs before each release.

### Cross-cutting

`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` versions bumped from `1.29.0` to `1.30.0`. Descriptions left untouched (no hook count or test count named there to update). `README.md` Version line and test count bumped to match (`52 skills, 33 commands, 596 tests`). `skills/index.md` `/strategic-read` skill and command rows updated to mention the new section arg; a v1.30 line added to the recent-versions block.

## v1.29.0 - 2026-05-23

v1.29 ships three on-demand liveness skills. Together they produce the "the OS knows where I am" feeling from file reads at task time, with no daemon, no SessionStart hook, no paid API. The release closes the gap between starting a session cold and orienting across the brain in one pass.

### Feature - /strategic-read

`/strategic-read` returns a 5-section state-of-the-OS report from the current file layer in one read. Sections: 1. Identity anchor, 2. Active commitments and pipeline, 3. Open decisions, 4. Active flags (with decay status per `rules/entry-conventions.md`), 5. Next 3 recommended moves. The skill reads `core/identity.md`, `context/priorities.md`, `context/decisions.md`, `context/clients.md`, `context/leads.md`, `cadence/daily-anchors.md`, `cadence/weekly-commitments.md`, `brain/flags.md`, and the last 20 entries of `brain/log.md` in that order. Missing files degrade gracefully: the section header renders with a `(missing: <path>)` line instead of fabricated content. A stale `## Today:` or `## Week of` header prepends a `STALE:` line so the reader knows to refresh cadence before acting on the synthesis. Read-only on the entire repo. Free-tier accessible: file read plus in-session synthesis, no external API call. The 5 section headers are a contract other skills may grep for.

### Feature - /log-reply

`/log-reply` ingests a pasted conversational thread (WhatsApp export, Telegram dump, email body, voice memo transcript) and routes it into the brain layer in one pass. The skill extracts participants, dates, key updates, commitments made, action items, and person or company mentions. One entry per distinct conversation lands in `brain/log.md` with an `#acted` tag and `#xref` wikilinks where the names are already in the wiki. Updates to `context/clients.md` and `context/leads.md` are proposed only; the operator confirms each before any write lands, per `rules/approval-gates.md`. Unknown names propose adding to `context/leads.md` with `Stage: Raw` per `templates/rules/entry-conventions.md`. Source format is never guessed: ambiguous pastes ask the operator to label as WhatsApp / Telegram / email / voice memo transcript. A `<private>...</private>` filter in Step 5 strips blocks the operator does not want persisted before any write. Multiple separate conversations in one paste are structured as separate log entries with their own IDs.

### Feature - /since-last-session

`/since-last-session` reports the delta since the last marker time. The marker sits at `brain/.last-session` as a single ISO-8601 timestamp; the skill owns it. Report shape: 1. Hours elapsed, 2. brain/log.md entries added since the marker, 3. Flags decayed in that window (per `Decay after:` markers), 4. Commitments now overdue from `cadence/daily-anchors.md` and `cadence/weekly-commitments.md`, 5. Files modified in `context/` (git diff names only). First run with no marker prints `No prior session found, creating marker now.`, seeds the marker, and stops. No delta report on the first run. Subsequent runs render the 5-section report and advance the marker. Skips Section 5 with `(install is not under git; skipping context/ diff)` on installs that are not under git, so the other four sections still render. A future SessionStart hook may also write the marker; the skill does not depend on the hook existing (deferred to v1.30 if needed).

### Cross-cutting

`skills/index.md` adds rows for the three new skills and three new commands. `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` versions bumped from `1.26.0` to `1.29.0`, descriptions updated with the new skill and command counts. `README.md` `Version` line and `Slash commands (N)` header bumped to match. 52 skills, 33 commands.

## v1.28.0 - 2026-05-23

v1.28 strips dev-only infrastructure off the public repo and closes one residual operator-name leak. The `tests/` directory (62 files) and the on-push pytest CI workflow are removed so plugin users no longer download 1.4 MB of test code they never run. The weekly leakage and drift audit workflow stays. A 25-name sweep across all tracked files surfaced three references to a private brand used as generic examples in `skills/brand-voice-interview/SKILL.md` and `templates/brand-voice.yml.template`, all three replaced with neutral examples in the same shape as the v1.27 cleanup of generic-example brand names. The maintainer keeps the test suite locally via `.gitignore` so parity guards continue to run before each release. No new features. No user-facing behavior change. 49 skills, 30 commands.

## v1.27.0 - 2026-05-22

v1.27 closes the last four findings from the 60-finding audit. `F38` consolidated the wiki-layer walk into one canonical helper. `F46` renumbered voice-interview phases to honest integers. `F34` removed the dangling `context/entities/` reference from the ingest skill. `F27` split the companies surface so prospects live at `companies/prospects/<slug>.md` while operator companies stay at the pre-existing path. The audit is complete. No findings remain open.

### Refactor (F38)

F38 consolidated the wiki-layer walk into `scripts/_common.py`. `scripts/wiki-build.py` and `scripts/query.py` now import `WIKI_LAYER_PREFIXES`, `wiki_layer_files`, and `normalize_wikilink_target` from one canonical helper instead of carrying near-duplicate `rglob` logic side by side. `templates/scripts/_common.py` mirrors the same helper so a fresh install gets the consolidated module. Cross-script parity is locked by `tests/test_walk_parity.py`, which runs both scripts against a controlled fixture corpus and asserts identical outputs on every commit. `tests/test_common.py` adds 15 unit tests covering the prefix set, the file walker, the wikilink normalizer, and the excluded-parts guard. `tests/test_templates_scripts_parity.py` had its allow-list for `_common.py` removed because both copies must now stay byte-identical. Skill docs `skills/wiki-build/SKILL.md` and `skills/lint/SKILL.md` point at the new module.

Empirical no-regression check on the real private OS content confirmed byte-identical `brain/relations.yaml` output: pre-refactor (`f38d6b1`) and post-refactor (`b503b74`) both produced 380 wiki links from 16 source files with zero diff lines.

### Refactor (F46)

F46 renumbered the phase headers in `skills/voice-interview/SKILL.md` and `skills/brand-voice-interview/SKILL.md` to honest integers and added operator-visible "Part X of 3" markers inside the model utterances. The pre-F46 numbering used fractional phases (`## Phase 0`, `## Phase 0.5`, `## Phase 2`, `## Phase 2.5`) that read as historical accretions rather than design intent; a maintainer or executor opening the file could not tell where one phase ended and the next began. `voice-interview` now runs Phase 1 Setup, Phase 2 Samples, Phase 3 Shaping (Q1-Q12, with Anti-examples as an H3 sub-section under the same Phase 3), Phase 4 Confirm-and-save, Phase 5 Final message. `brand-voice-interview` runs Phase 1 Setup, Phase 2 Positioning (Q1-Q13), Phase 3 Brand voice (samples + V1-V10 as a sub-section), Phase 4 Confirm-and-save, Phase 5 Visual capture (optional), Phase 6 Final message. The asymmetry (5 vs 6 phases) is documented in both SKILL bodies: brand has an extra Positioning phase because brand positioning has no equivalent file the way operator positioning lives in `core/identity.md`. Each SKILL now leads with a one-sentence marker-decision note so the next maintainer knows the integer phase numbers are for them while the three-part frame is for the operator. Two meta-comment lines were removed via the "would removing this change output?" heuristic; no question text, no schema field, no captured-language anchor was touched. One paired test edit in `tests/test_voice_interview_anti_examples.py` retargeted the only pinned phase-header assertion to the demoted H3 form so the test contract still verifies the section exists. All other test-pinned strings (Q9-Q12 prompts, the Q12 Bad/Good/Rule worked example, the storage-rule sentences, the pre-step section header, the four scan paths, the buyer-language and confirm-block labels, the four downstream skill names) survive verbatim.

### Fix (F34)

F34 removed a dangling `context/entities/<slug>.md` reference from the ingest skill. The path was named as a routing target in `skills/ingest/SKILL.md` Step 3 and Step 5, and echoed in `docs/skills.md`, but no such directory existed in templates, no other skill read or wrote there, and no install command created it. A user approving an "Entity" proposal would have hit a write into a path the OS had no convention for. The design pass (`plans/v1.27-f34-entities-schema-2026-05-22.md`) considered defining a schema and shipping a template; it landed on removal because the existing wiki nodes already cover what ingest needed to route to. The Step 3 table now lists `Person` (append to `context/clients.md`), `Decision input` (append to `context/decisions.md`), `Pattern` broadened to cover frameworks and concepts (append to `brain/patterns.md`), `Action item` (append to `cadence/`), and `Company` renamed from `Reference` and broadened to cover both existing and new organisations (append to `companies/<slug>-business.md`, propose creation if absent). Step 5's apply-bullets mirror those categories one-for-one. `docs/skills.md` was updated to match. A new `tests/test_no_phantom_entities.py` (4 tests) asserts the forbidden string does not reappear under `skills/`, `docs/`, `templates/`, `tests/`, `core/`, `cadence/`, `network/`, `roles/`, or `rules/` (allow-listing `CHANGELOG.md`, `plans/`, and the test file itself for historical mentions), and positively confirms that `skills/ingest/SKILL.md` declares the `Person` and `Company` rows and no longer declares the removed `Entity` row.

### Feature (F27)

F27 split the companies surface so the wiki has a typed location for prospects without disturbing the operator path. The pre-F27 schema used `companies/<slug>-business.md` for both companies the user runs and companies the user sells to or watches; the same fields meant different things in each case and the wizard surfaced only one template. Post-F27, operator companies stay at `companies/<slug>-business.md` (unchanged from v1.26) and prospect companies live at `companies/prospects/<slug>.md` from a new lightweight template `templates/prospect-context.template.md`. The operator path layout means no migration step is required for existing installs.

A new skill `skills/prospect-init/SKILL.md` creates the prospect file on demand: it asks 3 to 5 questions (name, sector, why tracking, current relationship stage, fit signals), confirms with the user, copies the template to `companies/prospects/<slug>.md`, and appends one line to `brain/log.md` tagged `#prospect-init`. The skill refuses to overwrite an existing prospect file and surfaces a routing question if the slug collides with an operator file. It is the prospect-side companion to `business-context-loader`, which stays operator-only.

Three downstream skills now check both paths at the call site, preferring the operator file when both exist: `skills/proposal-writer/SKILL.md` adds a two-path resolution step under pre-read item 3; `skills/client-update/SKILL.md` extends its company-context lookup the same way; `skills/strategic-analysis/SKILL.md` adds pre-read item 5 introducing company-specific context (previously absent from the SKILL body even though the wizard already advertised it as a reader). The ingest skill keeps a single `Company` routing row but names both target paths in priority order with a `prospect-init` proposal for unknown organisations the user does not run.

The `business-context-loader` description was tightened to "operator companies only" and points at `prospect-init` for prospect cases. The wizard's Phase 3.2.5 wording was clarified to call out operator-only and add a backlog item surfacing `prospect-init`. `readiness-check` Business Context bucket explicitly excludes prospect files from its count, and `docs/skills.md` was updated to reflect both paths in the ingest write-targets section plus a new `prospect-init` entry. `templates/business-context.template.md` and `templates/context/companies.md` each got a one-line note pointing at the prospect template.

A new test file `tests/test_companies_path_split.py` (22 tests) covers the prospect template shape, operator template path preservation, prospect-init skill declarations, two-path declarations across the three downstream skills, operator-first textual priority, ingest reconciliation with both paths, companies-index template pointer, and a `UserTruthFilesystemTests` class that simulates a fresh install in a `tmp_path`, copies the template, writes a prospect file, and asserts the destination path matches `companies/prospects/<slug>.md` with no operator collision. `tests/test_no_phantom_entities.py` was extended with a positive assertion that the ingest Company row names the prospect path (one extra test, total 5 in the file).

49 skills, 30 commands, 411 tests pass.

## v1.26.0 - 2026-05-22

Polish patch on the 60-finding audit. Six findings closed across two workstreams. Three findings (F27, F34, F38, F46) deferred to a v1.27 design plan because they need design work, not polish.

### WS1 mechanical polish (F45, F47, F35)

`F45` consolidated seven Python heredocs in `.claude/hooks/session-start-brief.sh` into a single subprocess that calls a new `.claude/hooks/session_start_brief.py` module emitting `@@SECTION` markers the bash script parses with awk. Output is byte-identical. Measured Windows session-start latency dropped from ~2.35s to ~0.45s, about a 5x improvement. The PowerShell variant `.claude/hooks/session-start-brief.ps1` already runs all date math and tip rotation in native PowerShell, so no parity edit was needed there.

`F47` reordered the preflight inside `run_index_mode` in both `scripts/query.py` and `templates/scripts/query.py` so the common-case token check fires before the edge-case empty-corpus walk. The two copies remain byte-identical, guarded by the parity test added in v1.25.3. A new test `test_common_case_preflight_runs_before_edge_case` exercises the common-case path and asserts that an empty root with a token-less question hits the token-check exit code, not the no-files exit code. If the order ever flips back, the test fails.

`F35` closed as a no-op. The audit finding described a contradiction between `templates/bootloader-claude-md.md` and the queue skill frontmatter. On inspection, the bootloader has no queue reference at all, and the queue skill is correctly on-demand (frontmatter triggers on natural-language phrases). The SessionStart hook reads `cadence/queue.md` to print a one-line brief summary; that coexists with on-demand skill invocation by design. Recorded here so the audit's after-state matches the artifact.

### WS2 short decisions (F25, F28, F36)

`F25` added a soft identity preflight to `priority-triage` and `unit-economics`. Both skills now run `python scripts/check-identity-ready.py` before producing output. On exit code 1, the returned line surfaces as a one-line note above the result and the skill continues. Output is still produced without identity set up, but the user gets told the recommendation gets sharper after `/founder-os:setup`. This is a softer pattern than the blocking preflight in `meeting-prep` because triage and math work without identity, they just work less well.

`F28` renamed `<HARD-GATE>` to `<Instruction-gate>` across eight files: `pre-send-check`, `pre-meeting`, `update`, `campaign-from-theme`, `brand-interview`, `brand-voice-interview`, `voice-interview`, and `review-responder`. The old label implied a runtime-enforced gate, but the tag is markdown decoration the model reads, not a script that exits non-zero on violation. The new name is honest about what the construct does. The body of the pre-send-check gate was also softened from "hard stop" to "instructional stop, not a runtime-enforced one - but treat it as a hard stop in your own behavior" so the honesty extends past the tag itself.

`F36` added an explicit `N/A` branch to Check 6 of `pre-send-check`. Some deliverables genuinely trigger no internal updates (a one-off thank-you, a reply to a known thread, a personal note). Marking those as PASS or FAIL was wrong; PASS implied a cross-reference was identified and queued, FAIL implied one was missing. The output format and the "one FAIL = HOLD" rule were updated so N/A is valid on Check 6 only.

### Deferred to v1.27

Four findings need design work, not polish, and are out of scope for v1.26: `F27` (`companies/<slug>-business.md` semantic split between prospects and operator businesses), `F34` (`context/entities/<slug>.md` schema or removing the ingest reference to it), `F38` (`wiki-build.py` rglob narrowing to mirror the query.py walking pattern), and `F46` (voice-interview phase split clarity).

48 skills, 30 commands, 366 tests pass.

## v1.25.3 - 2026-05-22

Closes a 60-finding audit run that surfaced bug clusters across the wizard, runtime, tests, and documentation surface. Bug-fix release. No new features. Every finding is either closed in code or closed by design with a test docstring update so the same item does not re-flag next audit.

### Templates/scripts payload parity

The `scripts/` directory at repo root and `templates/scripts/` (the payload the wizard copies to a fresh install) had drifted. Several scripts existed only in the repo root and never landed on a real install. `user-prompt-capture.py`, `check-private-names.py`, and `private-name-patterns.txt.template` now ship in `templates/scripts/`. Three other scripts (`menu.py`, `observation-rollup.py`, `brain-snapshot.py`) were out of sync and have been re-synced to the live versions. The wizard's copy list now references fourteen scripts and the hook-copy step references eight files. The durable guard for this is `tests/test_templates_scripts_parity.py`, which fails if any script lives in one location but not the other. Future drift gets caught at test time, not on a user's machine.

### Wizard placeholder substitution

Three placeholder gaps were leaving literal `{{FOUNDER_NAME}}` and `{{COMPANY_NAME}}` markers in installed files. The wizard now substitutes `{{FOUNDER_NAME}}` across the bootloader CLAUDE.md, the global CLAUDE.md, `core/identity.md`, and the avatar template. `templates/companies/business-context.template` had a name-mismatch (`{{COMPANY}}` vs `{{COMPANY_NAME}}`) that is now aligned. A universal `{{...}}` to `[NOT SET]` pass runs after every template copy so a half-substituted template never reaches the user as a literal placeholder. `uninstall.sh` drops the dead `HOOKS_TARGET` block left over from the v1.24.1 curl-installer cleanup. `update.md` and `uninstall.md` layer matrices were inconsistent on three rows (companies, MEMORY, notion-package) and now agree.

### Runtime correctness fixes

PowerShell hooks now read files with `-Encoding UTF8` so Windows machines on `cp1252` no longer mangle banner characters. The repo's `.githooks` scripts probe `python3` then fall back to `python`, fixing the case where a Windows install has only `python` on PATH. Sixteen skills that called out to `python scripts/*.py` were missing `allowed-tools` frontmatter and have been added; without the field, Claude Code could not register their tool surface. `brand-interview` and `your-deliverable-template` now route per-brand asset paths correctly when multiple brands exist. `install.sh` handles non-interactive stdin (the `curl | bash` install path), so update prompts no longer hang. `observation-rollup.py` uses `shutil.move` for cross-device safety. `private-name-patterns.txt.template` now ships starter examples and the wizard offers to auto-write the founder's name. `check-private-names.py` exits 1 when `git` fails instead of silently passing. `install-git-hooks.sh` verifies hook files exist before setting `core.hooksPath`. The `audit` skill declares `Agent` in `allowed-tools` so its parallel-dispatch path works on a fresh install.

### Test hardening against vacuous patterns

A pass through the test suite caught five tests that asserted weaker properties than their names implied. `test_all_seven_template_scripts_exist` was renamed to `test_all_fourteen` and now asserts the new 5 scripts plus the 2 that previously existed. `test_vague_phrase_is_gone` is now case-insensitive so it catches "Find" as well as "find". `test_skill_catalogue` had a regex that returned `None` silently when `skills/index.md` changed shape; it now fails loudly. `WikiBuildIdempotencyTests` now asserts edge presence before testing idempotency, so a broken extractor that produces zero edges can no longer pass the idempotency check. `email-drafter` has an explicit fallback to operator voice with a new gate-coverage test. A new test (`test_python_callers_declare_bash_in_allowed_tools`) asserts that every `SKILL.md` calling `python scripts/` declares `Bash` in `allowed-tools`. That test caught four surprise bugs in `client-update`, `linkedin-post`, `proposal-writer`, and `your-voice` skills that had been silently mis-declared.

### Documentation surface alignment

Eighteen documentation and surface-prose claims were out of date or contradicted by what the product actually does. README and AGENTS skill+command counts move from 45/27 to 48/30 to match the v1.25.0 brand-voice additions. README gains a welcome qualifier block matching the v1.25.2 banner (not team-shared, not always-on). Six-bucket alignment now reads the same across `readiness-check`, `status.md`, and `docs/commands.md`. The three new brand commands are listed in `docs/commands.md`. The legal-compliance domain count drops from 10 to 9 in the README to match the actual skill body. `CONTRIBUTING.md` replaces its `ROADMAP.md` reference with `docs/forking.md` (ROADMAP was removed in v1.24.1). `campaign-from-theme` had the banned word "optimized" in its body, which is now replaced. The setup skill's template inventory now lists all five missing top-level templates. `templates/identity.md` gains a jurisdiction placeholder. The `today` skill picks up the Day-1 setup gate so a fresh install does not hit a confusing empty view. `strategic-analysis` ships a Business Model Evaluation template that was referenced but missing. `session-handoff` drops a dead Notion MCP declaration. `ship-deliverable` defines writing-style precedence. `observation-rollup`'s description matches its per-week body rule. `today`'s description now includes "open decisions". The `verify` command's count is corrected from five to seven scripts to match what it actually checks. `skills/index.md` is version-stamped v1.25.3.

### F59 closed by design

Four `<!-- private-tag: not applicable -->` markers in skill files were flagged in the audit as potential private-tag leakage. They are not leakage. They are required infrastructure: `tests/test_private_tag.py` walks every skill and expects either a `<private>...</private>` block or an explicit "not applicable" comment so the audit cannot silently miss a skill. The markers stay. The test docstring is updated to explain the exemption so the same finding does not re-flag in a future audit.

### F20 and F41 honest deviations

F20 (templates/scripts parity comment pointers) was already correct in both files. No change was needed and none was made. F41 (a doc claim about brand routing) lived in `README.md`, not `CLAUDE.md` as the audit plan stated. Fixed in `README.md` line 174. Both are recorded here so the audit's after-state matches the artifact.

48 skills, 30 commands, 365 tests pass.

## v1.25.2 - 2026-05-21

Closes the install-handshake gap introduced in v1.25.1 and ships the cluster of fresh-install bugs surfaced by a full skills and scripts audit. v1.25.1 added "set up my second brain" as a natural-language trigger but the wizard then ran the same generic interview, leaving users who arrived via the second-brain phrasing with a mental model the product does not deliver. v1.25.2 closes the promise-vs-reality gap at the handshake and fixes the audit findings.

### Wizard Phase 0.0 reframe

`skills/founder-os-setup/SKILL.md` now runs a Phase 0.0 step before Phase 0 discovery starts. The wizard opens by naming what the user is getting (personal second brain - files on their machine, queryable by them across sessions) and what it is not yet, by design (not team-shared, not always-on). The user must acknowledge the frame before discovery begins. Users who arrived via "set up Founder OS" benefit from the reset too because the term is ambiguous to first-time readers.

### Welcome banner qualifier

`.claude/hooks/session-start-brief.sh` and `.claude/hooks/session-start-brief.ps1` add one qualifier line under the alternative phrasings: "Your personal brain - your files, queryable by you. Not team-shared. Not always-on." Readers of the banner who do not then trigger the wizard still see the truth of what the product delivers.

### Bootloader routing note

`templates/bootloader-claude-md.md` adds a one-line note to the first-time setup routing block explaining that the wizard opens with Phase 0.0 framing.

### Five preflight scripts now ship to fresh installs

The setup wizard's "scripts copy step" only copied seven Python helpers from `templates/scripts/`. Five preflight gate scripts (`check-voice-ready.py`, `check-brand-voice-ready.py`, `check-identity-ready.py`, `check-log-has-history.py`, `list-brands.py`) lived only in the repo's `scripts/` and were never copied. Every voice-coupled writing skill and every reasoning skill called these scripts and silently failed on fresh installs. All five now live in `templates/scripts/`, the wizard's copy step references twelve scripts, and the file-tree representation in Phase 2.2 lists them.

### Company-context path alignment across four skills

`readiness-check`, `proposal-writer`, `client-update`, and `ingest` all looked in `context/companies/<name>.md` for the per-company context file. The setup wizard and `business-context-loader` write to `companies/<slug>-business.md`. The four consumer skills now read from the producer's actual path. Effect: the 15% Business Context score now reflects real installs, and `proposal-writer` reads the prospect's context file instead of silently shipping a generic draft.

### Dead `/identity-interview` command replaced

The `readiness-check` Day-1 and "not set up" blocks recommended `/founder-os:identity-interview`, which does not exist. Both blocks now recommend `/founder-os:setup` (which captures identity) followed by `/founder-os:voice-interview` and `/founder-os:brand-interview`. A regression test guards against the dead command coming back.

### `email-drafter` `allowed-tools` added

The skill was missing the `allowed-tools` frontmatter field while declaring write behavior in the body. Added `allowed-tools: ["Read", "Write", "Edit", "Bash"]` so Claude Code can enforce the tool surface and so the skill registers correctly in plugin contexts.

### `$matches` automatic-variable collision in PowerShell hook

`.claude/hooks/session-start-brief.ps1` was assigning user data to `$matches`, PowerShell's session-global automatic variable. Renamed to `$rantMatches` to remove the collision risk in the unprocessed-rants block.

### `datetime.now()` race in `user-prompt-capture.py`

The rant-capture script called `datetime.now()` twice (once for the filename date, once for the frontmatter timestamp). A prompt submitted at midnight could land in yesterday's file with today's timestamp. Both values now derive from a single `datetime.now(timezone.utc).astimezone()` call.

48 skills, 30 commands, 359 tests pass.

## v1.25.1 - 2026-05-18

The setup wizard now fires on the phrasings a non-technical user would actually try first. v1.25.0 added the brand voice layer; v1.25.1 closes the trigger-surface gap so the founder does not have to know the magic phrase "set up Founder OS" to start.

### Expanded onboarding triggers

`.claude/commands/setup.md` and `skills/founder-os-setup/SKILL.md` descriptions now match: "set up my second brain", "help me set up my second brain", "help me onboard", "onboard me", "what do I do", "where do I start", "how does this work", "I'm new", "get me started" - alongside the original "set up Founder OS" / "install Founder OS" / "run the setup wizard".

### Welcome banner shows the alternative phrasings

The SessionStart brief on a fresh install (no `core/identity.md`) now lists three alternatives so the user sees their own words reflected back instead of having to guess. Both bash and PowerShell hook variants updated for parity.

### Bootloader teaches first-time routing

`templates/bootloader-claude-md.md` gets a new `## First-time setup routing` section. When `core/identity.md` is absent AND the user uses any of the trigger phrasings, route to the `founder-os-setup` skill without improvising. When `core/identity.md` exists, the same phrasings route as normal OS queries.

48 skills, 30 commands, 358 tests pass.

## v1.25.0 - 2026-05-18

The brand voice layer. Before this release, every voice-coupled writing skill assumed a single voice - the operator's. That works for an individual founder writing their own LinkedIn posts and emails. It breaks for an operator who runs an ecosystem of brands: a marketing manager managing several group brands, a founder with a personal voice that is not the brand voice, an agency where each client has its own brand register. v1.25 introduces a second voice layer that lives independently of the operator's personal voice. Writing skills route to the right one based on what the task asks for.

### Brand voice layer

New directory: `brands/<slug>/`. One folder per brand the operator runs. Each holds three files:

- `voice.yml` - how the brand writes. Same structure as operator voice (rhythm, opening style, banned words, anti-example pairs, samples), plus a `register` field (`plain-direct` / `measured-elegant` / `corporate-restrained` / `friendly-casual`) and a `speaker` field (`brand` / `founder-led` / `spokesperson-led`).
- `positioning.yml` - who the brand serves, what it sells, ICP, audience pain language, proof points, refused promises, regulatory forbidden claims, channel mix.
- `visual.yml` - per-brand visual identity (colors, fonts, logos). Same schema as the existing `core/brand-profile.yml`, scoped to one brand. Includes a new `ai_humans_allowed` flag for brands that forbid AI-rendered people in creative.

Captured via `/founder-os:brand-voice-interview`. One run per brand. Backward-compatible: if `brands/` does not exist, every existing skill behaves exactly as it did in v1.24.

### Three new skills

- **`brand-voice-interview`** - interactive interview that walks brand positioning first, then brand voice (samples first, shaping questions after). Captures both voice and positioning so campaign-from-theme and review-responder have what they need. Offers to chain into `brand-interview` for visual identity at the end.

- **`campaign-from-theme`** - turns one theme into a sequenced marketing campaign. Refuses to produce content until the operator answers five gate questions: speaker (operator or brand), objective (awareness / consideration / conversion / retention / advocacy), audience segment AND temperature (cold / warm / customer), channel-fit logic, and success metric. Output is a brief with sequencing rationale and 3 to 7 content drafts. The gate is the value - it forces audience and objective clarity that industry-standard generators skip.

- **`review-responder`** - drafts replies to incoming customer messages: Google reviews, Trustpilot, Instagram DMs, WhatsApp inquiries, customer emails, Facebook comments. Asks whose voice (operator or brand), what channel (sets length budget and formality), and what posture (warm thank-you, careful negative, factual answer, soft sell, de-escalation, reactivation). Outputs a draft in the right voice with public-reply awareness for review platforms.

### Voice routing in existing writing skills

Five skills now route between operator and brand voice based on task context:

- `linkedin-post`
- `email-drafter`
- `client-update`
- `content-repurposer`
- `proposal-writer`

Routing rules live in `your-voice/SKILL.md` and apply across all five. The decision is made by signal order: explicit brand mention in the user's request, explicit personal mention, channel-implies-brand, otherwise ask. Operators with one brand and a brand-oriented task get the brand voice picked silently with a one-line preamble in the output. Operators with multiple brands always get asked.

### Anti-AI baseline with brand registers

The universal anti-AI baseline (no em dashes, no rule-of-three, no negation-contrast, no banned phrases like "in a world where") remains the hard floor. Brand register relaxes a small set of allowances on top:

- `plain-direct` - no changes. Universal baseline applies as written.
- `measured-elegant` - allows craft vocabulary (considered, heritage, tailored) if in preferred_words. Slightly longer rhythm allowed.
- `corporate-restrained` - allows hedging language and formal sign-offs. Contractions usually off.
- `friendly-casual` - allows contractions always, one exclamation mark per piece, first-name greetings.

The banned-phrase list does not change per register. Registers add small allowances, never remove the floor.

### Brand-aware channel selection

`content-repurposer` now reads brand positioning when brand voice is loaded. Suggests only channels in `positioning.channels.primary` + `secondary`. Excludes `channels.off_limits` (e.g. a premium brand that refuses TikTok). Surfaces conflicts when the user asks for an off-limits channel.

### Three new templates

- `templates/brand-voice.yml.template`
- `templates/brand-positioning.yml.template`
- `templates/brand-visual.yml.template`

### Two new helper scripts

- `scripts/list-brands.py` - discovers brands under `brands/<slug>/`, reports each with voice + positioning readiness status. Used by writing skills to know what brands exist. Exits 0 with no output if no brands set up, so old skills behave unchanged.
- `scripts/check-brand-voice-ready.py` - mirror of `check-voice-ready.py` scoped to a single brand by slug. Used by writing skills before producing brand-coupled output.

### Three new commands

- `/founder-os:brand-voice-interview`
- `/founder-os:campaign-from-theme`
- `/founder-os:review-responder`

Skill count rises from 45 to 48. Command count rises from 27 to 30.

## v1.24.1 - 2026-05-18

Three end-to-end gaps that would have surfaced on a fresh clone. None changed visible behavior on existing installs. All three close paths where a new user would have hit a silent half-result and not known why.

### Setup wizard ships a valid weekly heading

`templates/cadence/weekly-commitments.md` has a `## Week of {{WEEK_START_DATE}}` heading that the SessionStart brief greps for and `/founder-os:verify` Check 7 validates. The setup wizard had explicit substitution rules for `{{role_noun}}`, `{{TODAY}}`, and `{{DATE}}` but missed `{{WEEK_START_DATE}}`. Without the rule, the literal placeholder stayed in the file and the weekly cadence line silently disappeared from every session brief on Day 1. v1.24.1 adds the missing rule in Phase 2.2 and tells the wizard to replace residual `{{...}}` markers in the weekly file with `[NOT SET]` so a half-substituted template never ships.

### Curl installer no longer copies hooks to a useless location

`install.sh` was copying hook files to `~/.claude/hooks/` after the clone. From that location the hooks resolved their repo path as `$HOME` and silently no-opped, and they were not registered in any `~/.claude/settings.json` so nothing fired them anyway. `docs/install.md` already documented that curl-install (Path E) hooks only fire when Claude Code is opened in the install directory, so the global copy was dead code that misled users. v1.24.1 removes the hook-copy block and the orphaned `HOOKS_TARGET` constant, then updates the "Next step" message to `cd $TARGET && claude` followed by `Say "set up Founder OS"`. `docs/install.md` step 3 was also stale on this behavior and is now aligned.

### Discovery test no longer false-positives on client-update

The `<private>` discovery test in `tests/test_private_tag.py` matches any skill that uses an update or write verb within 80 characters of `brain/`, `context/`, `MEMORY.md`, or `stack.json`. `skills/client-update/SKILL.md` matched the regex but writes client-facing deliverable drafts, not user speech to state files. The test docstring already supported an exemption marker for structured or computed writes. v1.24.1 adds the exemption to client-update so the full suite is clean.

### ROADMAP removed from the public repo

`ROADMAP.md` was a drift target. Historical release counts had already been mechanically patched with current counts at least once. CHANGELOG.md is now the single source of truth for what shipped, and `docs/forking.md` covers extension points. The file is gitignored so a re-created local copy does not accidentally land back in the public repo.

45 skills, 27 commands, 358 tests pass.

## v1.24.0 - 2026-05-15

Before this release, if you asked a writing skill to draft something without your voice profile set up, it would produce a generic draft - and it would do so silently, without telling you it was working blind. v1.24 changes that. Writing and reasoning skills now run a Python preflight before they produce anything. If a required file is missing or still contains template placeholders, the skill stops and tells you exactly why in one line. You can say "proceed anyway" and get a draft that's clearly labelled as running without your data. The label is the point.

### Voice gate

`scripts/check-voice-ready.py` runs before any voice-coupled output: LinkedIn posts, emails, client updates, proposals, and repurposed content. If `core/voice-profile.yml` is missing or still has template defaults (`[CHOOSE`, `[NOT SET]`, `{{`, `[example:`), the skill stops. If you want a draft anyway, say so - you get one that's labelled as using Claude defaults rather than your voice.

### Identity gate

`scripts/check-identity-ready.py` runs before reasoning skills: weekly review, decision framework, meeting prep, and strategic analysis. These skills reason from your actual situation. Without `core/identity.md` filled in, they would reason generically. The gate stops them and prompts setup.

### Log history gate

`scripts/check-log-has-history.py` runs before brain-pass and before the LinkedIn skill's brain-context step. On a fresh install with no dated entries yet, brain-pass skips the log search rather than returning confusing no-content results. Once you have real history, the gate passes and the full search runs.

These gates exit in code. The model cannot drift past an exit code the way it can drift from a prose instruction. Nine new tests document exactly what "ready" means for each gate. Full suite: 335 tests, all pass.

### Skill reliability table

Run `/founder-os:verify` to see every writing and reasoning skill mapped to its gate type - Python-enforced (deterministic) or instruction-only (model-dependent). `docs/calibrating-your-os.md` explains what that distinction means in practice. If you want to test a specific instruction-only skill yourself, the doc includes a five-step trace recipe: a spec, three to five real inputs, and 30 minutes per skill. No framework, no API call required.

45 skills, 27 commands, 335 tests.

## v1.23.1 - 2026-05-15

Three hardening patches shipped together.

**Privacy on shared machines.** If your OS folder lives somewhere that gets synced, backed up, or eventually forked, your brain and context files may contain names and paths that should stay local. `scripts/check-private-names.py` lets you define a list of patterns to protect. Any staged diff or commit message that matches a pattern blocks the commit before it goes out. Git hooks for pre-commit and commit-msg install with one command (`scripts/install-git-hooks.sh`). Your patterns file is gitignored - only a blank template is tracked, so the list stays on your machine. Five tests in `tests/test_private_name_hook.py`.

**Capture precision.** The v1.23 capture hook used proximity matching - a capitalized name within 80 characters of a meeting verb was enough to trigger a log suggestion. That was too loose. "I called the Python function", "I had a meeting with the Marketing team", "I spoke to God this morning" all fired. v1.23.1 requires three signals in the same sentence: a preposition after the meeting verb (with / to / from), the candidate name within 30 characters, and a first-person token (I / we / me / my). All three must be present. 12 behavioral tests and an 80-line annotated corpus (`tests/fixtures/founder_utterances.txt`) verify the gate holds.

**CI on three platforms.** Every push now runs `python -m unittest discover tests -v` across Ubuntu, macOS, and Windows on Python 3.11 and 3.12. Tests badge is in the README. The matrix confirmed the suite is clean cross-platform before this release shipped.

326 tests.

## v1.23.0 - 2026-05-15

FounderOS is built around capture. But before this release, capture only worked if you knew the slash commands. If you just talked - the way a founder actually uses a tool when they are in flow - nothing was captured. v1.23 closes that gap.

### Added - natural-language capture path

- **`.claude/hooks/user-prompt-capture.sh` + `.ps1` + `scripts/user-prompt-capture.py`** - new UserPromptSubmit hook wired in `.claude/settings.json`. Classifies every prompt against four shapes: rant (long, first-person, not a question), named-entity (capitalized name near a meeting verb), status update (first-person + completion verb), preference utterance ("from now on" / "I prefer" / "always X" / "stop doing Y"). Emits a `[capture-suggestion]` system note Claude honors before responding. Free-tier accessible. Stdlib regex only. No LLM call.
- **Eager rant capture.** Rants are written to `brain/rants/<date>.md` immediately with `processed: false` and `mode: unknown`, so the text is safe on disk even if the user walks away before answering the routing question. `<private>...</private>` blocks are stripped before writing. Closes the v1.22 silent-loss path where wall-of-text rants without `/rant` evaporated.
- **`templates/bootloader-claude-md.md`** - capture-routing block added at the top of operating rules. Lists the four signal shapes and how to honor them. Bootloader installs as the user's CLAUDE.md, so this routing reaches every new install.
- **`.claude/commands/rant.md`** - inverted from qualify-first to capture-first. Step 1 unconditionally writes to `brain/rants/`; Step 2 offers routing; Step 3 acts on the answer if given. If the user walks away, the rant is already saved.

### Added - discoverability

- **SessionStart welcome banner.** When `core/identity.md` is missing and a Founder OS marker is present, the brief prints a banner pointing the user to natural-language setup. Bash and PowerShell variants both ship. Stops the silent Day-0 failure where a fresh install saw nothing on first session open.
- **Unprocessed-rant count in SessionStart.** Always-on line in the brief when rants with `processed: false` exist. Prompts `/dream` when N >= 3. Closes the v1.22 gap where rants accumulated indefinitely until `/audit` flagged them at 30 days.
- **`scripts/menu.py`** - new `dream` capability surfaces in the capability menu only when unprocessed rants exist.

### Added - operator vocabulary

Description triggers extended on five skills so users do not need to know OS-internal names to be routed:

- **`skills/brain-log/SKILL.md`** - now recognizes "journal entry", "note to self", "diary", "log to journal", "I decided", "I made a decision", "decision: <text>".
- **`skills/weekly-review/SKILL.md`** - "my schedule", "this week's plan", "what am I working on this week".
- **`skills/priority-triage/SKILL.md`** - "my goals", "what are my goals", "show my goals".
- **`.claude/commands/capture-meeting.md`** - "I had a call with", "I spoke to", "I got a reply from", "heard back from", "they replied".
- **`templates/bootloader-claude-md.md`** + **`skills/founder-os-setup/SKILL.md`** - vocabulary map ("journal" -> brain-log, "schedule" -> cadence, "customers" -> clients, "goals" -> priorities) lands in both the bootloader and the setup orientation.

### Polish

- **`scripts/user-prompt-capture.py`** - named-entity detection now requires (a) the candidate not to be in a stop-list of common title-case nouns (months, days, tech brands, AI brands, founder-stack tool names, sentence-start verbs, kinship terms, internal departments, religious and cultural occasions) and (b) the candidate to appear within 80 characters of the meeting verb. Stops prompts like "I just called Python from my bash script", "I had a call with Notion's API team", "I called Mom yesterday", and "I spoke to Marketing this morning" from firing a capture suggestion.
- **Install phrase consistency.** `install.sh`, `README.md`, and `docs/install.md` now use "set up Founder OS" (two words), matching the documented trigger in `skills/founder-os-setup/SKILL.md`. The one-word variant "set up FounderOS" was untriggered.
- **`docs/install.md`** - curl-install path no longer claims hooks "fire on every session." New "How hooks fire on Path E" section explains that Path E hooks fire only when Claude Code is opened in the cloned folder; use Path A for hooks that activate everywhere.
- **CLAUDE.md, AGENTS.md, docs/tools-and-mcps.md** - skill and command counts caught up to current state (45 skills, 27 commands; `observation-rollup` row added to CLAUDE.md skill table; UserPromptSubmit hook listed in AGENTS.md hooks section).

### Tests added

- **`tests/test_user_prompt_capture.py`** - 21 tests covering `detect_shape` per fixture (rant, named-entity, status update, preference, none), stop-list filtering across 5 categories (tech brands, days/months, kinship terms, internal departments, religious/cultural occasions), proximity requirement, slash-command bypass, eager-rant frontmatter shape, private-tag filter, idempotent prepend on same-date file, malformed JSON envelope handled silently, no Founder OS install -> exit silently, named-entity is suggest-only and does not write.
- **`tests/test_session_hooks.py`** - 2 new tests for the v1.23 welcome banner: fires when `core/identity.md` is missing AND a Founder OS marker is present; does not fire when `core/identity.md` exists.
- **`tests/test_install_scripts.py`** - assertion updated for the "set up Founder OS" phrase.

45 skills, 27 commands, 297 tests (11 platform-skipped).

## v1.22.0 - 2026-05-14

Four tracks shipped together in the build-out session before the public release.

**Skill audit.** All 44 skills reviewed: 42 kept as-is, 2 improved. The `today` skill description was rewritten to describe output the user sees rather than implementation details. `approval-gates` now responds to "do I need approval for this" so the gate is discoverable by asking a natural question.

**Setup wizard adapts to your role.** The wizard now asks whether you are a founder, operator, or team-of-one. Positioning questions and menu capabilities branch by role. B2C operators get a subscriber-list option on the CRM prompt. The primary marketing channel you declare during setup routes the menu toward relevant content skills.

**Privacy tag.** Wrap any text in `<private>...</private>` and it is stripped before FounderOS writes anything to disk - brain-log, knowledge-capture, rant files, dream processing, auto-memory. Case-insensitive. Closes the gap where a rant or log entry might contain context that is useful in the moment but should not survive the session.

**Observation rollup.** `scripts/observation-rollup.py` compresses weekly observation files once a week has at least 7 days of data and ended at least 3 days ago. Source files are deleted only after the rollup is verified written. SessionStart surfaces a nudge when JSONL files older than 10 days are waiting.

**End-to-end test coverage.** `tests/test_e2e_critical_paths.py` covers 8 critical paths: setup wizard substitution, install/uninstall dry runs, verify check states, queue 3-cap gate, brain-pass empty-corpus response, and wiki-build idempotency. CI job added to the GitHub Actions workflow.

45 skills, 27 commands, 247 tests.

## v1.21.0 - 2026-05-14

v1.20 gave you natural-language routing. v1.21 makes the OS visible. You can now see what it is working on, check whether it is healthy, and trust that writing skills draft from your current state rather than starting cold.

### Added - execution queue

- **`cadence/queue.md` template.** Three lifecycle states: ACTIVE (max 3), BACKLOG, DONE. Conventions
  block with entry shape. Created by the setup wizard from `templates/cadence/queue.md`.
- **`skills/queue/SKILL.md`.** Five operations: read, add, start, done, park. 3-item ACTIVE gate:
  starting a fourth item surfaces the three current ACTIVE items and asks which gets paused or killed.
- **`.claude/commands/queue.md`.** Single command (`/founder-os:queue`). No subcommand files.
- **SessionStart brief.** ACTIVE queue items now render first after the date header. Missing or empty
  queue shows: `Active: 0/3 (queue empty - say "add to queue: <thing>" to start)`.
- **Readiness-check Queue bucket.** 5% weight. Full credit if ACTIVE > 0 and DONE in last 7 days > 0.
- **Weekly-review queue rolloff.** DONE entries older than 7 days roll to `brain/log.md`. ACTIVE
  entries older than 14 days surface for a keep/park decision.

### Added - verify health check

- **`skills/verify/SKILL.md`.** Read-only report across 8 substrate checks: plugin surface, hooks,
  scripts, MCPs, free-tier floor, wiki integrity, cadence staleness, auto-memory presence. Each check
  returns PASS / WARN / FAIL with a one-line reason. Never auto-fixes.
- **`.claude/commands/verify.md`.** Thin trigger for the verify skill (`/founder-os:verify`).
- **README post-install.** "Say 'verify the OS' (or run `/founder-os:verify`)" added near quick-start.

### Changed - five writing skills complete snapshot wiring

`email-drafter`, `sop-writer`, `content-repurposer`, `client-update`, and `proposal-writer` now read
`brain/.snapshot.md` before drafting. Open-flags block, must-do block, and voice/brand blocks apply
if the snapshot exists. Snapshot is optional context - skill proceeds without it if missing.

### Added - multi-archetype trace pass

- **`traces/v121-maya.md`.** Full setup + voice + menu + LinkedIn + queue flow against Maya (B2C, Stillpoint meditation app, Toronto).
- **`traces/v121-dev.md`.** Same flow against Dev (ops-not-founder, Mumbai logistics). LinkedIn replaced by SOP-writer.
- **`traces/v121-gaps.md`.** 5 gaps surfaced, 1 patched in v1.21 (weekly-review balance check now
  skips for non-owner operators), 2 deferred to v1.22, 2 accepted.

44 skills, 26 commands, 182 tests.

## v1.20.3 - 2026-05-10

Your voice profile could already capture what you tend to write - rhythm, preferred words, tone. It could not capture what you would never write: the structural patterns AI models produce naturally that you find generic or off-brand. v1.20.3 adds that layer.

### Changed - voice profiles now carry anti-examples

- **Voice profile schema.** `templates/voice-profile.yml.template` now includes `voice.anti_examples` with `pairs`, `contrarian_takes`, `aesthetic_crimes`, and `red_flags`.
- **Voice interview Phase 2.5.** `skills/voice-interview/SKILL.md` adds Q9 to Q12. The load-bearing Q12 walks the user through a BAD/GOOD pair before asking for 3 to 6 of their own.
- **Writing-skill cleanup filter.** `linkedin-post`, `client-update`, `proposal-writer`, `email-drafter`, and `content-repurposer` now scan drafts against `anti_examples.pairs`, aesthetic crimes, and red flags before returning the cleaned draft.
- **Release evidence.** `traces/v1203-pre-anti-examples.md` captures Marcus's v1.20.2 drift on a new LinkedIn topic. `traces/v1203-post-anti-examples.md` shows the same topic after the anti-example filter and pairs each rewritten line with the original drift.

### Tests

- Added coverage for the anti-example filter contract in all five writing skills.
- Added coverage for voice-interview Phase 2.5, Q9 to Q12, the Q12 worked example, and the new file output structure.

## v1.20.2 - 2026-05-10

Setup, voice interview, and brand interview were useful on their own - but after running all three, the writing skills still drafted generically. The data you entered was not flowing into the output. v1.20.2 closes that gap: buyer, offer, pain, buyer language, and brand proof now feed directly into every writing skill that needs them.

### Changed - intake now feeds output

- **Setup wizard positioning.** `skills/founder-os-setup/SKILL.md` adds three skip-able questions for who the founder sells to, what they sell, and the visible buyer pain. `templates/identity.md` now has a `## Positioning` section with `Sells to`, `Sells`, and `Buyer pain`.
- **Voice interview buyer language.** `skills/voice-interview/SKILL.md` adds two questions for the buyer's own words. `templates/voice-profile.yml.template` adds `buyer_language.first_sentence` and `buyer_language.phrases`. `your-voice` and `linkedin-post` now read the field.
- **Brand interview visual proof.** `skills/brand-interview/SKILL.md` asks for existing decks, sites, logo folders, proposals, or style guides. `templates/brand-profile.yml.template` adds `existing_assets`, and `your-deliverable-template` reads those references before choosing a visual direction.
- **Rant route.** `.claude/commands/rant.md` asks one question: decision, draft, plan, or capture. It routes to `decision-framework`, the right writing skill, `priority-triage`, `forcing-questions`, `brain-log`, or the existing rants file path.

### Changed - quality gates and small release items

- **Writing-skill voice gates.** `linkedin-post`, `client-update`, `proposal-writer`, `email-drafter`, and `content-repurposer` now stop when `core/voice-profile.yml` is missing or still template-filled, then ask whether to run the voice interview or proceed with defaults.
- **Today skill wrapper.** New `skills/today/SKILL.md` hosts the natural-language trigger "what's on for today?" for surfaces where slash commands do not fire.
- **README setup ladder.** The first setup path now uses "Say X (or run Y)" for setup, voice, and brand.
- **SessionStart Tip detection.** Bash and PowerShell hooks now count only explicit `#used-<capability>` tags or `#acted` lines that name the capability, so planning notes no longer suppress a Tip.
- **Release evidence.** `traces/v1202-first-60-min.md`, `traces/v1202-gaps.md`, and `traces/v1202-post-patch.md` show the before state, patch list, and output lift.

### Tests

- Added coverage for positioning prompts, buyer-language fields, brand visual proof, routed rant behavior, writing-skill gates, and tag-based Tip detection.

## v1.20.1 - 2026-05-10

Two structural fixes from the v1.20.0 release. The menu scoring algorithm belonged in code, not in the model - `scripts/menu.py` (stdlib, no LLM call) now owns the logic. The SessionStart tip was surfacing on fresh installs with no log history; it now requires at least 10 log entries spanning 30 days before suggesting anything, so new users get useful prompts instead of capability pitches for features they have not had time to use.

### Changed - menu has a real engine

- **NEW `scripts/menu.py` (489 LOC, stdlib only).** The scoring algorithm lives here. Reads state files (`brain/.snapshot.md`, `brain/flags.md`, `cadence/weekly-commitments.md`, `brain/log.md`, `core/voice-profile.yml`, `core/brand-profile.yml`, `context/priorities.md`, `drafts/`), scores capabilities against deterministic rules, returns the top 5 to 7 with a Day-1 starter set as the zero-state fallback. No LLM call. No network call. Free-tier accessible. Renders rows natural-language-first; slash commands appear only for capabilities that have a real `.claude/commands/<name>.md` file. Skill-only capabilities (`weekly-review`, `priority-triage`, `pre-send-check`) render natural-language only and never invent a slash form.
- **`skills/menu/SKILL.md` rewritten as a thin wrapper.** The skill invokes `python scripts/menu.py` and prints stdout verbatim. The model does not score capabilities. Reason: the v1.20.0 SKILL.md said "the model running this skill IS the menu engine," which is an LLM call by definition and contradicted the plan's "no LLM call inside the algorithm" constraint. The v1.20.0 implementation also invented `/founder-os:weekly-review` and `/founder-os:priority-triage` (commands that do not exist).
- **`tests/test_menu.py` rewritten as behavioural tests (15 tests).** Runs `scripts/menu.py` against fixture roots (zero-state, populated, missing snapshot) and asserts on stdout. Covers: zero-state returns Day-1 set, populated returns 5 to 7 rows, capability-to-command map never invents skill-only slash forms, closing line verbatim, no LLM/network imports, no banned phrases or em/en dashes in rendered output, SKILL.md surface points to the script.

### Changed - SessionStart Tip fresh-install gate

- **`.claude/hooks/session-start-brief.sh` and `.ps1`.** Tip line now requires `brain/log.md` to have at least 10 entries spanning at least 30 days before any Tip surfaces. Reason: v1.20.0 surfaced a Tip on a fresh install with an empty log because "never used" counted as eligible. Fresh installs should not get pitched a capability they have not had time to use. The 14-day age filter on individual capabilities is preserved on top of the global gate.
- **`tests/test_session_hooks.py` updated.** Removed the broken assertion that empty-log surfaces a Tip. Added: empty log omits Tip, log under 10 entries omits Tip, log spanning under 30 days omits Tip, seasoned log with all capabilities recently used omits Tip, seasoned log with at least one idle capability surfaces Tip with natural-language phrasing.

### Added - setup wizard test coverage

- **NEW `tests/test_setup_wizard.py` (26 tests, 3 test classes).** Parses `skills/founder-os-setup/SKILL.md` and asserts on the 4 + 4 multi-choice structure: tool-stack prompts (knowledge base, email, calendar, CRM/pipeline), work-style prompts (deep work time, decision style, communication style, what overwhelms you), skip-records-null behaviour, parse-everything-at-once backward compatibility, allowed-values tokens preserved, downstream schema field references intact (`Decision style:` in `core/identity.md`, `Communication style:` in `rules/operating-rules.md`). Plus prose hygiene checks (no em/en dashes, no banned phrases) on the MC sections.

### Changed - skill count drift corrected

- **`skills/index.md` rewritten.** Adds the `menu` skill row that v1.20.0 missed. Adds `/founder-os:menu` to the command table. Bumps skill count to 40 and command count to 21. Adds release notes for v1.20.0 and v1.20.1.
- **`README.md`.** Every live-state "39 skills" mention updated to "40 skills." Production stamp updated to v1.20.1.
- **`.claude-plugin/marketplace.json`** and **`.claude-plugin/plugin.json`.** Both `version` fields bumped to 1.20.1. Description fields updated to "40 skills."
- **`VERSION`.** 1.20.0 -> 1.20.1.
- **`ROADMAP.md`.** New v1.20.1 entry at the top of Shipped.

### Tests

107 tests, all passing in ~58s. Up from 76 in v1.20.0. New coverage: 4 menu behavioural tests above the 11 carried forward (15 total), 3 session-hook gate tests, 26 wizard MC structural tests.

### Out of scope (deferred to v1.21)

- README setup ladder rewrite (currently leads with `/founder-os:setup` etc.; v1.21 will rewrite as "Say X (or run Y)").
- `skills/today/SKILL.md` to host the "what's on for today?" trigger phrase (currently routes via the `/today` command only).
- Tip detection switching from log substring matches to `#used` tag matches (refinement, not a P0 blocker).
- Time-awareness primitive: session-to-session continuity, message timestamps, skipped-day detection. Captured as a separate planning track.

## v1.20.0 - 2026-05-10

FounderOS now routes on natural language. Slash commands stayed but became parenthetical shortcuts. New `/founder-os:menu` returns capability suggestions tailored to your current state. The release also closes two pass-1 findings deferred from v1.19.6: `scripts/query.py` zero-score fallback returns a no-positive-match block instead of graph-popular junk, and the setup wizard's tool-stack and work-style questions become 4 + 4 short multi-choice prompts instead of two long open-ended walls.

### Changed - command and skill descriptions lead with natural-language phrasing

- **Every file in `.claude/commands/*.md` (now 21) reworked.** Frontmatter `description` field leads with the natural-language phrasing the founder would actually say in chat. The slash command appears second, parenthetically. Tool-only commands (`/founder-os:lint`, `/founder-os:wiki-build`) lead with tool framing ("Audit the wiki" / "Rebuild the wiki graph") with the slash command alongside. Pattern: "Set up your voice profile. Say 'set up my voice profile' (or run /founder-os:voice-interview)." Reason: real users do not memorize a 21-command surface, and Cowork mode (which does not fire slash commands at all) needs natural language as the primary interface.
- **Every file in `skills/*/SKILL.md` (39) reworked the same way.** Trigger phrases the operator already uses ("prep me for my call", "what's on for today?", "run my weekly review", "I'm overwhelmed", "capture this", "log this", "help me decide") appear verbatim in the relevant skill descriptions so auto-trigger by description match keeps working. Skill behavior is unchanged.
- **`docs/commands.md` per-command reference table reworked.** Every row now leads with the natural-language phrasing.
- **`docs/skills.md` per-skill reference reworked.** Same pattern.

### Added - new `/founder-os:menu` capability discovery entry

- **New `.claude/commands/menu.md` and `skills/menu/SKILL.md`.** Say "show me what you can do" (or run `/founder-os:menu`). Returns 5 to 7 capability suggestions tailored to current state. Algorithm: read `brain/.snapshot.md` if present, current week's commitments from `cadence/weekly-commitments.md`, last 7 days of `brain/log.md`, and presence of `core/voice-profile.yml` and `core/brand-profile.yml`. Score capabilities against state. Examples of the surface_when rules: voice-interview surfaces when `core/voice-profile.yml` is missing or empty, weekly-review surfaces when current date is more than 6 days past the `## Week of` date, priority-triage surfaces when `context/priorities.md` has 3+ items rolled forward, audit surfaces when last `/founder-os:audit` invocation in `brain/log.md` is more than 14 days old. Each row: natural-language phrasing first, slash command shortcut parenthetical, one-sentence why-now. Zero-state safety: brand-new install with no snapshot returns the Day-1 starter set (voice-interview, brand-interview, priority-triage, today, ingest). No LLM call inside the algorithm. Free-tier accessible.
- **New `tests/test_menu.py`.** Covers zero-state install (Day-1 starter set), present-state install (context-aware top 5 to 7), missing snapshot (graceful fallback to profile-only context).

### Added - SessionStart brief surfaces one underused capability per week

- **`.claude/hooks/session-start-brief.sh` and `.claude/hooks/session-start-brief.ps1` add a Tip line.** After existing flags and stale-cadence checks, before the close, the brief now prints one sentence suggesting a capability the operator has not used in 14+ days. Algorithm scans the last 30 days of `brain/log.md` for `#used` or invocation tags, picks one capability that has not been invoked in 14+ days AND has a clear use-case match for current state. Pattern: "Try saying 'help me decide' next time you're stuck on a choice - the decision-framework skill walks you through it." If no eligible tip, the line is omitted (no "no tip" placeholder).

### Changed - README leads with natural-language as the primary surface

- **New "How to use it - talk to Claude" section near the top, after "What you actually get".** Three sentences: the OS routes on natural language, slash commands are speed shortcuts, the new `/founder-os:menu` is the single entry to discover what's available.
- **Slash command table gets a third "Or say…" column.** Every row now shows the natural-language equivalent alongside the slash form. Where the slash form has no natural-language equivalent (`/founder-os:lint`, `/founder-os:wiki-build`), the cell reads "tool invocation". The new `/founder-os:menu` is the first row.
- **No "Quick reference" or "Cheatsheet" section added.** Re-introducing a memorize-the-commands surface would defeat the point of the release.

### Fixed - `scripts/query.py` zero-score fallback returns "no positive match"

- **`scripts/query.py` and `templates/scripts/query.py`.** Previously, if `scored_candidates` was empty after scoring, the code still started traversal from the top-5 zero-score nodes, returning graph-popular junk. Now: if the highest-scoring candidate has score 0, return a structured no-match block with three suggestions (rephrase, add "rant" or "dump" if looking for a recent rant, run `/founder-os:brain-pass` for a synthesis across the whole brain layer). The point of the fix is honesty: do not return a "best guess" with a low-confidence warning when nothing matched.

### Fixed - `scripts/query.py` stop-word filter, light stemming, recency bonus

- **Tokenizer in `scripts/query.py` excludes a small list of English stop words** (a, an, the, of, to, in, on, for, with, by, at, from, is, was, are, were, be, been, has, have, had, do, does, did, this, that, these, those, what, when, where, why, how, who, my, your, our, their, can, could, should). Hardcoded list, no external dependency.
- **Light stemming strips common suffixes** (-s, -es, -ed, -ing, -ly, -tion). Hardcoded suffix list, no PyStemmer.
- **Recency bonus.** Files modified in the last 7 days get +0.5 score boost via `os.path.getmtime()`. Stdlib only.

### Fixed - `scripts/query.py` includes rants when the question is about rants

- **`INCLUDE_PREFIXES` logic now expands to include `brain/rants/`** when the query contains any of: "rant", "dump", "avoidance", "vent", "raw", "last N rants" (where N is a number). Detection is on the raw query string before tokenization. Case-insensitive substring match. Default is still rants excluded.

### Fixed - `brain-pass` preflights through `query.py`

- **`skills/brain-pass/SKILL.md`.** Brain-pass now first invokes `scripts/query.py` with the question to get the top candidate list, then synthesizes across those candidates. If query returns no positive match, brain-pass surfaces that to the operator and asks if they want to broaden the search. Brain-pass still always includes `brain/.snapshot.md` in its synthesis context regardless of query results.

### Changed - setup wizard tool-stack becomes 4 multi-choice prompts

- **`skills/founder-os-setup/SKILL.md` Phase 0.6 reworked.** The previous one-long-question pattern (knowledge base, email, calendar, CRM, automation, document storage in one prompt) becomes four sequential prompts, each with explicit options: knowledge base (Notion / Obsidian / Google Drive / local files only / other / skip), email (Gmail / Outlook / Apple Mail / other / none / skip), calendar (Google Calendar / Outlook / Apple Calendar / other / none / skip), CRM or pipeline tracking (Notion DB / HubSpot / Airtable / spreadsheet / nothing yet / skip). Each prompt is one sentence + one line of options. "Skip" works on every prompt, records `null` in `core/stack.json` and continues. If the user dumps everything in one chat reply ("Notion, Gmail, Google Calendar, no CRM"), the wizard parses it and skips the individual prompts. Backward compatibility preserved.

### Changed - setup wizard work-style becomes 4 multi-choice prompts

- **`skills/founder-os-setup/SKILL.md` work-style phase reworked.** Same pattern: deep work time (morning / afternoon / evening / variable / skip), decision style (gut / data / dialogue with someone / mixed / skip), communication style (direct and short / detailed and explanatory / skip), what overwhelms you (too many open loops / unclear next step / context switching / decision fatigue / other / skip). Existing schema in `core/identity.md` and `core/operating-preferences.yml` is preserved; only the prompt shape changed.

### Notes

- 21 commands now (added `menu`). 39 skills.
- 56 existing tests still pass plus new tests for menu, tip, query scoring, and the MC wizard.
- No new dependencies. Stdlib Python, bash, PowerShell only. Free-tier accessibility floor preserved.
- No banned phrases in new prose. No em dashes, no en dashes.
- Path A (plugin install) and Path B (manual git clone) prefix detection from v1.19.6 is preserved. New menu surfaces and SessionStart tips that reference slash commands use the same `<prefix>` substitution model where applicable. Always-bare commands stay bare.

## v1.19.6 - 2026-05-09

Setup orientation now adapts to how you installed. Path A (plugin) keeps the `/founder-os:` prefix throughout; Path B (manual git clone) drops it. A user following the orientation after a manual install previously hit "command not found" on every namespaced command in the post-setup checklist.

The orientation also flips from command-led to natural-language-led throughout. "Run `/founder-os:voice-interview`" becomes "Say 'set up my voice profile' (or run `/founder-os:voice-interview`)." The slash command is there for power users; the phrase is there for everyone else.

Cowork mode is now fully documented: what works when you open FounderOS in a shared Claude workspace (markdown reads and writes, MCPs, natural language routing) and what does not fire there (hooks, slash commands, SessionStart brief). Six-step setup recipe in `docs/install.md` for Cowork users.

### Fixed - wizard orientation now path-aware (Path A vs Path B)

- **`skills/founder-os-setup/SKILL.md` Phase 6.2 detects the command prefix before rendering the orientation block.** Path A (plugin install) keeps the `/founder-os:` namespace; Path B (manual git clone) drops it. The detection reads `.claude-plugin/marketplace.json` at the user's working directory: present means Path B (bare commands); absent means Path A (namespaced). The orientation now substitutes a `<prefix>` placeholder for `voice-interview`, `brand-interview`, `status`, and `uninstall`. On Path B `<prefix>` resolves to `/` so `<prefix>voice-interview` renders as `/voice-interview`; on Path A it resolves to `/founder-os:` so the same placeholder renders as `/founder-os:voice-interview`. Always-bare commands (`/today`, `/next`, `/pre-meeting`, `/capture-meeting`) render unchanged on both paths. Before this patch, a Path B user reading the orientation would have hit "command not found" on every namespaced command in the post-setup checklist.

### Fixed - orientation leads with natural language, slash commands are shortcuts

- **`skills/founder-os-setup/SKILL.md` Phase 6.2 orientation block flipped from slash-command-led to natural-language-led.** The previous prose said "Run `<prefix>voice-interview`" as the primary instruction. The new prose says "Say 'set up my voice profile' (or run `<prefix>voice-interview`)." Same change applied to brand profile, readiness check, daily view, weekly review, audit, and uninstall lines. The pattern was already present in the orientation for overwhelmed / learn / meetings / decisions sections; this change makes it consistent across the whole block. Reason: real users do not memorize a 20-command surface, and Cowork mode (which does not fire slash commands at all) needs natural language as the primary interface.
- **`docs/install.md` "After install" list rewritten with the same pattern.** Each step now leads with the natural-language phrasing and notes the slash command alongside. A one-line preface tells the reader why: "talking to Claude is the default, slash commands are optional shortcuts for power users."

### Fixed - Cowork mode is now documented end-to-end

- **`README.md` SessionStart claim qualified to "every Claude Code session open."** The previous wording implied the brief fires regardless of surface. Cowork users would have assumed the brief, the Stop hook, and slash commands work there; none of them do.
- **`README.md` adds a Path D section** pointing Cowork users at the FounderOS folder, naming what works (markdown reads/writes, MCPs, scheduled tasks) and what does not (hooks, slash commands), and pointing to the full setup recipe in `docs/install.md`.
- **`docs/install.md` adds a "Cowork mode" subsection** with a six-step setup recipe (open folder, attach `CLAUDE.md` as folder instructions, attach `brain/.snapshot.md` if present, talk in natural language, return to Claude Code for hooks/commits/cadence). Honest-limits block lists the four things that silently do not fire there.
- **`docs/install.md` "After install" list now includes `/today` and `/next`** as the first-day actions after the voice and brand interviews. The full Day-1 path is now visible from the install doc without bouncing through the README.

### Notes

- 56 tests still pass. No script changes; this is a docs and wizard-prompt patch.
- No new skills, no new commands. 39 skills, 20 commands. Same surface as v1.19.5.
- Free-tier accessibility floor preserved.

## v1.19.5 - 2026-05-09

Parser maintainability cleanup. v1.19.4's narrative described the parser as using a "single shared helper" for both flat and nested quoted-value handling, but the nested branch still had the unescape logic inlined. Behavior was identical, but the duplication was a future-drift trap. v1.19.5 makes the claim literally true.

### Changed - parse_edges nested branch routes through the unquote helper

- **`scripts/query.py:parse_edges()` and `templates/scripts/query.py:parse_edges()` nested-targets branch now calls `unquote()` instead of duplicating the quote-aware unescape inline.** The `target_quoted_re` regex captures the entire quoted token (including the outer quotes) in group 1 so it can be passed directly to `unquote()`. Both code paths now run through one helper, so future drift between the flat and nested handling is structurally prevented (an earlier review iteration found the two paths had drifted apart, producing different round-trip behavior for the same input shape). No behavior change; the existing 56 tests still pass.

### Notes

- 56 tests pass on git-bash. WSL bash was confirmed clean by an earlier review.
- No behavior change. The flat and nested paths now produce literally identical handling for any quoted-value input shape.
- No new skills, no new commands. 39 skills, 20 commands. Same surface as v1.19.4.

## v1.19.4 - 2026-05-09

Fifth-review patch. The quote-aware unescape introduced in v1.19.2 and narrowed in v1.19.3 was only applied to the nested `wiki_links:` list path. The flat curated path used a different (older) shape for handling quoted values, so the two paths disagreed on round-trip behavior. v1.19.4 unifies them.

### Fixed - flat curated quoted values round-trip the same way as nested targets

- **`scripts/query.py:parse_edges()` and `templates/scripts/query.py:parse_edges()` now use a single `unquote` helper for both the flat curated path (`source:` / `target:` / `from:` / `to:`) and the nested `targets:` list path.** v1.19.2 and v1.19.3 added quote-aware unescape to the nested path, but the flat path still used `value.strip().strip('"\'')` -- it stripped outer quotes but left any inner escape verbatim. A flat entry like `target: "foo\"bar"` parsed as `foo\"bar`, not `foo"bar`; `target: 'don\'t'` parsed as `don\'t`, not `don't`. The new `unquote` helper strips matching outer quotes and reverses only the matching escape (`\"` inside `"..."`, `\'` inside `'...'`). Three new tests cover the flat-path round-trip in both quote shapes plus the literal-backslash-preserved case.

### Notes

- 56 tests now pass on git-bash (was 53). Three new tests for the flat-path round-trip behavior.
- WSL bash verification: confirmed clean by an earlier review pass. v1.19.4 only narrows the parser; the WSL path is unchanged.
- No new skills, no new commands. 39 skills, 20 commands. Same surface as v1.19.3.
- Free-tier accessibility floor preserved.

## v1.19.3 - 2026-05-09

Fourth-review patch. v1.19.2's quoted-target escape-unescape over-applied across quote shapes, and the ROADMAP `v1.19.0` shipped bullet had not caught up to the corrected v1.19.0 narrative in CHANGELOG and README. Two fixes.

### Fixed - parse_edges escape-unescape is quote-char-aware

- **`scripts/query.py:parse_edges()` and `templates/scripts/query.py:parse_edges()` now only unescape `\"` inside double-quoted targets and only unescape `\'` inside single-quoted targets.** v1.19.2 unescaped both forms regardless of the surrounding quote, which was correct for the double-quoted output `scripts/wiki-build.py` writes but corrupted hand-written single-quoted YAML. A target like `'foo\"bar'` (where the user wants a literal backslash and a literal double-quote) would have parsed as `foo"bar`, losing the backslash. The unescape now reads the surrounding quote character from the regex group and only reverses the matching escape. New test `tests/test_query.py::ParseEdgesTests::test_single_quoted_target_preserves_backslash` locks the asymmetric behavior in.

### Fixed - ROADMAP v1.19.0 bullet matches CHANGELOG and README

- **ROADMAP `v1.19.0` shipped entry now reads "five user-visible fixes plus an attempted WSL fix" and points the WSLENV/p fix at v1.19.1.** v1.19.2 corrected the v1.19.0 summary in CHANGELOG and the v1.19.0 paragraph in README, but the parallel ROADMAP bullet still said "Six fixes" with the `WSLENV/p` work credited to v1.19.0. A reader skimming ROADMAP would have seen contradictory framing across the three public docs. Now consistent.

### Notes

- 53 tests now pass on git-bash (was 52). One new test for the single-quote-preserves-backslash edge case.
- WSL bash verification: confirmed clean by the v1.19.1 review pass. v1.19.2 added the round-trip fix on top; v1.19.3 keeps both and only narrows the unescape scope.
- No new skills, no new commands. 39 skills, 20 commands. Same surface as v1.19.2.
- Free-tier accessibility floor preserved.

## v1.19.2 - 2026-05-09

Third-review patch. The v1.19.1 release closed the v1.19.0 review's findings, but the patch narrative itself reintroduced the previous reviewer's tool name while explaining its earlier removal, the v1.19.0 summary still framed an incomplete fix as complete, and a parser edge case the third review surfaced was real. v1.19.2 closes all three.

### Fixed - parse_edges round-trips a target containing a literal double-quote

- **`scripts/query.py:parse_edges()` and `templates/scripts/query.py:parse_edges()` now unescape `\"` back to `"` after stripping the surrounding quotes.** `scripts/wiki-build.py` escapes a literal `"` inside a target as `\"` when writing the YAML line. The v1.19.1 parser read the captured group verbatim, so a target containing a literal double-quote round-tripped as `foo\"bar` instead of `foo"bar`. The serializer and parser are now symmetric. Edge case in practice (wikilinks rarely contain literal quotes), but a real correctness defect. One new test in `tests/test_query.py::ParseEdgesTests::test_quoted_target_with_escaped_quote_round_trips` locks the round-trip behavior in.

### Fixed - tool branding scrubbed from v1.19.1 patch narrative

- **CHANGELOG, README, and ROADMAP v1.19.1 narratives no longer name the previous reviewer by tool brand.** The v1.19.1 patch had added narrative explaining the v1.19.0 attribution scrub and re-leaked the brand name in the act of explaining the scrub. Replaced with neutral wording ("the previous reviewer" / "tool-branding attribution"). Same fix for one comment in `tests/test_query.py` that named the reviewer by brand. Three pre-existing mentions in published v1.16 / v1.7 narratives (a cross-agent file audience description, an external file path reference, and a delegatable-to-AI-agents line in ROADMAP) are descriptive rather than attribution and were not flagged in this review pass; they remain as-is.

### Fixed - v1.19.0 summary now honestly describes the WSL state at v1.19.0

- **CHANGELOG and README v1.19.0 summary paragraphs no longer claim the WSL test fix landed in v1.19.0.** The detailed CHANGELOG section (under "the test suite path conversion learns about WSL bash") was already corrected in v1.19.1 to say the WSL fix was "partial in v1.19, completed in v1.19.1". The short summary paragraphs at the top of the v1.19.0 entry and in README's Status section had not caught up: they still listed "the test suite passes on every Windows shell" / "falls back gracefully under WSL" as a v1.19.0 fix and described the `WSLENV/p` fix as v1.19.0 work. Both summaries now read five user-visible v1.19.0 fixes plus an attempted WSL fix that did not fully land, with a forward pointer to v1.19.1 where it actually lands.

### Notes

- 52 tests now pass on git-bash (was 51). One new test for the quoted-target escape round-trip.
- WSL bash verification: confirmed clean by the v1.19.1 review pass. The reviewer ran the suite under a `bash` that resolved to `C:\Windows\system32\bash.exe`, got 51/51 OK, and reported the converted hook path as `/mnt/c/path/to/founder-os/.claude/hooks/session-start-brief.sh`. v1.19.2 keeps that path and adds the round-trip fix on top, so 52/52 should pass on WSL too.
- No new skills, no new commands. 39 skills, 20 commands. Same surface as v1.19.1.
- Free-tier accessibility floor preserved.

## v1.19.1 - 2026-05-08

The v1.19 follow-up. A second review pass over v1.19.0 found one BLOCKER and three MAJOR issues that v1.19 either left open or introduced. v1.19.1 closes them. Four user-visible fixes plus three new tests.

### Fixed - WSL test path conversion no longer silently fails to "."

- **`tests/test_session_hooks.py:bash_path()` and `tests/test_post_tool_use_hook.py:to_bash_path()` now use `WSLENV/p` propagation and validate the converted path.** v1.19 added a `wslpath` probe that was supposed to handle the case where `bash` resolves to WSL bash on Windows. It did not work: a Windows-side env var does not cross into WSL bash unless `WSLENV` whitelists it, so `TARGET_PATH` arrived empty and the probe returned `.` (the cwd). The bash parse-test then attempted to parse a directory and failed 14 of 48 tests. The new path adds `WSLENV=TARGET_PATH/p` so the WSL launcher translates the Windows path into POSIX form before the bash subprocess reads it, rejects any probe result that is empty or `.`, and falls back to a manual `/mnt/<drive>/` shape when the bash binary is at `system32` (WSL) or `/<drive>/` otherwise (git-bash, MSYS2). v1.19 overstated this fix as "passes on every Windows shell"; the v1.19 entry below has been updated to describe what actually shipped, and the v1.19.1 fix here is what makes the claim true.

### Fixed - query and wiki-build now agree on scope

- **`scripts/query.py:candidate_files()` walks every prefix in `INCLUDE_PREFIXES`.** v1.19 widened the live rescan to `roles/` and `rules/` but missed `core/`, `cadence/`, and the rest of `context/`. The persisted wiki graph already included those (see `scripts/wiki-build.py:INCLUDE_PREFIXES`), so files like `context/clients.md`, `cadence/daily-anchors.md`, and `core/identity.md` were graph nodes that could never surface as query candidates. `INCLUDE_PREFIXES` is now defined in `scripts/query.py` as well, with an explicit comment to keep the two files in sync. Mirrored to `templates/scripts/query.py`. Two new tests build a synthetic install with one node per prefix and assert each surfaces.

### Fixed - parse_edges keeps quoted targets that happen to begin with a key word

- **`scripts/query.py:parse_edges()` now distinguishes quoted targets from unquoted record boundaries.** A wikilink target like `[[source: note]]` round-trips through `scripts/wiki-build.py` as `      - "source: note"`. The v1.19 parser stripped the surrounding quotes first, then matched `source:` against its key pattern, exited the targets block, and dropped the edge. The new state machine treats anything in quotes as a target (always), and only treats unquoted list items as potential boundaries. One new test locks the behavior in.

### Fixed - parked-decision decay prose matches what the hook actually does

- **`templates/rules/entry-conventions.md` and `templates/brain/decisions-parked.md` no longer claim the SessionStart hook auto-surfaces parked decisions on trigger.** The hook only fires on entries that explicitly set `Decay after:`; it does not evaluate trigger conditions. Both files now state that parked decisions surface manually during the Chief of Staff scan or weekly review, and that an explicit `Decay after:` line is the way to put one on the auto-surface path. Lint already excludes parked decisions from the `decay-gap` scan (v1.19 fix); this release brings the prose into line with that behavior.

### Fixed - tool branding removed from public release narrative

- **CHANGELOG, README, and ROADMAP v1.19 narratives no longer name the external reviewer.** `rules/commit-naming.md:11` bans AI-tool attribution in public history. The v1.19 narratives previously named the reviewing tool by brand in three public docs. Replaced with neutral wording ("external review" / "the review's NIT 11" / "external-review close"). The v1.19 commit message itself stays in history (cannot be amended without rewriting public history); future release commits will follow the rule.

### Notes

- 51 tests now pass on git-bash (was 48). Three new: one for parse_edges quoted-target-with-key, two for candidate_files walking each prefix in INCLUDE_PREFIXES.
- WSL bash verification: the path-conversion fix is correct in theory and reasoned through against `WSLENV/p` semantics, but I could not run the suite under WSL bash on this machine. If you have a Windows machine where `bash` resolves to WSL, run `python -m unittest discover -s tests` and confirm 51/51 pass; if any fail, please open an issue.
- No new skills, no new commands. 39 skills, 20 commands. Same surface as v1.19.0.
- Free-tier accessibility floor preserved.

## v1.19.0 - 2026-05-08

The external-review close. v1.16-v1.18 caught doc drift; v1.19 catches the substantive fixes surfaced by an independent review of v1.15.0. Five issues a user would actually notice: search now reads the wiki connections you build, search now covers role and rule files, fresh installs run clean again, the manual-clone install gets correct command guidance on Day 1, and the plugin marketplace shows the right version. Plus an attempted WSL bash test fix that did not fully land (v1.19 added a `wslpath` probe but did not propagate the path into WSL bash; v1.19.1 closes the gap with `WSLENV/p` and result validation). Plus three smaller doc fixes and the metadata that should have shipped earlier.

### Fixed - search now reads the wiki connections you build

- **`/founder-os:query` now uses the graph that `/founder-os:wiki-build` creates.** When you write `[[wikilinks]]` between files and run wiki-build, those connections land in `brain/relations.yaml`. Search was supposed to traverse that graph to find related results, but the parser was only reading old-format curated entries and silently dropping every auto-generated edge. The result: any link you wrote between files was invisible to search. Both the live script and the template now read the auto-generated nested format. Five new unit tests in `tests/test_query.py` lock in the behavior on both copies so the two cannot drift again.
  - Detail for engineers: `scripts/query.py:parse_edges()` now handles the nested `wiki_links:` block (`- source: <path>` followed by `targets:` and a list of quoted strings) on top of the old flat `from`/`to` pairs. Same change in `templates/scripts/query.py`.

### Fixed - search now covers your role and rule files

- **Live search rescan widened to `roles/` and `rules/`.** v1.14 added these directories to the wiki graph builder so cross-references inside role definitions and operating rules would land in `brain/relations.yaml`. The query side never caught up, so search results were missing nodes the graph already knew about. Now the two agree: search scans the same set of directories the graph builder records.
  - Detail for engineers: `scripts/query.py:candidate_files()` now walks `brain/knowledge/`, `companies/`, `network/`, `roles/`, `rules/`. Mirrored to the template.

### Fixed - fresh installs run clean again

- **Lint no longer warns about the seeded parked-decisions example as a stale entry.** A new install ships `brain/decisions-parked.md` with one example dated 2024-01-01 to teach the format. v1.15 added a "decay-gap" warning that flagged any flag, pattern, or parked entry older than 30 days without a `Decay after:` line. That broke the Day-1 promise: every new user saw a false warning on the very first lint run. Parked decisions are trigger-driven by convention (the file says so explicitly), so they are now excluded from the decay-gap scan. The other two scopes (flags and patterns) still surface real adoption gaps.

### Fixed - the test suite path conversion learns about WSL bash (partial in v1.19, completed in v1.19.1)

- **Tests probe `wslpath` after `cygpath`.** The suite was passing on git-bash and silently failing 14 out of 43 on a Windows machine where `bash` resolves to WSL. v1.19 added a `wslpath` branch but did not propagate the path argument into WSL bash, so the probe still returned `.` (its cwd) and the suite still failed there. v1.19.1 closes the gap with `WSLENV/p` propagation and a result-validation check; see the v1.19.1 entry above. The "43/43 pass" claim in v1.15-v1.18 release notes was true on git-bash and untrue on WSL; v1.19.1 is the release where it becomes true on both. v1.19 also ships five new tests that cover the search/wiki logic on top.

### Fixed - the manual-clone install gets correct Day-1 command guidance

- **`docs/first-day.md` now carries a Path B note at the top.** If you installed via manual git clone (Path B) instead of the plugin marketplace (Path A), the slash commands ship without the `/founder-os:` prefix. The README and `docs/install.md` already said so. The first-day walkthrough did not, so a Path B user running the walkthrough verbatim would hit "command not found" on the very first command. Closed.

### Fixed - the plugin marketplace shows the right version

- **`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` now read 1.19.0.** Both manifests had been stale at 1.13.0 since the v1.13 release. The README stamp was bumped in v1.16 and the `VERSION` file in v1.18, but the plugin manifests were left behind. The plugin marketplace reads from those manifests, so anyone installing through the marketplace was seeing a stale version stamp on a current build.

### Fixed - smaller doc and surface fixes

- **The decay convention doc names the right anchor fields.** `templates/rules/entry-conventions.md` was telling users that relative decay (`14d`, `90d`) computes from a `created` field. No template uses a `created` field. The actual scanner uses the flag heading date, the `First observed:` line on patterns, and the `Date parked:` line on parked decisions. The doc now matches.
- **The bare-slug ambiguity rule is spelled out in docs.** `docs/tools-and-mcps.md` was saying "lint will tell you" the deterministic pick when a `[[bare-slug]]` matched multiple files. The rule itself was only documented inside the lint skill. Now spelled out in the user-facing doc: scan `INCLUDE_PREFIXES` order (`core/`, `context/`, `cadence/`, `brain/`, `network/`, `companies/`, `roles/`, `rules/`), alphabetical within the first matching directory, first match wins.
- **The session-start brief visually closes correctly.** `=== end brief ===` is now the last line of the hook output. The `Observations:` status line used to print after that closure, so the visual boundary did not actually mark the end of the brief. Re-ordered in both the bash and PowerShell hooks.
- **The lint reference example block shows all four kinds of stale-content output.** v1.15 added `decay-gap` and `log-cap` outputs to lint but the rendered example block in the skill file still only showed the older two. Updated.

### Notes

- 48 tests now pass (was 43). Five new tests cover the search/wiki connection logic and run against both the live script and its template mirror to catch future drift between the two.
- No new skills, no new commands. 39 skills, 20 commands. Same surface, fewer silent failures.
- Free-tier accessibility floor preserved. Nothing in the install or daily-use path requires a paid AI subscription, API key, or external service.
- The review's NIT 11 (300-line cap wording: `templates/brain/index.md:62` says "hits 300", `skills/lint/SKILL.md:85` says "exceeds 300") is deferred and self-flagged as a v1.16+ punt by the reviewer; not blocking.

## v1.18.0 - 2026-05-08

Third-layer doc-drift release. v1.16 caught the root-level docs (README, ROADMAP, CLAUDE.md, AGENTS.md). v1.17 caught the first-day walkthrough and the bootloader template that becomes the user's CLAUDE.md after setup. v1.18 catches the per-skill and per-command reference docs (`docs/skills.md` and `docs/commands.md`), which still described the pre-v1.15 lint outcome. A user clicking through to either reference would see fewer lint surfaces than the skill actually prints. No code changes.

### Fixed - docs/skills.md and docs/commands.md describe the v1.15 lint output

- **`docs/skills.md` `### lint` Outcome line updated.** Was listing four lint findings: broken `[[wikilinks]]`, orphan files, entries past `Decay after:` date, provenance gaps, possible contradictions. Now also names: ambiguous slugs (lint names the deterministic pick, not just the candidate list), `decay-gap` (entries 30+ days old that lack a `Decay after:` field, soft signal), and `log-cap` (`brain/log.md` over 300 lines, reminder).
- **`docs/commands.md` `### /founder-os:lint` Outcome line updated.** Same gap, same fix. The two reference docs now describe the same surface as `skills/lint/SKILL.md` Check 1 and Check 3.

### Notes

- 43/43 existing tests still pass (no code changed).
- No new dependencies, no new skills, no new commands. Doc-only release.
- Free-tier accessibility floor preserved.

## v1.17.0 - 2026-05-08

Second-layer doc-drift release. v1.16 caught the user-facing root-level docs (README, ROADMAP, CLAUDE.md, AGENTS.md). v1.17 catches the documentation files a user reads AFTER install: the first-day walkthrough and the bootloader template that becomes the user's CLAUDE.md after `/founder-os:setup`. Both had a SessionStart-brief inventory frozen at v1.4 that missed two items added since: the `clients/<slug>/` auto-memory diff (v1.12) and the `Observations:` line (v1.15). A new user reading either file would see fewer brief surfaces than the hooks actually print on their machine. No code changes.

### Fixed - docs/first-day.md SessionStart inventory now lists all nine surfaces

- **`docs/first-day.md` "What SessionStart shows you" section heading and body updated.** Was titled "(v1.4)"; now reads "(v1.4 + v1.12 + v1.15)" so the reader knows the inventory tracks the actual hook output. Two missing surfaces added: `clients/<slug>/` folders without an auto-memory entry (v1.12) and the final `Observations:` line that surfaces `FOUNDER_OS_OBSERVATIONS` state (v1.15).

### Fixed - templates/bootloader-claude-md.md ships an accurate brief inventory to every fresh install

- **`templates/bootloader-claude-md.md` Fabric section updated.** The bootloader is what `/founder-os:setup` writes as the user's CLAUDE.md. Its SessionStart-brief description was missing the same two surfaces. Every fresh install since v1.12 has shipped a CLAUDE.md that under-reported the brief. Now matches what the hooks print.

### Notes

- 43/43 existing tests still pass (no code changed).
- No new dependencies, no new skills, no new commands. Doc-only release.
- Free-tier accessibility floor preserved.

## v1.16.0 - 2026-05-08

Docs-sync release. README, ROADMAP, CLAUDE.md, and AGENTS.md were claiming v1.13 surface state after v1.14 and v1.15 had already shipped earlier the same day. A first-time user cloning the repo would have seen version drift in the first thirty seconds (README "Production v1.13.0", VERSION file `1.15.0`). This release closes that drift. No code changes.

### Fixed - README claims now match shipped state

- **`README.md` "Production" stamp updated to v1.16.0.** Was `v1.13.0` after v1.14 + v1.15 shipped. The repo card on GitHub-rendered README would have shown a stale version to anyone landing on the repo cold.
- **`README.md` Status section gains v1.14, v1.15, and v1.16 prose.** Was telling the v1.13 story. New users now see the most recent three releases described before older ones.
- **`README.md` "Version" line updated.** Was `Version 1.13.0`, now reads `Version 1.16.0`.

### Fixed - ROADMAP Shipped list extends through v1.16

- **`ROADMAP.md` Shipped list updated.** Was last updated at v1.13.0. Now includes v1.14.0 (wiki integrity), v1.15.0 (wiki-hardening Phase 2), and v1.16.0 (this docs-sync entry).

### Fixed - CLAUDE.md and AGENTS.md SessionStart-brief inventory matches what the hooks actually print

- **`CLAUDE.md:178` SessionStart-brief description now names the `Observations:` line.** v1.15 added a final "Observations: enabled" or "Observations: disabled (set FOUNDER_OS_OBSERVATIONS=1 to enable)" line so the silent-disable case is visible. The CLAUDE.md inventory previously did not list it.
- **`AGENTS.md:121` SessionStart-brief description gets the same update.** Cross-agent docs (Codex, Gemini) now describe the same printed surface as the live hooks.

### Notes

- 43/43 existing tests still pass (no code changed).
- No new dependencies, no new skills, no new commands. Doc-only release.
- Free-tier accessibility floor preserved.

## v1.15.0 - 2026-05-08

Wiki-hardening Phase 2. v1.14.0 closed four wiki-integrity issues (graph scope, link dedupe, orphan exemptions, stale-content field name). The same audit surfaced five more places where the OS quietly degrades without telling the user: a missing `Decay after:` field is silent, `brain/log.md` past its 300-line cap is silent, ambiguous `[[bare-slug]]` resolution is undefined, the observation log silently disables when `FOUNDER_OS_OBSERVATIONS` is unset, and a fresh Obsidian vault looks broken on day 0 because the seeded files are not cross-linked. All five are surfaced (not auto-fixed) in this release. No new skills, no new commands, no new tests, no script changes.

### Fixed - lint surfaces the decay-convention adoption gap

- **`skills/lint/SKILL.md` Check 3 now flags entries that lack `Decay after:`.** The decay scanner in `.claude/hooks/session-start-brief.sh` is forward-only by design: it only fires on entries that explicitly include the field. Any flag, pattern, or parked decision written before the user reads the convention silently never qualifies for Review Due. Lint now scans `brain/flags.md`, `brain/patterns.md`, and `brain/decisions-parked.md`, and emits `decay-gap` lines under STALE CONTENT for entries 30+ days old without the field. Capped at 5 oldest per file. Soft signal, not a defect. Hook behaviour is unchanged.

### Fixed - lint warns when brain/log.md breaches its 300-line cap

- **`skills/lint/SKILL.md` Check 3 now flags `brain/log.md` over 300 lines.** The cap is documented in `templates/brain/log.md:2` and `templates/brain/index.md:33` but no script enforces it. Lint now emits `log-cap` under STALE CONTENT with current line count and the manual-archive path. No auto-archive (the user runs that manually per the existing convention).

### Fixed - lint names the deterministic pick on bare-slug ambiguity

- **`skills/lint/SKILL.md` Check 1 ambiguous-slug rule rewritten.** Was "flag with the candidates", which left three different behaviors for one syntax (lint reported only candidates, wiki-build stored the literal string, Obsidian prompted the user). Lint now also names the deterministic pick: scan in `scripts/wiki-build.py:INCLUDE_PREFIXES` order, alphabetical within the first matching directory, first match wins. Output format updated accordingly. No script change. Resolution is a query-time concern; v1.14.0 already settled the build/store path.
- **`docs/tools-and-mcps.md` Obsidian section now documents the rule.** Sub-section "Bare-slug ambiguity" added under `### Obsidian`, naming the lint output and the path-form disambiguation (`[[brain/index.md]]`).

### Fixed - SessionStart brief surfaces FOUNDER_OS_OBSERVATIONS state

- **`.claude/hooks/session-start-brief.sh` and `.ps1` now print observation-log status on every open.** Before, `scripts/brain-pass-log.py` exited 0 silently when the env var was absent; the user could believe observations were recording when they were not. The brief now ends with one line stating "Observations: enabled" or "Observations: disabled (set FOUNDER_OS_OBSERVATIONS=1 to enable)" regardless of state. The silent-disable path is now visible.

### Fixed - day-0 Obsidian graph empty is expected, not broken

- **`docs/tools-and-mcps.md` Obsidian section now names the day-0 expectation.** A first-time user opening the vault sees an empty graph view because the seeded files are not retrofitted with cross-references (the wikilink convention is forward-only by design). New "Day-0 expectations" sub-section explains why the graph is empty on first open and how it fills in (write `[[wikilinks]]` between files, run `/founder-os:wiki-build` to refresh).

### Notes

- 43/43 existing tests still pass after these changes. No new tests added (the changed surfaces are documentation-style and shell-output only; existing `test_session_hooks.py` exercises hook output structure).
- No new dependencies. No API key needed. Free-tier accessibility floor preserved.
- The new Obsidian sub-sections in `docs/tools-and-mcps.md` use `####` (H4) so they nest correctly under `### Obsidian`. The plan draft used `###` literally, which would have made them siblings of Obsidian rather than children.
- `scripts/wiki-build.py` and `scripts/query.py` unchanged. v1.14.0 already settled the build and query path; this release is surface-and-doc fixes only.

## v1.14.0 - 2026-05-08

Wiki integrity release. An audit prompted by an Obsidian-vault user question surfaced four issues that quietly degrade the memory and operational layer: cross-references inside `roles/` and `rules/` were silently dropped from the graph, `[[file]]` and `[[file.md]]` produced separate graph nodes, lint flagged most seeded root files as orphans on a fresh install, and one stale-content rule named a field that no template uses. All four are closed in this release. No new skills, no new commands, no new tests.

### Fixed - wiki layer scope now matches what Obsidian sees

- **`scripts/wiki-build.py` and `templates/scripts/wiki-build.py` now include `roles/` and `rules/` in `INCLUDE_PREFIXES`.** A `[[wikilink]]` written inside `rules/operating-rules.md` or `roles/coo.md` was previously invisible to `brain/relations.yaml` while Obsidian rendered the edge in its graph view. The two views now agree.
- **`skills/wiki-build/SKILL.md` and `skills/lint/SKILL.md` scope sections updated to match.** Lint and wiki-build had parallel wiki-layer scopes that drifted by hand; both now point at `scripts/wiki-build.py:INCLUDE_PREFIXES` as the canonical source of truth, with explicit cross-file sync notes in the scripts.

### Fixed - `[[file]]` and `[[file.md]]` dedupe to one graph node

- **`scripts/wiki-build.py` and the template now apply `normalize_target()` at extraction.** Trailing `.md` is stripped (`#anchor` preserved), and Windows backslashes are converted to forward slashes. `[[priorities]]` and `[[priorities.md]]` previously produced two unrelated nodes in `brain/relations.yaml`. They now collapse to one. The case of the slug is preserved so display intent is not lost.
- **`scripts/query.py` `wikilink_edges()` applies the same normalization.** The in-memory traversal graph and the persisted graph now agree on node names, which prevents silent partial-match misses during `index` and `timeline` queries.

### Fixed - lint orphan check no longer floods on a fresh install

- **`skills/lint/SKILL.md` orphan exemption list extended.** Was missing `context/clients.md`, `context/companies.md`, `context/decisions.md`, `brain/needs-input.md`, `brain/index.md`, `brain/relations.yaml`, all of `roles/`, and all of `rules/`. A user running `/founder-os:lint` after `/founder-os:setup` will no longer see those seeded roots reported as orphans. Restores the "fresh install runs clean" promise.

### Fixed - stale-content rule cites a field that exists

- **`skills/lint/SKILL.md` stale-content rule renamed.** Was "Any client row with last-touch field 30+ days behind today"; the seeded template uses `Last contact`. Updated to name `Last contact` explicitly while still allowing equivalent last-touch field names.

### Notes

- 43/43 existing tests still pass after these changes. Smoke-tested by running `wiki-build.py` against a populated install.
- Free-tier accessibility floor preserved. No new dependencies, no API key needed, no behavior change for existing users with no `[[wikilinks]]` in their wiki layer yet.
- Plugin-internal `templates/`, `skills/`, `.claude/`, `docs/`, and `raw/` remain excluded from the wiki layer.

## v1.13.0 - 2026-05-08

The install-ergonomics and hardening release. v1.12 shipped the cross-session memory diff but a full audit found the public install paths still had a handful of walls a first-time user would hit cold from the README. v1.13 closes those walls, hardens the query command against shell injection, and makes sure the setup wizard actually ships the fixed runtime helpers. No new skills, no new commands.

### Fixed - install paths now reach a working setup

- **Path B no longer sends users to a non-existent command.** README told Path B users to run `/founder-os:setup`, but Path B is a manual clone with no plugin namespace active. The bare command is `/setup`. Aligned across README, `docs/install.md`, `docs/commands.md`, and the "Start here" quick-reference table.
- **Path A now tells users about `/reload-plugins`.** After `/plugin install`, the plugin namespace does not activate until reload. Users who typed `/founder-os:setup` and got "command not found" had no signal what to do. README and `docs/install.md` now name the fallback.
- **Path A verify step uses the real Claude Code command.** `/plugin list` is not a Claude Code slash command; the real surface is `/plugin` plus the Installed tab. `docs/install.md` updated.

### Fixed - phantom commands and skills removed

- **`/loop weekly` references removed.** `CLAUDE.md` (which ships into every fresh install) and `docs/first-day.md` told users to schedule wiki-build via `/loop weekly`. There is no `/loop` command. Both files now describe the weekly cadence in plain language.
- **`skill-creator` references replaced.** `CLAUDE.md` and `templates/roles/index.md` told users to "scaffold with skill-creator". No such skill ships. Both now say "copy an existing `skills/<name>/` folder and modify it", which matches `CONTRIBUTING.md`.
- **`weekly-review` is now correctly framed as a skill, not a command.** `docs/first-day.md` and `skills/readiness-check/SKILL.md` no longer surface `/founder-os:weekly-review` as a slash command. Users are told to say "run my weekly review" instead.
- **Day 1 STALE bug closed.** `templates/cadence/daily-anchors.md` ships with a `{{DATE}}` placeholder. The wizard PHASE 2.2 now has an explicit substitution step. Without this, the SessionStart brief would report STALE on the very first session.

### Fixed - cross-session memory diff actually fires on macOS

- **`session-start-brief.ps1` now probes `python3` first, then `python`.** macOS users running pwsh have only `python3` on the PATH; the v1.12 hook used `python` and silently no-op'd, breaking the marquee v1.12 feature for that audience.

### Fixed - setup wizard ships the fixed helpers

- **`templates/scripts/wiki-build.py` now matches the live `scripts/wiki-build.py`.** The template was the un-refactored copy. Every fresh Path A install would have written the broken version over the fixed one. Both now accept `--root`, both raise `SystemExit`, both share docstring.
- **`scripts/wiki-build.py` accepts `--root`.** Module-level `Path.cwd()` was replaced with an argparse-resolved root, so calling the script from a hook, a subdirectory, or via an absolute path now operates on the right tree instead of silently scanning the wrong one.

### Fixed - shell injection hardened on query command

- **`/founder-os:query` no longer interpolates `$ARGUMENTS` into a shell line.** The previous procedure could execute user input containing `;`, `|`, backticks, or `$(...)`. The command now passes plain questions via an environment variable and rejects flag tokens that contain shell metacharacters.

### Fixed - cross-platform reliability

- **`session-start-brief.sh` daily-staleness compare is locale-stable.** Was POSIX string compare which depends on locale collation; now delegates to Python with an `LC_ALL=C` fallback when Python is absent.
- **`.github/scripts/format_issue.py` works on Windows.** Was hardcoded to `/tmp/audit_findings.json`; now mirrors `audit.py`'s `findings_path()` helper so local Windows debug runs do not crash.
- **`.github/scripts/audit.py` resolves repo root via git.** Was anchored on `Path(".")`; now finds the repo root with `git rev-parse --show-toplevel` so a contributor running it from a subfolder gets correct results.
- **`.github/scripts/fix_advisor.py` no longer hard-errors without an API key.** Lazy-imports the `anthropic` SDK and skips gracefully if the key or SDK is missing. Free-tier accessibility floor preserved.
- **Test path-conversion fallback uses git-bash convention.** `tests/test_session_hooks.py` and `tests/test_post_tool_use_hook.py` previously fell back to WSL2's `/mnt/<drive>/` shape when `cygpath` was missing. Git-bash uses `/<drive>/`. Both files corrected.

### Changed - doc accuracy across surfaces

- **Setup wizard prompt count aligned.** README, `docs/commands.md`, and `docs/first-day.md` all now say "about 15 to 20 prompts across 6 phases". Was three different framings.
- **Voice and brand interview times aligned at 10 minutes each.** Was inconsistent (15/10/5-10) across README, command files, and the wizard itself. Setup ladder total updated to 40 minutes.
- **`AGENTS.md` says three hooks ship, not two.** SessionStart brief, opt-in PostToolUse observation log, session-close revenue check.
- **`docs/tools-and-mcps.md` zero-MCP list expanded to 35 skills.** Earlier the list named 22 while the prose claimed 35.
- **`skills/index.md` header bumped from "as of v1.10" to "as of v1.13".** Release notes now cover v1.11, v1.12, and v1.13.
- **ROADMAP shipped order corrected.** Was v1.10 -> v1.12 -> v1.11. Now v1.10 -> v1.11 -> v1.12 -> v1.13 in chronological order.
- **`CLAUDE.md` Windows-hooks note matches `docs/install.md`.** Was telling Windows users they need git-bash; the install doc says PowerShell works automatically. The PowerShell wiring is canonical.
- **Banned-style polish.** Eight corporate phrasing instances replaced with plain alternatives across user-facing prose.

### Notes

- 43/43 tests pass after every fix in this release. No new tests added; the existing suite covers the changed code.
- Free-tier accessibility floor preserved. Nothing in the install or daily-use path requires an API key, embeddings, or external service.
- Skill count stays 39, command count stays 20, hook count stays 3 (six files counting bash/PowerShell pairs and the opt-in observation log). No surface change.

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
