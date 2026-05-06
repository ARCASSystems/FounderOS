# Flags

> Two types live here. Read at every session start. The SessionStart brief surfaces OPEN flags, Week 3+ severity, and any flag past its `Decay after:` date.

---

## Lifecycle

Every flag has a state:

- **OPEN** - raised, not addressed
- **ESCALATED** - action taken but not resolved
- **RESOLVED** - the underlying behaviour changed, with evidence

Flags that stay OPEN or ESCALATED for 2+ weeks get a severity bump.

## Severity ladder

- **Week 1:** Surface once. Note it.
- **Week 2:** Escalate. Name the pattern.
- **Week 3+:** Direct question before any other work. "This has been flagged for N weeks. What is actually blocking this? Is this a priority or should we kill it?"

## Decay convention

Default `Decay after: 14d` on every flag. After the decay date, the SessionStart brief surfaces the flag for keep / kill / escalate review. Full convention spec in `rules/entry-conventions.md`.

---

## Two flag types

### Type 1: Role performance flag

Things the OS (Claude) should be doing differently. Captured when the founder corrects behaviour or gives feedback on how the system is working.

```
[YYYY-MM-DD] [FLAG] [what the issue is] | [what should change]
Status: OPEN. Severity Week 1.
Decay after: 14d
Trigger to escalate: [specific condition]
```

### Type 2: Friction or stall flag

Things in the founder's work that are stuck, stalling, or creating drag. Captured when a priority hasn't moved in 2+ weeks, a commitment was made and not kept, or a decision is being avoided.

```
[YYYY-MM-DD] [STALL] [what's stalled] | [last known status] | [suggested prompt]
Status: OPEN. Severity Week 1.
Decay after: 14d
Trigger to escalate: [specific condition]
```

---

## Example (delete this section once your first real flag is logged)

## YYYY-MM-DD - Outreach has not started this week

Status: **OPEN.** Severity Week 1. Tag: #pipeline.

The week is closing without any outbound touches logged. Pipeline file shows no new rows.

Decay after: 14d.

Trigger to escalate: 7 more days with no rows added to context/clients.md.

---

<!-- Real flags go below. Newest at the top. -->
