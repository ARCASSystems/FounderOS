# Founder OS Skills

> Single source of truth for the skill and command registry. `CLAUDE.md` points here instead of repeating the list; [`../docs/skills.md`](../docs/skills.md) is the long-form mirror of these same skills. When skills or counts change, update this file first, then mirror to `docs/skills.md`.

62 skills as of v1.36. v1.34 adds `linkedin-network-scan` - rank your own LinkedIn data export against an ICP you define, without the raw CSVs ever entering the assistant's context. A deterministic local script (standard library only, no pip install) scores every connection and collapses the export to a compact ranked worklist; the assistant reads only the small digest. Free plan only, message content never read. v1.32 adds `profile-router` - the layer that reads who is operating the OS and what it should lead with, writing `core/profile.md` at setup so every skill opens with what this operator's situation needs. v1.32 also lands the registry rows for five generic tooling skills ported from the private source: `skill-creator`, `web-fetch-extract`, `memory-pass`, `cross-link`, and `github-ops`. v1.29 adds three on-demand liveness skills: `strategic-read` (5-section state-of-the-OS report on demand), `log-reply` (ingests pasted threads from WhatsApp / Telegram / email / voice memo transcript into `brain/log.md` with proposed context updates), and `since-last-session` (reports the delta since the last marker time, then advances the marker). All three are free-tier accessible: file reads plus in-session synthesis, no external API call. v1.27 added `prospect-init` (lightweight per-prospect file creator under `companies/prospects/<slug>.md`) alongside the F27 operator/prospect path split, the F34 ingest cleanup, the F46 voice-interview phase renumber, and the F38 wiki-walk consolidation. v1.25 adds the brand voice layer: an operator can now run multiple brands with separate voice + positioning per brand, distinct from the operator's personal voice. Three new skills (`brand-voice-interview`, `campaign-from-theme`, `review-responder`) and voice-routing across the five voice-coupled writing skills. v1.24 adds Python preflight gates to 10 writing and reasoning skills (no new skills, hardened existing ones). v1.23 added the natural-language capture path (no new skills, new hook + bootloader rewrite). v1.22 added `observation-rollup` (weekly JSONL compression) and `legal-compliance` (jurisdiction-aware legal reference). v1.21 added `queue` (execution queue with 3-item ACTIVE cap) and `verify` (read-only health check across 8 substrate points). v1.20.0 was the natural-language routing release plus `/founder-os:menu`. v1.20.2 added the `today` wrapper skill. v1.20.3 added anti-example voice depth. v1.10 added the runtime brain context layer plus brain-pass. The setup wizard (`founder-os-setup`) is the entry point. All others activate via natural language phrasing or via `/founder-os:<command>`.

