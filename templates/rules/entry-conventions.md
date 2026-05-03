# Entry Conventions: Bi-temporal + Decay

Standard metadata fields for entries inside `context/decisions.md`, `context/priorities.md`, `brain/flags.md`, `brain/patterns.md`, and `brain/decisions-parked.md`.

Two purposes:
1. **Bi-temporal tracking.** Never overwrite a live entry. Append a new one and mark the old as superseded. Past state stays queryable.
2. **Decay.** Stale flags, patterns, and parked decisions surface as "Review Due" in the SessionStart brief instead of accumulating silently.

This is a writing convention, not a schema validator. New entries follow it. Old entries adopt it the next time they are touched. No backfill pass.

---

## The fields

Add as bullet sub-fields directly under the `### Entry Heading`, after existing fields like `Status`, `Date`, `Context`.

### Bi-temporal (use on decisions, priorities, parked-decisions)

- `Superseded by:` - link to the replacing entry. Format: `filename.md#heading-slug` or `[[wikilink]]`. Sets the old entry to read-only history.
- `Invalidated on:` - date (YYYY-MM-DD) the entry was marked superseded. Pairs with `Superseded by`.
- `Replaces:` - link back from the new entry to the one it superseded. Optional but useful for audit.

### Decay (use on flags, patterns, parked-decisions)

- `Decay after:` - absolute date (YYYY-MM-DD) OR relative duration (`14d`, `90d`). When the date passes (or relative duration elapsed from `created`/`Date parked`), the entry surfaces as Review Due.
- `Decay reason:` - one line on why this decay window. Optional but recommended for non-default values.

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

## What this is not

- **Not a frontmatter schema for the file.** The file-level frontmatter (if any) stays as-is. These are per-entry sub-fields.
- **Not a rewrite mandate.** Existing entries do not need backfilling. Adopt on next touch.
- **Not a substitute for git.** Git keeps full history. These fields make "show me what's still live" a one-line query without `git log` archaeology.
- **Not validated by tooling at write time.** The decay scanner reads what's there; it does not enforce schema. Keep names exact (case-sensitive, single colon, space after).

---

## Cross-reference

- `brain/index.md` - log modes + flag lifecycle
- `brain/relations.yaml` - entity-to-entity link graph (the wiki substrate)
- `rules/operating-rules.md` - SessionStart protocol and stale-context rule
- `rules/approval-gates.md` - what auto-runs vs requires explicit yes
