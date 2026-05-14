---
title: FounderOS v1.22.0 final-release review
reviewer: Codex
target_commit: 5f45183
date: 2026-05-14
recommendation: SHIP WITH PATCHES
---

# FounderOS v1.22.0 - Codex final-release review

## Headline

Ship only after the expanded critical patch set below. The repo is close, but a second full-folder architectural pass found additional first-run, rollback, uninstall, privacy, command-contract, and Windows hook blockers beyond the original seven findings.

## Critical findings (must fix before tag)

### Finding 1 - Full test suite is not green on Windows

- **Claim:** The release cannot claim final test coverage while `python -m unittest discover tests` fails on this Windows checkout.
- **Evidence:** Command: `python -m unittest discover tests`; output: `Ran 247 tests in 47.186s` and `FAILED (failures=5)`. Failures include `test_install_sh_parses`, `test_uninstall_sh_parses`, `test_dry_run_names_operations`, `test_rollup_count_reported_when_enabled`, and `test_stale_jsonl_nudge_fires`.
- **Impact:** Functional integrity and cross-platform parity. Windows users hit the same bash path and hook-env edges the suite is meant to guard.
- **Fix:** Patch the bash test path conversion so WSL/Git Bash receives a valid path. Fix the SessionStart observation-rollup test harness or hook env handling so `FOUNDER_OS_OBSERVATIONS=1` is honored in the temp install.

### Finding 2 - Setup omits v1.20 and v1.22 runtime scripts

- **Claim:** Fresh setup-created OS folders do not receive `scripts/menu.py` or `scripts/observation-rollup.py`, so two shipped command surfaces can fail after setup.
- **Evidence:** `skills/founder-os-setup/SKILL.md:360-366` copies only five helpers: `wiki-build.py`, `query.py`, `brain-snapshot.py`, `brain-pass-log.py`, and `memory-diff.py`. `skills/menu/SKILL.md:15-21` requires `scripts/menu.py`. `skills/observation-rollup/SKILL.md:20-21` requires `scripts/observation-rollup.py`. `templates/scripts/` contains only the five older helpers.
- **Impact:** Functional integrity and user-truth verification. A stranger who runs setup into a working folder can later say "show me what you can do" or "roll up observations" and hit missing script paths.
- **Fix:** Add `templates/scripts/menu.py` and `templates/scripts/observation-rollup.py`. Update setup Phase 2.2 to copy seven helpers, verify all seven, and update tests to assert those exact files exist in `templates/scripts/`.

### Finding 3 - Primary channel is asked but not stored

- **Claim:** The new B2C primary-channel path is not persisted because `stack.json` has no `primary_channel` field.
- **Evidence:** `skills/founder-os-setup/SKILL.md:117` asks the main channel question, and `skills/founder-os-setup/SKILL.md:125` maps it to `primary_channel`. `stack.json:6-17` has no `primary_channel`; `stack.json:19-31` has no allowed values for it. `scripts/menu.py:277-287` reads `data.get("primary_channel")`.
- **Impact:** User-truth verification. The team-of-one creator path appears supported but the menu cannot weight Instagram, YouTube, or newsletter after setup.
- **Fix:** Add top-level `primary_channel: null` and `_allowed_values.primary_channel` to `stack.json`. Update Phase 5.0 field list and tests to assert the field is present and writable.

### Finding 4 - Public repo still leaks private-review names

- **Claim:** The required private-context sweep has non-zero tracked matches.
- **Evidence:** `rg -n "Alistair|Aranha|2547468" notes traces --hidden` returns `traces/v121-maya.md:6` and `notes/v1.7-codex-findings.md:39` with `Alistair`.
- **Impact:** No leakage of private or personal context. The brief says each match is critical regardless of size.
- **Fix:** Redact the names or remove the tracked trace/note artifacts from the public release. Re-run the full private-name regex against tracked files before tagging.

### Finding 5 - README and reference docs disagree with the shipped surface

- **Claim:** The first-touch docs still describe an older catalogue, so a clean install can fail its own verify expectations.
- **Evidence:** Live filesystem count is 45 skill folders and 27 command files. `README.md:98` says `### Skills (42)`. The README skill table has 43 skill rows and omits `menu` and `observation-rollup`; the command table at `README.md:168-193` has 26 command rows and omits `/founder-os:observation-rollup`. `docs/skills.md` lacks `queue`, `verify`, and `legal-compliance`; `docs/commands.md` lacks `queue` and `verify`.
- **Impact:** Documentation drift and user experience. `skills/verify/SKILL.md:34-47` checks count consistency, so a healthy repo can report a warning.
- **Fix:** Update README to 45 skills and 27 commands and add the missing rows. Update `docs/skills.md` and `docs/commands.md` to match the live directories.

