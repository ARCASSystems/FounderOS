# Brain System

The brain is the running memory layer of the Founder OS. It captures what happens so patterns emerge and nothing important gets lost.

---

## Three Log Modes

Every entry in `log.md` uses one of three modes:

### (a) Log and Move On - tag: #context
Use when something happened and you just need a record. No follow-up needed.

> Format: `[DATE] #context [what happened]`

### (b) Log and Cross-Reference - tag: #xref:[target]
Use when this entry connects to another file, decision, or person. The target tells you where to look.

> Format: `[DATE] #xref:decisions [what happened and why it connects]`
> Common targets: decisions, priorities, flags, clients, [person-name]

### (c) Log and Act - tag: #acted
Use when something was captured AND an action was taken (file updated, decision made, task added).

> Format: `[DATE] #acted [what happened] -> [what was done]`

---

## Files in This System

| File | Purpose | Cap |
|------|---------|-----|
| `log.md` | Running log of what happened | 300 lines |
| `patterns.md` | Emerging patterns surfaced from the log | No cap |
| `flags.md` | Active flags: role performance + friction/stall | No cap |
| `decisions-parked.md` | Decisions that need a trigger before they can be made | No cap |
| `needs-input.md` | What is blocked on the user's input | No cap |
| `knowledge/` | Distilled notes from books, calls, articles, and experiments | One file per topic |
| `rants/` | Raw voice dumps captured by `/rant`, processed by `/dream` | One file per day |
| `archive/` | Monthly archives when log hits 300 lines | - |

---

## Knowledge Layer

`brain/knowledge/` holds durable notes that future skills can read back. `knowledge-capture` writes topic files and updates `brain/knowledge/README.md`. Proposal and strategy skills read frontmatter and top headings when relevant.

---

## Rant and Dream Loop

`/rant` captures a raw voice dump verbatim into `rants/<YYYY-MM-DD>.md`. No structure asked. The volume is the thinking.

`/dream` processes all unprocessed rants. Distils into the brain layer (patterns, flags, parked, needs-input, client signals). Writes a 5-line digest to `log.md`. Flips each rant's `processed:` flag.

Run `/dream` whenever the brain feels noisy. Weekly as part of the retro is a good cadence.

---

## Archive Protocol

`log.md` is capped at 300 lines so the file every skill reads stays small as the install ages. When it grows past the cap, age the oldest entries out instead of carrying months of history in the hot file. This is the running-log half of the Session Protocol context discipline: a small desk, the rest of the history in the filing cabinet.

The safe path is the deterministic script (say "archive my log", or run `python scripts/log-archive.py`):
1. The oldest entries move to `archive/log-[YYYY-MM].md`, grouped by month.
2. The most recent entries stay in `log.md`.
3. A one-line pointer is left at the foot of `log.md` saying where the history went. The pointer is the cache summary: it says history exists and where, without carrying the detail.

The script never splits an entry, never archives an entry it cannot date, and is idempotent (a re-run while under the cap does nothing). Preview with `python scripts/log-archive.py --dry-run` first.

On a surface that cannot run the script, do the same by hand: move the oldest entries to `archive/log-[YYYY-MM].md`, keep the recent ones, and leave the pointer line. Do not clear the whole log. Keep the most recent entries so the desk still has current context, and carry forward any open `#xref` threads.