| Skill | Status | Replaces |
|-------|--------|---------|
| [founder-os-setup](founder-os-setup/SKILL.md) | Ready | Onboarding flow |
| [readiness-check](readiness-check/SKILL.md) | Ready | OS health audit. Run via `/founder-os:status`. |
| [ingest](ingest/SKILL.md) | Ready | File a source into raw/ with provenance. Propose wiki updates. Run via `/founder-os:ingest`. |
| [lint](lint/SKILL.md) | Ready | Read-only audit of wiki integrity. Run via `/founder-os:lint`. |
| [wiki-build](wiki-build/SKILL.md) | Ready | Walk markdown, extract `[[wikilinks]]`, refresh auto-generated graph in `brain/relations.yaml`. Companion to lint. Run via `/founder-os:wiki-build`. |
| [query](query/SKILL.md) | Ready | Multi-hop traversal across `brain/relations.yaml` plus core operating files. Run via `/founder-os:query`. |
| [brain-snapshot](brain-snapshot/SKILL.md) | Ready | Generates and documents the runtime context payload skills consume at task time. Output lives at `brain/.snapshot.md`. |
| [brain-pass](brain-pass/SKILL.md) | Ready | Semantic retrieval over the brain layer. Synthesises answers across log, knowledge, decisions, flags, patterns. Run via `/founder-os:brain-pass "<question>"`. |
| [audit](audit/SKILL.md) | Ready | Composite OS health report (readiness + lint + wiki + brain staleness + voice completeness). Run via `/founder-os:audit`. |
| [menu](menu/SKILL.md) | Ready | Capability discovery. Say "show me what you can do" or run `/founder-os:menu`. Returns 5 to 7 capability suggestions tailored to current state. |
| [today](today/SKILL.md) | Ready | Today brief wrapper. Say "what's on for today?" or run `/today`. |
| [weekly-review](weekly-review/SKILL.md) | Ready | |
| [priority-triage](priority-triage/SKILL.md) | Ready | Reclaim, Taskade |
| [brain-log](brain-log/SKILL.md) | Ready | |
| [decision-framework](decision-framework/SKILL.md) | Ready | |
| [forcing-questions](forcing-questions/SKILL.md) | Ready | Anti-shiny-object gate before new initiatives start. Run via `/founder-os:forcing-questions`. |
| [session-handoff](session-handoff/SKILL.md) | Ready | |
| [handoff-protocol](handoff-protocol/SKILL.md) | Ready | Human-to-human or role-to-role handoff artifact. |
| [context-persistence](context-persistence/SKILL.md) | Ready | Source-backed context lookup before asking the user to repeat themselves. |
| [meeting-prep](meeting-prep/SKILL.md) | Ready | |
| [knowledge-capture](knowledge-capture/SKILL.md) | Ready | Distilled notes in `brain/knowledge/`. Read back by proposal-writer and strategic-analysis. |
| [email-drafter](email-drafter/SKILL.md) | Ready | Lavender, Grammarly |
| [sop-writer](sop-writer/SKILL.md) | Ready | |
| [founder-coaching](founder-coaching/SKILL.md) | Ready | Culture Amp, Lattice |
| [bottleneck-diagnostic](bottleneck-diagnostic/SKILL.md) | Ready | Founder dependency diagnostic. |
| [unit-economics](unit-economics/SKILL.md) | Ready | |
| [content-repurposer](content-repurposer/SKILL.md) | Ready | Jasper, Copy.ai |
| [strategic-analysis](strategic-analysis/SKILL.md) | Ready | |
| [pre-send-check](pre-send-check/SKILL.md) | Ready | Hard gate before shipping a client-facing deliverable |
| [blind-spot-review](blind-spot-review/SKILL.md) | Ready | Second-pass review before pre-send. |
| [ship-deliverable](ship-deliverable/SKILL.md) | Ready | Final composition gate (template + anti-AI + blind-spot + pre-send). Run via `/founder-os:ship-deliverable`. |
| [approval-gates](approval-gates/SKILL.md) | Ready | Auto-run, ask-first, or refuse gate checks against `rules/approval-gates.md`. |
| [data-security](data-security/SKILL.md) | Ready | Data class and tool-safety check before sending content to external services. |
| [legal-compliance](legal-compliance/SKILL.md) | Ready | Jurisdiction-aware legal reference layer. |
| [your-voice](your-voice/SKILL.md) | Ready | Generic AI tone for all written output |
| [your-deliverable-template](your-deliverable-template/SKILL.md) | Ready | Canva templates, generic CV/deck builders |
| [voice-interview](voice-interview/SKILL.md) | Ready | Captures user's writing voice into core/voice-profile.yml |
| [brand-interview](brand-interview/SKILL.md) | Ready | Captures user's visual brand into core/brand-profile.yml or brands/<slug>/visual.yml |
| [brand-voice-interview](brand-voice-interview/SKILL.md) | Ready | Captures a brand's voice and positioning into brands/<slug>/voice.yml + positioning.yml. One run per brand. Separate from voice-interview which captures operator voice. |
| [campaign-from-theme](campaign-from-theme/SKILL.md) | Ready | Turns a theme into a funnel-gated marketing campaign. Refuses to draft until speaker, objective, audience temperature, channels, and success metric are all answered. |
| [review-responder](review-responder/SKILL.md) | Ready | Drafts replies to incoming customer reviews, DMs, WhatsApp, emails. Asks whose voice (operator or brand) and applies channel + posture constraints. |
| [business-context-loader](business-context-loader/SKILL.md) | Ready | Per-company context file scanner and gap router (operator companies only) |
| [prospect-init](prospect-init/SKILL.md) | Ready | Lightweight per-prospect file creator. Captures 3-5 fields and writes `companies/prospects/<slug>.md`. Companion to business-context-loader (which is operator-only). Run via `/founder-os:prospect-init <slug>`. |
| [strategic-read](strategic-read/SKILL.md) | Ready | On-demand state-of-the-OS report. 5 sections: Identity anchor, Active commitments and pipeline, Open decisions, Active flags, Next 3 recommended moves. Read-only. Free-tier accessible. Pass a section key (`identity`, `commitments`, `decisions`, `flags`, `next-moves`) to render only that section. Run via `/founder-os:strategic-read [section]`. |
| [log-reply](log-reply/SKILL.md) | Ready | Captures a pasted thread (WhatsApp, Telegram, email body, voice memo transcript) into `brain/log.md`. Proposes (never auto-writes) updates to `context/clients.md` and `context/leads.md`. Per `rules/approval-gates.md`. Run via `/founder-os:log-reply`. |
| [since-last-session](since-last-session/SKILL.md) | Ready | Delta report since the last marker time. 5 sections: hours elapsed, brain/log.md entries added, flags decayed, commitments overdue, files modified in `context/`. Marker at `brain/.last-session`. First-run seeds the marker and stops. Run via `/founder-os:since-last-session`. |
| [linkedin-post](linkedin-post/SKILL.md) | Ready | Voice-coupled LinkedIn post writer |
| [client-update](client-update/SKILL.md) | Ready | Voice-coupled client status update writer |
| [proposal-writer](proposal-writer/SKILL.md) | Ready | Voice and brand-coupled proposal writer. Reads `brain/knowledge/` for past wins. |
| [queue](queue/SKILL.md) | Ready | Execution queue with 3-item ACTIVE cap. Say "what's on my plate" or "add to queue: <thing>". Surfaced in SessionStart brief. |
| [verify](verify/SKILL.md) | Ready | Read-only substrate health check across 8 checks. Say "verify the OS". Never auto-fixes. |
| [observation-rollup](observation-rollup/SKILL.md) | Ready | Compress weekly observation logs. Say "roll up observations" or "compress old logs". Run via `/founder-os:observation-rollup`. |
| [profile-router](profile-router/SKILL.md) | Ready | Reads who is operating the OS and what it should lead with. Maps five variants (founder, career-mover, builder, student, team-internal) to lead surfaces and framing. Writes `core/profile.md` at setup. Say "update my profile". |
| [skill-creator](skill-creator/SKILL.md) | Ready | Create, improve, and tune skills. Hard description-length check before any description write. |
| [web-fetch-extract](web-fetch-extract/SKILL.md) | Ready | Fetch a URL and extract structured data inline per a natural-language goal. Free-tier safe, no LLM API call. Backed by `scripts/scrape.py`. |
| [memory-pass](memory-pass/SKILL.md) | Ready | Audit `MEMORY.md` Active Project Context against current files. Surfaces stale claims. Never writes without confirmation. |
| [cross-link](cross-link/SKILL.md) | Ready | Propose `[[wikilink]]` insertions for backtick paths and prose path mentions in one file. Companion to wiki-build. |
| [github-ops](github-ops/SKILL.md) | Ready | GitHub operations via the `gh` CLI: issues, pull requests, releases, repo state. |
| [linkedin-network-scan](linkedin-network-scan/SKILL.md) | Ready | Free Sales Navigator alternative. Rank your own LinkedIn export against an ICP you define; a deterministic local script (stdlib only) collapses the raw CSVs to a compact ranked worklist the assistant reads instead of the full export. Free plan only, message content never read, nothing sent. Backed by `scan.py` + `icp.example.yaml`. |
| [reconnect-prompt](reconnect-prompt/SKILL.md) | Ready | Turns an expired-token or 401 failure into one copy-paste reconnect prompt and logs the failed call to `system/quarantine.md`. Never retries, never asks for credentials. Called by integration-touching skills on auth failure. Run via `/founder-os:reconnect-prompt`. |
| [list-pruner](list-pruner/SKILL.md) | Ready | Cleans a contact list before outreach: removes duplicate emails, flags missing fields, scores each row High / Medium / Low. Accepts a CSV path or pasted table. Composes with `linkedin-network-scan`. Run via `/founder-os:list-pruner`. |
| [finance-import](finance-import/SKILL.md) | Ready | Parses a finance CSV export into a normalized markdown summary at `finance/<period>/summary.md`, totalled by category. Read-only at the source. Feeds `unit-economics`. Run via `/founder-os:finance-import`. |

