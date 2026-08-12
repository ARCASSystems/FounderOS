# Changelog

All notable releases. Format follows the user-value-first commit naming rule (`rules/commit-naming.md`).

## v1.53.1 - 2026-08-12

Three advertised install paths failed and blamed the founder for it: a correct plugin install was told to reinstall, a git-less ZIP install was refused connectors for a reason that was false, and a missing version marker became the founder's homework. An outside review of v1.53.0 caught the pattern; this patch closes it. Pack: `updates/1.53.1-your-install-was-right-all-along.md`.

### Fixed - setup finds its own instructions on a plugin install

The setup command resolved its wizard relative to the working directory, which on a plugin install is the founder's own folder - empty on purpose. It now resolves from the plugin engine first (`${CLAUDE_PLUGIN_ROOT}`, then a search of the plugin directory), falls back to the working directory for clone and ZIP installs, and when nothing resolves it suggests a restart instead of telling a correctly-installed founder to reinstall. The verify and own-your-history skills stop hardcoding one plugin path for the same reason: plugin managers move their folder layout between versions, and a wrong guess read a healthy install as broken. Own-your-history also now stops before the first save if it cannot find the operator ignore file, because a first save with no ignore rules writes secrets into history permanently.

### Fixed - connectors work with no git installed

`set-secret` proved "this file can never be committed" by asking git, and on a machine with no git the failed question read as "not protected" - so every connector was refused on the exact path the README advertises as needing no git, with a message blaming a file that was configured correctly. Where a repository exists git still answers; where none does, the shipped `.gitignore` is read directly and the target must match a line of it exactly. Same pass hardened the writer: a target carrying folder parts is refused outright instead of quietly landing at `.env`, and a newly created secrets file is user-only where the platform supports it.

### Fixed - a missing version marker routes to repair, not to the founder

"Update Founder OS" on an install with no VERSION file replied "Create VERSION with the current plugin version and re-run", which a non-technical founder cannot act on. Missing now means `unknown`: the update says it cannot tell what is installed, refreshes the engine to the current release, restores the marker, and skips only the guided walkthrough of what changed, since there is no known starting point to walk from. Full deleted-file repair waits on the install manifest (`scripts/repair_install.py`); the command names that boundary so the next builder knows what completes it.

### Fixed - the privacy guard no longer suggests blocking your own name

The own-your-history flow offered to add the founder's own name to the private-name patterns. Their name lives in the identity file by design, so the very first save failed right after they said yes to a privacy feature. The guard is now offered for what it is for - names that must never enter the files at all, a client under NDA - and the skill expects most people to skip it.

### Docs - install claims match the code

The plugin registers slash commands, not hooks; hooks are wired by setup into the OS folder and fire when Claude Code opens there. `docs/install.md` said hooks register automatically across every project - three places, all corrected, plus an honest "How hooks fire on Path A" paragraph. The curl installer printed `/founder-os:setup` on a path where commands are bare (`/setup`), and claimed a piped re-run asks a question it cannot read; both now match `install.sh`. The setup reference derives its helper count from disk instead of a hand-maintained number that had already gone stale.

Counts unchanged: 95 skills, 45 commands, 847 tests.

## v1.53.0 - 2026-08-11

A founder spent four chats looking for work that had never moved, then could not read the answer she was given. `/founder-os:where` answers "where is my work" with the project and the folder in her words, and names every folder that exists on one computer only. Pack: `updates/1.53.0-find-your-own-work.md`.

### New - `where`, the answer to "I cannot find my work"

`python scripts/where.py` walks the install once and groups recent work by project, newest first, naming the folder the way a person would name it. The OS's own machinery is excluded and the brain and operating files collapse to one line, because burying the answer under sixty skill files is how the previous answer became unreadable.

The second half is the part nobody asks for. A project folder git has been told to ignore is invisible to every safety net the OS has, so the work at the highest risk of vanishing was the work nothing ever mentioned. Every folder now carries an explicit line: backed up, or exists only on this computer. A ZIP install with no version history says so rather than staying silent, since silence reads as reassurance.

Read-only, standard library, no key. It opens nothing, moves nothing, renames nothing, and it never reorganizes what it found - a founder asking where something is has not asked for a tidy-up, and a tidy-up is what makes the next search harder.

### New - the register is enforced in the skill, not left to judgment

`skills/where/SKILL.md` carries the real failed answer and the working answer side by side, and bans the vocabulary that broke the first one: System Layer, User Layer, untracked, gitignored, the remote. Every one of those was accurate. None of them is English. The skill also fires unprompted when a founder says work has gone missing and the assistant is about to explain the folder structure instead - that explanation is the failure, not the fix.

### Docs

New `where` entries in `skills/index.md`, `docs/skills.md`, and `docs/commands.md`; the script joins the setup copy list so a fresh install receives it. Counts to 95 skills and 45 commands. Suite 840 -> 847.

## v1.52.0 - 2026-08-10

A seat's read-list can finally grow. Tag a knowledge note with the seats that should read it and each one gets a pointer to it - never its contents - folded into its own instruction sheet. Decline once and the decline is recorded, so the question never comes back. Pack: `updates/1.52.0-the-brain-feeds-the-team.md`.

### New - the knowledge fold, one optional frontmatter field

`brain/knowledge/*.md` may carry `seats:`, and `scripts/agents_sync.py` folds a `## Knowledge routed to you` section into the agent file of every seat it names: one line per note carrying id, topic and path. Never a sentence of the body - the seat opens the file when it runs, which keeps the knowledge layer's do-not-hard-parse rule intact and stops a long note becoming a long prompt. Capped at 20 per seat, most recently captured first, with an overflow line naming how many more are tagged, because a silent truncation reads as completeness.

Three states, and the third is the one that earns the release. Absent means never reviewed. A list of ids means routed. `seats: none` means reviewed and deliberately routed to nobody - the tombstone that records a decline. Without it every declined note returns every morning, which is how a person learns to ignore every question the OS asks, including the ones that mattered.

### New - two propose surfaces, neither of which tags anything on its own

`knowledge-capture` compares a new note's subject against each registry row's `job_description` and proposes at most ONE seat in one line. No obvious match, no question. `morning-loop` gains a lowest-priority candidate class: one untagged note per run, ranked behind everything that moves real business state, only when a slot is free after the real asks, and never at stage 1 of a fresh install. Both write on the answer - a yes writes the ids and runs `apply`, a no writes `none` - so the field's state is itself the record that the question is closed.

### Changed - no new file-ownership logic, and that is the point

The fold happens inside `render_agent`, so v1.50.1's body digest already covers it: tagging a note flips the seat to `[stale]`, `apply` converges, and a seat file the operator edited stays `[modified]` and is never clobbered. A `seats` id matching no live row renders nothing and is reported by `check` as a non-fatal `[dangling-tag]` - the bad-wikilink treatment, never auto-cleaned, because a retired seat's notes should still be tagged if the seat comes back. `compute()` and both subcommands take `--knowledge-dir`; a missing directory is a valid install, not an error.

An install with zero tagged notes renders **byte-identical** agent files to v1.51.0. That is asserted by a test, not hoped for.

### Changed - the assistant's charter matches the grant its skill declares

`morning-loop` now declares `Bash(python scripts/agents_sync.py:*)` in `allowed-tools`, so `templates/roles/employees.yaml` grants it on the `daily-assistant` row and names the knowledge note's seats field in `may_write`. The charter audit reads both directions and would have failed the build otherwise.

### Docs

`rules/digital-employees.md` and its template copy carry the read-list-grows doctrine with the three-state table. `templates/brain/knowledge/README.md` documents the field beside the note shape. README carries the feature line and the status line; `skills/index.md` carries the header clause. Suite 830 -> 840.

## v1.51.0 - 2026-08-07

The security story now fits on one page you can read before any yes - and the page survived the same outside review as v1.50.1, which rewrote its first draft in six places until every claim matched the code. Pack: `updates/1.51.0-what-leaves-your-machine-on-one-page.md`.

### New - `rules/security-baseline.md`, the security picture on one page

What leaves the machine, surface by surface, each row with its named recipient, trigger, and default state: the model session (the one constant of a hosted model), cloud sessions, each voice tier with its local port and key location, the scrape helper request by request, in-skill web fetch and search, GitHub operations through `gh`, connectors, and git push. Then connector and MCP trust in plain words, where secrets live (`.env` and `.mcp.local.json`, gitignored, enforced by the connect helper), and the guard chain - framed honestly as a rejection layer, not proof: hooks can be bypassed and CI runs after push, and the page says so instead of rounding up to "can never happen".

It closes with the five questions to ask before any yes - the same five the `hire` passport prints, written down as your own checklist for anything that wants in from outside. The page also says plainly which protections are rules the assistant follows (one yes per capability) and which are mechanical (the id validation, the digest ownership check, the secret scanner), because knowing the difference is the informed half of informed choice.

Referenced where the decision actually happens: the `hire` passport's WHAT LEAVES HOME line, SECURITY.md (everyday picture vs vulnerability reporting), the README's local-first section, and llms.txt. Ships verbatim in `templates/rules/` like every other doctrine file - it describes the machine, not the founder.

## v1.50.1 - 2026-08-07

The first outside review of v1.49.0 and v1.50.0 (an independent CTO pass over the full range, run before any new public building) returned 18 findings; every reproduced one is fixed here. Pack: `updates/1.50.1-what-the-first-outside-review-caught.md`.

### Fixed - a seat id is a filename, never a path

A registry row with an id like `../../README` used to write OUTSIDE `.claude/agents/` and could overwrite a repository file while reporting success. Ids are now validated at load (lowercase letters, digits, inner hyphens, max 64), duplicate ids are rejected, and a mechanical containment check refuses any write or delete that would land outside the agents folder.

### Fixed - the secret scanner no longer prints what it says it hides

A line carrying both a secret and a second violation (an em dash, a private name, an attribution trailer) was echoed raw by the second finding - the scanner printed the very value its secret finding hid. The secret check now runs first on every line, and when it fires the whole line is hidden for every finding on it.

### Fixed - your edits to a generated agent file survive

Ownership used to be the marker line alone, so any edit you made below it was silently clobbered on the next apply and deleted on retirement. The marker now records a digest of the generated body: an edited file is reported `[modified]`, fails the exit code, and is never overwritten or deleted. A hand-written file shadowing a rostered seat now fails `check` too, instead of hiding under a success line.

### Fixed - a correction has to be aimed at the OS to be captured

Quoted feedback ('The client wrote, "you already asked me that"'), reported speech ("I told Alex to get to the point"), and long narrative containing a correction-shaped phrase no longer register as corrections of the OS. Every correction shape now sits behind the short-reply gate, a quotation guard, and a reported-speech guard - conservative on purpose, because a false capture that survives an accidental yes becomes a standing behaviour change.

### Fixed - a fresh install can talk to its starter team

Setup copied the registry and the generator but never ran it, so the five advertised roles existed as rows nobody could dispatch by name. Setup now runs `python scripts/agents_sync.py apply` then `check` right after the registry and scripts land, and stops loudly if either fails.

### Fixed - the unwatched-run count stops guessing

