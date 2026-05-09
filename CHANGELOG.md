# Changelog

All notable releases. Format follows the user-value-first commit naming rule (`rules/commit-naming.md`).

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

Hotfix from a two-pass external review. Three things closed: the wizard's final orientation handed Path B users namespaced commands that do not work on a manual clone, the README plus install doc under-instructed Cowork users on what does and does not fire there, and the orientation tone across the wizard and install doc led with slash commands the way technical docs do - but real founders will not memorize a 20-command surface. The orientation now leads with natural-language phrasing ("say 'set up my voice profile'") and treats slash commands as parenthetical shortcuts for power users. Same release also fixes a self-introduced rendering bug found while applying the tone rewrite (the prefix substitution would have rendered without a leading slash on Path B). No script changes.

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
- WSL bash verification: confirmed clean by the v1.19.1 review pass. The reviewer ran the suite under a `bash` that resolved to `C:\Windows\system32\bash.exe`, got 51/51 OK, and reported the converted hook path as `/mnt/c/arcas_dev/ARCAS/founder-os/.claude/hooks/session-start-brief.sh`. v1.19.2 keeps that path and adds the round-trip fix on top, so 52/52 should pass on WSL too.
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
- **Banned-style polish.** Eight "unlocks" / "leverage (verb)" / "optimize" instances replaced with plain alternatives across user-facing prose.

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
