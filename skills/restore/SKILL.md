---
name: restore
description: >
  Undo the founder's OS back to an earlier saved version, non-destructively, wrapping git so they never type a git command. Trigger on "undo", "undo to before this morning", "restore to yesterday", "roll back", "go back to last week", "revert my changes", or any plain request to return to an earlier state. Saves the current work as a safety version FIRST, aborts if that safety save is blocked, then records the undo as a NEW version so the undo itself is reversible. Never rewrites history, never `git reset --hard`, never loses uncommitted work.
why: "Undo is the feature that makes a non-technical founder trust the OS with their work. It only earns that trust if it can never lose anything, so the whole design is fail-safe: safety-save first, abort on any doubt, and keep every prior state recoverable."
enhance: "Run save often so there are clean points to undo back to. If the founder is vague about when, show history first and offer two or three concrete days to pick from."
allowed-tools: ["Bash", "Read"]
mcp_requirements: []
---

# Restore

Runs on: local-exec - runs a local script; on a cloud surface I read the results, I do not run it.

Undo the founder's OS to an earlier saved version, without ever losing work. Wraps git. Local only. Two phases with a confirmation in between, so nothing destructive happens without the founder seeing it first.

## The safety promise (read before running)

This verb is fail-safe by construction:
- It saves the current work as a safety version BEFORE touching anything.
- If that safety save is blocked by the privacy guard, the whole undo is ABORTED and nothing is moved.
- The undo is recorded as a NEW version on top of history, so the state you undid FROM stays recoverable. History is never rewritten.

Never work around these. Never run `git reset --hard`, `git checkout` that discards files, or a force operation to "make undo work." If the script aborts, relay why and stop.

## Pre-flight

- If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`
- If `scripts/caveman_git.py` does not exist, stop with: `Version control helper not found. Run /founder-os:update to install it.`

## Procedure

1. **Find the target.** If the founder named a clear point ("yesterday", "last Friday"), use it. If they are vague, run the history verb (`python scripts/caveman_git.py history`), show two or three concrete days, and ask which one. Do not guess a target the founder did not confirm.

2. **Phase 1, safety save (this also previews the undo).** Run:

       python scripts/caveman_git.py restore --to "<target>" --safe-commit

   - The script prints `Resolved target: <sha>`. Keep that exact SHA. You MUST pass it to phase 2, because the safety save moves the current version and a relative reference like "yesterday" would then point somewhere else.
   - If the output starts with `UNDO ABORTED`, the safety save was blocked by the guard. Relay the reason in plain words, tell the founder nothing was changed and nothing was lost, and STOP. Do not run phase 2. Do not bypass the guard.
   - Otherwise the script lists the files an undo would change. Show that list to the founder.

3. **Confirm.** Ask the founder to confirm they want to undo to that version, given the files that will change. If they say no, stop. The safety save already made is harmless and stays as a normal version.

4. **Phase 2, apply the undo.** Only after a yes, run with the resolved SHA from phase 1:

       python scripts/caveman_git.py restore --to "<resolved-sha>" --apply

   Relay the result plainly: the files are back to the earlier version, recorded as a new version, and the prior state is still recoverable (say "what changed" to see it).

5. If at any point the script reports a hook blocked a commit, relay it and stop. Never bypass.

## Runtime honesty

This verb runs a local script and changes local files. On a surface that cannot run a script or write files (a web-only agent), say so plainly: you can explain what an undo would do and help the founder pick a target, but you cannot perform the undo there. They run it in Claude Code or another local-runtime agent pointed at the folder.

## Rules

- Always phase 1 before phase 2. Never skip the safety save.
- Abort the whole undo if the safety save is blocked. Never move the tree after a blocked safety save.
- Pass the resolved absolute SHA to phase 2, never a relative reference.
- Never `git reset --hard`, never a discarding checkout, never force, never push, never rewrite history.
- No em dashes or en dashes. Hyphens only.