`agent_runs.py summary` subtracted verdict totals from run totals, so an old, duplicate, or queue-level verdict could mark an unreviewed run as watched. Every run now carries a `run_id`, a verdict recorded with `--ref run:<id>` names the run it grades, unwatched counts the runs no verdict names, and verdicts tied to no run are reported separately. `employee-review` now reads the run log as first-class evidence and refuses a review only when verdicts, filed items, AND run rows are all empty.

### Fixed - the documented failure path records the failure

The generated closing act and all five starter skills' run-record blocks omitted `--read`/`--produced` and told a failing run to record without the `--could-not` reason the script requires - so following the instructions on a failure produced an error and no record at all. All seven surfaces now show the working form. Also in this pass: the remote-safety guard matches only the public FounderOS repository instead of every ARCASSystems repository, the generated agent files make the no-external-calls rule conditional on the row's own `never` field instead of contradicting connector-carrying charters, and `hire` now states plainly which of its gates are procedure and which are mechanical, running the charter audit as an explicit step of every hire.

## v1.50.0 - 2026-08-06

The team gets one door to grow through, and every seat becomes someone you can talk to. v1.49 gave the team a memory of its own runs; this closes the loop the operator actually feels: how a new team member comes to exist, right-sized, and how you manage one without learning a second system. Pack: `updates/1.50.0-the-team-grows-through-one-door.md`.

### New - `hire`, the Chief of Staff's door

Say "I need help with X" or "this keeps eating my week" and the OS answers as an org designer, not a chatbot. The `hire` skill walks a six-rung shape ladder - an answer, a preference line, a skill, a script, a chartered seat, a team - and picks the SMALLEST shape that removes the job, with one sentence on what the next rung up would have bought. That sentence is the anti-naivety half of the feature: most recurring pains die at rung one to four, and a user who is told that, with the reason, can trust the one hire that is proposed. The doctrine bar stays honest (a job that recurred three times and was corrected twice), hiring ahead of it is the operator's explicit call and is recorded as such, and a rung-6 "team" is refused when one seat would do.

Every proposed hire ends with an informed-choice passport before the yes: what it may touch, what it never does, what it costs to run, what leaves the machine (nothing, unless a connector is named), and how to fire it. A yes given without those five things is not consent, it is hope - and the users this OS is for are often new to all of it. The same rule covers outside capabilities: a plugin pack, an MCP connector, or a tool is proposed with its exact source and its own passport, one yes each, never installed silently.

A team, when one is actually earned, is a workflow whose handoffs you can read: one seat per judgment stage, deterministic stages kept in code, and each stage's read-list naming the previous stage's output - so `python scripts/agent_runs.py list` reads back as a relay, who did what, in what order, where the baton was dropped. Builds route to `skill-creator` (which has carried the process-to-team design rules since v1.48); `hire` decides what should exist, it does not duplicate the builder.

### New - every seat is an addressable agent, generated from its row

`scripts/agents_sync.py` generates one `.claude/agents/<seat>.md` per non-retired row in `roles/employees.yaml`: the job, the measure, the read-list, the charter's tools verbatim, the prohibitions, the honest status, and the run-record closing act. The registry stays the single source - you manage a team member by editing their row, not by maintaining a second file that quietly disagrees with the first. `check` reports drift and fails loud, `apply` converges, a retired row's agent file is removed with it, and a hand-written agent file is named and never touched. Firing a seat is one line: set the row to retired, run apply.

### Fix - the doctrine no longer disagrees with itself

v1.49's run-log section landed in `templates/rules/digital-employees.md` but not in the repo-root `rules/` copy an in-place install actually reads. Both copies now carry it, plus the new shape-ladder section, and they are identical again.

## v1.49.0 - 2026-08-05

The OS starts learning how you want to be worked with, and the team starts keeping its own record. Both answer the same question: what can a folder of files do that the memory in a chat app cannot? Not more memory. Memory that lands where it gets read **before** the OS acts, in a file you can open and argue with. Pack: `updates/1.49.0-it-learns-how-you-want-to-be-worked-with.md`.

### New - a behaviour layer that fills from your own corrections

`core/working-preferences.md` records how you want to be worked with: decide for me or give me options, show the working or just answer, what never to ask twice, what a normal answer looks like, what "done" means, and anything the OS proposed once and got told off for. It is read before output, the same way `core/voice-profile.yml` is read before anything is written. That is the whole difference between this and a memory a model might recall after you complain.

It ships empty on purpose and fills one line at a time, and every line carries the date and the sentence it came from. No row without evidence, and no row without your yes: sessions may propose, only you promote. The capture hook classifies a fifth prompt shape - a correction of how the OS is working ("too long", "you asked me that already", "just pick one") - and routes it the way a name correction already routes: applied in that same reply first, then offered as a saved row in one line. `/founder-os:dream` gains a fifth target class for preferences found in rants; because it runs unattended, its candidates land in a **Proposed** table and wait for the morning loop to ask. Nothing in Proposed ever gates output.

Read points, because a layer nothing reads is a diary: the bootloader every session, `brain/.snapshot.md` (which nine output-producing skills already read), `founder-next-move`, and `morning-loop` - which reads it as a gate on its own questions, since a loop built to stop asking answered questions failing at exactly that would be the worst version of this. The session brief counts proposed rows and stays silent when there are none. Every read point carries on without the file, which is the normal state of a fresh install.

The bar it is built to clear is the one `context/names.md` already clears: **the same correction should never have to be given twice.**

### New - the runner records the run, so you stop being the recording device

`run_record_source` on every org-chart row used to be a sentence naming a place, and nothing wrote there. So the only trace a job left was a verdict you typed, and a verdict only exists for a run you were watching. That made the verdict ledger a sample biased toward the runs you happened to see, read by `employee-review` as if it were the record. A job that misbehaved quietly, in the runs nobody watched, was invisible to the machinery built to catch it.

`scripts/agent_runs.py` writes one line per run to `brain/agent-runs.jsonl` as the job's closing act: what triggered it, what it read, what it produced, how it ended, and what it could not do. Append-only, standard library, no key, and it refuses money amounts and contact details outright the way the provisional-fact ledger does. `refused` is a first-class outcome rather than a failure, because a propose-only job declining under its charter is the charter working. `employee_verdict.py render` now shows runs beside verdicts so the gap is readable - fourteen runs, three graded - and `drift` reports an `active` row the run log has never seen, which is the check `active` always claimed to mean. All five starter roles carry the grant on both sides of the seam, charter and skill, and the charter audit holds them together.

Two limits stated in the doctrine rather than implied away: a run line says a run happened, never that its output was good, and a job that does not record cannot be told apart from a job that did not run - which is why the drift finding names both possibilities instead of picking one.

## v1.48.1 - 2026-08-05

The voice patch. An end-to-end review checked the optional voice layer's claims against the code and against the live vendor APIs instead of against its own documentation, and four things failed. Pack: `updates/1.48.1-voice-that-works-on-day-one.md`.

### Fix - the paid mouth was broken on arrival

`add-mouth`'s ElevenLabs engine asked for `eleven_monolingual_v1`, which the vendor has retired: the live API answers `400 unsupported_model, deprecated and no longer available`. Anyone who paid for ElevenLabs and wired the premium mouth got a failed request and no reason. The model is now `eleven_multilingual_v2`, verified against a live key, overridable as `"model"` in `voice/mouth-config.json`, and the failure message separates the two real causes: a retired model id (400) or a voice that needs a paid plan (402). The realtime installer's usage example had the same class of defect - it showed `--model gemini-live-2.5-flash-native-audio`, a name no key returns - and now names the real one. Both tier docs stopped presenting model ids as facts: they carry the date they were checked and point at `python voice/live_server.py --models`, which is the only source of truth that belongs to your key.

### Fix - "set up my voice" now lands in the right skill

Voice means two different things in this OS. `voice-interview` captures how you WRITE, the profile every writing skill reads. `add-voice` installs SPEAKING and LISTENING. Their trigger phrases overlapped almost exactly ("set up my voice" against "set up voice"), and neither named the other, so the same sentence could open either one and a first-timer could end up installing a runtime they never asked for. Both descriptions now claim their own half and name the sibling, `add-voice` asks a one-line check before installing anything when the phrasing was ambiguous, and the voice-interview opening says plainly that it is not the talking-out-loud one.

### Fix - the realtime privacy line now matches what the code does

The docs said your files and the answers read from them stay local, and only the conversation leaves. Half of that was true. When the realtime front asks your local brain a question, the answer is sent back into the cloud session so the front can speak it, so the slice of your brain you hear read aloud has been to the model. The skill, the disclaimer, and the architecture note now say it the accurate way: the file stays home, the sentence does not, and a fact too sensitive for a cloud model should be asked in text or on Tier 0-local. The same section carries the lesson from the private build that has run this loop longest: a system prompt asking a model to be discreet is a request, not a guarantee, and this layer ships no outbound filter.

## v1.48.0 - 2026-08-05

The arrival release. v1.47 fixed how the OS reads its own past; this one fixes the front door. The thought process, in one line: we watched how people actually arrive - real first-time users pitching ideas the way they would to any chatbot, an operator asking for a team of single-job assistants for her creative process, founders with years of notes already on disk - and the OS assumed someone they are not: a founder with a business, a terminal, and no history. Every change below is one of those real arrivals getting a door. Pack: `updates/1.48.0-the-door-is-a-double-click.md`.

### New - download, extract, double-click

`Start Founder OS.bat` (Windows) and `Start Founder OS.command` (Mac) ship at the repo root. Double-clicking opens Claude Code in the folder and starts the setup wizard talking; on a set-up install the same double-click just opens your OS - it is the standing front door, not a one-shot installer. Missing Claude Code gets a plain-language pointer and the download page, never a bare error; missing Python gets a heads-up before the wizard would have found it twenty minutes in. The honest limits ship in the files and the docs: the start file cannot install Claude Code or the paid plan, Windows may warn once about a downloaded script, and macOS wants right-click-Open on first run. Both files are plain text and say so, both were verified live with a stubbed `claude` on both branches, and the `.command` carries its exec bit through GitHub's ZIP so a Mac extract is double-clickable. The wizard copies both into fresh plugin-path OS folders too, so every install shape ends double-clickable.

### New - setup can adopt the notes you already have

The most common real arrival was the one setup did not model: an existing Obsidian vault or markdown folder with years in it. The wizard now has an adopt path ("set up Founder OS inside my vault", or one follow-up question when you name Obsidian or local files as your knowledge base). It moves the OS in next to your notes under four hard rules: create only what is missing, never write over an existing file (an existing CLAUDE.md is shown as a diff to accept or decline, like an update), ask once per collision, and name back what was left untouched. The wiring is stated honestly at setup and in the new `docs/adopt-existing-notes.md`: Claude reads any note on demand and your `[[wikilinks]]` keep working, but structured search (timeline, ID lookup, brain pass) covers the OS's own folders - the bridge is "capture this", adopt-as-you-go, not a silent promise of indexed history.

### New - "I have an idea" is now a real front door

