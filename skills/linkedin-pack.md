# LinkedIn Pack

A logical pack, not a folder. Claude Code discovers skills as top-level directories under `skills/`, so the pack is held together by convention rather than nesting:

- every member skill is named `linkedin-*`
- one front door: `linkedin-start` (say "help me with my LinkedIn")
- one shared reference the brand skills read: `skills/linkedin-pack-references/linkedin-algorithm.md`
- this manifest

## What the pack is

You bring one file - the LinkedIn data export LinkedIn already lets you download - and the pack turns it into whatever outcome you are actually chasing. The data is the same; the outcome is what you choose. Everything runs locally, on a free LinkedIn account and Python's standard library, within LinkedIn's terms. No scraper, no paid tool, no automated actions, no account-ban risk. Message content is never read.

## The front door

**`linkedin-start`** is the entry. It reads what the OS already knows, asks for your export, gives one honest disclaimer, and routes you to the outcome you want. You do not need to know the skill list first - you name the outcome, it aims the data there.

## The outcomes and the skills behind them

| Outcome | Skill path | Status |
| --- | --- | --- |
| Front door (pick your outcome) | `linkedin-start` | Ready |
| Leads (rank your network vs a sales ICP) | `linkedin-network-scan` + `icp.example.yaml` | Ready |
| A better job (rank vs a career ICP) | `linkedin-network-scan` + `icp.career.example.yaml` | Ready |
| A louder brand (content lane your network rewards) | `linkedin-power-audit` then `linkedin-brand-direction` | Building (this release) |
| A healthier network (role gaps vs your goal) | `linkedin-power-audit` network-gap read | Building (this release) |
| Revive dormant contacts | `linkedin-warm-revival` (needs `audit.json` from the audit) | Building (this release) |
| Content execution (write the post) | `linkedin-post` (algorithm-aware) | Ready |

## The shared reference

`skills/linkedin-pack-references/linkedin-algorithm.md` is the single source of algorithm truth for the pack: what the LinkedIn feed actually rewards, dated and flagged for re-verification. The brand and content skills read it and degrade gracefully if it is absent. Skills cite it; they do not restate it inline and drift.

## Honest about the data's limits

A LinkedIn export is a strong read of the network you already have, not a prospecting database. It is title-only and point-in-time, carries no location field, no headcount or firmographics, email mostly blank, and no engagement data on other people. Every deliverable in the pack states this. Where a paid tool genuinely wins (enrichment, finding strangers, sending at scale, live intent signals), the pack says so rather than overselling.

## Dependencies between members

- `linkedin-warm-revival` requires `audit.json`, produced by `linkedin-power-audit`. The front door enforces this: it runs the audit first.
- `linkedin-brand-direction` reads the audit's network composition plus the algorithm reference. It is a reasoning layer; it never touches the scoring engine.
- `linkedin-network-scan` owns the scoring engine (`scan.py`). Other members reuse its outputs; they do not re-rank.
