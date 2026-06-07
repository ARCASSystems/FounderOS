---
name: profile-router
description: >
  Decide who is operating the OS and what it should lead with for them. Fires during setup (the wizard calls it to infer a variant and write core/profile.md) and any time the operator says "update my profile", "what should the OS lead with for me", "set my profile", or "re-detect my profile". Maps five operator variants - founder, career-mover, builder, student, team-internal - to the surfaces the OS opens with and the frame it speaks in. Reads core/profile.md and core/identity.md. Never forks the OS: every skill stays available to every variant. The variant only changes what leads.
why: "The same OS serves a founder, a career-mover, a builder, a student, and an internal team member differently - the variant changes what the system opens with, without ever removing a skill from anyone."
enhance: "Keep core/identity.md current so re-detection has real signal - the router infers the variant from who you actually are, not from a one-time setup answer."
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep"]
mcp_requirements: []
---

# Profile Router

Runs on: local-writes - creates or edits files in your OS folder; needs an agent with write access.

The OS works for more than one kind of person. A founder, a job-seeker, a solo builder, and a student all get the same scaffold - facts about themselves, a record of decisions, a place for what is stalling, a worked example to copy. Only the task differs. This skill decides which task leads, so the first thing a new operator sees is the thing their situation needs, not a generic menu.

This is the "meet the human" layer. On first contact the OS reads who is using it and adapts to them - least adaptation on their side, their ease, their language. A stranger should feel it work with them the way it works with the person who built it.

## What it does not do

- It does not lock anything. Every skill is available to every variant. The variant changes the opening surfaces and the framing, nothing else.
- It does not fork the OS into separate products. One scaffold, five lead-routings.
- It does not assess personality or score the operator. It reads the words, the goal, and the technical comfort already captured in setup, and picks the closest variant.

## Detection signals

Read `core/identity.md` and the wizard's discovery answers. Pick the variant whose signals fit best. When two fit, ask one short question rather than guess.

| Variant | Signals in their words and goal |
|---|---|
| **founder** | Runs a business, has clients or a pipeline, talks about delivery and revenue, role is founder or operator, overwhelm is open loops or context switching. |
| **career-mover** | Between roles or planning a move, mentions a CV, interviews, applications, a portable record of their value, proving impact to a future employer. |
| **builder** | Ships projects solo, talks about building and shipping, a side project, a product, has trouble finishing or focusing rather than finding work. |
| **student** | Learning, studying, a course, research, capture and recall. No business, no job search. Wants to remember and think, not sell or ship. |
| **team-internal** | A team or company wants to run this internally, mentions rolling it out to staff, multiple employees seeing the files. |

Default when signals are thin: **founder** if they named a business, **builder** if they named a project, **student** if they only described learning. Set `confidence: low` and say so in `signals`.

## The variant map

Each variant resolves to lead surfaces, a frame, and a technical-comfort default. Write these into `core/profile.md`.

### founder
- **lead surfaces:** `context/priorities.md`, `cadence/weekly-commitments.md`, `context/decisions.md`, `context/clients.md`, `cadence/queue.md`
- **frame:** Stop being the bottleneck. The brain holds what you cannot.
- **technical comfort:** medium

### career-mover
- **lead surfaces:** `core/identity.md` positioning, a proof-of-value record in `brain/knowledge/`, an application tracker, `decision-framework`, `meeting-prep` for interviews
- **frame:** Carry your leverage between jobs. The brain is yours, not the employer's.
- **technical comfort:** medium

### builder
- **lead surfaces:** `cadence/queue.md` (three-item cap), `forcing-questions`, `today`, `ship-deliverable`
- **frame:** One thing at a time. The brain parks the rest so you finish.
- **technical comfort:** high

### student
- **lead surfaces:** `ingest`, `knowledge-capture`, `brain-pass`, the daily `brain/log.md`
- **frame:** Your second brain remembers so you can think.
- **technical comfort:** low

### team-internal (held)
- **routing:** Set them up as the closest individual variant - **founder** if they run the company, **operator-flavoured founder** otherwise. Log the team interest to `core/setup-backlog.md`: "Team or company rollout requested. Founder OS installs per person today; shared-team state is a later tier."
- **frame:** Founder OS installs per person today. I will set you up as an individual operator and note the team interest.
- **technical comfort:** medium

## How to run

1. Read `core/profile.md`. If `variant` is already set and the operator did not ask to re-detect, return the current routing and stop.
2. Read `core/identity.md` and any discovery answers in context. Match against the signal table.
3. State the pick in one line and the lead it implies, then ask for a yes or an adjustment. One line, not a form. Example: "You sound like someone moving between roles, so I will lead with your positioning and a record of your wins. That right?"
4. On a yes or an adjustment, write the variant, `detected on` (today), `confidence`, `signals`, `lead surfaces`, `frame`, and `technical comfort` into `core/profile.md`.
5. Tell the operator they can change it any time, and that nothing is locked - the variant only changes what the OS opens with.

## Language guards (all output)

- Lead with brain portability: the brain is the durable asset and it travels; the agent reading and writing it is a swappable mouth and hands.
- Explain capability through human analogues, not jargon, when the operator's technical comfort is low or medium.
- Never use the words "governance" or "diagnostics" in operator-facing copy. Say judgment, how decisions get made, what is stalling, what to look at first.
- Meet the human where they are. A student gets plain language and capture. A builder gets focus and finishing. The OS adapts to them, not the other way round.
