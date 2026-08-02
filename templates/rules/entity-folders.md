# Entity folders - how an identity thickens over time

A person, a venture, or a recurring topic starts as one file. If the relationship is real, that file grows: notes from a call, a document they sent, what you decided, what changed. Past a point one file stops working. The current read of who they are gets buried in history, and the history gets flattened every time you rewrite the top.

The fix is not a bigger file. It is a folder with a fixed shape, so the identity and its evidence stop competing for the same page.

## Stage 1: one file

`context/entities/<slug>.md`. Front matter carries the identity fields; the body is yours to write however you think.

```yaml
---
entity: <slug>
type: person | venture | topic | org
status: active | dormant | archived
reviewed: YYYY-MM-DD        # the last time you confirmed this read is still true
---
```

Most entities stay here forever. That is the right outcome, not a failure to graduate. A folder for someone you speak to twice a year is overhead with no reader.

## Stage 2: the folder

When the file crosses a threshold, the OS PROPOSES a promotion. You approve it. Never automatic: a folder created without a real deep-dive is an empty stub, and an empty stub invites the model to fill it in.

Any one of three thresholds proposes:

1. **Size.** The file passes roughly 400 lines, or its history section is longer than its current read.
2. **Touch frequency.** Six or more dated entries, or touches in three of the last four weeks.
3. **You say so.** Always sufficient on its own.

After promotion the shape is fixed, so every entity folder reads the same way:

```
context/entities/<slug>/
  profile.md    the identity - who or what this is, where it stands now, how you work with it
  log.md        dated evidence, append-only, newest at the bottom
  sources/      their documents, kept as sent, never edited after filing
```

`profile.md` carries only the CURRENT read. `log.md` takes the history. That split is the whole point: a profile you have to re-read from scratch every time is a log, and a log you rewrite is not evidence of anything.

Append-only means append-only. A correction is a new dated block that points back at the earlier one. You never edit an old block, in `log.md` or in anything under `sources/`. Being able to see that you were wrong in May, and when you found out, is worth more than a tidy file.

## Review, so a profile never quietly fossilises

Every entity carries a `reviewed:` date. A read of someone written six months ago and never confirmed is not knowledge. It is an old assumption in a confident voice, and you will act on it without noticing.

The weekly review surfaces entities where `reviewed:` is 60 or more days old AND real dated touches have landed since. Entities that simply went quiet are NOT surfaced: dormancy is not debt. Each surfaced entity takes one of three outcomes:

- **Confirmed.** Still true. Stamp today's date on `reviewed:`.
- **Corrected.** The read changed. Edit `profile.md`, append the correction to `log.md` with today's date, re-stamp.
- **Archived.** It is over. Set `status: archived`. It stops being surfaced and stays readable.

An unconfirmed fact stays unconfirmed inside a profile until you confirm it. Moving into a nicer folder does not promote it.

## Ask about the gap, do not resolve it

Accumulation gives you a thick file about someone. It does not give you the thing that predicts what they will actually do: the distance between how they say something works and how it demonstrably runs.

When a capture shows that gap - you describe an intended way of working, and the log shows a different pattern - the OS asks about it instead of picking a side. Three lines, riding the questions the morning loop already asks you:

```
Designed intent: <what was said should happen>
Enacted practice: <what the log shows happening>
The gap: <ask - never resolve it yourself>
```

Your answer lands in `profile.md`. If the OS silently overwrites the profile with whichever version is newer, it destroys the most useful thing in the file: the reason a stated process and a real one diverge. Nobody writes that down unless something asks.

## What this is not

- **Not a CRM.** No pipeline stage, no score, no owner field. Stage lives where it already lives, in your pipeline files. Two places holding stage is a bug, not a feature.
- **Not for clients.** A client with an engagement, invoices, and deliverables outgrows this. Give them their own folder under `clients/` and leave a pointer here.
- **Not automatic.** Promotion proposes; you approve. Same gate as every other write in the OS.

## The check

    python scripts/entity_check.py            # human report
    python scripts/entity_check.py --json     # machine form

It reports promotion candidates and which threshold each crossed, overdue reviews, and shape drift (a folder missing `profile.md` or `log.md`, a file with no `reviewed:` date). Read-only. It never writes, never promotes, never edits a profile.