Watch a first-time founder - often a student - open any AI chat: they pitch the idea itself ("people wait in lines for hours, my solution is an app where..."), and they get what a chatbot gives: a startup layout, a course, a feature list. The OS's propose engine always knew the right answer for that stage (name one real customer, talk to five of them this week, no building yet) but nothing fired on how these users actually speak. `founder-next-move` - one of the five natively-discoverable skills - now triggers on "I have an idea", "is this a good idea", "help me validate my idea", and the raw pitch itself. It parses the pitch the way the wizard parses a ramble (problem = customer clue, solution = venture, their words = stage evidence), offers to capture it, and answers in their vocabulary with a move that needs a phone and no money - never a business plan, never a refusal that sends a 19-year-old back to a generic chatbot.

### New - "turn my process into assistants" builds a team the way a real operator specced it

The ask arrives in work vocabulary, not tool vocabulary: an operator describes how she produces a deliverable - research, then a mood board, then the activation concepts - and wants named single-job assistants, one per step. `skill-creator` now fires on that ask and carries her design rules, taken from a real working session: capture the process in the operator's own words before building (sop-writer or a pasted voice-note transcript), one job per assistant so a bad output blames the employee and not the team, the human keeps the taste decisions (the assistant researches and presents options, the operator picks), effectiveness before efficiency (run it manually until it produces what you would have, only then scale), and a seat is earned then registered in `roles/employees.yaml` with an honest charter. `AGENTS.md` gained the other half: any connected agent doing recurring work - an SEO engine, an outreach drafter, a video pipeline - is a candidate employee under the same contract: charter is the grant, propose-only or draft-only stated, runs recorded, seats earned, and nothing ever sent on the operator's behalf. `GEMINI.md` points its agents at the same section.

### Fix - coming back after weeks reads as a welcome, not a wall

Use it three days, disappear five weeks, return: the old brief opened with every flag, decay item, and stale warning at once - at exactly the moment the product should be gentlest. Past 14 days of log silence the SessionStart brief now compacts to a welcome naming the gap, the queue, a flags count ("waiting, not lost" - counts, never the item-by-item list), and one offer: "catch me up", or just start. Two lines are deliberately kept at full strength because they do not pause for absence: stale cadence (it gates planning) and overdue compliance deadlines.

### Fix - people research carries sources, or says it is unverified

`meeting-prep` researched the person across the table (new-prospect research, thin-context web search) with none of the claims discipline v1.46 installed everywhere else - and a wrong fact about a human is the research error the founder repeats to their face. Researched facts in a brief now carry `(source: url, date)` inline, a same-name check runs before anything is attributed to the person (name collisions are the classic failure), and anything unsourced is written as "unverified - confirm on the call", which turns a landmine into a discovery question.

### Fix - the synced-folder capture channel now comes with the actual steps

`docs/capture-anywhere.md` recommended pointing a phone at "your cloud-synced OS folder" - but a default install is not synced anywhere, and the doc never said so. It now walks the five-minute setup honestly: move the OS folder into the cloud folder (with the one-machine-at-a-time rule stated plainly), the two-action iPhone Shortcut, the Android folder-pairing route, and email-to-self named as the zero-setup fallback when a platform fights back.

## v1.47.0 - 2026-08-04

The it-remembers-correctly release. A three-way audit (user experience, architecture, data retrieval) ran over v1.46.0 with every key claim verified by executing the shipped scripts, and everything fixable inside the existing machinery shipped the same night. Pack: `updates/1.47.0-it-remembers-and-correctly.md`. The one-line thesis: the OS filed things well and read them back badly, and every fix below is one of the two directions of that.

### Fix - the memory the OS reads is now actually current

Twenty-five skills read `brain/.snapshot.md` as "the operator's state right now", and nothing ever refreshed it - so from day 2 every draft, proposal, and triage was aimed at week-old flags presented as today's. Two-ended fix: every reader now checks the snapshot's `date:` line and regenerates past 3 days (three skills whose tool grant deliberately excludes shell access report staleness instead of fixing it silently), and the Stop hook regenerates the snapshot after every session's writes, so the ordinary case never even hits the check. The snapshot also gained the block that was always missing: active patterns from `brain/patterns.md` - the one file that records what the OS has LEARNED (3+ repetitions, evidence, impact) previously reached no output-producing skill at all. And the five pack front doors (pipeline, content, delivery, decisions, linkedin), the first thing a user hits, now read the snapshot before routing instead of cold-starting at the exact moment the user is judging the product.

### Fix - the archive, the rants, and the misspelled name stop being silent losses

`log-archive.py` ages entries into `brain/archive/` - and the search scope excluded `archive`, so at the shipped 300-line cap a six-month user had most of their history invisible to keyword search, to timeline, and even to exact-ID lookup, which returned an honest-looking "not found" for an entry sitting on disk. Archive is now in scope for all three query modes. Same class: `catch-up` files every mobile and inbox capture into `brain/rants/`, which the index skipped unless the question contained a magic word ("rant", "dump") - raw captures are now always searchable at a score penalty, so a distilled entry outranks the dump it came from but the dump is never invisible. And the names glossary, which corrected spellings at capture time and was never read at ask time, now expands the question: asking about "Janice" finds facts filed under "Jansi", and a near-miss name in a no-match result gets a "Did you mean" line (stdlib difflib, same free-tier floor).

### Fix - the entry is the retrieval atom, not the file

Timeline mode dated whole files by frontmatter-or-mtime, which stamped every brain file "today" and made "what happened in March" structurally unanswerable. It now parses the dated entry headings already on disk, so one file with entries months apart returns only the in-window entries, each with its own date and ID - plus `--from`/`--to` for a direct date-range question. Index mode stops citing the file's first ID for a match 200 lines down: the citation is now the entry that actually matched. And one shared regex (`scripts/_common.py`) now parses every shipped heading form - the audit found `menu.py` pinned to a form no writer produces, so its recent-log reader returned empty forever, the audit nag never cleared, and a six-month veteran still rendered as day-one zero-state. A parity test holds the brief hook's literal copy identical.

### Fix - day one stops contradicting the README

Fourteen verified paper cuts, the class that makes a stranger quit: the README's own first-session card promised "every one works on a fresh install" while its draft prompt hard-stopped on the voice gate (reordered and told honestly); Windows "Extract All" nests a folder inside a folder and nothing said to open the inner one; ZIP users were handed `/founder-os:`-prefixed commands their install does not have; `/next` and `/update` refused to run on data-folder installs by testing for a plugin file setup never creates; "40 min total" setup is honestly about 90 (it now says so, with a stopping point); day 2 opened with a jargon scold about a stale "anchor" (now an offer in plain words); day 1's `/today` rendered a screen of `[NOT SET]` placeholders (now a warm one-question start); the seeded example entries surfaced as Review Due with nothing saying they are demos (they now label themselves); the quarantine line pointed a non-technical user at a file that opens with PowerShell (now: say "what broke" and the OS explains); every session ended with `FOUNDER_OS_OBSERVATIONS=1` shell jargon (silent unless enabled); the curl installer silently auto-updated when piped (now refuses without an explicit env yes) and could not find Windows' `py -3` Python; the update command could stall on its own `state/` scratch folder and used `base64 -d` before curl on boxes that lack it; and the wizard disagreed with itself about how many scripts it copies.

### Fix - the health check can finally see the sharpest silent failure

The five natively-discoverable skills - the ones that fire when you describe a situation rather than name a command - stop firing the moment their source drifts from the `.claude/skills/` copy, and `/verify` reported PASS through exactly that state (live at audit time: 5 of 5 drifted). Check 9 now runs `skills_sync.py --check` and fails loudly with the one-command fix. Retrieval misses also stopped impersonating evidence of absence: "No matching knowledge files found." in proposal and analysis output - which reads as "no knowledge exists" when the truth is "my keyword matcher missed" - now names the searched terms and points at the deeper pass.

## v1.46.0 - 2026-08-02

The truth-about-our-own-numbers release. Capture-side honesty already shipped: a name or an amount heard once waits as unconfirmed until you confirm or cut it. This release covers the other direction - what the OS produces when it researches, sizes, prices, and analyses. Pack: `updates/1.46.0-tells-the-truth-about-its-own-numbers.md`.

### New - three claim tiers and a script that reads the document back

A verification pass over a real seven-document AI-assisted research pack found about 40 suspect claims in four repeating classes: precise statistics with no source, verbatim quotes attributed to people that appear nowhere findable, universal negatives nobody can verify, and arithmetic that does not reconcile - one cost row off by 11 percent in a table whose other nine rows were right. `rules/research-integrity.md` defines the answer: every load-bearing claim carries `[MEASURED]` (the artifact and the command that re-derives it), `[SOURCED]` (one live URL and the retrieval date), or `[ESTIMATE]` (the assumption stated inline so a reader can swap it). Two hard rules sit on top: a quote carries a retrievable link and date or it is deleted, and "no tool does X" gets rewritten as the bounded search actually run. `scripts/claims_check.py` is the second pass - standard library, no key, warn-first, never edits the document. `strategic-analysis`, `unit-economics` and `proposal-writer` name the rule; `ship-deliverable` gained Link 3.5 to run it on research-class deliverables. The reviewer is deliberately not the writer.

### New - self-diligence, the investor read of your own venture

Say "what would an investor ask me about this business" and the OS scores five dimensions - market potential, differentiation, team, business model and commercial path, readiness for the conversation - against evidence in your own files, then produces a SWOT, the critical challenges, a disclosed-gaps section, and the questions a diligence analyst would ask. The rule the whole skill rests on: anything the files cannot ground becomes a question to you, never an invented answer and never a hedge. No evidence is not a middling score, it is reported as unscored with the question that would fix it. The disclosed-gaps section is a feature rather than an apology: a real diligence analysis of a pre-seed company named audited-downward metrics, an honest coverage ledger, and a named known-risks section as the reason its confidence went up.

### New - entity folders, so an identity thickens instead of sprawling

A person, venture or topic starts as one file in `context/entities/`. When it outgrows one file - size, touch frequency, or you say so - `scripts/entity_check.py` proposes promotion to a folder with a fixed shape: `profile.md` holds the current read, `log.md` holds dated evidence append-only, `sources/` holds their documents as sent. You approve the promotion; it never happens on its own. Entities carry a `reviewed:` date and the weekly review surfaces any 60+ days stale that have real touches since, so a profile written in February is never read in August as if someone still stood behind it. An entity that simply went quiet is not surfaced, because dormancy is not debt. And when your stated way of working and the log disagree, the morning loop asks about the gap rather than picking a side - designed intent, enacted practice, and the question - because nobody writes down why the two diverge unless something asks. This takes the branch that v1.27's F34 declined: that removal was correct because the path had no directory, no schema, no reader and no install step. All five now ship, and `tests/test_no_phantom_entities.py` was rewritten to assert the backings directly rather than ban a keyword, which makes it a stricter guard than the one it replaces. Record: `plans/v1.46-entities-schema-supersedes-f34-2026-08-02.md`.

### Changed - positioning that says the true thing in both directions

The README now states the ownership line plainly: every other tool in this category asks you to make your operating logic legible to their platform, and what they keep is the record of how your business runs; this is files on your machine you can read, edit, fork, and keep the day the vendor disappears. It also states the gap in the same breath - the OS runs when you open it and when a hook fires, not all day on its own - because a positioning line that only says the flattering half is the thing this release exists to argue against. A first-session prompt card gives nine sentences to type after setup, and `docs/a-day-in-the-os.md` walks nine real situations end to end. That page carries no percentage and no multiplier anywhere, deliberately: a scenarios page is exactly where invented numbers go.

