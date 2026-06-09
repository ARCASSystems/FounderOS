# Delivery Pack

A logical pack, not a folder. Claude Code discovers skills as top-level directories under `skills/`, so the pack is held together by convention and by the links in this manifest rather than by nesting. The members do not share a name prefix; this manifest reads them as one connected unit.

This is the operations function for a founder who is also the delivery team. It covers the path from "I owe a client something" to work that is prepped, produced, and checked before it ships.

## The front door

[delivery-start](delivery-start/SKILL.md) is the entry. Say "get me ready to deliver this" or "I have client work due". It reads what the OS knows about the client and the work, gives one honest disclaimer, and routes you to the step you need. It also makes sure the ship gate is offered before anything leaves your machine.

## What the pack is

You owe a client a session, an update, a process, a document, or a finished piece. The pack readies each one and, critically, gives a solo founder the second pair of eyes they do not have: a real risk pass and a pre-send check before the work ships. Everything runs locally and free. The OS preps, writes, builds, and checks; it never sends to the client for you.

## The outcomes and the skills behind them

| Outcome | Skill | Status |
| --- | --- | --- |
| Front door (owed work to shipped work) | [delivery-start](delivery-start/SKILL.md) | Ready |
| Prep a client session | [meeting-prep](meeting-prep/SKILL.md) | Ready |
| Write a client status update | [client-update](client-update/SKILL.md) | Ready |
| Document a process to hand off | [sop-writer](sop-writer/SKILL.md) | Ready |
| Build a branded document | [your-deliverable-template](your-deliverable-template/SKILL.md) | Ready |
| The final ship gate | [ship-deliverable](ship-deliverable/SKILL.md) | Ready |
| Nine-category risk pass | [blind-spot-review](blind-spot-review/SKILL.md) | Ready |
| Seven-check pre-send gate | [pre-send-check](pre-send-check/SKILL.md) | Ready |

## The shared gate

The pack's center of gravity is the ship gate. [ship-deliverable](ship-deliverable/SKILL.md) composes [blind-spot-review](blind-spot-review/SKILL.md) (nine risk categories) and [pre-send-check](pre-send-check/SKILL.md) (seven final checks) and reports every failure in one pass. For a founder with no one to review their work, this is the most valuable habit in the pack: run it before anything reaches a client. The gate surfaces risk; it does not certify the work.

## Honest about the limits

The OS readies and checks; it does not deliver. It does not send to the client, schedule the work, or track the engagement on the client's side. Branded rendering needs a real brand profile, not placeholders. The ship gate raises what you missed; it does not make the work correct, that judgment stays yours. Its strength is being the careful reviewer a solo operator lacks.

## Dependencies between members

- `ship-deliverable` runs `blind-spot-review` first; the pre-send gate's first check fails if no blind-spot pass has run, so the gate enforces the order.
- `client-update`, `sop-writer`, and the writers read `core/voice-profile.yml`; set your voice so the work sounds like you.
- `your-deliverable-template` needs `core/brand-profile.yml` (or `brands/<slug>/visual.yml`) with real values to render in your identity.
