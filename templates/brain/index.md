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

When `log.md` hits 300 lines:
1. Move all entries to `archive/log-[YYYY-MM].md`
2. Clear `log.md`
3. Add a one-line summary at the top of the new `log.md`: "Archived [month] log. Key threads: [list]"
4. Carry forward any #xref entries that are still open