## Commands

This plugin ships 34 slash commands:

| Command | Purpose |
|---------|---------|
| [/founder-os:menu](../.claude/commands/menu.md) | Show 5 to 7 capability suggestions tailored to current state. Say "show me what you can do" or run `/founder-os:menu`. Read-only. |
| [/founder-os:setup](../.claude/commands/setup.md) | Run the Founder OS setup wizard. Generates identity, priorities, decisions, cadence, and brain files from a guided interview. |
| [/founder-os:voice-interview](../.claude/commands/voice-interview.md) | Capture how you write into `core/voice-profile.yml`. Activates the voice-coupled writing skills. |
| [/founder-os:brand-interview](../.claude/commands/brand-interview.md) | Capture your visual identity into `core/brand-profile.yml`. Activates branded outputs. |
| [/founder-os:brand-voice-interview](../.claude/commands/brand-voice-interview.md) | Capture a brand's voice and positioning. One run per brand. Different from voice-interview (operator personal voice). |
| [/founder-os:campaign-from-theme](../.claude/commands/campaign-from-theme.md) | Turn one theme into a funnel-gated marketing campaign. Five gate questions before any draft. |
| [/founder-os:review-responder](../.claude/commands/review-responder.md) | Draft replies to incoming customer messages (reviews, DMs, WhatsApp, emails). Asks whose voice, then drafts with channel + posture constraints. |
| [/founder-os:status](../.claude/commands/status.md) | Read-only OS readiness check. Returns a weighted score and the next 3 high-impact moves. |
| [/founder-os:ingest](../.claude/commands/ingest.md) | File a source (URL, file path, or pasted text) into `raw/` with provenance. Propose wiki updates you approve. |
| [/founder-os:lint](../.claude/commands/lint.md) | Read-only wiki audit. Cross-references, orphans, stale content, provenance, possible contradictions. |
| [/founder-os:wiki-build](../.claude/commands/wiki-build.md) | Refresh the auto-generated wiki graph in `brain/relations.yaml`. Idempotent. |
| [/founder-os:query](../.claude/commands/query.md) | Return the top 3 to 5 OS nodes for a multi-hop question. Plain markdown traversal, no embeddings. |
| [/founder-os:brain-pass](../.claude/commands/brain-pass.md) | Synthesise an answer across the brain layer with citations. Use when a question spans multiple brain files. |
| [/founder-os:audit](../.claude/commands/audit.md) | Composite OS health report across readiness, lint, wiki, brain staleness, and voice completeness. |
| [/founder-os:forcing-questions](../.claude/commands/forcing-questions.md) | Six-question gate before any new initiative, scope expansion, or fresh idea is started. |
| [/founder-os:devil](../.claude/commands/devil.md) | Devil's advocate. Runs the output bias self-check (`rules/biases.md`) against a claim or decision. Read-only. |
| [/founder-os:ship-deliverable](../.claude/commands/ship-deliverable.md) | Final read-only gate before any external deliverable leaves your machine. |
| [/founder-os:legal-setup](../.claude/commands/legal-setup.md) | Set up legal-compliance for the founder's jurisdiction. |
| [/founder-os:legal-add-source](../.claude/commands/legal-add-source.md) | Add a legal source URL or PDF path to the loaded jurisdiction. |
| [/founder-os:legal-update](../.claude/commands/legal-update.md) | Refresh legal-compliance source freshness. |
| [/founder-os:rant](../.claude/commands/rant.md) | Qualify a raw voice dump, then route to a decision, draft, plan, log, or capture path. |
| [/founder-os:dream](../.claude/commands/dream.md) | Distil unprocessed rants into patterns, flags, parked decisions, needs-input, and client signals. Writes a 5-line digest to `brain/log.md`. |
| [/founder-os:update](../.claude/commands/update.md) | Pull the latest System Layer files (skills, templates, commands, hooks) without touching your personal data. Subcommands: check, rollback. |
| [/founder-os:uninstall](../.claude/commands/uninstall.md) | Cleanly remove Founder OS. Default mode preserves your data; `--purge` removes everything. |
| [/pre-meeting](../.claude/commands/pre-meeting.md) | Hard gate before any meeting. Requires capture artifact + ask. Logs to brain/log.md. |
| [/capture-meeting](../.claude/commands/capture-meeting.md) | Routes a transcript or brain dump into brain/log.md, context/clients.md, and open commitments. |
| [/today](../.claude/commands/today.md) | 20-line one-screen view of today. Anchor, open decisions, active flags, last 3 log entries, next calendar event. |
| [/next](../.claude/commands/next.md) | One recommended next action across priorities, deals, and cadence. |
| [/founder-os:queue](../.claude/commands/queue.md) | Manage the execution queue. Say "what's on my plate" or "add to queue: <thing>". ACTIVE is capped at 3. |
| [/founder-os:verify](../.claude/commands/verify.md) | Read-only substrate health check across 8 checks. Say "verify the OS". Never auto-fixes. |
| [/founder-os:observation-rollup](../.claude/commands/observation-rollup.md) | Compress weekly observation logs. Say "roll up observations" or "compress old logs". |
| [/founder-os:strategic-read](../.claude/commands/strategic-read.md) | On-demand state-of-the-OS report. 5 sections by default. Pass a section key (`identity`, `commitments`, `decisions`, `flags`, `next-moves`) to render only that section. Read-only. |
| [/founder-os:log-reply](../.claude/commands/log-reply.md) | Capture a pasted thread (WhatsApp, Telegram, email body, voice memo transcript) into `brain/log.md`. Proposes context updates; operator confirms each before any write to `context/clients.md` or `context/leads.md`. |
| [/founder-os:since-last-session](../.claude/commands/since-last-session.md) | Delta report since the last marker time. Marker at `brain/.last-session` updates at end of run. First run seeds the marker and stops. |

