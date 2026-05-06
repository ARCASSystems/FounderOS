# Approval Gate Matrix

What runs silently, what requires your explicit yes, and what is blocked outright. Customize this file to match how you want your OS to behave.

When an action is not on this list, default to **Confirm** unless it is obviously read-only.

---

## Auto (silent - just do it)

No prompt, no narration. Reversible by edit or git revert. Frequency: many per session.

| Action | Why auto |
|---|---|
| Read any file in the repo | Always allowed |
| Append to `brain/log.md` (any tag) | Log is append-only by design |
| Append to `brain/patterns.md`, `brain/flags.md`, `brain/decisions-parked.md`, `brain/needs-input.md` | These files are the brain layer's append targets |
| Update `context/clients.md` rows for known clients | Capture-meeting flows already enforce this |
| Run `/founder-os:wiki-build` and update `brain/relations.yaml` between sentinel markers | Auto-extracted; idempotent; hand-curated `relations:` section is preserved |
| Move entries from `brain/log.md` into `brain/archive/<YYYY-MM>.md` per archive protocol | Documented in `brain/index.md` |
| Append to `system/quarantine.md` with `Status: ACTIVE` | Quarantine convention |
| Output from any SessionStart hook | Read-only surfacing |
| Cache writes (`.claude/`, `node_modules/`, `__pycache__/`, etc.) | Tooling state |

---

## Confirm before (one-line statement of intent + wait for yes)

State what you are about to do and why, then wait. The cost of pausing is low; the cost of an unwanted action is high.

| Action | Why confirm | Override condition |
|---|---|---|
| Edit `core/identity.md` | Rare, high stakes; identity changes ripple across all skills | Explicit "update identity to..." instruction |
| Supersede a live entry in `context/decisions.md` or `context/priorities.md` (vs append-new) | Bi-temporal rule: never overwrite live decisions; new entry + mark old as `Superseded by:` | Explicit "supersede X with Y" instruction |
| Send email (drafts are fine; sending is not) | Outbound communication has audience; drafts are reversible, sends are not | Explicit "send the draft" instruction |
| Create / update / delete calendar events | Calendar is shared with people who plan around it | Standing instruction |
| Push to a remote git repo | Any push affects shared state | Explicit "push" instruction |
| Retire or remove an existing skill | Other skills and commands may reference it | Explicit "remove skill X" instruction |
| Rewrite a script in `scripts/` or `.claude/hooks/` (vs minor edits) | Hooks affect every session; scripts can corrupt data | Explicit "rewrite the X script" instruction |
| Run a migration script (anything that touches 3+ files structurally) | Hard to reverse if the migration logic is wrong | Always confirm; never standing |
| Create a new top-level directory at repo root | Folder structure is part of the OS contract | Explicit "create folder X" instruction |
| Enable a remote scheduled agent | Routines run autonomously and can push to main | Always confirm; routines are created disabled by default |
| CRM writes (create / update contacts, accounts, opportunities) | Outbound CRM state has downstream consequences | Explicit "create the contact" instruction |
| Production database writes | Production data | Always confirm; never standing |

---

## Blocked outright (only with explicit, current instruction - never standing)

Even with a previous "yes," these require a fresh explicit instruction every time.

| Action | Why blocked |
|---|---|
| `git push --force` to any branch | Overwrites remote history; can clobber upstream work |
| `git reset --hard` against uncommitted changes or published commits | Destroys work; not reversible |
| Skipping hooks (`--no-verify`, `--no-gpg-sign`) on commits | Hooks exist for a reason; skipping bypasses safety |
| Adding AI attribution to commits (`Co-authored-by: Claude`, `Generated with` footers) | Operator owns the work product; AI authorship dilutes that |
| Sending mass outreach (10+ recipients in a single batch) | High blast radius; every batch needs explicit review |
| Posting to public social platforms from any agent | Posts go through human hands first |
| Deleting files in `core/`, `network/`, `companies/` | Source-of-truth folders; deletion needs explicit reason |
| Touching `.git/config` or git user config | Author identity must stay correct |

---

## How this matrix interacts with other rules

- The **stale-context rule** (operating-rules.md) is upstream of this matrix. Before any time-anchored action, refresh the cadence files first. The matrix governs WHAT to confirm; the stale-context rule governs WHEN to refresh inputs.
- **Hook failures** that should write to `system/quarantine.md` (per Quarantine convention) bypass this matrix - silent failure logging is auto by design.

---

## When this matrix is wrong

This file is the codified version of how you want your OS to behave. It will drift. When it drifts:

- An action confirmed twice in a row that you would rather happen silently -> demote to Auto.
- An action that ran silently and broke something -> promote to Confirm.
- A standing instruction that you regret giving -> revoke it; the action returns to its default gate here.

Updates to this file go through the same Confirm gate as other rules edits. State the proposed change, wait for yes.
