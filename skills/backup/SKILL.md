---
name: backup
description: >
  Back up the founder's OS to a destination they choose, on command only. Trigger on "back this up", "back up my OS", "set up a backup", "push this somewhere safe", "mirror this offsite", or any plain request to keep an offsite copy. Destination-agnostic: GitHub is the recommended default for long-term durability, but OneDrive, Notion, or staying purely local are all first-class. Never forces a GitHub account or a new tool. Local version control already works fully without this; backup is the next level, not a requirement.
why: "Owning your files means choosing where the safety net lives. Forcing one destination (a GitHub account, a new tool) would break the autonomy-over-lock-in promise. The founder picks; the OS does the wiring or hands them the steps."
enhance: "Once a backup destination is set, run a backup after any big work session. The GitHub path can re-push with one ask; the file-copy paths take one command."
allowed-tools: ["Bash", "Read"]
mcp_requirements: []
---

# Backup

Runs on: local-exec - runs a local script; on a cloud surface I read the results, I do not run it.

Keep an offsite copy of the founder's OS, to a destination they choose. On command only. Opt-in. Local version control (save, history, restore) already works fully without any of this; backup is the next level.

## Pre-flight

- If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`
- Version history must cover the founder's own files before any backup, on every destination. Check both: a `.git/` folder exists at the OS root, and `git ls-files core/identity.md` prints that path. If either fails (a ZIP install that never ran "own my history", or a git folder that still uses the shipped developer `.gitignore`, which leaves out every file of theirs), do NOT run `gh repo create`, do NOT `git init` here, and do NOT copy the folder yet. Say in one plain sentence why: `Before I back this up, your version history has to cover your own files - right now it does not, so a backup would hold only the Founder OS engine and none of your work.` Then run the `own-your-history` skill (read `skills/own-your-history/SKILL.md`), which asks its own yes, turns version history on for their files and switches on the push guard. When it finishes, come back here and start again at the top of this Pre-flight. If they decline, stop: nothing is backed up, and say so.
- Make clear up front: nothing here is required. Their files and full version history live on their machine already. This adds an offsite copy.

## Step 1: pick a destination

Offer these, with the honest trade-off, and let the founder choose. Do not force one.

- **GitHub (recommended for long-term durability).** A private repo they own. Best for keeping full version history offsite and restoring on a new machine. Needs a free GitHub account and the `gh` CLI.
- **OneDrive, Dropbox, or iCloud.** Simplest if they already use one. The folder syncs as files; version history rides along inside the `.git` folder.
- **Notion.** A reference mirror only, not a live restore target. Useful if Notion is their home base, but it does not preserve git history. Be honest about that limit.
- **Stay local.** A valid choice. Their work is already saved and undoable locally. Offer to revisit backup later.

## Step 2: wire the chosen destination

### GitHub
Do NOT re-implement gh auth or repo creation here. Use the `github-ops` skill (read `skills/github-ops/SKILL.md`).
1. Check `gh auth status`. If not authenticated, give the founder the exact step (`gh auth login`) and stop until done. Do not pretend it is connected.
2. Create a PRIVATE repo they own: `gh repo create <name> --private --source . --remote origin` (confirm the name with them first).
3. Prove it is private before anything is pushed: `gh repo view <owner>/<name> --json isPrivate --jq .isPrivate`. Only when that prints exactly `true`, record the confirmation, both lines: `git config founderos.privateRemote origin` and `git config founderos.privateRemoteUrl "$(git remote get-url --push origin)"`. The push guard (`.githooks/pre-push`) refuses every push of the founder's data to any remote not named there at that address, so without this line the push in step 4 is refused - by design.
   - If it prints anything else (`false`, an error, nothing), do NOT set it and do NOT push. Say plainly: "That repository is public, or I could not confirm it is private, so I have not pushed anything. Your data stays on this machine." Offer to make it private (`gh repo edit <owner>/<name> --visibility private --accept-visibility-change-consequences`, on their yes), then run the check again from the top of this step.
   - Never set `founderos.privateRemote` or `founderos.privateRemoteUrl` by any other route: not from the repo name, not from the founder saying it is private, not to quiet a refused push. The value means "GitHub said this is private", and it is worth only as much as that.
4. Push: `git push -u origin <current-branch>`. Only on the founder's explicit yes. Never force push. If the push guard refuses it, read its message to the founder and go back to step 3; never set the value just to get past it.
5. Confirm the push landed (`gh repo view --web` or report the repo URL). Do not claim it pushed until `git push` returned success.

### OneDrive / Dropbox / iCloud
If the OS folder is already inside the synced folder, it is already backing up; confirm the path and say so. If not, give the founder the move: copy the whole OS folder (including the hidden `.git` folder, which holds the version history) into their synced folder, then open it from there. Offer to do the copy if they give a destination path.

### Notion
Be explicit that this is a reference mirror, not a restore point. If they want it, hand them the manual export step (or use a Notion MCP only if one is connected and they ask). Do not claim history is preserved.

### Local copy
Copy the whole OS folder, including the `.git` folder, to the path they name. One command, plain confirmation of where it landed.

## Step 3: degrade honestly

If the chosen tool is missing or unauthenticated (no `gh`, not logged in, no synced folder, no version history over their files), do NOT fake success. Missing version history routes to `own-your-history` (see Pre-flight); never improvise a `git init` here, because the shipped developer `.gitignore` would then leave out every file of theirs and the backup would look done while holding none of their work. Print the exact steps the founder needs and stop. Say plainly what is and is not done.

## Runtime honesty

This verb runs local commands (git, gh, file copy). On a surface that cannot run them, say so and hand the founder the steps for their chosen destination; do not claim a backup ran.

## Rules

- On command only. Never back up on your own.
- Never force a GitHub account or any single destination.
- The GitHub path reuses `github-ops`. Do not duplicate gh logic here.
- Never force push. Never push without an explicit yes.
- Set `founderos.privateRemote` and `founderos.privateRemoteUrl` only after `gh repo view --json isPrivate` returned `true` for that exact repository. Never to get past the push guard.
- Never claim a backup happened until the command returned success.
- No em dashes or en dashes. Hyphens only.
