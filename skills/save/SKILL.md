---
name: save
description: >
  Save the founder's work as a new version, wrapping git so they never type a git command. Trigger on "save my work", "save this", "save my progress", "commit my work", "checkpoint this", "save a version", or any plain request to record the current state. Stages every changed file by path (never `git add -A`) and commits with a plain-language message. If the privacy guard blocks the commit (a private name, a dash, an AI-attribution line, or a secret), the reason is surfaced and nothing is saved.
why: "Version control is the biggest literacy wall in onboarding. Wrapping it in one verb gives a non-technical founder full history and undo without learning git, and keeps the you-own-your-files promise real."
enhance: "Save often. Each save is a point you can undo back to later, so frequent saves make the restore verb far more useful."
allowed-tools: ["Bash", "Read"]
mcp_requirements: []
---

# Save

Runs on: local-exec - runs a local script; on a cloud surface I read the results, I do not run it.

Record the founder's current work as a new version. Wraps git so they never see a git command. Local only. This never pushes anywhere.

## Pre-flight

- If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`
- If `scripts/caveman_git.py` does not exist, stop with: `Version control helper not found. Run /founder-os:update to install it.`

## Procedure

1. Run `python scripts/caveman_git.py save`. To pass a short plain-language note the founder gave ("save my pricing rework"), use `python scripts/caveman_git.py save --message "<note>"`. Do not invent a note; the script writes an honest default if you pass none.
2. Read the script output and relay it in plain language:
   - On success it prints `Saved.` and the list of files that changed. Tell the founder what was saved in one line.
   - On a block it prints `Could not save.` and the guard reason. Explain in plain words what tripped the guard (a private name, an em or en dash, an AI-attribution line, or a secret in a file), and that nothing was saved. Do not bypass the guard. Do not retry with a flag that skips it.
3. Never run `git add -A`, `git add .`, or `git push`. The script stages by path and commits locally; that is the whole job.

## Runtime honesty

This verb runs a local script. On a surface that cannot run a script (a web-only agent), say so plainly: you can show the founder what would be saved, but you cannot perform the save there. They run it in Claude Code, or on any local-runtime agent pointed at the folder.

## Rules

- Local only. Never push.
- Explicit staging only. Never `git add -A` or `git add .`.
- Never bypass the privacy guard. A blocked save means real content needs fixing, not skipping.
- No em dashes or en dashes in anything you write. Hyphens only.