### Finding 6 - Forward-looking language contradicts final-release posture

- **Claim:** Some docs still imply ARCAS Systems will ship later features.
- **Evidence:** `README.md:202` says `Notion duplication template (planned)`. `README.md:290` says `Company OS layer (planned, not shipped)`. `README.md:321` says the Notion Starter Kit is in development. `skills/query/SKILL.md:143` parks embeddings and graph DBs for a `future version`.
- **Impact:** Documentation drift and maintenance posture realism. The final release says no v1.23 and community forks only.
- **Fix:** Replace future-shipping phrasing with final dispositions: declined, archived design material, or fork-only starting point. Do not imply ARCAS will ship those paths later.

### Finding 7 - Setup can write placeholder-heavy cadence files

- **Claim:** Setup says it personalizes quarterly and annual cadence files, but the wizard does not capture enough inputs and the templates still contain raw placeholders.
- **Evidence:** `skills/founder-os-setup/SKILL.md:322-323` says `quarterly-sprints.md` and `annual-targets.md` are personalized. `templates/cadence/quarterly-sprints.md:3-42` contains placeholders such as `{{QUARTER}}`, `{{GOAL_1}}`, `{{METRIC_1}}`, and `{{DAY}}`. `templates/cadence/annual-targets.md:3-61` contains placeholders such as `{{YEAR}}`, `{{BET_1}}`, and `{{TARGET}}`. `templates/cadence/daily-anchors.md:14-16` leaves `{{ANCHOR_TASK}}`, `{{COMMITMENTS}}`, and `{{DEEP_WORK_WINDOW}}`.
- **Impact:** User-truth verification. A new user can finish setup, run `/today`, and see template tokens instead of a usable operating state.
- **Fix:** Either ask the needed cadence questions during setup or write honest empty-state values such as `[NOT SET]`, then add backlog items for the first daily, quarterly, and annual fill-in.

## Quality concerns (should fix, can ship without)

### Finding 8 - Bootloader still talks as if every user is a founder

- **Claim:** The role substitution is too narrow for operator and team-of-one users.
- **Evidence:** `templates/bootloader-claude-md.md:19` says `who the founder is`; `templates/bootloader-claude-md.md:58` repeats it; `templates/bootloader-claude-md.md:125` says `how the founder wants the OS to behave`. `skills/founder-os-setup/SKILL.md:372-374` maps `team_of_one` to `operator`.
- **Impact:** User experience for the new archetypes. Operator-not-founder and solo creator users get a bootloader that partly reverts to the original B2B founder frame.
- **Fix:** Use a second placeholder for role label, or rewrite those lines as "person running this OS." Map `team_of_one` to `creator` or `solo operator`, not plain `operator`.

### Finding 9 - Legal jurisdiction matching is inconsistent

- **Claim:** Legal setup maps UAE variants to `references/uae`, but the legal skill tells the model to match the literal jurisdiction string to a folder.
- **Evidence:** `skills/legal-compliance/SKILL.md:21-27` gives examples such as `UAE-Dubai-Mainland` and then says to match the string to `references/<jurisdiction>/`. The only shipped jurisdiction folders are `_template` and `uae`. `.claude/commands/legal-setup.md:33-34` says UAE variants use `references/uae/`.
- **Impact:** Functional integrity for legal questions. A hand-written `jurisdiction: UAE-Dubai-Mainland` can cause a false refusal even though UAE references ship.
- **Fix:** Add normalization rules to `skills/legal-compliance/SKILL.md`: UAE, UAE-Dubai-Mainland, UAE-Abu-Dhabi-Mainland, UAE-DIFC, and UAE-ADGM all load `references/uae/`.

### Finding 10 - Private-tag filter is clearer in rules than in writing surfaces

