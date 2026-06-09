---
name: pipeline-start
description: >
  The front door to the Pipeline pack: turn a name into a tracked, worked deal. Trigger on "turn this name into a deal", "track this prospect", "help me with my pipeline", "I met someone, help me pursue them", "work this lead", "new business with <name>", "follow up with <name>", or any open-ended business-development request where the user has a person or company but no clear next step. You name who you want to pursue; the OS captures them as a tracked record, reads what it already knows, and routes you to the next move: research, a first message, a meeting brief, or a proposal. One honest disclaimer, no full onboarding, and it never sends anything for you. Routes to prospect-init, business-context-loader, meeting-prep, email-drafter, proposal-writer, list-pruner, or reconnect-prompt depending on where the deal is.
why: "A founder running BD alone does not think in skills, they think 'I met someone, now what'. This is the one entry that turns a name into a tracked deal and points at the right next move, so nobody has to learn which of seven pipeline skills they need first."
enhance: "Have the person's name and company to hand, and a one-line memory of where you met or why they matter. With that the OS can open a real prospect record in the same session instead of a blank one."
summary: "Name who you want to pursue; the OS tracks them and routes you to the next move."
allowed-tools: ["Read", "Bash"]
mcp_requirements: []
---

# Pipeline Start

Runs on: reasoning - this skill reads what the OS already knows and routes you to the member skill that does the work. It does not run an engine of its own and it never sends a message for you. On a read-only or cloud surface, it explains the same route without claiming a file was written.

This is the front door to your pipeline. You have a name, a company, or a lead. Underneath that one person sit several moves: capture them so they are tracked, learn what you can, prep the call, write the first message, scope the work. This skill reads what the OS holds, then points the same name at the move you actually need next, without making you learn which skill does what.

The principle: do more for you than you asked, in priority order, and never invent a fact you do not have. If the OS does not know whether they have budget, who else decides, or whether they replied, it says so rather than guessing.

## The moves behind one name

| You want | What it means | Where it routes |
| --- | --- | --- |
| **Track them** | get this person out of your head and into a record you can work | `prospect-init` (writes `companies/prospects/<slug>.md`) |
| **Know them** | what you already hold on them or their company before you reach out | `business-context-loader` (for a company you run) or a quick research pass |
| **Reach them** | a first message or a follow-up in your voice | `email-drafter` |
| **Meet them** | a brief for the call: what to ask, what to watch for | `meeting-prep` |
| **Scope them** | a proposal or quote once the conversation is real | `proposal-writer` |
| **Clean a list** | a contact export to prune before any outreach | `list-pruner` |

Not sure where the deal is? Say "just get them tracked" and the OS runs `prospect-init` first (the cheapest, most useful move), then names what each later step would add so you choose with the record in front of you.

## The flow

### 1. Read the state first

Before asking anything, check what the OS already knows:

- Is there already a record at `companies/prospects/<slug>.md` for this person or company? Does `core/identity.md` say who you sell to? Is there a prior note in `brain/log.md`?
- **Cold install** (no `core/`, no prospects): go straight to capture. Do not push the user through full onboarding to track one name.
- **An OS that already knows them**: reuse it. If a prospect record exists, open it and route to the next missing step (no context yet, no meeting prepped, no proposal sent) instead of starting over.

Branch on the state you actually find. Do not assume cold.

### 2. Capture first, so the deal is tracked

The first move for an untracked name is almost always `prospect-init`. It captures three to five fields (who, company, where you met, why they matter, the next step) and writes `companies/prospects/<slug>.md`. That file is the deal: every later move reads from it and writes back to it, so the pipeline stays honest instead of living in your head.

If the person is a company you already run rather than a prospect, route to `business-context-loader` instead, which owns your own companies.

### 3. One honest disclaimer

Before routing, say one true thing and only one:

> I can track this deal and draft every step, but I do not send anything for you and I do not enrich a contact from the open web. Tracking means a local file you own; reaching out means a draft you review and send. Tell me where this deal is and I will aim the right move at it.

Never imply the OS has already contacted them or knows their intent. It tracks and drafts. You send.

### 4. Route to the move

- **Track them** -> `prospect-init`, then return here and offer the next step.
- **Know them** -> `business-context-loader` for a company you run, or a focused research pass for a prospect (web-fetch-extract if a public page is worth reading), folded back into the prospect record.
- **Reach them** -> `email-drafter`, which writes in your voice (set `core/voice-profile.yml` for it to sound like you, falls back to anti-AI defaults if not).
- **Meet them** -> `meeting-prep`, which builds the brief from the prospect record and your commitments.
- **Scope them** -> `proposal-writer`, which reads the prospect context plus past wins in `brain/knowledge/` and writes the proposal in your voice.
- **Clean a list** -> `list-pruner`, which dedupes, flags gaps, and scores a CSV or pasted table before you work it.

Follow the skill you route to for the actual run. This skill hands off; it does not re-implement the work.

### 5. Deliver the path, not a file dump

When the routed skill finishes, frame the result as the path from a cold name to a closed deal: here is who they are, here is the next move, here is the message or brief ready to use. Update the prospect record so the next session opens already knowing where the deal stands.

### 6. Offer more than they asked

After delivering, name the moves they did not pick, in one line each. "You came to track them. The same record can draft your first message, prep the call when it lands, and turn into a proposal when it is real. Want any of those?" Invite, never gate. If they say no, stop cleanly and leave the record tracked.

### 7. Keep the loop honest

Every outreach move (a message drafted and sent, a call prepped, a proposal sent) belongs in the prospect record and in `brain/log.md` in the same session. That is how the deal stays trackable instead of drifting. If the user tells you an outreach happened off-system, capture it before moving on.

## Honest positioning (say this, do not oversell)

Lead with the defensible truth: the OS tracks the deal in a plain file you own, drafts every step in your voice, and reads your own context so you are not starting cold. It is free and local; nothing is sent without you.

Be honest where a paid tool genuinely wins: enriching a contact from the open web, finding net-new strangers, sending sequences at scale, and live intent signals. The OS works the relationships you already have and the deals you already named, not a database of people you have never met.

## When NOT to use

- When the user already named a specific job ("write the follow-up email", "prep my call with <name>", "track <company>") - route straight to that skill; the front door is for the open-ended "I have a name, now what".
- To mass-message a list. The OS drafts and tracks; it does not run outreach campaigns.

## Files this skill routes to

- `skills/prospect-init/SKILL.md` - capture a prospect into `companies/prospects/<slug>.md`.
- `skills/business-context-loader/SKILL.md` - load and refresh context for a company you run.
- `skills/email-drafter/SKILL.md` - draft the first message or follow-up in your voice.
- `skills/meeting-prep/SKILL.md` - build the brief for the call.
- `skills/proposal-writer/SKILL.md` - write the proposal or quote.
- `skills/list-pruner/SKILL.md` - clean a contact list before outreach.
- `skills/reconnect-prompt/SKILL.md` - turn a tool auth failure into one reconnect prompt if an integration drops mid-flow.
- `skills/pipeline-pack.md` - the pack manifest, with the full member map.
