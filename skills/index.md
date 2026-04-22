# Founder OS Skills - Plan B Registry

14 skills included. The setup wizard (`founder-os-setup`) is the entry point.
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

## Commands

In addition to skills, this plugin ships one slash command:

| Command | Purpose |
|---------|---------|
| [/pre-meeting](../.claude/commands/pre-meeting.md) | Hard gate before any meeting. Requires capture artifact + ask. Logs to brain/log.md. |

## Status

All 14 skills merged from the `founder-os-product` branch on 2026-04-22. Each skill is generic (no ARCAS-specific references, no personal names). Voice-neutral for adaptation by the setup wizard using the founder's identity and writing-style rules.

Scrubbed for brand leakage as part of the 2026-04-22 launch-prep pass. Any new skill added to this registry must pass the banned-token guard in `rules/plan-a-plan-b.md` before commit.