- **Claim:** The central spec is clear, but the four writing surfaces compress it enough that models may differ on mixed-case closing tags.
- **Evidence:** `rules/operating-rules.md:20-33` states the case-insensitive tag rule and procedure. The surfaces only carry a one-line summary: `skills/brain-log/SKILL.md:169`, `skills/knowledge-capture/SKILL.md:150`, `.claude/commands/rant.md:51`, and `.claude/commands/dream.md:60`.
- **Impact:** User experience and privacy. A model reading only the invoked surface might mishandle `<PRIVATE>...</private>`.
- **Fix:** Paste the five-step procedure from `rules/operating-rules.md` into all four writing surfaces or instruct each surface to read that rules section before writing.

### Finding 11 - Weekly review ignores the structured role field

- **Claim:** The operator skip check relies on prose instead of the role token setup writes.
- **Evidence:** `skills/founder-os-setup/SKILL.md:74` stores `role:` in `core/identity.md`. `skills/weekly-review/SKILL.md:124-127` skips the Marketing/Sales/Delivery check based on phrases such as `I report to`, `I'm not the founder`, and `ops manager`.
- **Impact:** User-truth verification for operator-not-founder. A correct `role: operator` can still be missed if the identity prose lacks those phrases.
- **Fix:** Check `role: operator` first, then use the phrase scan only as a fallback.

### Finding 12 - Uninstaller leaves observation hooks behind

- **Claim:** `uninstall.sh` removes old hook names, not the shipped PostToolUse observation hook names.
- **Evidence:** `.claude/settings.json:39` and `:43` register `post-tool-use-observation.sh` and `.ps1`. `uninstall.sh:21-28` lists `post-tool-use.sh` and `post-tool-use.ps1`.
- **Impact:** Functional integrity for cleanup. A user who uninstalls may leave active hook copies behind.
- **Fix:** Replace the two old hook names in `uninstall.sh` with `post-tool-use-observation.sh` and `post-tool-use-observation.ps1`, then add a test that compares hook names against `.claude/settings.json`.

### Finding 13 - Maintenance docs send mixed signals

- **Claim:** Contribution docs say both "we do not merge into this repo" and that docs or skill improvements may be accepted.
- **Evidence:** `CONTRIBUTING.md:25` says `we don't merge into this repo`; `CONTRIBUTING.md:30-31` accepts docs and skill improvements; `CONTRIBUTING.md:35-36` mentions private-repo triage and roadmap fit after final release.
- **Impact:** Maintenance posture realism. A 2027 contributor will not know whether upstream accepts anything beyond critical breakage.
- **Fix:** State one policy: upstream accepts critical breakage, security, and docs that contradict code; all new skills and integrations belong in forks.

### Finding 14 - Observation rollup counts the wrong session key

- **Claim:** Rollup summaries can report `Unique sessions: 0` for real PostToolUse logs.
- **Evidence:** Real hooks write `session` in their JSONL shape, as covered by `tests/test_post_tool_use_hook.py:151`. `scripts/observation-rollup.py:71` counts `session_id`. A hook-shaped rollup produced `Unique sessions: 0`.
- **Impact:** Functional integrity for W4. Users get misleading weekly observation summaries.
- **Fix:** Accept both `session` and `session_id`, prefer `session`, and update rollup tests to use actual hook output fixtures.

### Finding 15 - Dry-run install stops before showing operations

- **Claim:** `install.sh --dry-run` does not preview planned work unless Python 3.11 is already installed.
- **Evidence:** Command: `bash install.sh --dry-run`; output: `[error] Python 3.11 or newer is required.` and no `[dry-run]` operation list. The prerequisite failure exits before the dry-run block at `install.sh:142-145` and planned operations are printed only at `install.sh:152-160`.
- **Impact:** Install ergonomics. A cautious user cannot preview what the installer will do before provisioning every prerequisite.
- **Fix:** In dry-run mode, report prerequisite status but still print planned clone, hook-copy, and target operations, then exit with a clear dry-run status.

### Finding 16 - PostToolUse hook fallback differs by shell

- **Claim:** Bash and PowerShell PostToolUse hooks can write different `intent` values when jq is absent and the input contains embedded newlines.
- **Evidence:** Same escaped-newline input produced PowerShell `intent:"edit brain/log.md - hello world"` and bash `intent:"edit brain/log.md - hello"`. The bash Python fallback emits newline-delimited fields at `.claude/hooks/post-tool-use-observation.sh:84-93`.
- **Impact:** Cross-platform parity and telemetry quality. The same tool call can roll up differently by platform.
- **Fix:** Have the bash Python fallback emit JSON or NUL-delimited fields, then parse those fields without truncating embedded newlines.

## Polish observations (optional)

