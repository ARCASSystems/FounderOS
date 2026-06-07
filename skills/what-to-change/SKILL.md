---
name: what-to-change
description: >
  The flagship "what should I change in my business now" routine. Trigger on "what should I change", "what to change in my business", "what's the most important thing to fix", "monthly review", "where should I focus this month", or "what needs to change now". Returns exactly three ranked changes, each gated on a dated citation you can open, in a plain-language urgent/important matrix. It reads only from a deterministic candidate gatherer that excludes parked, paused, and resolved items, so it never manufactures urgency from a stale or already-decided item. If fewer than three changes have real dated signal, it says so rather than padding. Closes by proposing one concrete skill improvement for you to approve, never auto-editing.
why: "An OS that sits unused is dead weight. This is the routine that earns its keep: it checks the real dated signal in your brain layer and tells you the three things worth changing now, with the receipts. The hard part is honesty - the documented failure is false urgency, so the candidate gate and parked filter are mechanical, not a promise."
enhance: "Run it monthly, or whenever you feel busy but unsure what matters. The more honestly your flags and log carry dates and parked markers, the sharper the three changes get."
allowed-tools: ["Bash", "Read"]
mcp_requirements: []
---

# What to change

Runs on: local-exec - runs the candidate gatherer script and reads its output; on a surface that cannot run a script, read the brain files directly and apply the same parked/dated rules by hand, and say you did.

The routine that tells the founder the three things worth changing in their business right now, each backed by a dated source they can open. It exists to beat the one failure that kills this kind of routine: false urgency from a parked or already-handled item.

## Pre-flight

- If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`
- If `scripts/what-to-change.py` does not exist, stop with: `Routine helper not found. Run /founder-os:update to install it.`

## Procedure

1. **Gather candidates (mechanical).** Run `python scripts/what-to-change.py gather`. This returns JSON: `as_of`, `within_days`, `parked_excluded`, `count`, and `signals`. Each signal carries `source`, `anchor`, `date`, `age_days`, `kind`, and `title`.
   - The gatherer has ALREADY excluded parked, paused, and resolved flags and anything named in `brain/decisions-parked.md`. Do NOT add candidates from your own reading of the brain files. The gatherer's signal list is the ONLY candidate pool. This is the guard against false urgency - respect it.

2. **Honesty gates on the count.**
   - `count == 0`: say plainly "No change has real dated signal in the last `within_days` days. Nothing to surface this period." Then stop. Do not invent work.
   - `count < 3`: present only what qualifies, and say so in literal words, for example "Only two changes have real signal this period; here they are." Do NOT pad to three.
   - `count >= 3`: pick the three highest-signal changes (most recent, decay-passed, or highest flag severity).

3. **Verify each citation resolves.** For each change you surface, build its citation `[source: <source>#<anchor>]` from the signal and confirm it with `python scripts/what-to-change.py resolve <source>#<anchor>`. If a citation does not resolve, drop that change - never surface an unresolvable source.

4. **Rank in an urgent/important matrix.** Place each of the three in plain language:
   - Urgent + important: do this week.
   - Important, not urgent: schedule it.
   - Urgent, not important: delegate or batch it.
   Say which quadrant each change sits in and why, in one sentence.

5. **Progressive disclosure.** Lead with the three headlines only (one line each, with the quadrant and the citation). Then offer: "Say 'more on 1' for the evidence and the first step." Drill in only when asked. Do not dump all the detail up front.

6. **Declare freshness.** State the input age in one line: `as_of` date, the `within_days` window, and how old the newest signal is (`age_days` of the most recent). If the newest signal is more than `within_days` old, say the picture may be stale and suggest logging recent work first.

7. **Recursive skill-update prompt (closing step).** After the three changes, look at the recent `signals` of kind `activity` for a task the founder did by hand more than once. If you see a repeated manual pattern, propose ONE concrete skill change for approval: "You did X by hand in [dated entries]. Want a skill that does it next time?" Wait for a yes. NEVER edit a skill without explicit approval. If no clear pattern repeats, skip this step rather than inventing one.

## Output shape

```
What to change now (as of YYYY-MM-DD, signal from the last N days)

1. <headline> - <quadrant> [source: brain/flags.md#<anchor>]
2. <headline> - <quadrant> [source: brain/log.md#<date>]
3. <headline> - <quadrant> [source: brain/flags.md#<anchor>]

Say "more on 1/2/3" for the evidence and the first step.

(One skill idea: you did <X> by hand on <dates>. Want a skill for it?)
```

If fewer than three qualify, the list is shorter and a line says so.

## The failure this routine guards against

The documented failure mode (carried from the private morning-brief work) is a parked or done item resurfacing as fresh urgency. The guards, in order:

- The candidate gate: only dated signal in the window, from the gatherer.
- The parked filter: the gatherer drops parked / paused / resolved items mechanically.
- Resolvable citations: every change opens to a real dated source.
- The under-three rule: say-so, never pad.

If you ever surface a change with no resolvable dated source, the routine has failed - drop it.

## Runtime honesty

This runs a local script. On a web-only surface that cannot run it, read `brain/flags.md` (OPEN / ESCALATED only, skip PARKED / PAUSED / RESOLVED), `brain/log.md` (recent dated entries), and `brain/decisions-parked.md` (the parked exclusion list) by hand, apply the same dated-within-N and parked rules, and tell the founder you gathered by hand because the script could not run here.

## Rules

- Exactly three changes, or fewer with a say-so line. Never more, never padded.
- Every change carries a resolvable `[source: file#anchor]`. No citation, no surface.
- Never surface a parked, paused, resolved, or done item as urgent.
- Never auto-edit a skill. The recursive prompt proposes; the founder approves.
- No em dashes or en dashes in anything you write. Hyphens only.
