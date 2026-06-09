# Pipeline Pack

A logical pack, not a folder. Claude Code discovers skills as top-level directories under `skills/`, so the pack is held together by convention and by the links in this manifest rather than by nesting. The members do not share a name prefix the way the LinkedIn pack does; this manifest is what reads them as one connected unit.

This is the business-development function for a founder who runs BD alone. It covers the path from a name to a tracked, worked, closed deal.

## The front door

[pipeline-start](pipeline-start/SKILL.md) is the entry. Say "turn this name into a deal" or "help me with my pipeline". It reads what the OS already knows, captures the person as a tracked record, gives one honest disclaimer, and routes you to the next move. You do not need to know the member skills first; you name who you want to pursue and it aims the right step at them.

## What the pack is

You bring a name, a company, or a lead. The pack turns it into a deal you can actually work: tracked in a plain file you own, researched from what you already hold, reached with a drafted message, prepped for the call, and scoped with a proposal. Everything runs locally and free. The OS drafts and tracks; it never sends, never auto-enriches from the open web, and never runs outreach at scale. You stay the one who hits send.

## The outcomes and the skills behind them

| Outcome | Skill | Status |
| --- | --- | --- |
| Front door (name to next move) | [pipeline-start](pipeline-start/SKILL.md) | Ready |
| Track a prospect | [prospect-init](prospect-init/SKILL.md) | Ready |
| Load context for a company you run | [business-context-loader](business-context-loader/SKILL.md) | Ready |
| Draft the first message or follow-up | [email-drafter](email-drafter/SKILL.md) | Ready |
| Prep the call | [meeting-prep](meeting-prep/SKILL.md) | Ready |
| Write the proposal or quote | [proposal-writer](proposal-writer/SKILL.md) | Ready |
| Clean a contact list before outreach | [list-pruner](list-pruner/SKILL.md) | Ready |
| Recover from a tool auth failure | [reconnect-prompt](reconnect-prompt/SKILL.md) | Ready |

## The shared record

The pack has no shared reference file; it has a shared record. Each prospect lives at `companies/prospects/<slug>.md`, written by `prospect-init` and read and updated by every later move. That file is the deal. Keeping it current is what makes the pipeline trackable instead of living in your head, and it is what the revenue-loop discipline checks: an outreach move and a record update belong in the same session.

## Honest about the limits

The OS works the relationships you already have and the deals you already named. It does not find net-new strangers, enrich a stale contact from the open web, send sequences at scale, or read live intent signals. Where a paid prospecting tool genuinely wins (finding people you have never met, enrichment, sending at volume), the pack says so rather than overselling. Its strength is turning the names you do have into worked deals, in your voice, with nothing sent without you.

## Dependencies between members

- `proposal-writer` reads the prospect record plus past wins in `brain/knowledge/`; richer context produces a sharper proposal, but it degrades gracefully when those are thin.
- `email-drafter`, `client-update`, and other writers read `core/voice-profile.yml`; set your voice so outreach sounds like you, or accept anti-AI defaults.
- `business-context-loader` owns companies you run; `prospect-init` owns prospects you are pursuing. The front door picks the right one.
