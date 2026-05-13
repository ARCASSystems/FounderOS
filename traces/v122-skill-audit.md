---
trace: v122-skill-audit
version: 1.22.0
date: 2026-05-14
purpose: W2 skill disposition for all 44 skills. Method - read each SKILL.md body and frontmatter, check body length, description lead, script references, skeleton markers. Disposition each KEEP / IMPROVE / ARCHIVE.
---

# v1.22 Skill Audit

## Summary

- Total skills audited: 44
- KEEP: 42
- IMPROVE: 2
- ARCHIVE: 0

No skills are half-built or broken. All script references point to files that exist. No frontmatter or body contains skeleton/stub quality markers.

---

## Disposition Table

| # | Skill | Lines | Script refs valid | Description leads with natural language | Disposition | Change (if IMPROVE) |
|---|-------|-------|-------------------|-----------------------------------------|-------------|---------------------|
| 1 | approval-gates | 72 | N/A | No - describes triggers but has no "Say X" phrase | IMPROVE | Add "Say 'do I need approval for this'" to description |
| 2 | audit | 82 | N/A | Yes - "Say 'audit the OS'" | KEEP | |
| 3 | blind-spot-review | 99 | N/A | Yes - "Say 'find blind spots'" | KEEP | |
| 4 | bottleneck-diagnostic | 154 | N/A | Yes - "Say 'what's blocking me'" | KEEP | |
| 5 | brain-log | 173 | brain-snapshot.py - exists | Yes - "Trigger on 'capture this'" | KEEP | |
| 6 | brain-pass | 122 | query.py, brain-pass-log.py - both exist | Yes - "Say 'what did I decide about X'" | KEEP | |
| 7 | brain-snapshot | 110 | brain-snapshot.py - exists | Yes - "Say 'refresh the brain snapshot'" | KEEP | |
| 8 | brand-interview | 264 | N/A | Yes - "Say 'set up my brand profile'" | KEEP | |
| 9 | business-context-loader | 151 | N/A | Yes - "Say 'load context for <company>'" | KEEP | |
| 10 | client-update | 118 | brain-snapshot.py - exists | Yes - "Trigger on 'update the client'" | KEEP | |
| 11 | content-repurposer | 86 | brain-snapshot.py - exists | Yes - "Trigger on 'repurpose this'" | KEEP | |
| 12 | context-persistence | 73 | N/A | Yes - "Say 'what do we know about <topic>'" | KEEP | |
| 13 | data-security | 81 | N/A | Yes - "Say 'is this safe to paste'" | KEEP | |
| 14 | decision-framework | 141 | brain-snapshot.py - exists | Yes - "Trigger phrases: 'help me decide'" | KEEP | |
| 15 | email-drafter | 124 | brain-snapshot.py - exists | Yes - "Trigger on 'write an email'" | KEEP | |
| 16 | forcing-questions | 106 | N/A | Yes - "Say 'should I start this'" | KEEP | |
| 17 | founder-coaching | 361 | brain-snapshot.py - exists | Yes - "Trigger on 'check in on'" | KEEP | |
| 18 | founder-os-setup | 520 | N/A | Yes - "Say 'set up Founder OS'" | KEEP | |
| 19 | handoff-protocol | 93 | N/A | Yes - "Say 'hand this off to <person>'" | KEEP | |
| 20 | ingest | 165 | N/A | Yes - "Trigger on 'ingest this'" | KEEP | |
| 21 | knowledge-capture | 152 | brain-snapshot.py - exists | Yes - "Trigger on 'capture this'" | KEEP | |
| 22 | legal-compliance | 234 | N/A | Yes - "Trigger on: legal question, regulation" | KEEP | |
| 23 | linkedin-post | 210 | brain-snapshot.py, query.py - both exist | Yes - "Trigger on 'write a LinkedIn post'" | KEEP | |
| 24 | lint | 180 | N/A | Yes - "Say 'lint the wiki'" | KEEP | |
| 25 | meeting-prep | 146 | N/A | Yes - "Trigger on 'prep me for my call'" | KEEP | |
| 26 | menu | 52 | menu.py - exists | Yes - "Say 'show me what you can do'" | KEEP | |
| 27 | pre-send-check | 135 | N/A | Yes - "Trigger on 'check this before I send'" | KEEP | |
| 28 | priority-triage | 75 | N/A | Yes - "Trigger on 'I'm overwhelmed'" | KEEP | |
| 29 | proposal-writer | 188 | brain-snapshot.py - exists | Yes - "Trigger on 'write a proposal'" | KEEP | |
| 30 | query | 143 | query.py - exists | Yes - "Say 'what blocks <priority>'" | KEEP | |
| 31 | queue | 123 | N/A | Yes - "Say 'what's on my plate'" | KEEP | |
| 32 | readiness-check | 236 | N/A | Yes - "Trigger on 'check my OS readiness'" | KEEP | |
| 33 | session-handoff | 193 | N/A | Yes - "Trigger on 'summarize this for a new session'" | KEEP | |
| 34 | ship-deliverable | 85 | N/A | Yes - "Say 'ship this'" | KEEP | |
| 35 | sop-writer | 81 | N/A | Yes - "Trigger on 'write an SOP'" | KEEP | |
| 36 | strategic-analysis | 115 | N/A | Yes - "Trigger on 'analyze this market'" | KEEP | |
| 37 | today | 12 | N/A | Yes - "Say 'what's on for today?'" but description contains meta-language | IMPROVE | Remove "Thin skill wrapper" from description; restate as user value |
| 38 | unit-economics | 89 | N/A | Yes - "Trigger on 'run the numbers'" | KEEP | |
| 39 | verify | 190 | N/A | Yes - "Say 'verify the OS'" | KEEP | |
| 40 | voice-interview | 300 | N/A | Yes - "Say 'set up my voice profile'" | KEEP | |
| 41 | weekly-review | 139 | N/A | Yes - "Trigger on 'run my weekly review'" | KEEP | |
| 42 | wiki-build | 82 | wiki-build.py - exists | Yes - "Say 'rebuild the wiki graph'" | KEEP | |
| 43 | your-deliverable-template | 298 | N/A | Yes - "Say 'make a CV'" | KEEP | |
| 44 | your-voice | 213 | N/A | Yes - "Trigger on every writing task" | KEEP | |

