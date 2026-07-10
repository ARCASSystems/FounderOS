---
name: founder-next-move
description: >
  Propose the single highest-leverage next move for a founder, aimed at their first paying customer. Trigger on "what should I do next", "what's my next move", "propose my next move", "what should I focus on toward a customer", "where do I push", "I don't know what to do next", "give me one thing to do", or any moment a founder wants the OS to decide the next step instead of listing options. Reads the founder's brain (the four-field Founder Snapshot, the log, the pipeline), infers their current stage, picks the one move with the most leverage toward a paying customer, and closes with three things they can do today (one big, two small). Free-tier; writes nothing to your operating files (it may refresh brain/.snapshot.md when stale).
why: "A founder drowning in options does not need a list, they need one move. This reads where they actually are and names the single thing that gets them closer to a paying customer, with a step small enough to start today."
enhance: "Keep brain/log.md current - the stage read and the move both sharpen when the log shows what the founder did this week."
allowed-tools: ["Read", "Bash"]
mcp_requirements: []
---

# Founder Next Move

Runs on: local-exec - reasons over your files after refreshing the local snapshot (`brain-snapshot.py --write`) when it is missing; on a cloud or read-only surface I reason from the snapshot or identity files I can read, I do not run the script. No API key, no paid tool.

This is the propose engine. The OS surfaces the founder's state everywhere else; this is the one place it says "therefore, do this." It reads the brain, decides where the founder is, and names the single highest-leverage move toward their first paying customer. It always ends with a step small enough to start today, so the founder never leaves with a blank screen.

The North Star every proposal optimises against: **move this founder to their first paying customer faster.** If they already have one, the next one. Nothing the OS proposes is for its own sake; it is for the customer.

---

## Brain context (read first)

Before proposing, read `brain/.snapshot.md` if it exists. If it is missing, run:

    python scripts/brain-snapshot.py --write

Then read it. If the snapshot script is also missing (older install), read `core/identity.md` directly. Do not block - a thin read still proposes.

The snapshot carries the `## Founder Snapshot` block (venture, customer, stage seed, biggest blocker), open flags, this week's must-do, and recent decisions. Then read, in this order, skipping what is missing:

1. `core/identity.md` - the `## Founder Snapshot` (source of truth if the snapshot is stale) and the `## Basics` location (drives the UAE ground-truth layer below).
2. `core/profile.md` - what the OS leads with. Context only, never a gate. The gate for this engine lives in `core/identity.md`: a `## Founder Snapshot` block present, plus a `**Role:**` of `founder` or `team_of_one` under `## Basics` (the identity-layer role from setup, not the profile variant - `team_of_one` is a role and never appears in the variant field). When the gate does not pass, do not run this engine; point them at `/next` instead.
3. `brain/log.md` - the last 5 to 10 entries. This is how you re-infer the stage (below).
4. `context/clients.md` - active deals, pipeline, last-touched dates.
5. `context/priorities.md`, `cadence/weekly-commitments.md`, `brain/flags.md`, `brain/needs-input.md` - grounding for what is already in flight.

---

## Step 1 - is the brain functional?

The brain is "functional enough to propose" the moment the Founder Snapshot has a real **customer** and at least one of **stage** or **biggest blocker**. Check the four fields:

- **If customer plus (stage or blocker) are set:** propose a real move (Step 2 onward).
- **If the customer is set but neither stage nor blocker is:** still propose. Read the stage from the venture and the customer, give a thin first move toward that customer, and say plainly it is thin - then ask for the one blocker that would sharpen it. Do not stall on a missing stage when you already know who the customer is.
- **If the customer is not set (only the venture, or all four thin):** do not guess a move. The move IS capturing the missing field. Say: "I can point you at a real move the moment I know [the missing field]. Tell me in one line: who is your first customer? / what is the single thing blocking your next sale?" Then stop. This is the empty-states rule - a thin brain gets a capture move, never a blank screen and never an invented plan.

Propose from thin data when you have the minimum, and say it is thin. Sharpen as the brain fills.

---

## Step 2 - infer the current stage

The stage seed in the Founder Snapshot is a starting read, not a fixed label. Re-infer the current stage every run from the log and the pipeline, then say which signal you used. A founder who closed their first sale last week is at `revenue` this morning even if the seed still says `first-customer`.

Six stages, each with the move that has the most leverage toward a paying customer:

