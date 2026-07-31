# Entry Conventions: IDs + Bi-temporal + Decay

Standard metadata fields for entries inside `context/decisions.md`, `context/priorities.md`, `brain/flags.md`, `brain/patterns.md`, `brain/decisions-parked.md`, `brain/needs-input.md`, `brain/log.md`, and `brain/knowledge/`.

Three purposes:
1. **Stable IDs.** Every new entry gets a per-channel, per-day, zero-padded counter. Skills can cite `#log-2026-05-07-003` instead of restating content.
2. **Bi-temporal tracking.** Never overwrite a live entry. Append a new one and mark the old as superseded. Past state stays queryable.
3. **Decay.** Stale flags and patterns surface as "Review Due" in the SessionStart brief instead of accumulating silently. Parked decisions are trigger-driven by default (not date-driven), so the hook does not auto-surface them; you check their trigger conditions manually during the Chief of Staff scan or weekly review. If you want a parked decision on the auto-surface path, set an explicit `Decay after:` line on it.

This is a writing convention, not a schema validator. New entries follow it. Old entries adopt it the next time they are touched. No backfill pass.

---

## Citations-by-ID

Every new entry written to a brain channel gets a stable ID at write time. The ID is what other skills cite. Without it, summaries like `/dream` end up restating content instead of pointing to it.

### Format

`<channel>-<YYYY-MM-DD>-<NNN>`

- `<channel>` is one of: `log`, `pattern`, `flag`, `parked`, `need`, `know`.
- `<YYYY-MM-DD>` is the entry date.
- `<NNN>` is a 3-digit zero-padded counter for that channel on that date, starting at `001`.

Channel mapping:

| File | Channel |
|---|---|
| `brain/log.md` | `log` |
| `brain/patterns.md` | `pattern` |
| `brain/flags.md` | `flag` |
| `brain/decisions-parked.md` | `parked` |
| `brain/needs-input.md` | `need` |
| `brain/knowledge/<topic>.md` | `know` |

### Examples

- `log-2026-05-07-001`
- `pattern-2026-05-07-001`
- `know-2026-05-07-002`

### Where the ID lives

The ID is the first frontmatter line of every entry. For list-based files like `brain/log.md`, the ID can also appear at the end of the entry heading line in parentheses:

```
### 2026-05-07 #context Got off the call (log-2026-05-07-003)
```

Both forms work. The frontmatter form is canonical when an entry has frontmatter. The trailing-parenthetical form is the fallback for short list entries.

### Counter rules

- Per channel, per day. The counter resets to `001` each day, per channel.
- No global counter. Resolving the next ID requires only reading the day's existing entries in that file (no shared state).
- IDs are stamped at write time, never retroactively. Existing entries without IDs are not retrofitted.
- IDs are case-sensitive lowercase only.

### How a writer picks the next ID

1. Scan today's existing entries in the target file for the highest counter on that date for that channel.
2. Increment by 1.
3. Stamp the new entry with the resulting ID.
4. If no entries exist for today in that channel, start at `001`.

---

## The fields

Add as bullet sub-fields directly under the `### Entry Heading`, after existing fields like `Status`, `Date`, `Context`.

### Bi-temporal (use on decisions, priorities, parked-decisions)

- `Superseded by:` - link to the replacing entry. Format: `filename.md#heading-slug` or `[[wikilink]]`. Sets the old entry to read-only history.
- `Invalidated on:` - date (YYYY-MM-DD) the entry was marked superseded. Pairs with `Superseded by`.
- `Replaces:` - link back from the new entry to the one it superseded. Optional but useful for audit.

### Decay (default on flags and patterns; opt-in for parked decisions)