## Status

62 skills. Each skill is generic: no founder-specific references, no personal names. Voice-neutral for adaptation by the setup wizard using the founder's identity, voice profile, and brand profile. Operators running multiple brands capture each brand voice separately via `brand-voice-interview`.

Release notes:

- v1.2 added the three voice-coupled skills (`linkedin-post`, `client-update`, `proposal-writer`) and `readiness-check`.
- v1.3 added `ingest` and `lint` (Karpathy-pattern wiki ops). Additive, no behaviour changes elsewhere.
- v1.4 added `wiki-build` and the brain substrate (decay convention, quarantine, approval gate matrix, SessionStart brief).
- v1.5 wired the wizard's captured answers (decision style, communication style, tool stack) through to six daily skills (`sop-writer`, `meeting-prep`, `email-drafter`, `strategic-analysis`, `decision-framework`, `your-voice`). `/rant` and `/dream` shipped with the `brain/rants/` folder. Auto-memory `MEMORY.md` template seeded by the wizard.
- v1.6 added eight translated operating skills (`forcing-questions`, `ship-deliverable`, `approval-gates`, `handoff-protocol`, `context-persistence`, `data-security`, `blind-spot-review`, `bottleneck-diagnostic`) plus `query` and `audit`. `brain/knowledge/` now feeds `proposal-writer` and `strategic-analysis`.
- v1.7 added stable entry IDs, progressive query modes, and opt-in observation logging.
- v1.8 added query test coverage for `scripts/query.py`.
- v1.9 added hook test coverage and documented the query `--root` flag.
- v1.10 added `brain-snapshot` (runtime context payload at `brain/.snapshot.md`), wired nine output-producing skills to consume it (meeting-prep, weekly-review, strategic-analysis, decision-framework, founder-coaching, knowledge-capture, unit-economics, priority-triage, brain-log), added `brain-pass` (semantic retrieval across the brain layer with citations), and auto-invoked brain-pass from meeting-prep and linkedin-post.
- v1.11 closed v1.10 install gaps so Path A users actually get the runtime brain context. Setup wizard now copies all runtime helpers, the wiki-build script ships at repo root, `/founder-os:update` and `/founder-os:uninstall` cover scripts and rules, PowerShell hooks parse ISO dates with InvariantCulture, and `.gitattributes` keeps `.sh` and `.py` LF-only on Windows clones. No new skills, no new commands.
- v1.12 added a hook-only memory-diff helper that runs from the SessionStart brief and flags `clients/<slug>/` folders without an auto-memory entry. No new skills, no new commands. Test count rose from 34 to 43.
- v1.20.0 was the discoverability release. Natural-language routing, the new `menu` skill (`/founder-os:menu`), and SessionStart Tip line. 21 commands, 56 + new tests.
- v1.20.1 corrected the v1.20.0 skill-count drift (docs claimed 39 skills after `menu` brought the filesystem total to 40), extracted the menu engine into `scripts/menu.py`, gated the SessionStart Tip line on a state-signal AND age requirement so a fresh install with no log history stays quiet, and added wizard test coverage for the 4 + 4 multi-choice prompts.
- v1.20.2 added positioning, buyer language, existing visual proof, a routed rant path, writing-skill voice gates, the `today` wrapper skill, and tag-based Tip use detection.