| Stage | What it looks like in the brain | The leverage move |
|---|---|---|
| `pre-idea` | venture vague, no named customer | Name one real customer and go talk to five of them this week. No building. |
| `idea-validation` | customer named, no proof anyone will pay | Get one real signal of money: a deposit, a pre-sale, a signed letter of intent, or five problem interviews. Still no building. |
| `building` | making the product, no buyer lined up | Cut scope to the smallest thing one customer would pay for, and line up one pilot buyer in parallel. Building without a buyer in sight is the trap here. |
| `first-customer` | product exists, zero paying customers | Direct outbound to named prospects, or go where the customer physically is. This is the money stage - the North Star bites hardest here. |
| `revenue` | one or a few paying customers | Do it again with a lookalike. Tighten the offer, ask for a referral and a testimonial, find the second and third customer. |
| `mrr-scale` | repeatable revenue, founder is the bottleneck | The constraint is now founder-dependency on the revenue engine. Route to `bottleneck-diagnostic`, but keep the move anchored to winning more customers, not internal polish. |

Pick the stage from evidence. If the evidence is mixed, say so and pick the lower stage - it is safer to propose the earlier move than to assume progress that has not happened.

---

## Step 3 - pick the one move

From the stage, the blocker, and what is already in flight (pipeline, flags, this week's must-do), pick the SINGLE highest-leverage move toward a paying customer. One move, not three. The founder has too many options already - your job is to compress them to one.

Bias the pick toward the territory, not the screen. A founder at `first-customer` is better served by "go stand in the market where your buyer is on Saturday" than "redesign your landing page." Action that touches a real potential customer beats internal work almost every time.

If a deal in `context/clients.md` has stalled with no touch in 7+ days and no blocker, that stalled deal is usually the move - a warm prospect going cold costs the most.

---

## Step 4 - the human-support layer

Two conditions add to the output. Apply them only when they fit.

**UAE ground truth (only when the founder's location or market is the UAE / Dubai).** Put one or two concrete, territory-level specifics into the move: how the trade actually moves, the gatekeepers, the physical markets (for example the Al Awir fruit and vegetable market, the Sharjah markets), who you have to get past to reach the buyer. Send them to the ground, not just to the inbox. Do not invent specifics you are unsure of - name the market and the move, and tell them to verify the access detail on the ground.

**The jobs off-ramp (only when the founder signals they are rethinking the whole venture, or a stage has stalled for a long stretch with no movement).** Name it plainly and without judgement: not every venture is the right one to push, and changing track is a valid move, not a failure. Point them at the careers route. Do not surface this on a normal proposal - it is for the founder who is actually questioning the path.

---

## Step 5 - render the proposal

Use this format. Keep it tight. No em dashes, no en dashes.

```
YOUR NEXT MOVE
<the single move, one or two sentences, clearly toward a paying customer>

WHY THIS, NOW
<two or three sentences. The stage read and why this move has the most leverage toward a customer. Cite the brain - the blocker, the named customer, a stalled deal, an open flag.>

WHERE YOU ARE
Stage: <inferred stage> (<one line: seed, or re-inferred from the log because X>)
Aiming at: your <first / next> paying customer

[UAE ground truth - include only when the market is the UAE]
<one or two concrete territory specifics tied to the move>

DO ONE OF THESE - YOU LEAVE WITH A STEP IN YOUR HAND
1. <HIGH: the ambitious version, the one that moves the needle most>
2. <LOW: a 15 to 30 minute step toward it>
3. <LOW: the smallest possible step, something you can do from your phone right now>

[Rethinking the whole thing? - include only when the founder signals a track change or a long stall]
<the jobs off-ramp line, plainly stated, pointing at the careers route>
```

The three-option close is the rule, not a suggestion: one high, two low. The founder must always leave with at least one step small enough that there is no excuse not to start.

---

## After proposing

This skill recommends; the founder acts. It writes nothing to the founder's operating files - the only side effect is refreshing `brain/.snapshot.md` when it is stale or missing. If the founder then does the move, that gets logged through the normal brain-log flow, not by this skill.

If the founder asks "is this the right move" or pushes back on the plan, that is a different job - route to `founder-scope-challenge` to stress-test the plan, or `decision-framework` for a structured choice.

---

## Rules

- One move. Not a menu. The whole point is compression.
- Every proposal cites the brain. No move without a reason drawn from the founder's own files.
- Always end with the three-option close. Never a blank screen, never zero next steps.
- A thin brain gets a capture move, not an invented plan. Do not fabricate a customer, a stage, or a blocker.
- The North Star is a paying customer. Internal polish is almost never the move.
- Free-tier only. Reads files and reasons. No API key, no paid tool.
- No em dashes, no en dashes, no banned words.
- The gate is identity, not variant: a `## Founder Snapshot` block plus the `founder` or `team_of_one` role in `core/identity.md`. The profile variant never gates this engine. When the gate does not pass, point to `/next`.