## v1.45.1 - 2026-08-02

The fourth-pass patch. An independent end-to-end review (Codex) ran over the pushed v1.45.0 - the fourth independent pass on this range - and every confirmed finding shipped the same weekend. Pack: `updates/1.45.1-honest-boundaries.md`.

### Fix - uninstall could destroy operator data

The standalone `uninstall.sh` kept a preserve-list (seven directories, three files) that had fallen behind the layer model, then deleted everything else - taking `capture/`, `brands/`, `roles/`, `system/`, `rules/`, `memory/`, `os-config.yaml`, and any setup-created company folder with it. Both uninstallers now work the only safe way round: they delete a named list of system paths and touch nothing else, so a path the list has never heard of survives by construction. The command uninstaller also stops removing `rules/` (update classifies it as founder-personalized), and purge mode now actually removes everything it claims to, asking per folder about root directories it cannot name.

### Fix - the boundary language now matches Claude Code's documented behavior

Claude Code reads a skill's `allowed-tools` as pre-approval, not as a wall that blocks unlisted tools - restrictive enforcement is an open upstream request. Every sentence that said "the list Claude Code enforces" now says the true thing: the grant is a written contract living in two places kept identical, the charter audit names drift between them in both directions, and anything outside a grant routes through the operator's own permission prompts rather than running silently. The audit itself got the teeth the claim needs: it now checks the reverse direction (a charter tool no chain skill declares), parses every frontmatter shape Claude Code accepts (inline, multiline list, space-separated), flags an empty declaration, compares case-sensitively because script paths differ by case on Linux, and catches interpreter-wide wildcards like `Bash(python *)`.

### Fix - a fresh extract now actually installs the discoverable skills

`skills_sync.py --check` on a pristine ZIP reported five skills missing from `.claude/skills/` - the model could not see today, catch-up, or the next-move engine natively, because setup only ever generated the capability page. Setup now runs `--apply`, proves it clean with `--check`, then generates the page.

### Fix - smaller honesty and correctness repairs from the same review

Future-dated verdicts no longer trigger reviews; impossible calendar dates (2026-99-99) now fail the entry guard instead of passing shape-only checks; a completed review with zero accepted diffs still stamps `last_review` so REVIEW DUE clears; the weekly review and the generic snapshot recipe refresh a stale cache at 3 days like the propose engine; the morning loop prioritizes and closes asks in `brain/needs-input.md`, not only its twin; a ZIP install on a machine that happens to have git asks before `git init` instead of switching version history on unconsented; the wizard's date substitutions use Python instead of a Unix `date` a no-git Windows box may not have; `roles/`, `system/`, and setup-created company folders joined every layer list including update's opening gate and confirmation; and the README's offer was corrected line by line - the query proof's real syntax, the provisional ledger's deliberate refusal of money and contact data, the undo net's editor-tools-only honesty, "no blank templates" reworded to name the deliberate waits, and the capture-to-distil pipeline stated as it runs.

## v1.45.0 - 2026-07-31

The wider-door release. Two doors, one product: the OS now works end to end for a person who will never run git, and for an employee running one role inside a company. Neither reading costs the founder anything.

### New - the OS for a person who will never run git

The principle, now enforced in the text and not just the code: git may power the OS, it is never the interface. The machinery already degraded well (session snapshots as the undo floor, a first-class ZIP update path, the caveman verbs wrapping git); the words had not caught up.

- **`rules/commit-naming.md` says up front it lives in the version-history layer** and never fires on an install without history. Its push-cadence section already scoped itself to multi-machine setups; the rejected-push line now explains recovery in plain words instead of rebase jargon.
- **The global template stops writing git advice into your global config.** "Verify with git status" became "verify with a file read"; the history rules are named as dormant without history.
- **Session end is honest about memory.** The old first step said commit to git. The new one says the truth: files persist the moment they are written, and the next session reads them with nothing else needed. The tour's "your repo is your memory" became "your files are your memory". This is the whole cross-session contract for a no-git install, and it is now stated everywhere it was implied.
- **Updates never require a git command on any path.** One doc claimed Path B updates are manual via `git pull`; it now points at "update Founder OS" like every other path. `docs/install.md` gained one section naming the three layers: folders that are yours (never written by an update), folders that are the OS's (replaced freely), and the three files in between (proposed as diffs, never imposed).
- **The version verbs describe saved versions, not git internals.** The skills catalogue's save / history / restore / backup entries dropped `git status`, `git log`, and reset flags from user-facing lines, keeping one honest sentence that git is the plumbing underneath.

### New - works for an employee, not only a founder

An employee running part of a job is the operator of that part. The wizard's role question (own the business / run a role inside one) existed since the role fork landed; the operator answer now leads somewhere instead of into a silently degraded install.

- **The Role Snapshot** - the operator twin of the Founder Snapshot in `core/identity.md`: the part of the job you run, who you answer to, what is yours to own, what is not yours to decide, and the biggest blocker. Discovery captures it with the same manners as the founder flow: one question at a time, everything skip-able, never an invented answer. Each install carries exactly one of the two blocks.
- **The propose engine gained an operator path.** The North Star changes from the next paying customer to the work you own in front of the person waiting on it. Same compression, same one-big-two-small close. `/next` routes on the identity role and whichever block exists, the SessionStart brief words its nudge for the path, and `brain-snapshot.py` carries either block.
- **The account manager serves both readings.** For a founder it drafts the client update; for an employee it drafts the status update to whoever you answer to. Same skill, same formats, same draft-only gate - `context/clients.md` is the stakeholder register either way.
- **The copy sweep.** Every line that read false to a non-founder was fixed in place: README, first-day, the ramp, the tour, the update packs, the shipped templates in rules/, roles/, cadence/, context/, brain/ and network/, and the seat skills. The word for the human is the operator; the founder reading loses nothing.

### Fix - what the second stranger walk caught

The same walk that closed v1.44 ran again over this release and its findings were fixed in the range, not filed: the SessionStart brief was the one surface still founder-only; `brain/needs-attention.md` shipped in templates but was never on the wizard's copy tree, leaving the assistant seat's first input missing on every fresh install; the reviewer seat held a script grant wide enough to write the ledger its charter forbids (narrowed to the two read-only subcommands its skill runs); the account manager's row promised an absolute refusal the skill softens with a labelled opt-out; five surfaces said the health check has eight checks when it has nine; and the tour claimed all five roles ready when the account manager waits on the voice step, which it now says.

### New - the charter holds, and the README makes the offer