### Finding 17 - Test substance around observation rollup can be tighter

- **Claim:** The W4 aggregate test checks useful strings but does not parse the rollup as a structured artifact.
- **Evidence:** `tests/test_observation_rollup.py` includes a substring check for `21`, tool names, skill names, and session IDs.
- **Impact:** Test substance. A future formatting change could satisfy the substring while miscounting totals.
- **Fix:** Add a small parser or exact-line assertions for total observations, per-tool counts, skill counts, and unique sessions.

### Finding 18 - `notes/` and old traces are not release-clean

- **Claim:** The final public repo still contains internal review artifacts without a clear reader contract.
- **Evidence:** `git ls-files notes traces` lists tracked `notes/v1.7-*` and `traces/v121-*`. `git status --short --untracked-files=all` lists `.agents/`, five `traces/v1202-*` and `v1203-*` files, plus the review brief.
- **Impact:** User experience and public repo hygiene. A stranger sees development residue mixed with product docs.
- **Fix:** Remove internal notes and old traces from the public tag, or add a short `traces/README.md` that names what is intentionally retained.

## Full-folder second-pass architectural addendum

This addendum is from a fresh read-only pass across the whole folder, not just the v1.22 delta. I used four subagents in parallel for scripts/hooks/install/update, skills/commands, templates/release docs, and test architecture, then verified the highest-risk claims locally before adding them here. I also re-ran `python -m unittest discover tests`; it still ran 247 tests and failed with the same 5 failures listed in Finding 1. `python -m py_compile` passed for the seven root scripts and the three `.github/scripts/*.py` helpers.

### Finding 19 - Default uninstall can delete `stack.json`

- **Claim:** Default uninstall is not preserving all User Layer data because `stack.json` is treated as user-owned by update/setup but removed by uninstall.
- **Evidence:** `.claude/commands/update.md:15` and `:50` classify `stack.json` as User Layer. `skills/founder-os-setup/SKILL.md:467` writes generated tool bindings into it. `.claude/commands/uninstall.md:110` and `:119` delete `stack.json` in default mode. `uninstall.sh:41-44` preserves only `MEMORY.md` and `CLAUDE.md` as files, then removes the install directory at `uninstall.sh:187`.
- **Impact:** Data loss. A founder can run the documented default uninstall, believe personal data is preserved, and lose their local tool bindings.
- **Fix:** Preserve `stack.json` in both uninstall surfaces and add lifecycle tests for every User Layer path named in `/founder-os:update`.

### Finding 20 - `/founder-os:update rollback` has no backup on the normal clean-tree path

- **Claim:** The rollback procedure only restores from a stash that often will not exist.
- **Evidence:** `.claude/commands/update.md:138-140` uses `git stash push` before applying updates. On a clean tree, that command creates no stash because there are no local changes. Rollback then only searches for a `founder-os-update-backup-` stash at `.claude/commands/update.md:91-95`, while the update itself mutates paths from `FETCH_HEAD` at `.claude/commands/update.md:147-148`.
- **Impact:** The command promises rollback support, but a normal successful update from a clean install cannot be rolled back automatically.
- **Fix:** Record the pre-update commit/treeish, create a real backup branch/archive, or copy System Layer paths to a timestamped backup before checkout. Rollback should restore from that reference, not only from `git stash`.

### Finding 21 - Windows SessionStart compliance deadlines do not surface in PowerShell

- **Claim:** The PowerShell hook checks compliance deadlines before its date object exists.
- **Evidence:** `.claude/hooks/session-start-brief.ps1:166` gates compliance output on `$todayDt`, but `$todayDt` is initialized later at `.claude/hooks/session-start-brief.ps1:221`. `tests/test_session_hooks.py:87-112` only parse PowerShell hooks; they do not execute this compliance behavior.
- **Impact:** Windows users can miss overdue or upcoming compliance deadlines even though README promises SessionStart will surface them.
- **Fix:** Initialize `$todayDt` before the compliance block and add a PowerShell behavioral test with due and overdue `context/compliance.md` entries.

### Finding 22 - `/founder-os:brain-pass` cannot run its required preflight

- **Claim:** The command wrapper disallows the tool the skill requires.
- **Evidence:** `.claude/commands/brain-pass.md:4` allows only `Read`, `Grep`, and `Glob`. `skills/brain-pass/SKILL.md:30-34` requires running `python scripts/query.py` before synthesis.
- **Impact:** The slash command says to run the brain-pass skill end to end, but it cannot execute the script-backed preflight under its own tool contract.
- **Fix:** Add `Bash` to `.claude/commands/brain-pass.md` or remove the script preflight requirement from the skill.

