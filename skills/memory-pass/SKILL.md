---
name: memory-pass
description: >
  Use when memory entries may be stale - after a 7+ day session gap, after a close, block, or
  unblock event, or when a person or project mentioned in conversation contradicts an existing
  memory claim. Audits Active Project Context entries in MEMORY.md against brain/log.md,
  context/clients.md, context/decisions.md. Never touches Behavioral Guards. Say "run a memory
  pass", "check my memory", or "is my memory stale".
why: "Memory that silently goes stale is worse than no memory - a closed deal still listed as open, or a paused contact still surfaced as live, quietly skews every skill that reads it."
enhance: "Run it after any seven-day-plus gap or any close, block, or unblock event - those are the moments memory most often drifts from what is actually true."
summary: "Audit memory entries for stale claims after a gap or a status change."
allowed-tools: ["Read", "Grep", "Edit"]
mcp_requirements: []
---

# Memory Pass

Runs on: local-writes - creates or edits files in your OS folder; needs an agent with write access.

Cross-checks Active Project Context memory entries against current file state. Surfaces contradictions, proposes targeted edits, writes nothing without confirmation.

**Failure this addresses:** the agent loads MEMORY.md and treats every entry as current. A memory line says a relationship is "paused" while `brain/log.md` shows you re-opened it last week. A memory line says a deal is "exploratory" while the log shows it closed the same day. Neither contradiction surfaces until you mention it. This skill makes the contradiction visible before it costs you.

---

## Where memory lives

The auto-memory file is at `~/.claude/projects/<project-slug>/memory/MEMORY.md`, set up by `/founder-os:setup`. The `<project-slug>` is the path-encoded form of your repo location. If you do not know the exact path, ask the operator to confirm it before reading, or check the `templates/memory/MEMORY.md` structure to recognise the section headers.

MEMORY.md is organised into sections. This skill only ever touches **Active Project Context**.

---

## When to run

- Any session where the operator mentions someone whose status feels different from what memory says
- First session after a 7+ day gap
- After any close, block, unblock, or relationship reversal
- On demand when the operator asks for a memory pass.

**Never run on:** Behavioral Guards (permanent TTL - these are rules, not factual claims about current state).

---

## Protocol

### 1. Load Active Project Context

Read MEMORY.md. Collect every entry under `## Active Project Context`. Each entry has a linked file and a `load if:` condition.

### 2. Check each entry

For **person-centric entries** (a named prospect, client, or contact):
- Grep `brain/log.md` for the person's name - read the 3 most recent matching `### ` headers
- Read their row in `context/clients.md` (and `context/leads.md` if your install uses a separate leads file) for stage and last touch
- Check `brain/flags.md` for any open flag mentioning them

For **project-centric entries** (a build, a campaign, an initiative):
- Grep `brain/log.md` for the project slug - read the 3 most recent `### ` headers
- Read the linked memory file body - check its `decay_after` if set
- If a plan file is referenced, check whether it still exists at the stated path

Files that may not exist on every install: `context/leads.md`, `brain/flags.md`. If a referenced file is missing, skip that check and note the gap. Do not block.

### 3. Build a contradiction table

```
| Memory file | Claim | Evidence | Status |
|---|---|---|---|
| project_contact_paused.md | Relationship on hold | log.md: re-opened 7 days ago | STALE |
| project_deal_exploratory.md | Exploratory, call pending | log.md: CLOSED same day | STALE |
| project_self_serve.md | Light touch, resume on trigger | log.md: no mention in 14d | FRESH |
```

**Status values:**
- **STALE** - file evidence clearly contradicts the memory claim
- **FRESH** - evidence matches or is silent (absence of evidence is not contradiction)
- **CHECK** - ambiguous; show evidence and let the operator decide

Skip entries where the linked memory file is missing. Note the gap but do not block.

### 4. For each STALE or CHECK row

Write a one-line proposed edit in plain language. Show it.

Wait for the operator to say **YES / NO / SKIP** per row. Do not batch-apply.

On **YES**:
- Edit the linked memory file: update the body to reflect current state, add or update the `updated:` date in frontmatter
- If moving to Expired: change the MEMORY.md index line from `## Active Project Context` to `## Expired / Superseded`

On **NO** or **SKIP**: leave unchanged.

### 5. Log

<!-- private-tag: not applicable: writes a structured, computed audit summary (counts of checked/updated/expired entries), not user-provided speech, so the <private> exclusion filter does not apply. -->

Append one line to `brain/log.md`:

```
### YYYY-MM-DD (memory-pass: N checked, N updated, N expired) - #memory #maintenance
```

---

## What not to touch

- `## Behavioral Guards` section - permanent TTL, skip entirely
- `## Reference` entries - external system pointers, no current state to cross-check
- MEMORY.md header or structure - only move entries between sections, never rewrite the index headers
- Any entry where the operator says NO or SKIP

---

## Quick reference

| Entry type | Check source | Contradiction signal |
|---|---|---|
| Person | log.md + clients.md (and leads.md if present) | Status changed, relationship reversed, project closed |
| Project | log.md + plan file existence | Phase complete, scope changed, project killed |
| Architecture | CLAUDE.md + referenced files | File renamed or deleted, decision superseded |
| Decay date | Entry frontmatter | `decay_after` date has passed |

---

## Hard rules

- Never write to MEMORY.md or any linked memory file without an explicit per-row YES.
- Never touch Behavioral Guards.
- Do not claim integrations this install lacks. If `context/leads.md` or `brain/flags.md` is missing, skip the check and say so plainly.
- No em dashes or en dashes. Hyphens only. No banned words.
