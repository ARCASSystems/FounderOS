# Decisions - Parked

> Decisions that cannot be made yet because a trigger condition has not been met. These are NOT forgotten - they are waiting. Check this file during the Chief of Staff scan. If a trigger condition is now true, surface the decision.

Decay is trigger-driven, not date-driven. No `Decay after:` line by default. The SessionStart brief surfaces a parked decision the moment its trigger fires. See `rules/entry-conventions.md`.

---

## Format

```
### [Decision Name]
Date parked: [YYYY-MM-DD]
Decision: [what needs to be decided]
Trigger to revisit: [the specific condition that makes this decision ready]
Context: [why it was parked, what information was available]
Options on the table: [brief list if known]
```

---

## Example (delete once your first real parked decision lands)

### Whether to hire a part-time ops lead

Date parked: YYYY-MM-DD
Decision: Hire a part-time ops lead now, or defer until revenue passes a threshold
Trigger to revisit: Monthly recurring revenue crosses the figure named in `context/priorities.md` annual goals, OR three weeks in a row where ops work blocks delivery
Context: Strong candidate from the network surfaced in [YYYY-MM] but cash runway makes the hire premature
Options on the table: Hire now (15 hrs/wk, fixed retainer), hire on revenue trigger, or restructure delivery to stop creating ops debt

---

<!-- Real parked decisions go here. Newest at the top. -->

