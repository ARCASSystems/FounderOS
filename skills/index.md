# Founder OS Skills

39 skills included as of v1.12 (37 from v1.9 plus `brain-snapshot` and `brain-pass`, both added in v1.10). v1.7 added stable entry IDs, token-aware progressive query, and an opt-in observation log. v1.8 added a query test suite. v1.9 added hook test coverage and documented the query `--root` flag. v1.10 added the runtime brain context layer (a deterministic snapshot every skill can consume at task time, plus a brain-pass skill that synthesises answers across the brain layer with citations). v1.11 was launch hardening (no new skills, install ergonomics fixed). v1.12 added a hook-only memory-diff helper that flags `clients/<slug>/` folders missing from auto-memory (no new skills, no new commands). The setup wizard (`founder-os-setup`) is the entry point. All others activate via `/skill-name`, `/founder-os:<command>`, or are invoked implicitly by roles.

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
| [your-voice](your-voice/SKILL.md) | Ready | Generic AI tone for all written output |
| [your-deliverable-template](your-deliverable-template/SKILL.md) | Ready | Canva templates, generic CV/deck builders |
| [voice-interview](voice-interview/SKILL.md) | Ready | Captures user's writing voice into core/voice-profile.yml |
| [brand-interview](brand-interview/SKILL.md) | Ready | Captures user's visual brand into core/brand-profile.yml |
| [business-context-loader](business-context-loader/SKILL.md) | Ready | Per-company context file scanner and gap router |
| [linkedin-post](linkedin-post/SKILL.md) | Ready | Voice-coupled LinkedIn post writer |
| [client-update](client-update/SKILL.md) | Ready | Voice-coupled client status update writer |
| [proposal-writer](proposal-writer/SKILL.md) | Ready | Voice and brand-coupled proposal writer. Reads `brain/knowledge/` for past wins. |

## Commands

This plugin ships twenty slash commands (nineteen from v1.9 plus `/founder-os:brain-pass`):

| Command | Purpose |
|---------|---------|
| [/founder-os:setup](../.claude/commands/setup.md) | Run the Founder OS setup wizard. Generates identity, priorities, decisions, cadence, and brain files from a guided interview. |
| [/founder-os:voice-interview](../.claude/commands/voice-interview.md) | Capture how you write into `core/voice-profile.yml`. Activates the voice-coupled writing skills. |
| [/founder-os:brand-interview](../.claude/commands/brand-interview.md) | Capture your visual identity into `core/brand-profile.yml`. Activates branded outputs. |
| [/founder-os:status](../.claude/commands/status.md) | Read-only OS readiness check. Returns a weighted score and the next 3 high-impact moves. |
| [/founder-os:ingest](../.claude/commands/ingest.md) | File a source (URL, file path, or pasted text) into `raw/` with provenance. Propose wiki updates you approve. |
| [/founder-os:lint](../.claude/commands/lint.md) | Read-only wiki audit. Cross-references, orphans, stale content, provenance, possible contradictions. |
| [/founder-os:wiki-build](../.claude/commands/wiki-build.md) | Refresh the auto-generated wiki graph in `brain/relations.yaml`. Idempotent. |
| [/founder-os:query](../.claude/commands/query.md) | Return the top 3 to 5 OS nodes for a multi-hop question. Plain markdown traversal, no embeddings. |
| [/founder-os:brain-pass](../.claude/commands/brain-pass.md) | Synthesise an answer across the brain layer with citations. Use when a question spans multiple brain files. |
| [/founder-os:audit](../.claude/commands/audit.md) | Composite OS health report across readiness, lint, wiki, brain staleness, and voice completeness. |
| [/founder-os:forcing-questions](../.claude/commands/forcing-questions.md) | Six-question gate before any new initiative, scope expansion, or fresh idea is started. |
| [/founder-os:ship-deliverable](../.claude/commands/ship-deliverable.md) | Final read-only gate before any external deliverable leaves your machine. |
| [/founder-os:rant](../.claude/commands/rant.md) | Capture a raw voice dump into `brain/rants/<YYYY-MM-DD>.md`. No structure asked. |
| [/founder-os:dream](../.claude/commands/dream.md) | Distil unprocessed rants into patterns, flags, parked decisions, needs-input, and client signals. Writes a 5-line digest to `brain/log.md`. |
| [/founder-os:update](../.claude/commands/update.md) | Pull the latest System Layer files (skills, templates, commands, hooks) without touching your personal data. Subcommands: check, rollback. |
| [/founder-os:uninstall](../.claude/commands/uninstall.md) | Cleanly remove Founder OS. Default mode preserves your data; `--purge` removes everything. |
| [/pre-meeting](../.claude/commands/pre-meeting.md) | Hard gate before any meeting. Requires capture artifact + ask. Logs to brain/log.md. |
| [/capture-meeting](../.claude/commands/capture-meeting.md) | Routes a transcript or brain dump into brain/log.md, context/clients.md, and open commitments. |
| [/today](../.claude/commands/today.md) | 20-line one-screen view of today. Anchor, open decisions, active flags, last 3 log entries, next calendar event. |
| [/next](../.claude/commands/next.md) | One recommended next action across priorities, deals, and cadence. |

## Status

39 skills. Each skill is generic: no founder-specific references, no personal names. Voice-neutral for adaptation by the setup wizard using the founder's identity, voice profile, and brand profile.

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

All additions across v1.2 through v1.12 are additive. No existing skill behaviour was changed without an explicit version note.