- v1.20.3 added anti-example voice depth to the voice interview and five writing skills. No behaviour changes to other skills.
- v1.21 added `queue` and `verify`.
- v1.22 added `legal-compliance`, `observation-rollup`, `linkedin-post`, and a `client-update` voice-coupling depth pass.
- v1.23 closed the capture-path promise from v1.22. A new UserPromptSubmit hook routes user input through four shape detectors (rant, named-entity, status update, preference) and emits capture suggestions Claude honors. Rants are eagerly written to `brain/rants/<date>.md`. SessionStart fires a welcome banner on fresh installs and surfaces unprocessed-rant count. Five operator-vocabulary triggers added to existing skills. No new skills.
- v1.24 added Python preflight gates to ten existing skills (five voice-coupled writing skills, four reasoning skills, brain-pass). When a required file is missing or template-filled, the gate exits in code and the skill stops with a one-line reason instead of producing silently-generic output. No new skills.
- v1.25 added the brand voice layer. Three new skills (`brand-voice-interview`, `campaign-from-theme`, `review-responder`). New `brands/<slug>/` directory holds per-brand voice + positioning + visual files. Five voice-coupled writing skills (linkedin-post, email-drafter, client-update, content-repurposer, proposal-writer) now route between operator voice and brand voice based on task context. Backward-compatible: operators without `brands/` set up see no behavior change. Operators with one or many brands get voice-correct output without manual switching. Anti-AI baseline adapts by brand register (plain-direct, measured-elegant, corporate-restrained, friendly-casual). Universal banned-phrase list and hard floor unchanged.

- v1.29 added three on-demand liveness skills (`strategic-read`, `log-reply`, `since-last-session`) and their wrapper commands. All three are free-tier accessible: file reads plus in-session synthesis, no external API call. The `since-last-session` marker at `brain/.last-session` is owned by the skill itself; a future SessionStart hook may also update it, but the skill does not depend on the hook existing.

- v1.30 added the SessionStart liveness hook that v1.29 deferred. The hook reads `brain/.last-session` on every Claude Code session boot and prints one line below the brief about elapsed time since the last `/since-last-session` run. The hook does not call any LLM, does not write the marker, and does not block session start. Plus a section argument on `/strategic-read` so the report can be scoped to one of the 5 sections without generating the others. No new skills; one new hook; one arg extension.

All additions across v1.2 through v1.30 are additive. No existing skill behaviour was changed without an explicit version note.