### Finding 23 - `forcing-questions` writes after being documented as read-only

- **Claim:** The command reference says read-only, but the skill writes to user data on GREEN and PARK paths.
- **Evidence:** `docs/commands.md:224` says `/founder-os:forcing-questions` is read-only with optional logging. `skills/forcing-questions/SKILL.md:76` writes to `context/priorities.md` and `brain/log.md` on GREEN. `skills/forcing-questions/SKILL.md:80` writes to `brain/decisions-parked.md` on PARK.
- **Impact:** User-truth and approval-gate breakage. A founder can run a supposedly read-only gate and have priorities or parked decisions changed.
- **Fix:** Make the skill chat-only until explicit approval, or update the command docs and require a post-verdict confirmation before any write.

### Finding 24 - The macOS one-line curl install fails on stock Bash

- **Claim:** The public simplest install path is advertised for macOS, but the script requires Bash 4+ while the documented command pipes to default `bash`.
- **Evidence:** `README.md:57-65` recommends `curl ... | bash` for macOS/Linux/git-bash. `docs/install.md:9-15` says the path works on macOS. `install.sh:92-97` rejects Bash versions below 4 and tells macOS users to install a newer Bash.
- **Impact:** A default macOS user running the exact documented command can fail before setup.
- **Fix:** Make `install.sh` compatible with Bash 3.2, or change the macOS documentation to install/use Homebrew Bash before presenting the one-liner as supported.

### Finding 25 - The `<private>` exclusion rule is not enforced across all persistent write paths

- **Claim:** The central privacy rule says all persistent writes must strip `<private>...</private>` blocks, but tests and surface instructions cover only four write paths.
- **Evidence:** `rules/operating-rules.md:9-16` applies the tag to all persistent writes, auto-memory, and future write skills. `tests/test_private_tag.py:14-20` covers only brain-log, dream, knowledge-capture, and rant. `.claude/commands/capture-meeting.md:39-64` writes to `brain/log.md`, `context/clients.md`, `context/decisions.md`, and `brain/flags.md` without a private-tag filter. `.claude/commands/pre-meeting.md:41-49` appends user-provided meeting gate answers to `brain/log.md` without the filter. `skills/founder-os-setup/SKILL.md:247-259` writes auto-memory without naming the filter.
- **Impact:** Privacy. A user can mark sensitive text private in a meeting capture, pre-meeting gate, setup answer, or future write path and still have it persisted.
- **Fix:** Add the same five-step filter procedure to every command or skill that writes user-provided content, and expand tests to discover all write surfaces rather than hard-coding four names.

### Finding 26 - `/founder-os:verify` can report scripts healthy while shipped script-backed skills are missing

- **Claim:** Verify still checks only the old five helper scripts.
- **Evidence:** `skills/verify/SKILL.md:64-76` checks `query.py`, `brain-snapshot.py`, `wiki-build.py`, `memory-diff.py`, and `brain-pass-log.py`. It does not check `scripts/menu.py` or `scripts/observation-rollup.py`, even though `skills/menu/SKILL.md:15-18` and `skills/observation-rollup/SKILL.md:20-21` require those scripts.
- **Impact:** A fresh install can be missing advertised script-backed capabilities while `/founder-os:verify` still prints a healthy script check.
- **Fix:** Include all required runtime scripts in verify, setup copy lists, template mirrors, and script-reference tests.

## Additional quality concerns from the second pass

### Finding 27 - Path B bootloader still names Path A commands

- **Claim:** Manual-clone users are told to use bare commands, but the generated bootloader template still contains namespaced slash commands.
- **Evidence:** `README.md:16` says Path B users should drop `/founder-os:`. `docs/install.md:95-97` repeats that manual clone uses `/setup`. `templates/bootloader-claude-md.md:60` names `/founder-os:voice-interview`, and `templates/bootloader-claude-md.md:109-111` names `/founder-os:ingest`, `/founder-os:lint`, and `/founder-os:wiki-build`.
- **Impact:** A manual-clone user can finish setup and receive a generated `CLAUDE.md` that points to commands that do not exist in their install mode.
- **Fix:** Add command-prefix substitution to the bootloader, or use natural-language phrasing without slash-command forms.

