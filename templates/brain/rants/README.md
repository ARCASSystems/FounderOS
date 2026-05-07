---
processed: true
---

# Rants

Raw voice dumps. The volume is the thinking. Nothing is asked to be concise here.

> This README is not a rant. The frontmatter above (`processed: true`) tells the SessionStart brief and `/dream` to ignore it.

## File format

One file per day: `YYYY-MM-DD.md`. Newest entry at the top. Each entry has frontmatter:

```yaml
---
captured: <ISO 8601 timestamp, e.g. 2026-04-25T14:32:00+04:00>
processed: <true|false>
---
```

A `processed:` value of `false` means `/dream` has not yet distilled this entry into the brain layer. After distillation it flips to `true`.

Rants are never edited or deleted after capture. Raw text is the audit trail.

## How they get in

`/rant <whatever you want to say>` - drops the text into today's file with a timestamp.

## How they get processed

`/dream` - reads all `processed: false` rants, distils into:

- `brain/patterns.md` (recurring themes)
- `brain/flags.md` (stalls, frustrations)
- `brain/decisions-parked.md` (ideas to revisit)
- `brain/needs-input.md` (asks or blockers)
- `context/clients.md` (client signals)

Writes a 5-line digest to `brain/log.md` so the user sees what surfaced.

Marks each processed rant `processed: true`.

## Cadence

`/dream` runs whenever you choose. Run it after a stretch of rants. Run it weekly as part of the retro. Run it when the brain feels noisy.
