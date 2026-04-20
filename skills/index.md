# Founder OS Skills — Plan B Registry

14 skills included. The setup wizard (`founder-os-setup`) is the entry point.
All others activate via `/skill-name` or are invoked implicitly by roles.

| Skill | Status | Replaces |
|-------|--------|---------|
| [founder-os-setup](founder-os-setup/SKILL.md) | Ready | Onboarding flow |
| weekly-review | Pending translation from Plan A | |
| priority-triage | Pending translation from Plan A | Reclaim, Taskade |
| brain-log | Pending translation from Plan A | |
| decision-framework | Pending translation from Plan A | |
| session-handoff | Pending translation from Plan A | |
| meeting-prep | Pending translation from Plan A | |
| knowledge-capture | Pending translation from Plan A | |
| email-drafter | Pending translation from Plan A | Lavender, Grammarly |
| sop-writer | Pending translation from Plan A | |
| founder-coaching | Pending translation from Plan A | Culture Amp, Lattice |
| unit-economics | Pending translation from Plan A | |
| content-repurposer | Pending translation from Plan A | Jasper, Copy.ai |
| strategic-analysis | Pending translation from Plan A | |

## How Translation Works

Each "Pending translation from Plan A" skill already exists in `skills/<name>/SKILL.md` on main.
Translation = copy the skill to `founder-os-product/skills/<name>/SKILL.md` and:
- Strip brand-specific references (see banned tokens list in the parent repo's plan-a-plan-b.md)
- Swap vendor names for `{placeholder}` per the Stack Abstraction table
- Generalize specific company examples to generic founder examples

Run translation using the `Update Founder-OS-Product` command described in `rules/plan-a-plan-b.md`.