### Finding 28 - Hook registration runs both shell variants unconditionally

- **Claim:** `.claude/settings.json` wires Bash and PowerShell hooks together instead of selecting the current platform.
- **Evidence:** `.claude/settings.json:3-14`, `:18-29`, and `:33-44` register both shell variants for SessionStart, Stop, and PostToolUse. `docs/install.md:170-172` says there is no double-output risk. Only `.claude/hooks/post-tool-use-observation.sh:20-27` has a Windows guard; the SessionStart and Stop bash hooks do not.
- **Impact:** Windows without Bash can see hook command failures, and Windows with both shells can produce duplicate SessionStart or Stop output.
- **Fix:** Use one platform-selecting wrapper, or add guards to Bash SessionStart and Stop hooks so they no-op on Windows when PowerShell is the intended path.

### Finding 29 - Legal answers can mutate reference freshness outside `/legal-update`

- **Claim:** Normal legal Q&A is allowed to update source metadata, bypassing the dedicated update command's confirmation flow.
- **Evidence:** `skills/legal-compliance/SKILL.md:170` requires web search for time-sensitive legal questions. `skills/legal-compliance/SKILL.md:178` then tells the model to update reference files and `sources.yml` after refresh.
- **Impact:** High-stakes reference files can change during an ordinary legal answer, and the user may not realize a system reference set was modified.
- **Fix:** Normal legal answers should report stale-source status and recommend `/founder-os:legal-update`; only the legal-update command should write source freshness metadata.

### Finding 30 - Observation rollup deletes raw telemetry while presenting itself as safe

- **Claim:** The rollup surface is described as safe/idempotent, but the script removes source JSONL files.
- **Evidence:** `skills/observation-rollup/SKILL.md:14` says the operation is safe to run anytime. `skills/observation-rollup/SKILL.md:32` says the source JSONLs are deleted after rollup. `scripts/observation-rollup.py:196` calls `unlink()` on rolled files.
- **Impact:** Detailed observation history is irreversibly reduced to aggregate markdown without an explicit data-loss warning or confirmation.
- **Fix:** Require confirmation before deletion, or move source JSONLs to an archive folder after rollup.

### Finding 31 - Natural-language routing collides across command surfaces

- **Claim:** Generic phrases route to multiple different behaviors.
- **Evidence:** `skills/readiness-check/SKILL.md:4` and `.claude/commands/status.md:2` claim "audit the OS", while `skills/audit/SKILL.md:3` and `.claude/commands/audit.md:2` use the same phrase for the composite audit. `skills/brain-log/SKILL.md:4`, `skills/knowledge-capture/SKILL.md:4`, and `.claude/commands/capture-meeting.md:2` all claim "capture this" or "log this".
- **Impact:** Dictated input can trigger a readiness score instead of a full audit, or write to the wrong capture path.
- **Fix:** Reserve "audit the OS" for the composite audit. Narrow meeting capture to "capture this meeting/call" and add precedence rules for generic capture phrases.

### Finding 32 - Wiki-build command scope drifts from the skill

- **Claim:** The command describes a narrower graph scope than the actual skill.
- **Evidence:** `skills/wiki-build/SKILL.md:30` includes `roles/` and `rules/`. `.claude/commands/wiki-build.md:39` lists only `core/`, `context/`, `cadence/`, `brain/`, `network/`, and `companies/`.
- **Impact:** Users and maintainers can misunderstand what graph nodes should appear.
- **Fix:** Make the command defer to the skill/script scope, or update the command list to match.

### Finding 33 - "E2E critical path" tests are mostly prose checks

- **Claim:** Several tests named as end-to-end coverage do not execute the behavior they claim to warranty.
- **Evidence:** `tests/test_e2e_critical_paths.py:6` says tests verify documented behavior, but setup, verify, queue, and brain-pass checks are mostly `assertIn` checks such as `tests/test_e2e_critical_paths.py:211` and `:234`. `tests/test_queue.py:3` also says it reads files to verify documented behavior.
- **Impact:** Queue transitions, setup copy-list generation, verify scoring, and brain-pass routing can regress while tests pass as long as the prose remains.
- **Fix:** Add executable temp-repo harnesses for queue add/start/done/park, setup copy-list generation, verify healthy/broken fixtures, and brain-pass/query preflight contracts.

### Finding 34 - Legal invariants have no tests