---

## ARCHIVE list

None. All 44 skills are production-quality.

The `bottleneck-diagnostic` skill was flagged as a potential skeleton in the v1.22 plan ("no bottleneck-diagnostic-style skeletons"). The plan used it as an example of what NOT to allow - it was not itself a skeleton candidate. Current body (154 lines) has a complete self-assessment / external-assessment split, five scored dimensions, output format, and routing table. KEEP.

The `today` skill is intentionally thin (12 lines) by design - it is a wrapper that delegates to `/today`. The thinness is correct behavior, not incomplete work. The IMPROVE item is the description language, not the body.

---

## IMPROVE detail

### approval-gates

Current description: "Check whether an action needs approval before doing it. Triggers when the founder is about to send, publish, pay, sign, delete, or push something public. Reads `rules/approval-gates.md` and classifies the action as auto-runnable, ask-first, or refused. Other skills call this internally."

Issue: no "Say X" invocation phrase. A user who wants to proactively check before acting has no phrase to use.

Change: add "Say 'do I need approval for this' or 'should I ask first'" to description. Update "the founder" to "you" (role-agnostic).

### today

Current description: "Show the today brief. Say 'what's on for today?' (or run /today). Thin skill wrapper for the daily one-screen view."

Issue: "Thin skill wrapper" is implementation-detail language that a user browsing the skill catalogue does not benefit from knowing. It describes how the skill works, not what the user gets.

Change: remove "Thin skill wrapper" clause; rewrite closing to describe the output the user sees.

---

## Script existence check

Scripts referenced across skill bodies:
- `scripts/brain-snapshot.py` - EXISTS
- `scripts/query.py` - EXISTS
- `scripts/brain-pass-log.py` - EXISTS
- `scripts/wiki-build.py` - EXISTS
- `scripts/memory-diff.py` - EXISTS
- `scripts/menu.py` - EXISTS

All references valid. No broken script paths found.

---

## Skeleton / stub marker check

Searched all 44 SKILL.md files for:
- Frontmatter `status: draft`, `status: skeleton`, `status: stub`
- Body section headers `# TODO`, `## TODO`
- Body text `\[skeleton\]`, `\[stub\]`, `\[PLACEHOLDER\]`

Zero matches. No quality markers found in any live skill.