- `Decay after:` - absolute date (YYYY-MM-DD) OR relative duration (`14d`, `90d`). When the date passes (or the relative duration elapses from the entry's anchor date - flag heading date for flags, `First observed:` for patterns, `Date parked:` for parked decisions), the entry surfaces as Review Due. The `Decay anchor missing` block surfaces entries that use a relative duration but lack the matching anchor.
- `Decay reason:` - one line on why this decay window. Optional but recommended for non-default values.

Parked decisions are trigger-driven by default. The hook does not evaluate trigger conditions, so a parked decision without `Decay after:` will never auto-surface; you check it manually during the Chief of Staff scan or weekly review. Set `Decay after:` explicitly only when you also want a date-based reminder.

---

## Defaults by file

| File | Default decay | Bi-temporal applies? |
|---|---|---|
| `brain/flags.md` | 14 days from creation | No (flags resolve, not supersede) |
| `brain/patterns.md` | 90 days from first observation | No |
| `brain/decisions-parked.md` | No auto-decay (trigger-condition-driven) | Yes |
| `context/decisions.md` | No auto-decay | Yes |
| `context/priorities.md` | No auto-decay | Yes |

These defaults describe the **convention** for what window to write. They are NOT auto-applied. The SessionStart scanner only fires on entries that explicitly include the `Decay after:` field. An entry written without the field will never surface as Review Due, regardless of age. This is deliberate: it keeps the file noise-free and lets old entries adopt the convention only on next touch.

In practice: when you write a new flag/pattern/parked entry, write the `Decay after:` line at the same time. If you forget, the scanner stays silent and the entry never decays.

Override defaults by setting `Decay after:` explicitly on the entry. A blocker may want a 7d window; a long-tail pattern may want 180d.

---

## Worked examples

### Bi-temporal: a superseded decision

Old entry (in `context/decisions.md`):

```
### Pricing tier - DECIDED 2026-04-24
- Decision: Three tiers at AED 5K, 15K, 75K.
- Superseded by: decisions.md#pricing-tier-revised-2026-06-01
- Invalidated on: 2026-06-01
```

New entry (in `context/decisions.md`, above the old one):

```
### Pricing tier revised - DECIDED 2026-06-01
- Decision: Two tiers at AED 7K and 25K. 75K removed.
- Replaces: decisions.md#pricing-tier-decided-2026-04-24
- Notes: Anchor tier had zero conversions in Q2.
```

### Decay: a flag with explicit window

```
### 2026-05-04 - Onboarding video script overdue
- Status: OPEN. Severity Week 1.
- Decay after: 7d
- Decay reason: Script is a 30-min job; if not done in a week, escalate or kill.
```

### Decay: a pattern relying on the default

You write `First observed: 2026-05-04` and `Decay after: 90d` on the entry. The scanner computes the decay date from those fields. If you forget either, the scanner stays silent.

---

## How "Review Due" surfaces

The SessionStart hook scans these files for past-decay entries and prints a `Review Due:` block. Each entry then needs a keep / kill / refresh call.

States after Review Due triggers:

- **Keep** - extend `Decay after:` to a new date with a one-line reason.
- **Kill** - move entry to file's archive section or delete.
- **Refresh** - entry still relevant but needs new evidence; reset `Decay after:` to today + default.

The hook also surfaces a separate `Decay anchor missing` block when an entry has a relative decay (e.g. `14d`) but no anchor date to compute from. That tells you to add the missing `First observed:` or `Date parked:` line.

---

## Why-first doctrine files

Everything above governs per-entry rows. This last convention governs the other kind of markdown: the doctrine and capability files a session reads to know how to act - `rules/*.md`, `system/*.md`, and `skills/*/SKILL.md`.

**The rule:** a doctrine file states, at the top, the problem it exists to solve, before it explains what it does. A fresh session (or a fresh person) has to be able to tell load-bearing doctrine from a scratch note without being told. A file that never says why it exists gets ignored or misapplied.

**The form**, either one:

- **Frontmatter `why:`** - one line naming the problem the file solves. This is the canonical form.
- **A body why-marker** - for a file with no frontmatter, a `## Why this exists` heading or an opening line naming the problem, in roughly the first 45 lines.

`description:` alone does not satisfy this. Description says what a skill does and when to fire it. Why says what breaks without it. Those are different questions, and only the second one survives the file being rewritten.

**Scope and adoption.** Forward-only, like everything else here. `rules/` and `system/` are where a missing why actually costs you something, so they are the default scope. Skill files already carry a description, so a why there is an improvement rather than a gap. Nothing gets backfilled: files adopt the convention the next time you touch them.

`python scripts/selfdoc_check.py why` lists what is missing it, and `/founder-os:lint` surfaces the count as one advisory line. See `rules/os-as-harness.md` for why this is one of four properties that keep an OS maintainable rather than merely documented.

---

## The canonical form

Everything above describes what to write. This section is the exact shape a writer has to produce, because the fields are read by more than one thing and a field spelled slightly differently is simply never read.

**A field line is:** an optional list marker, then the field name exactly as written below, then one colon, then one space, then the value. Nothing else on the line.

```
- Decay after: 14d
- Invalidated on: 2026-06-01
- Superseded by: decisions.md#pricing-tier-revised-2026-06-01
```

**The field names, case-sensitive and complete:**

`Decay after:` `Decay reason:` `Superseded by:` `Invalidated on:` `Replaces:` `First observed:` `Date parked:`

**The values that have a fixed shape:**

| Field | Accepts |
|---|---|
| `Decay after:` | `YYYY-MM-DD`, or a relative duration written as digits then `d` (`14d`, `90d`) |
| `Invalidated on:` | `YYYY-MM-DD` |
| `First observed:` | `YYYY-MM-DD` |
| `Date parked:` | `YYYY-MM-DD` |
| `Decay reason:`, `Superseded by:`, `Replaces:` | free text, one line |

**An entry ID is:** `<channel>-<YYYY-MM-DD>-<NNN>`, lowercase, with the counter always three digits and zero-padded. `flag-2026-05-04-001`, never `flag-2026-05-04-1`. The channel must match the file it sits in, per the mapping above.

### What enforces this

`.githooks/pre-commit` checks the added lines of any staged brain-channel file against the form above, and refuses the commit when a field name is a near-miss (`Decay After:`), a dated value is unreadable (`Decay after: two weeks`), or an ID uses the wrong channel or a short counter. Escape hatch: `ALLOW_ENTRY=1`.

Three things it deliberately does not do. It reads only added lines, so old entries are never dragged into a form they predate. It ignores unfilled template slots like `[YYYY-MM-DD]`. And it says nothing about whether an entry is any good, because that is a judgment and this is a form check.

The reason it is worth a gate at all: a mistyped field fails silently. The entry looks right, the scanner never sees it, the item never surfaces for review, and nothing anywhere tells you. That is the one failure mode a form check is genuinely good at catching.

---

## What this is not

- **Not a frontmatter schema for the file.** The file-level frontmatter (if any) stays as-is. These are per-entry sub-fields.
- **Not a rewrite mandate.** Existing entries do not need backfilling. Adopt on next touch, and the commit gate reads added lines only so it can never demand otherwise.
- **Not a substitute for version history.** History keeps every past state. These fields make "show me what's still live" a one-line query without digging through the timeline.
- **Not a quality check.** The gate checks the shape of a field, never the worth of an entry. Whether a flag deserves 14 days or 90 is yours.

---

## Cross-reference

- `brain/index.md` - log modes + flag lifecycle
- `brain/relations.yaml` - entity-to-entity link graph (the wiki substrate)
- `rules/operating-rules.md` - SessionStart protocol and stale-context rule
- `rules/approval-gates.md` - what auto-runs vs requires explicit yes