- **Claim:** The highest-stakes surface has no fixture coverage.
- **Evidence:** `skills/legal-compliance/SKILL.md:27` requires refusal/no fallback for unloaded jurisdictions. `skills/legal-compliance/SKILL.md:54` covers source freshness checks. `skills/legal-compliance/SKILL.md:178` covers refresh writes. `rg -n "legal" tests` returns no matches.
- **Impact:** Jurisdiction refusal, UAE alias resolution, stale-source warnings, duplicate source handling, and legal-update confirmation gates can regress without test failure.
- **Fix:** Add fixture-based legal tests for those invariants before final tag.

### Finding 35 - Maintenance and security docs omit current release surfaces

- **Claim:** Final-maintenance docs do not match the install paths and executable surfaces that now matter.
- **Evidence:** `CONTRIBUTING.md:29` asks reporters for install path A, B, or C, while `docs/install.md` defines Path E, A, B, and D. `SECURITY.md:15-18` scopes `skills/`, `.claude/`, `.github/scripts/`, manifests, and hooks, but omits root `scripts/`, `install.sh`, and `uninstall.sh`.
- **Impact:** Post-final bug and security reports can be misrouted or treated as out of scope despite hitting release-critical code.
- **Fix:** Update triage labels to A/B/D/E and include root scripts plus install/uninstall scripts in security scope.

## Positions on the eight known concerns

1. Test timing - Accept the Windows timing, not the failures. A 42 second Windows run is tolerable for a markdown-and-scripts repo entering maintenance mode. Do not delete useful tests only to hit a 30 second wall-clock target. But the current suite fails on this checkout, so patch correctness first and treat timing as non-blocking after green.

2. Amend on session-3 commit - Accept. The amend was unpushed and added release-summary text, so it is not a user-facing risk. The local reflog shows HEAD moved from `e566e5a` to `1688df0` and then to `5f45183`; that explains the mismatch between the user prompt and the brief. Review target should be the checked-out HEAD, `5f45183`.

3. Untracked files - Do not commit them as-is. `.agents/` duplicates command-skill wrappers and the old v1202/v1203 traces are development residue. Delete or ignore them before tagging. Keep `traces/v122-codex-final-review-brief.md` only if the repo has an explicit trace-retention policy; otherwise do not tag it.

4. Aggregates test strength - Strengthen it. The present test is better than a file-exists check, but substring matching is too weak for a final maintenance tag. Assert exact total, per-tool counts, skill counts, and session count.

5. Private-tag case-insensitivity - Patch the four writing surfaces. The central spec is clear enough, but an invoked command body should not require the model to remember the rules file. Mixed-case pairs like `<PRIVATE>...</private>` should be explicitly accepted anywhere the filter is documented.

6. Team-of-one archetype coverage - Not fully covered. The role question and subscriber-list option are real, but `primary_channel` is not stored and team-of-one is mapped to `operator` in the bootloader. That path is better than v1.21 but not final-release safe.

7. Legal-compliance scope honesty - The scope is honest overall. The skill clearly says UAE ships as the worked reference set and non-UAE jurisdictions must load sources. The bug is not overclaiming; it is folder normalization for UAE variants.

8. notes/ and notion-package/ presence - `notes/` should not be in the public final tag unless there is a README explaining why review notes are product artifacts. `notion-package/` can stay only if it is framed as archived design material or fork input, not an in-development path ARCAS will later ship.

## Confidence

High confidence on the critical findings above. I read the brief end to end, ran the full test suite, ran key scripts directly, checked install/uninstall dry-run behavior, swept for private-name matches, counted live skills and commands, inspected plugin manifests under `.claude-plugin/`, traced setup, stack, menu, legal, weekly-review, and the private-tag surfaces, and used four subagents for parallel checks across scripts/hooks, skills/commands, templates/release docs, and test architecture.

Gaps: I did not complete a fresh network clone from GitHub because this checkout already contained the target commit and local untracked artifacts. I did not run a real macOS machine; the Bash 3.2 issue is inferred from the documented command and the script's explicit Bash 4 gate. I did not run a live Claude Code plugin install/uninstall cycle; lifecycle findings are from command/script source inspection plus test evidence.

## Final recommendation

SHIP WITH PATCHES. Patch Findings 1 through 7 and 19 through 26 before tagging v1.22.0. Findings 8 through 18 and 27 through 35 should be fixed in the same patch if time allows because this is the final feature release, but they are not enough on their own to block the tag once the critical set is closed.
