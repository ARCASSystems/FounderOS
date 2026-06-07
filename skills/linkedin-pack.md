# LinkedIn Pack

A logical pack, not a folder. Claude Code discovers skills as top-level directories under `skills/`, so the pack is held together by convention and by the links in this manifest rather than by nesting:

- every member skill is named `linkedin-*`
- one front door: [linkedin-start](linkedin-start/SKILL.md) (say "help me with my LinkedIn")
- one shared reference the brand skills read: [linkedin-algorithm.md](linkedin-pack-references/linkedin-algorithm.md)
- this manifest, which links to every member so the pack reads as one connected unit

## What the pack is

You bring one file - the LinkedIn data export LinkedIn already lets you download - and the pack turns it into whatever outcome you are actually chasing. The data is the same; the outcome is what you choose. Everything runs locally, on a free LinkedIn account and Python's standard library, within LinkedIn's terms. No scraper, no paid tool, no automated actions, no account-ban risk. Message content is never read.

The local entrypoint is [run.py](linkedin-start/run.py). It accepts the ZIP or folder once,
unwraps nested exports privately, drafts the targeting lens from available Founder OS
positioning, runs the pack, writes the completed worklists and first three posts under
`~/FounderOS/outputs/linkedin/<date>/`, then deletes the temporary extracted data.

## The front door

[linkedin-start](linkedin-start/SKILL.md) is the entry. It reads what the OS already knows, asks for your export, gives one honest disclaimer, and routes you to the outcome you want. You do not need to know the skill list first - you name the outcome, it aims the data there.

## The outcomes and the skills behind them

| Outcome | Skill | Status |
| --- | --- | --- |
| Front door (pick your outcome) | [linkedin-start](linkedin-start/SKILL.md) | Ready |
| Leads (rank your network vs a sales ICP) | [linkedin-network-scan](linkedin-network-scan/SKILL.md) + [icp.example.yaml](linkedin-network-scan/icp.example.yaml) | Ready |
| A better job (rank vs a career ICP) | [linkedin-network-scan](linkedin-network-scan/SKILL.md) + [icp.career.example.yaml](linkedin-network-scan/icp.career.example.yaml) | Ready |
| A louder brand (content lane your network rewards) | [linkedin-power-audit](linkedin-power-audit/SKILL.md) then [linkedin-brand-direction](linkedin-brand-direction/SKILL.md) | Ready |
| A healthier network (role gaps vs your goal) | [linkedin-power-audit](linkedin-power-audit/SKILL.md) network-gap read | Ready |
| Revive dormant contacts | [linkedin-warm-revival](linkedin-warm-revival/SKILL.md) (needs `audit.json` from the audit) | Ready |
| Content execution (write the post) | [linkedin-post](linkedin-post/SKILL.md) (algorithm-aware) | Ready |

## The shared reference

[linkedin-algorithm.md](linkedin-pack-references/linkedin-algorithm.md) is the single source of algorithm truth for the pack: what the LinkedIn feed actually rewards, dated and flagged for re-verification. The brand and content skills read it and degrade gracefully if it is absent. Skills cite it; they do not restate it inline and drift.

## Honest about the data's limits

A LinkedIn export is a strong read of the network you already have, not a prospecting database. It is title-only and point-in-time, carries no location field, no headcount or firmographics, email mostly blank, and no engagement data on other people. Every deliverable in the pack states this. Where a paid tool genuinely wins (enrichment, finding strangers, sending at scale, live intent signals), the pack says so rather than overselling.

## Dependencies between members

- [linkedin-warm-revival](linkedin-warm-revival/SKILL.md) requires `audit.json`, produced by [linkedin-power-audit](linkedin-power-audit/SKILL.md). The front door enforces this: it runs the audit first.
- [linkedin-brand-direction](linkedin-brand-direction/SKILL.md) reads the audit's network composition plus the algorithm reference, writes the fixed-schema direction, and updates the local pack-state pointer. It never touches the scoring engine.
- [linkedin-network-scan](linkedin-network-scan/SKILL.md) owns the scoring engine (`scan.py`). Other members reuse its outputs; they do not re-rank.