A third-pass architecture review ran before the push and its confirmed findings landed in the range. The structural one: the registry claimed "there is no second list to drift from" while every seat skill's `allowed-tools` frontmatter - the skill's declared runtime list - was wider than its charter row. Every seat is now narrowed to the exact scoped grants its row states, the charter audit (`employee_verdict.py charters`) reads the seam and names any drift, and the doctrine, the first-day doc, and the README state the true mechanism. Around it: default uninstall now preserves everything update protects (`capture/`, `brands/`, `roles/`, `system/`, `rules/`, `os-config.yaml`), `roles/` and `system/` joined the User Layer lists, the morning loop and the weekly retro now genuinely surface REVIEW DUE (closing the verdict loop's missing trigger), the propose engine and housekeeping refresh a stale `brain/.snapshot.md` instead of only a missing one, and the morning loop reads `brain/needs-input.md` beside its near-twin so `/dream`'s parked questions stop falling between two files. The README itself was rebuilt as the offer it should have been: what you get on day one, the one habit that makes it compound, who runs it, and a "prove it in ten minutes, offline" section - because the strongest claims here are the checkable ones. Pack: `updates/1.45.0-the-charter-holds.md`.

## v1.44.0 - 2026-07-29

The usability release. A group stress-tested the product and named the risk in one line: the backend is not the problem, someone who did not build it being unable to drive it is. The comparison was a terminal, the most capable thing on the machine and useless if you do not know how to talk to it. So this release stops shipping workflows and ships people. A founder should finish setup feeling handed a team, not handed a folder of markdown.

### New - your OS is five named roles

- **`roles/employees.yaml` ships with five roles instead of empty.** The assistant who runs your morning. The one who names your next move. The note-taker who files what you captured away from your desk. The account manager who drafts the client update. The reviewer who reviews the other four. Each is backed by a skill that is on your disk, carries a written job description and an exact list of what it may touch, and arrives `gated` - defined, with nothing run yet.
- **Setup introduces them by name.** The tour used to end by showing you six files. It now ends by telling you who you have and what each one will give you tomorrow morning. Six files is a folder. Five roles is a team.
- **Only a run you watched moves a row to `active`.** The chart claims nothing that has not happened, which is the whole reason it is worth reading. Grading a role takes one line and is what every later review reads.
- **The doctrine says what the file does.** An empty org chart was called the honest one. The sharper version, now written: a chart that lies is what is dishonest, and a gated row backed by a skill you can open is an introduction rather than a promise. Propose-only and draft-only are also separated, because a job that writes nothing and a job that writes a draft and stops before sending need different tool grants.

### Fix - the org chart had never actually reached anyone

`roles/employees.yaml`, `rules/digital-employees.md` and the two scripts behind them shipped in v1.43 and were never on the setup wizard's copy list, so no install ever received them and `employee-review` would have failed on its first command. Six other files were in the same state, including four rules files and the scripts behind the ship gate, the provisional-fact ledger, the lint self-check and the fetch-and-extract skill. The v1.43 update pack told founders to run a command that did not exist on their machine. All of it now ships, and the copy step reads the folder rather than a list that can silently fall behind it.

### New - autonomy on a schedule you can read

- **`cadence/first-30-days.md`** decides how much the OS does for you and when that changes. Days 1 to 7 it watches and asks one question a day. Days 8 to 21 it proposes, and nothing acts without a yes. Day 22 onward it acts inside the gates you already approved. The morning loop reads the file and holds itself to the stage.
- **No scheduler, and no surprises.** The dates are written down and compared against today. A missing file means full speed, so an older install never goes quiet for a reason it cannot see. Say "skip the ramp" and it is over.
- **The floor is not part of the ramp.** Nothing leaves your machine without you, on day 400 the same as day 1.

### New - what this is, in writing

The question nobody had answered on paper: how is this different from someone using Claude or ChatGPT well? Four things, now in `README.md` and `docs/first-day.md`. The context is a folder you own, so a better model next year reads the same files. Nothing becomes a fact because it was said once. Five named roles that are graded, rather than one assistant accountable for nothing. And a gate between a draft and a send that lives in a permission grant rather than in a polite sentence in a prompt.

Also stated plainly rather than left implied: this is for founders and for people running teams, each person runs their own, and pay, private profiles and personal data never pass between two of them. Several people inside one live session is not something this does, and the docs say so instead of being vague about it.

### New - two commit guards and a generated capability page

- **A line-ending guard.** One stray carriage return turns off git's normalization and restyles a whole file, so the real diff vanishes into churn and the next machine to append writes a mixed one. Public users are cross-platform by definition, which makes this the kind of corruption you cannot reasonably debug. `raw/` is exempt. Override: `ALLOW_EOL=1`.
- **An entry-form guard.** A decay field spelled `Decay After:` is never read by anything. The entry looks right, never surfaces for review, and nothing tells you. Added lines in the brain channels are now checked against the canonical form, which `rules/entry-conventions.md` now specifies exactly. Forward-only, so nothing old is dragged into a form that postdates it. Override: `ALLOW_ENTRY=1`.
- **`docs/what-this-can-do.md`** answers "what can this actually do", generated from the skills on your disk and never maintained by hand. A hand-kept list is wrong the first week somebody forgets, and a wrong capability list is worse than none because it teaches you the OS cannot do something it can. The commit hook refuses a skill change that leaves the page stale and names the one command to rebuild it.

### Fix - a red test suite that was mostly lying

Fifty-eight tests were failing and three more were passing without testing anything. Every one of them drove the `.sh` and `.ps1` hooks that v1.42 deleted when the hooks moved to a single Python dispatcher. Worse than the red ones: a set that sat behind a platform skip saying the bash hook is muted on Windows, while the real reason was that the file no longer existed. A skip that names the wrong reason never gets looked at again.

The behaviour survived the move, so the tests followed it rather than being deleted. Both platform variants collapse into one per file, and there are no platform skips left in any of them. Two more were red against correct code: one asserted a hardcoded script list that the verify skill had deliberately replaced with a glob, and one carried a fixture whose hardcoded dates drifted out of the tier it was asserting as the calendar moved. Both are fixed at the test, which is the rule this release also wrote down: a checker reporting a finding that is not real teaches you to skim past the ones that are.

### New - four structural writing tells

The banned-word list catches vocabulary. These four survive a find-and-replace, which is what makes them the ones left once the words are clean: an aphorism budget of one per document, no label-colon paragraph openers, no defining a thing by what it is not, and a docstring that is a contract rather than a case study.

## v1.43.0 - 2026-07-25

The harness release. The OS gains doctrine for how it keeps itself usable as it grows, a few small loops that make an improvement land instead of being rediscovered next month, and an update channel that stops a new release from costing you the edits you made. Five new skills, four new standard-library scripts, no new dependency, and nothing you have to keep running.

### New - updating no longer costs you your own edits

- **An update is a conversation, not a download.** `/founder-os:update` still pulls the System Layer, then walks the release packs in `updates/` with you. One pack per release per group of changes, each stating what changed, who can skip it, the files it touches, and a step-by-step protocol. Same command, richer behavior, no second command to learn.
- **Three-way merge on anything you may have edited.** Three versions exist: the old shipped file, the new shipped file, and yours. The update works out what the release actually changed and proposes that on top of your version, leaving your edits alone. One file, one diff, one yes, never a batch. On a genuine conflict it puts your version back, shows both, and applies nothing until you choose - because a refused update is a working install and a silently merged one might not be.
- **`os-config.yaml` makes an update about your install, not about the product.** It records which of ten modules you actually run, so parts about things you never adopted get skipped and announced rather than walked through. It also holds the two values shipped code must never assume, your document font and the author name on generated documents, which is why the ship gate reports those checks as skipped rather than passing on a guess when they are unset. The setup wizard writes it.
- **Every pack names the one file to copy if you run no tooling at all.** A pack that cannot state that does not ship: a change that cannot be described as a by-hand step is too complicated to be an update.

### New - the OS explains itself, and reviews itself

- **`rules/os-as-harness.md`** names the four properties that keep an OS maintainable rather than merely documented: doctrine files say why they exist, scripts document their own contract, a repeated failure gets fixed at the engine instead of corrected again, and the OS fits the person running it. The standing guardrail is stated plainly - this is a self-observing OS, not a self-modifying one. Everything proposes, you decide.
- **`rules/context-discipline.md`** covers long sessions: where tokens go, what belongs in code rather than a prompt, and the running build log plus the 30% rule that let a session which fills up resume with nothing lost.
- **`rules/hands-resilience.md`** is the four-rung fallback ladder for when a tool you depend on stops working, plus a registry you fill in with your own tools. It ships with placeholder rows and no claims about what works.
- **`rules/digital-employees.md`** is the org chart doctrine for once several recurring jobs run for you, including the rule that a job's charter IS its permission grant rather than prose beside it.
- **`os-evolve`** turns an audit or a pile of flags into one dated plan with evidence per gap, numbered execute prompts, and a reconcile line each. It never executes its own prompts: a session that plans and executes in one breath marks its own homework.
- **`founder-review`** reviews you rather than your work. A scorecard counted from your own files, at most five coaching questions, at most three dated commitments. Private by default, and a measure with no instrument reports "no instrument" instead of a guessed number.

### New - four questions each morning, and the answers land where they belong

- **`morning-loop`** asks at most four questions drawn from what is genuinely waiting, each with narrow options and a recommendation first, then writes every answer into the file that owns it and closes the thing that raised it in the same pass. That second half is the one usually skipped, and skipping it is why the same question shows up on five mornings. A quiet morning reports itself as quiet rather than inventing a question.
- **It ends with a coach line**: yesterday's step scored from the files where the files can tell, and today's single step named. Your own hands, doable today, never a build the OS should be running itself. The weekly and monthly reviews read that line.
- **`/today` and `/next` changed what counts as progress.** Surfaces report what moved (a reply, a decision, a payment), not how many items were closed, and when nothing moved that is the line. Work needing your own hands surfaces as an action in your words, never as another entry on a list, because answering a full plate by adding to it is not help.

### New - the OS is honest about what it does not know

- **A name heard once stays unconfirmed until you say otherwise.** Something said in a call and never spelled out now waits in a ledger instead of sitting in your notes reading like a fact. Confirming it records the value and names the file it belongs in, and writing it there stays your step. The ledger refuses to hold an email, a phone number, or an amount. Single-source capture is the normal case, and it leaves nearly every proper noun unconfirmed while reading perfectly fluent - `catch-up` now says that out loud, including that the fix is a second source rather than a better transcript.
- **A verdict loop for recurring jobs.** One line after a run you actually saw is the whole input to a review that proposes changes to the job rather than asking you to correct it again. Review is due on two triggers only, and with no verdicts nothing is ever due: a review with no evidence to read is an invitation to invent a performance story. The charter audit catches the common invisible failure, a job whose description says it only proposes while its actual grant covers every script on the machine.
- **`employee-review`** turns those verdicts into a shown diff on the job's definition, and never applies its own diff. Proposing retirement is a valid outcome, and a retired row keeps its place with a dated why.
- **`capture-sweep`** notices what was recorded and proposes where each item goes, sorted into a conversation, training media, internal talk, or personal. Personal is skipped and counted, never filed.

### New - a skill that nothing can find never runs

- **Verify checks skill reachability** (Check 9). A well-written skill that no command names, no registry row lists, no docs entry mentions, and no other skill points at is reachable from nothing while looking perfectly healthy from the outside. `skills/discoverable.yaml` promotes the handful worth reaching the moment you describe a situation rather than after the model reads a registry.

### Sharper - three surfaces you already use

- **The ship gate runs a deterministic scan first.** A leftover `[FILL]`, last month's date, or a tool credited as the author is caught by a grep instead of by your attention, which leaves the reading passes free for whether the content is actually true. SKIP is a first-class result naming what a text scan cannot judge, so nothing is silently guessed.
- **Closing a queue item takes a one-line verdict** - ok, needs-work, or failed, never self-graded, and skipping is free. Those lines are the only honest record of what your OS is good at.
- **Lint reports doctrine that never says why it exists**, as one advisory line, forward-only.

### Ships empty on purpose

The employees registry, the banned-words exceptions file, the culture template, the needs-attention file, and the workflow map. An empty org chart is honest, and one full of jobs that never ran is worse than none. Each says what fills it in and when.

## v1.42.1 - 2026-07-16

The clean-machine patch. A full end-to-end install test on a pristine machine (ZIP path, a rambling non-technical founder at the wizard, no API key, no git identity) surfaced one blocker and a set of gaps between claim and behavior. All fixed here. No new skills or commands.

### Fix - setup finishes on a clean machine

- **The privacy guard no longer blocks the founder's own name.** Setup used to offer the founder's own name as the first guard pattern and then track `core/identity.md` - so the guard it had just installed blocked setup's own first commit and every later save touching their name. Patterns are now for names that must never enter your files (a client under NDA); your own name is tracked by design, and the anti-publish protection is the remote-safety guard, which already refuses any commit that could push personal data to the public repo.
- **A mangled guard pattern warns instead of dying silently.** A shell echo can turn `\b` into a backspace byte, shipping a pattern that matches nothing while the installer reports it loaded. The guard now names and skips any pattern with control characters or invalid regex, at every run.
- **Git authorship is confirmed, not assumed.** On a machine that already carries someone else's git identity (family or work computer), setup and own-your-history now read the configured name back and ask if it is you, instead of silently recording the founder's history as someone else. Own-your-history's already-has-git path also checks identity exists before its first save, so it cannot fail with git's "tell me who you are" wall.

### Fix - hooks fire everywhere, before setup

- **Each hook command tries all three Python spellings** (`python`, `python3`, `py -3`) with the braced `${CLAUDE_PROJECT_DIR}` form, so the session brief and the undo floor fire on a fresh extract on macOS boxes with only `python3`, Windows boxes with only the `py` launcher, and bash-less Windows where hooks run under cmd. Setup still writes the one discovered interpreter after the interview.
- **The PreCompact save-before-you-forget instruction actually reaches the model** through the supported `hookSpecificOutput.additionalContext` channel. The old plain print went to the debug log and nothing else.

### Fix - honest tracking, honest gates

- **Session tools never read a parallel session's change log.** The Stop-hook revenue check and the change manifest fall back to the newest session log only when no session id arrived at all; a known session that wrote nothing now stays silent instead of evaluating another session's changes.
- **The unrestorable-file label says why** ("no pre-edit copy - over 2 MB or snapshot failed") instead of always claiming the file was over 2 MB.
- **The in-place install no longer overwrites the private-tag exclusion rules:** the personalized operating-rules template now carries the `<private>` contract, so writing it over the shipped file loses nothing.
- **The voice gate points at the interview that fills it** (voice-interview), not back at setup, which leaves the profile templated by design.
- **Verify looks where MCPs actually live** (`.mcp.json` at root and per project, not just settings.json) and no longer counts shipped syntax examples as broken wikilinks, so a pristine install can report a clean pass.
- **Facebook counts as a main channel and accounting software gets a real stack field.** A local-services founder's "Facebook, everybody's on the neighborhood groups" and "QuickBooks for the money stuff" now land in `stack.json` (`primary_channel: facebook`, `accounting: quickbooks`) instead of being extracted and then thrown away as backlog prose.
- **The wizard reads the founder in front of it:** technical comfort can override the variant default when the interview shows a non-technical operator, a vague stage answer is inferred from facts the founder already stated and read back for confirmation, project folders default into the OS root with the trade-off named, company `.mcp.json` defaults to an honest empty config, and the computed auto-memory slug normalizes underscores and dots the way Claude Code does.

## v1.42.0 - 2026-07-10

The install-and-honesty release. It clears the blockers a clean-machine ZIP install hit, replaces the dual-shell hooks with one cross-platform dispatcher, and reconciles every self-claim against what the code actually does. No new skills or commands.

### New - one hook dispatcher instead of a shell pair per event

- **Every hook now runs through `scripts/hooks/dispatch.py`, one settings entry per event.** The OS used to register a bash script and a PowerShell script for each event, so a Windows box with no bash (or a Linux box with no PowerShell) printed an interpreter-not-found error on every fire. Python is already a prerequisite, so a Python dispatcher needs no shell: there is nothing to be missing.
- **Session-close handlers run in a fixed order.** The revenue check and the change manifest both read the working tree before the auto-save commits it. The old event array did not guarantee that order; the dispatcher does (revenue-check, then changes-manifest, then autosave).
- **The nine `.sh`/`.ps1` pairs are gone**, the session brief is consolidated into `session_start_brief.py`, and the hooks-parity gate now enforces the dispatcher shape.

### Fix - ZIP is a first-class install path

- **A ZIP extract is detected as its own install and set up in place**, instead of being misread as a plugin install that split the founder's data into a fresh empty folder with no skills or commands.
- **Git identity is set before the first commit**, and the privacy guard is wired and proven live between `git init` and that first commit, so the commit no longer fails on a machine with no configured `user.name` and can never land unguarded.
- **A Python check runs before the interview**, not twenty minutes into it, with the same three-probe sequence (`python`, `python3`, `py -3`) everywhere so bare `python3` no longer fails silently on Windows.
- **The empty-state message leads with the universal phrase "set up Founder OS"** and routes `/setup` vs `/founder-os:setup` by install path.

### Fix - your history and identity stay yours

- **The full User Layer is tracked when you own your history**, via a shipped operator gitignore, so "full version history" covers identity, priorities, decisions, clients, cadence, and brain, not just a rolling snapshot floor.
- **Remote safety before the first data-tracking commit:** own-your-history renames the public `origin` to `founderos-upstream` and disables its push URL, and a guard refuses to let a User-Layer-tracking repo point a push at the public FounderOS repo. One `git push` can no longer publish your identity.
- **The remote-safety guard checks every push destination on a remote** - all pushurl values if any are set, otherwise all url values, because git pushes to every one of them. A second push URL can no longer hide a public one.
- **The git privacy hooks find Python the same way setup does** (`python`, then `python3`, then `py -3`), so a Windows machine with only the py launcher gets a live guard instead of a silent pass.

### Fix - updates propose, they do not overwrite

- **Your `CLAUDE.md`, `rules/`, and `settings.json` are no longer replaced wholesale on update.** Updates land in the `templates/` copies; the flow diffs live against new and proposes a migration you read and accept.
- **Apply is staged and rollback is real.** Incoming files are staged and verified before activation, two manifests are recorded, and rollback restores the pre-update state and deletes anything the update introduced. Any apply failure auto-triggers rollback.

### Fix - claims match the code

- **The revenue-loop check actually fires.** It reads the per-session change record instead of a `git status` that was always empty on a fresh install (both tracked files are gitignored), so the check no longer silently never runs.
- **The undo manifest only offers a restore for files it can put back**, quotes paths in printed commands, and restores created files by deleting them on confirm.
- **The PreCompact line says what the hook does** (it asks the summary to keep unwritten facts and instructs the assistant to file them after compaction; it does not write files itself).
- **The README no longer claims "nothing leaves your machine" without the plain version:** files stay on your disk, what you read into a session goes to Anthropic under your plan terms, and ARCAS receives nothing, runs no server, keeps no telemetry.
- **Runs-on labels name the local execution the skills actually do** instead of over-claiming portability.
- **The setup tour's version-history offer says what is true** - the history lives in the folder on your disk - instead of a blanket "nothing leaves your machine".
- **The release floor names its one pip exception:** the optional scrape helper asks for three packages and falls back to the built-in fetcher without them; every other shipped script is standard library only.
- **The last doc references to the retired bash/PowerShell hook pairs are gone** - CLAUDE.md and the install and forking guides now describe the dispatcher.

### Fix - verify catches broken installs

- **A data folder passes only if its plugin engine is reachable** (version read from the plugin manifest); an unreachable engine now FAILs with "engine not found" instead of auto-passing.
- **The scripts check enumerates the shipped scripts dynamically and syntax-checks every one, including the hook dispatcher**, with a parse that writes nothing to disk so the skill's read-only claim holds. Missing Python is a hard FAIL, resolving the old WARN/FAIL contradiction. The report example's footer now matches its rows.
- **The hooks check verifies all six events in the dispatcher shape**, not just SessionStart, and the free-tier grep covers the full shipped script set.

### Fix - enum and data-flow hygiene

- **`founder-next-move` gates on the identity role and a present Founder Snapshot**, so a `builder`-variant founder is no longer redirected away from the propose engine.
- **`business_model` captured at setup is now written to `stack.json`**, so `unit-economics` reads the real model instead of null.

### Change - house voice and history hygiene

- **Every em and en dash across the tracked tree is gone** (194 across 23 files), and a new full-tree baseline gate in the privacy guardian holds the whole repo at zero so a dash can never silently regress. The gate enumerates files NUL-delimited and skips binaries by NUL-byte detection, so an unusual filename or a UTF-8-valid binary cannot break the scan.
- **The commit naming rule now documents release commits:** user-visible present-tense subject, version in the tag and body, never as the subject.

## v1.41.2 - 2026-07-09

A consistency-hardening sweep across the Second Brain release arc. No new features; every claim the OS makes about itself now matches what it does.

### Fix - setup copy steps can no longer under-copy

- **The hook-merge instruction names all six hook events.** Re-running setup over a pre-v1.40 install previously merged only four events into an existing `settings.json`, silently dropping PreToolUse (the undo floor) and PreCompact (the memory flush). Both are now named explicitly, with the consequence of omitting them stated.
- **The script verify count matches the copy list.** The copy step says twenty-one Python helpers; the verification line said nineteen - a literal reader could pass verification with `session_changes.py` and `skill_health.py` missing. Both now say twenty-one, and the Phase 2.2 file tree lists all twenty-one.

### Fix - update protects everything setup creates

- **The User Layer protect list now covers `core/` in full plus `capture/` and `brands/`.** Previously only `core/identity.md` was named; the founder's profile, avatar, voice and brand profiles, inbox drops, and per-brand voices matched neither layer list, which the instruction-gate treats as refuse-and-ask.
- **GIT-mode backups capture dirty trees.** Step 7 now commits uncommitted System Layer edits before creating the backup branch, so the rollback claim ("captures the entire pre-update state") is true on a dirty tree instead of quietly false.
- **Plugin-path updates point at the right command.** The README's marketplace section said `/founder-os:update`, which refuses to run in the data folder that path creates; it now says `/plugin update`, matching the install guide.

### Fix - verify works on every install shape

- **Check 1 and the version header are install-mode aware:** a Path A data folder (engine in the plugin, no local `skills/`) reports PASS instead of a spurious WARN, and a missing `VERSION` falls back to the plugin manifest.
- **Check 5 greps the seven core scripts, not the whole tree:** documenting an optional key name (add-voice's free-tier upgrade, connect's `.env` writer) is not requiring a key, and a fresh perfect install no longer opens its first health check with a false warning.
- **The sample output is internally consistent** (footer tally matches the example lines), since the model imitates it at the end of every setup.

### Change - small claim-to-behavior alignments

- Seeded-content lists include the pattern seed; the snapshot-first boot is no longer contradicted by "reads them every session" taglines; the Playbook link is one URL everywhere; the own-your-history follow-up no longer points at itself; setup pitches the git graduation phrase exactly once.

## v1.41.1 - 2026-07-09

Same-day correction to v1.41.0, applying the product's own bar: a feature earns its place by changing behaviour or compounding, not by looking good once.

### Remove - the session-one HTML card

- **`templates/founder-card.html` and the card render step are gone.** A rendered file the founder must open outside the flow adds friction instead of removing it, does not compound, and does not change what they do next. The session-one proof is now the real thing: the post-setup tour runs the founder's first `founder-next-move` proposal in the flow and states the compounding contract plainly - every session feeds the brain, so the moves sharpen because they are read from real state, not guessed. `founder-next-move` is back to read-only.

### Change - git named as the recommended steady state

- **The ZIP is the door, git is the destination.** README and the install doc now say it: enter with the ZIP, and when settled say "own my history" once - the OS installs and wires git itself (`own-your-history`, shipped in v1.40.0), after which updates flow through git instead of ZIP re-downloads and git maintains itself. ZIP overlay updates remain the fallback for installs that stay git-less.

## v1.41.0 - 2026-07-09

The proof-and-payoff patch on the Second Brain release: setup proves it wired up before it says "done", and session one now hands the founder something they can see. Same floor: one Claude plan, no key, nothing leaves the machine.

### Add - setup proves itself before the finish line

- **The setup wizard now runs the `verify` health check automatically** at the end of Phase 6, before it tells the founder they are done, and reads the eight-check result back in one plain line. A partial install - a script that did not copy, a missing Python, an unwired hook - now surfaces in the last minute of setup instead of days later mid-task. A FAIL blocks the finish line until it is named and fixed. This is the "never say ready without a check that says so" rule, lived by the product rather than left to the user to invoke.

### Add - a showable card in session one

- **`templates/founder-card.html`** is a self-contained, dependency-free one-page card that opens the same offline as online. The setup tour and `founder-next-move` fill it from the founder's own Founder Snapshot and proposal, then write `your-next-move.html` to the OS root: venture, customer, where you are, biggest blocker, the single next move, and the one step to start today.
- **`founder-next-move` renders the card on demand** ("show my card", "make my founder card"), and setup renders it automatically in the post-setup tour for the founder and team_of_one variants. It is the one visible artifact a first-timer can screenshot or stick on a wall, and it refreshes every time they ask for their next move. A thin brain with no customer set skips the card rather than render a hollow one.

### Change - engagement framed as a floor with a payback, not a chore

- **The "who this is NOT for" note now names the exchange:** drop a thought in when it happens, glance at the brief on open, and the OS stops you re-remembering the same open loops and re-deciding the same calls. The honest filter stays - if you will not talk to it at all, it sits unused - but the daily-and-weekly floor now reads as the low-cost, admin-subtracting trade it is.

## v1.40.1 - 2026-07-08

The Second Brain release, wave two: memory that provably survives, retrieval that stays cheap as the brain grows, and money math that speaks the operator's business model. Same accessibility floor: one Claude plan, no key, no paid service, no git required.

### Add - save before you forget (PreCompact memory flush)

- **A PreCompact hook fires when the session context is about to be compacted.** It instructs the model to carry every unwritten decision, commitment, status change, and captured fact through the summary and write them to the brain files immediately after - `brain/log.md`, `brain/flags.md`, `context/clients.md`, `brain/decisions-parked.md`. Continuity lives in the files, never in summary prose. Ships as a .sh/.ps1 pair, wired in `settings.json`, copied by setup, quiet outside a set-up install.

### Add - the housekeeping sweep (retrieval quality IS memory quality)

- **Say "run housekeeping" and every piece of accumulated OS debt lands on one screen**, each line with its severity and exact fix command: stale cadence, rants aging unprocessed, log past its cap, stale wiki graph and snapshot, broken links, decay-due flags, client folders with no memory entry, ACTIVE quarantine entries, and skill health. Detect mode is read-only, always.
- **"housekeeping fix" clears the reversible half in dependency order** - anchor bump, dream, log archive, unambiguous pointer repoints, wiki-build, snapshot refresh - narrating each step, then hands back a punch-list of the judgment calls and a verify table filled by re-reading each side-effect, never by trusting an exit code. Judgment items (the weekly review, link triage, keep/kill calls) are never run unattended.
- **New `scripts/skill_health.py`** detects description bloat (over 900 chars warn, over 1024 fail - the silent-install risk) and dead skill pointers. Its first run against this repo caught a real dead pointer in `log-reply`, now fixed.

### Change - boot from the snapshot once the brain has grown

- **Measured day-one boot at ~8k tokens against a ~5k target**, most of it in files that grow with use. The bootloader now orients from `brain/.snapshot.md` when it is fresh (open flags, must-do, recent decisions, staleness in a few hundred tokens) and opens `context/decisions.md`, `context/clients.md`, `brain/flags.md`, and `brain/log.md` only when the task touches that domain. A stale snapshot falls back to full reads and offers the refresh - it is never treated as current state.
- **The provenance rule is now stated in `rules/approval-gates.md`:** authored files (identity, voice, brand, rules) are yours and the OS only proposes; accumulated memory (log, flags, MEMORY.md facts) is the OS's write zone and what memory-pass audits; dated working notes are written once and aged out. The gates existed; now the rule they enforce has a name.
- **The SessionStart brief's silence contract is documented:** sections print only when they have something to report, so a clean OS opens near-silent and anything the brief says deserves attention.

### Add - the OS knows how the business makes money

- **A `business_model` axis in `stack.json`** (service / ecommerce / saas_software / marketplace / content_creator / regulated_deep_tech / other), captured at setup by inference-and-confirm rather than a cold question, never guessed. Role said who; stage said where; this says how the money works.
- **`unit-economics` leads with the model's numbers:** utilization and day rate for services, contribution margin and inventory turns for ecommerce, MRR and churn for SaaS, GMV, take rate, and liquidity for marketplaces, RPM and income concentration for creators. Textbook-stable mappings - determinism is honest here.
- **The domain-honesty rule for regulated and deep-tech operators**, stated once at setup and enforced in the money layer: the OS carries capture, decisions, cadence, memory, and accounting-level math for any business; it does not generate compliance, science, or clinical judgment, and it routes those to the operator's own expertise instead of improvising. A confident wrong domain assumption survives review precisely because it looks like the other numbers - so it is never produced.

### Cross-cutting

- Skill count 86 -> 87, command count 37 -> 38 across every parity surface. Everything new is free-tier: file reads, local scripts, no key, no paid tool. `memory-pass` was already ported in v1.32; this wave audited it rather than duplicating it.

## v1.40.0 - 2026-07-08

The Second Brain release. It attacks the value equation directly: less effort to own the system (install is three steps and nothing typed), less delay before it earns its keep (capture works from your phone the same day), and more proof it deserves trust (an undo floor with no prerequisites, a security story with receipts). Every path holds the accessibility floor: one Claude plan, no extra key, no paid service, and now - no git.

### Add - the ZIP install path (own it in 10 minutes)

- **Path 0: download the ZIP, extract, say "set up Founder OS".** No git, no curl, no terminal command. Git left the prerequisites entirely - the README asks for three things now (Claude Code, a paid plan, Python), and the install doc leads with the path that needs nothing installed.
- **`/founder-os:update` works without git.** On a ZIP install it re-downloads the archive itself, overlays only System Layer paths against the User Layer protect list, backs up to a folder instead of a branch (rollback included), and ends with a plain-language digest of what changed between your version and the new one. `CHANGELOG.md` and `GEMINI.md` joined the System Layer list so the digest and the agent bridges stay current.
- **Setup and every hook degrade honestly when git is absent.** Phase 2.3 skips init with a plain sentence instead of an error, the auto-save hook stays silent, and nothing nags.

### Add - own your history (git as a graduation, not a prerequisite)

- **Say "own my history" and the OS installs git itself - one consent-gated yes, nothing for you to type.** It names the exact install command before you agree, initializes the repository, wires the privacy guard BEFORE the first commit so no version predates it, and records version one with the same engine every later save uses. `save`, `history`, and `restore` now route here instead of erroring on a git-less install, and the post-setup tour makes the offer exactly once, warmly, with zero pressure.

### Add - the session-changes undo floor (undo before git exists)

- **Every file the OS touches is snapshotted before every write.** A PreToolUse hook copies the pre-edit bytes on first touch per session; a Stop hook renders a per-session manifest; the new `/founder-os:changes` command shows it on demand: every file, the action, the change size, and a one-command restore per file. No git required - on a ZIP install this IS the undo surface, and after graduation it keeps running as a second net. Failures land in `system/quarantine.md`, never silently swallowed, and the recorder always exits 0 so it can never block a write.

### Add - capture anywhere (feed the brain from your phone)

- **`capture/inbox/` plus the `catch-up` skill.** Drop phone dictations, voice-note exports, emailed notes, or pasted saved-messages piles anywhere they can land as text; say "catch up" and the OS files each into `brain/rants/` with provenance and `processed: false`, so the existing `/dream` flow takes over. Raw in, raw kept - your words are never rewritten at capture time. The setup wizard now asks how you will capture away from the laptop, and `docs/capture-anywhere.md` ranks the channels by friction.
- **A names glossary makes transcription errors a handled convention.** `context/names.md` holds canonical spellings and observed mis-hearings. Known names correct silently; unknown names stay as heard, marked `(sp?)`, and are asked about once, in one batch; every correction appends to the glossary so the same mishearing never survives twice. Numbers and facts the OS is unsure of are never silently "fixed". `capture-meeting` runs the same name pass, and dual-source captures reconcile by a fixed hierarchy (a document beats agreement, agreement beats a single source, your correction beats everything).

### Add - the local-first security story, with receipts

- **`docs/why-local-first.md`.** The 2026 agent-framework incident as the counterfactual: 135,000+ exposed instances, plaintext key files, a poisoned skills marketplace - every failure mode needed a listening server, a stored API key, or a third-party registry, and the OS has none of the three. Sources cited, honest limits stated (your laptop is the perimeter, connectors are your choice, cloud sessions are a different posture), and the repo-as-sync-contract pattern documented for power users.

### Fix - honest badges and claims

- **The README badge row now points at CI gates that exist** (doc and install parity, guardian, LinkedIn pack acceptance) instead of a `test.yml` workflow that never shipped, and the status line stopped claiming a test count the public repo cannot verify.
- **The voice scaffold learned the missing-state lesson.** The realtime front has no clock and no memory across wakes; the architecture doc now documents per-wake clock injection, files-as-continuity, and the desk-and-filing-cabinet model, so nobody wiring voice repeats the confident-wrong-time bug the private build hit.

### Cross-cutting

- **CI gained a hooks-parity gate:** every hook must ship and register a .sh/.ps1 pair, enforced instead of trusted. Skill count moved 84 -> 86 and command count 35 -> 37 across every parity surface. New skills (`own-your-history`, `catch-up`) and commands (`/founder-os:changes`, `/founder-os:catch-up`) are free-tier: local files, local scripts, no key, no paid tool.

## v1.39.0 - 2026-06-20

The propose release. The OS stops waiting to be asked. Once a founder's brain holds enough, it reads where they are and names the single next move toward a paying customer, then attacks the plan behind it. Every path holds the accessibility floor: one Claude plan, no extra key, no paid service.

### Add - the propose engine (`founder-next-move`)

- **Say "what should I focus on next?" and the OS proposes one move, not a list.** It reads the founder's brain (the four-field Founder Snapshot, the log, the pipeline), infers their current stage (pre-idea, idea-validation, building, first-customer, revenue, mrr-scale), picks the single highest-leverage move toward a paying customer, and closes with three things they can do today: one big, two small, so they never leave with a blank screen. The North Star every proposal optimises against is the first paying customer.
- **Stage is inferred and kept current, never a static field.** The onboarding "where are you now" answer seeds it; the engine re-reads the log every run and re-infers, so a founder who just closed a sale is read as having moved on the next morning. The six-stage model is the OS's internal lens for choosing the move, not a curriculum delivered to the founder.
- **It handles a thin brain instead of stalling.** With a customer and a stage or a blocker it proposes a real move; with less it proposes the capture move that unlocks the rest, and never invents a customer, a stage, or a blocker. Empty states do not dead-end.
- **Fires two ways.** On demand, and as a one-line nudge in the SessionStart brief once the brain is functional. `/next` now routes a founder to the propose engine and keeps the existing ranking for everyone else.

### Add - the scope challenge (`founder-scope-challenge`)

- **Say "challenge my plan" and the OS attacks the plan, not the person.** Three modes it runs on a founder's plan: Expand (the plan is too small, name the bigger move being avoided), Hold (the plan is right-sized, defend it against the next shiny thing), and Reduce (the plan is bloated, cut to the one move that reaches a customer). Brutal on the plan, human on the person. One test decides every challenge: does this reach a paying customer faster.

### Add - the founder front door at setup

- **The setup wizard captures the four fields the OS proposes from.** Venture in one line, who the customer is, where the founder is now, and the single biggest blocker, asked in founder-journey language, reusing what the founder already said rather than re-asking. They land in `core/identity.md` under a Founder Snapshot block, which `brain-snapshot` now surfaces so every reasoning skill reads them from the same runtime payload.
- **A post-setup tour replaces the silent finish.** After the wizard, the OS shows the founder the files they now own, reflects their Founder Snapshot back, and gives three things to say next, so a non-technical founder is never left at a blank screen wondering what setup created.

### Change - one OS, one voice for a founder

- **The coaching speaks the same human-support layer as the propose engine.** First paying customer as the North Star, UAE-market ground truth where the market is the UAE (the trade moves on the ground, not just the screen), and an honest jobs off-ramp for the founder who is genuinely rethinking the venture. Brutal on the plan, human on the person, across both surfaces.
- **Skill count moved 82 -> 84 across every parity surface.** The two new skills are reasoning-only and free-tier: they read files and reason, no key, no paid tool. The forkable technical lane (an idea-to-spec path, deeper automation, vector retrieval) stays documented as a provision for the few who code, not pre-built for a user who is not in the room.

## v1.38.0 - 2026-06-10

The Ease release. The front door, the heartbeat, and the optional voice scaffold, cut from `develop` to a release. Every core path holds the accessibility floor: one paid Claude plan, no extra API key, no paid service.

### Add - the voice scaffold tail (an optional mouth, optional hands, and a tuning loop)

- **`add-mouth` - say "add a mouth" to have an answer read aloud or rendered to an audio file, from any skill, without the full conversational loop.** The default mouth is your operating system's own voice (Windows SAPI, macOS say, Linux espeak) - no key, no paid service, no install, and your text never leaves the machine. A free fully-local upgrade (Piper) gives a better voice offline; ElevenLabs is the one paid mouth, never a default and never auto-selected. `say.py` prints which engine spoke and whether it was local every time, so a "local" claim is never silent. It speaks what it is given; it does not generate content or send the audio anywhere.
- **`add-hands` - say "add hands" to let the OS do things, behind a confirm gate.** Safe, reversible, local actions run freely: open a file, folder, app, or link; save a note to your log. Anything irreversible stops for an explicit yes and shows you the action first - the shipped example is running a command, which is OFF until you turn it on and still asks every time. Sending, posting, and computer control are named honestly as not built; the dispatcher refuses them rather than improvising, and when they land they arrive in the confirm class behind the same gate. The gate is the design, not a wrapper: the OS never takes an action you cannot undo without asking.
- **`tune` - say "tune" and it reads your local voice telemetry and proposes the next instant handler.** It reads the gitignored turn logs the voice skills already write (which routes you use, how slow each was, and on the realtime tier what you tend to ask), and surfaces the recurring request that is not yet an instant handler so it stops being slow. It is propose-only: it never edits a handler or a config, and it says so plainly when there is too little data to recommend anything. Free and fully local, no key, no external call.
- **Voice stays optional and is not a headline.** The OS is complete as text. These three skills plug a mouth, hands, and a tuning loop into the same brain for anyone who wants them, each opt-in, each with its cost and locality stated before you commit. Skill count moved 79 -> 82 across every parity surface. `docs/voice-extension.md` keeps its honest posture unchanged - text is the whole product.

### Change - two surface-copy corrections

- **The "desktop-only" claim is fixed.** The README said Claude Code was desktop-only with no mobile surface. That is wrong: Claude Code runs locally as a CLI and through the cloud app (claude.ai/code), so a session can be started and driven from a phone, running in a remote sandbox on a branch. The line now says so without overclaiming - the local-first path stays your machine, the cloud path is there when you are away from it.
- **The Wispr Flow name is dropped from the dictation line.** It called out one paid dictation app by name, which read as an endorsement and a soft dependency. The line now points at dictation generally - the built-in input plus any voice-to-text tool you already use.

### Add - role packs (the flat skill list becomes functions a founder covers alone)

- **The skills are now organised into role packs, each opened by one front-door wedge.** A pack is a function a solo founder runs alone (Pipeline, Content, Delivery, Money, Decisions, and the existing LinkedIn), and each opens with one skill that asks for the outcome you want and routes you to the member that delivers it. You arrive for one job and the front door invites you into the rest, never forces you. A pack is a naming convention plus a manifest, not a folder: every skill stays a top-level directory and every skill stays available to everyone, so packing changes discovery, not access.
- **Four new front-door wedge skills.** `pipeline-start` (turn a name into a tracked deal), `content-start` (one idea into a week of content), `delivery-start` (get ready to deliver client work and gate it before it ships), and `decisions-start` (get unstuck on a choice or a list). Each reads what the OS already knows, gives one honest disclaimer, routes to the existing member skills, and never re-implements an engine. They join the existing `linkedin-start`; `unit-economics` is the Money pack's front door, so no fifth wedge was needed.
- **Five new pack manifests.** `skills/pipeline-pack.md`, `content-pack.md`, `delivery-pack.md`, `money-pack.md`, and `decisions-pack.md`, each naming the front door, the members, the shared input or discipline, the honest limits, and the inter-member dependencies. They follow the existing `skills/linkedin-pack.md` pattern: a link hub that reads the pack as one connected unit.
- **Discovery wiring.** The `menu` engine gained the four front doors as discovery capabilities (natural-language only, no invented slash forms), and `profile-router` now leads each operator variant with the pack front doors that fit it: a founder is invited into Pipeline, Delivery, and Decisions, a career-mover into Content and Decisions, a builder into Decisions. Nothing is locked; the variant only changes what surfaces first.
- **No new member skills, no new dependencies.** The wedges route to skills that already shipped, so the packs add reach without adding paid tools or breaking the free-tier floor. Skill count moved 75 -> 79 across every parity surface. The brain and meta skills and the voice scaffold stay shared substrate, not packed.

### Add - give your OS a voice (the first installable capability of the modular scaffold)

- **`add-voice` skill - say "add voice" and talk to your OS out loud.** The OS ships as a complete text brain; this adds an optional mouth and ears on top of the same brain. It is the first of the "add a part" capabilities (voice, then a mouth, then hands) that plug into the brain.
- **The default needs no extra key.** Tier 0 holds the accessibility floor: your browser's built-in speech recognition (ears) and speech (mouth) plus the reasoning CLI you already run the OS in (brain, `claude -p` by default - no API key, it uses the subscription you already have). A small local Python setup (`skills/add-voice/setup.py`, standard library only, no pip install) wires a gitignored `voice/` runtime bound to your machine. Run `python voice/server.py` and a local page lets you hold-to-talk and hear the answer; "save" appends what you said to `brain/log.md`.
- **One honest disclaimer, stated up front.** In Chrome and Edge the browser sends your audio to its vendor to transcribe - no key and no cost, but not fully local. The page and the docs say so. The fully-local upgrade (faster-whisper + Piper) and the realtime upgrade (Gemini Live on a free Google AI Studio key) are opt-in, each with its cost-and-accuracy trade stated before you commit. A premium ElevenLabs mouth is a deliberate paid choice, never a default.
- **Tier 1 realtime is wired - say "add voice --realtime".** A sub-second streaming conversation on a free Google AI Studio key: a realtime model (Gemini Live) hears you, takes turns, and speaks back in its OWN native voice, while the no-key reasoning CLI you already run stays the back-brain that reads your files. Two models, two jobs. `skills/add-voice/setup_realtime.py` prints the cost-and-accuracy disclaimer first, installs the two deps (google-genai, websockets), copies the realtime page and bridge into the gitignored `voice/`, and inherits the Tier-0 brain command; the key is stored only in `.env` via the connect flow (`connect gemini`). It engages instantly on every turn and pauses only when you say "thinking" out loud; the brain reads run off the audio loop so they never freeze the voice; every turn is recorded locally to `voice/live-log.md`. The realtime tools read the OS and make one safe append (save to log) - sending and computer control stay a separate, gated "add hands". The honest disclaimer is load-bearing: a free key has a free daily quota on Flash models and heavy realtime use can move onto paid per-token rates, stated before you commit.
- **Built to degrade, never dead-end.** No reasoning CLI on PATH -> ears and save-to-brain still work. No browser speech (Firefox, Safari) -> a text box keeps the loop working. Every turn logs to a local-only `voice/runtime-log.jsonl` so failures are visible. The brain context is kept deliberately lean (a short preamble plus a small identity slice, never the whole repo) so a long session does not bloat and fail.
- **Docs.** `docs/voice-extension.md` updated from "DIY, no command" to point at the skill while keeping its honest posture (text is the whole product; voice is optional). Skill count moved 73 -> 74 across every parity surface.

### Change - keep a long session lean (context discipline made explicit)

- **The Session Protocol now governs a long session, not just the boot load.** The bootloader already said "load only what you need" at session start. It now adds the rule that was missing: across a long session, do not re-read a whole file you already hold, retrieve narrowly (grep the line or read the one section) for a small answer, and treat the SessionStart brief plus `brain/.snapshot.md` as the always-on desk while the rest of the repo is a filing cabinet opened only for the task in hand. This is the named fix for an OS that slows down and starts to error many turns into a session as context fills.
- **`log-archive` skill - say "archive my log".** The running log had a documented 300-line cap and a `brain/archive/` folder, but nothing implemented the aging. Now a deterministic script (`scripts/log-archive.py`, standard library only, no LLM call) moves the oldest entries out of `brain/log.md` into monthly `brain/archive/log-YYYY-MM.md` files and leaves a one-line pointer behind. The pointer is the cache summary: history exists and is one hop away, without sitting in the file every skill reads. It never splits an entry, never archives an entry it cannot date, conserves every entry, and is idempotent. Preview with `--dry-run`. Skill count moved 74 -> 75 across every parity surface.

### Fix - realtime voice could not connect its key on a fresh install

- **The gemini connector now ships to fresh installs.** The realtime voice tier added the gemini connector to `scripts/connect.py` but not to the `templates/scripts/` copy the setup wizard places in a new install, so a freshly installed OS could not run `connect gemini` and the realtime key path was dead on a clean clone. The template now matches the live script.
- **Adding a second free key is documented as an explicit step.** `references/realtime-architecture.md` now spells out how to add `GEMINI_API_KEY2` for quota headroom: create another free AI Studio key (optionally in a second Google account for a separate daily quota) and store it with `connect.py set-secret GEMINI_API_KEY2` on stdin. The front rotates to it automatically on quota.

## v1.37.0 - 2026-06-06

### Add - one folder you own, plus two more role modes

A minor release with two user-facing wins: the OS now installs into a folder you own instead of a hidden cache dir, and the role system gains the two modes the docs used to wave away.

#### Install into one folder you own

- **The OS lands in a folder you own, not an app cache.** Install used to clone into `~/.claude/plugins/founder-os`, a tool-managed path that reads like a cache and gets wiped on plugin update, while the wizard built your living data somewhere else. The result was split-brain: your files in one place, the hooks wired to another. Now the curl and git-clone paths set up in place, so your data, your hooks, and your commands all live in one folder you own (default `~/founder-os`). The plugin path still keeps its engine where Claude Code needs it to discover commands and hooks, but the wizard builds your OS in the folder you own and names the engine as separate, invisible plumbing.
- **Engine and data are named as the separate things they are.** The install message and the docs now say it plainly: the folder is yours, a normal git repo you can back up, move, or fork, and nothing phones home. The plugin (if you use that path) is just the Claude engine that operates on the folder.
- **An existing install is detected, not duplicated.** A pre-v1.37 install at the old cache path is found and kept, so re-running setup does not leave you with a divergent second copy.

#### The role system is real now

- **Two new role modes: CSO and CTO.** They ship as files in `templates/roles/` and the setup wizard installs them, so the OS now carries six role modes instead of four. CSO holds the portfolio view across everything you run (entity health, time and attention balance, catching strategy that is really just motion). CTO keeps your tool stack and automations coherent (an infrastructure registry, a smallest-viable-option automation protocol, and health monitoring). Both are reference-until-invoked: they stay out of default routing so they never compete with COO for everyday work, and they activate only when you ask ("act as CSO", "switch to CTO"). The docs used to tell you to copy a skill folder to get these. That was wrong. They are roles, and now they are shipped as roles.
- **The BD trigger is honest.** BD claimed it became the default mode once you had "5+ live prospects", but nothing in the product reads that count, so the flip never happened. The copy now says what is true: invoke BD explicitly, or it shifts in when the task is clearly pipeline work. No documented automatic behavior the product does not deliver.
- **You are told how to switch lens.** The README roles block now states the plain phrase: say "switch to CMO" (or any role) to change lens yourself, because a non-technical founder will not guess it.

### Cross-cutting

VERSION bumped to 1.37.0. Both manifest version fields and the README status line updated to match. Role-mode count statements reconciled from four to six across `README.md`, `CLAUDE.md`, `AGENTS.md`, `llms.txt`, both manifests, the bootloader template, and `roles/index.md`. A new CI guard, `.github/scripts/check_role_parity.py` (wired into the doc-parity workflow), asserts every role file on disk is named by `roles/index.md` and the setup wizard's copy list, so a future doc refactor cannot silently drop a role from the wizard while CI stays green. Skill count unchanged at 62, command count unchanged at 34, test count unchanged at 643 (no new tests; the new role files are markdown the wizard copies). The two new role files were checked against the private-name, em-dash, and vendor-leak guards before commit.

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
