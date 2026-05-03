# Founder OS Skills

27 skills included in v1.4. The setup wizard (`founder-os-setup`) is the entry point.
All others activate via `/skill-name` or are invoked implicitly by roles.

| Skill | Status | Replaces |
|-------|--------|---------|
| [founder-os-setup](founder-os-setup/SKILL.md) | Ready | Onboarding flow |
| [readiness-check](readiness-check/SKILL.md) | Ready | OS health audit. Run via `/founder-os:status`. |
| [ingest](ingest/SKILL.md) | Ready | File a source into raw/ with provenance. Propose wiki updates. Run via `/founder-os:ingest`. |
| [lint](lint/SKILL.md) | Ready | Read-only audit of wiki integrity. Run via `/founder-os:lint`. |
| [wiki-build](wiki-build/SKILL.md) | Ready | Walk markdown, extract `[[wikilinks]]`, refresh auto-generated graph in `brain/relations.yaml`. Companion to lint. Run via `/founder-os:wiki-build`. |
| [weekly-review](weekly-review/SKILL.md) | Ready | |
| [priority-triage](priority-triage/SKILL.md) | Ready | Reclaim, Taskade |
| [brain-log](brain-log/SKILL.md) | Ready | |
| [decision-framework](decision-framework/SKILL.md) | Ready | |
| [session-handoff](session-handoff/SKILL.md) | Ready | |
| [meeting-prep](meeting-prep/SKILL.md) | Ready | |
| [knowledge-capture](knowledge-capture/SKILL.md) | Ready | Notes from books, podcasts, conversations (no source preservation - use `ingest` if you need provenance) |
| [email-drafter](email-drafter/SKILL.md) | Ready | Lavender, Grammarly |
| [sop-writer](sop-writer/SKILL.md) | Ready | |
| [founder-coaching](founder-coaching/SKILL.md) | Ready | Culture Amp, Lattice |
| [unit-economics](unit-economics/SKILL.md) | Ready | |
| [content-repurposer](content-repurposer/SKILL.md) | Ready | Jasper, Copy.ai |
| [strategic-analysis](strategic-analysis/SKILL.md) | Ready | |
| [pre-send-check](pre-send-check/SKILL.md) | Ready | Hard gate before shipping a client-facing deliverable |
| [your-voice](your-voice/SKILL.md) | Ready | Generic AI tone for all written output |
| [your-deliverable-template](your-deliverable-template/SKILL.md) | Ready | Canva templates, generic CV/deck builders |
| [voice-interview](voice-interview/SKILL.md) | Ready | Captures user's writing voice into core/voice-profile.yml |
| [brand-interview](brand-interview/SKILL.md) | Ready | Captures user's visual brand into core/brand-profile.yml |
| [business-context-loader](business-context-loader/SKILL.md) | Ready | Per-company context file scanner and gap router |
| [linkedin-post](linkedin-post/SKILL.md) | Ready | Voice-coupled LinkedIn post writer |
| [client-update](client-update/SKILL.md) | Ready | Voice-coupled client status update writer |
| [proposal-writer](proposal-writer/SKILL.md) | Ready | Voice and brand-coupled proposal writer |

## Commands

This plugin ships thirteen slash commands:

| Command | Purpose |
|---------|---------|
| [/founder-os:setup](../.claude/commands/setup.md) | Run the Founder OS setup wizard. Generates identity, priorities, decisions, cadence, and brain files from a guided interview. |
| [/founder-os:voice-interview](../.claude/commands/voice-interview.md) | Capture how you write into `core/voice-profile.yml`. Unlocks the voice-coupled writing skills. |
| [/founder-os:brand-interview](../.claude/commands/brand-interview.md) | Capture your visual identity into `core/brand-profile.yml`. Unlocks branded outputs. |
| [/founder-os:status](../.claude/commands/status.md) | Read-only OS readiness check. Returns a weighted score and the next 3 high-leverage moves. |
| [/founder-os:ingest](../.claude/commands/ingest.md) | File a source (URL, file path, or pasted text) into `raw/` with provenance. Propose wiki updates you approve. |
| [/founder-os:lint](../.claude/commands/lint.md) | Read-only wiki audit. Cross-references, orphans, stale content, provenance, possible contradictions. |
| [/founder-os:wiki-build](../.claude/commands/wiki-build.md) | Refresh the auto-generated wiki graph in `brain/relations.yaml`. Idempotent. |
| [/founder-os:update](../.claude/commands/update.md) | Pull the latest System Layer files (skills, templates, commands, hooks) without touching your personal data. Subcommands: check, rollback. |
| [/founder-os:uninstall](../.claude/commands/uninstall.md) | Cleanly remove Founder OS. Default mode preserves your data; `--purge` removes everything. |
| [/pre-meeting](../.claude/commands/pre-meeting.md) | Hard gate before any meeting. Requires capture artifact + ask. Logs to brain/log.md. |
| [/capture-meeting](../.claude/commands/capture-meeting.md) | Routes a transcript or brain dump into brain/log.md, context/clients.md, and open commitments. |
| [/today](../.claude/commands/today.md) | 20-line one-screen view of today. Anchor, open decisions, active flags, last 3 log entries, next calendar event. |
| [/next](../.claude/commands/next.md) | One recommended next action across priorities, deals, and cadence. |

## Status

27 skills. Each skill is generic: no founder-specific references, no personal names. Voice-neutral for adaptation by the setup wizard using the founder's identity, voice profile, and brand profile.

The three voice-coupled skills (`linkedin-post`, `client-update`, `proposal-writer`) and the readiness-check skill were added in v1.2. The `ingest` and `lint` skills (Karpathy-pattern wiki ops) were added in v1.3 - both additive, no existing skill behavior changes. The `wiki-build` skill was added in v1.4 along with the underlying brain substrate (decay-aware brain layer, quarantine catch-net, approval gate matrix template, SessionStart brief). All v1.4 additions are additive.
