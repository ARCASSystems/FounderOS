# Founder OS Skills - Plan B Registry

20 skills included. The setup wizard (`founder-os-setup`) is the entry point.
All others activate via `/skill-name` or are invoked implicitly by roles.

| Skill | Status | Replaces |
|-------|--------|---------|
| [founder-os-setup](founder-os-setup/SKILL.md) | Ready | Onboarding flow |
| [weekly-review](weekly-review/SKILL.md) | Ready | |
| [priority-triage](priority-triage/SKILL.md) | Ready | Reclaim, Taskade |
| [brain-log](brain-log/SKILL.md) | Ready | |
| [decision-framework](decision-framework/SKILL.md) | Ready | |
| [session-handoff](session-handoff/SKILL.md) | Ready | |
| [meeting-prep](meeting-prep/SKILL.md) | Ready | |
| [knowledge-capture](knowledge-capture/SKILL.md) | Ready | |
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

## Commands

This plugin ships five slash commands:

| Command | Purpose |
|---------|---------|
| [/founder-os:setup](../.claude/commands/setup.md) | Run the Founder OS setup wizard. Generates identity, priorities, decisions, cadence, and brain files from a guided interview. |
| [/founder-os:update](../.claude/commands/update.md) | Pull the latest System Layer files (skills, templates, commands, hooks) without touching your personal data. Subcommands: check, rollback. |
| [/pre-meeting](../.claude/commands/pre-meeting.md) | Hard gate before any meeting. Requires capture artifact + ask. Logs to brain/log.md. |
| [/capture-meeting](../.claude/commands/capture-meeting.md) | Routes a transcript or brain dump into brain/log.md, context/clients.md, and open commitments. |
| [/today](../.claude/commands/today.md) | 20-line one-screen view of today. Anchor, open decisions, active flags, last 3 log entries, next calendar event. |

## Status

20 skills. Each skill is generic: no ARCAS-specific references, no personal names. Voice-neutral for adaptation by the setup wizard using the founder's identity, voice profile, and brand profile.

Scrubbed for brand leakage as part of the 2026-04-22 launch-prep pass. Any new skill added to this registry must pass the banned-token guard in `rules/plan-a-plan-b.md` before commit.
