---
name: own-your-history
description: >
  Turn on full version history for a Founder OS install that does not have it yet - the graduation step for ZIP installs. Trigger on "own my history", "turn on version history", "turn on full history", "install git", "set up version control", or when the save, history, or restore skills find git missing and route here. With one explicit yes, the OS installs git itself, turns the folder into a repository, records the first version, and wires the privacy guard. The founder never types a git command.
why: "The ZIP install path deliberately ships without git so nothing stands between the founder and owning the system. Full history is still worth having - so the OS performs the graduation itself, consent-gated, instead of sending the founder to a download page."
enhance: "Run this once the OS has proven useful - usually week one. Before it, session snapshots cover undo; after it, every save is a permanent point in time you can restore to."
allowed-tools: ["Bash", "Read", "Write"]
mcp_requirements: []
---

# Own your history

Runs on: local-exec - runs local commands; on a cloud surface I explain the steps, I do not run them.

Graduates a git-less install (usually the ZIP path) to full version history. The OS does the work; the founder gives one yes.

## Pre-flight

- If `core/identity.md` does not exist, stop with: `Founder OS not set up here. Run /founder-os:setup first.`
- If a `.git/` directory exists AND `git --version` succeeds, check whether the history actually covers the founder's data before declaring victory:
  - Run `git ls-files core/identity.md`. Empty output means the shipped developer `.gitignore` is still in place and history records only the engine, none of their data. Do not stop - skip to step 4a and complete the ownership flip.
  - Run `git remote -v`. If any remote's push destination (pushurl if set, otherwise url) points at `github.com/ARCASSystems`, the push path is unsafe. Do not stop - skip to step 4a.
  - Otherwise version history is fully on and fully theirs. Say so, remind them of the three verbs ("save my work", "what changed", "undo to before this morning"), and stop. Nothing to do.

## Procedure

### 1. Say what will happen, then wait for yes

Explain in plain language, sized to what is actually missing:

- If git is not installed: "I will install Git for you - it is the free, standard version-history tool, and you will never have to touch it directly. Then I will turn this folder into a repository, record today as version one, and switch on the privacy guard that blocks your private names from ever being committed. One yes and I do the rest."
- If git is already installed but the folder is not a repository: same message minus the install line.

Name the exact install command that will run so nothing is hidden:

- Windows: `winget install --id Git.Git -e --source winget`
- macOS: `xcode-select --install` (Apple's own developer tools include git), or `brew install git` if Homebrew is present
- Linux: `sudo apt-get install git` (or the distro equivalent - dnf, pacman)

Wait for a clear yes. Anything else: "No problem. Session snapshots keep covering your changes - say 'own my history' whenever you want the full timeline." Stop.

### 2. Install git (only if missing)

Run the platform command from step 1. Then verify: `git --version`.

If the verify fails because the new install is not on the current session's PATH (common on Windows), be straight about it: "Git installed, but this session cannot see it yet. Restart Claude Code and say 'own my history' again - it will pick up where we left off." Stop. Do not fake success.

### 3. Record who the history belongs to

Git records a name and email on every version. Both stay on this machine - nothing is published anywhere.

Use the founder's name from `core/identity.md`. Ask one question for the email: "What email should version history record? It stays local - your real one, or just `you@local` if you prefer." Then set both locally (never globally):

```
git config user.name "<name>"       # run inside the OS folder after init
git config user.email "<email>"
```

### 4. Initialize and record version one

1. `git init` in the OS root.
2. Set the local identity from step 3.
3. Own the data: run the remote-safety check from step 4a (a fresh `git init` has no remotes, so this is instant), then copy `templates/operator.gitignore` over `.gitignore`. If `templates/` is not in the OS folder (Plugin install), resolve the source from the plugin root at `~/.claude/plugins/founder-os/templates/operator.gitignore`. The shipped `.gitignore` is the developer one that ignores the founder's own files; the operator one tracks their data and ignores only secrets, the private-name patterns file, runtime state, and per-machine settings. Without this swap, "full version history" silently records only the engine. On a plugin-path install there may be no `.gitignore` at all yet - the copy still runs; with no gitignore, secrets and runtime state would enter history on the very first save.
4. Wire the privacy guard BEFORE the first commit: `git config core.hooksPath .githooks`. Confirm `scripts/private-name-patterns.txt` exists; if it has no active pattern, offer to add the founder's own name now (`\bTheirName\b`, written with a file-write tool, never a shell echo).
5. Record the first version with the same engine every later save uses: `python scripts/caveman_git.py save --message "Version history begins"`. Explicit staging, guard-checked, local only.

### 4a. Complete ownership on an install that already has git

The clone path arrives here: git and engine history exist, but the developer `.gitignore` keeps the founder's data out of it, and `origin` pushes at the public repo. One yes ("I will make your version history cover your own files too, and make it impossible to accidentally publish them"), then, in this order - push safety BEFORE the data becomes trackable:

1. Remote safety. For each remote whose push destination points at `github.com/ARCASSystems` (normally `origin` on a clone):
   - `git remote rename origin founderos-upstream`
   - `git remote set-url --push founderos-upstream DISABLED`
   Updates still flow in from `founderos-upstream`; nothing can flow out. Say it plainly: "Updates still arrive from the public repo; pushing anything back to it is now impossible."
2. Copy `templates/operator.gitignore` over `.gitignore`.
3. Confirm the privacy guard is wired (`git config core.hooksPath` returns `.githooks`; if not, run step 4.4).
4. Confirm git knows who the history belongs to: `git config user.name` and `git config user.email` inside the OS folder. If either is empty, run step 3 above (Record who the history belongs to) first - on a machine with no global git identity, the save below otherwise fails with git's "tell me who you are" error.
5. Record the flip: `python scripts/caveman_git.py save --message "Your data now has version history"`. This first save brings their data into history, guard-checked.

Then continue to step 5.

### 5. Confirm in plain language

Tell them what they now own: a full local timeline. "Save my work" records a version, "what changed" shows the history, "undo to before this morning" rolls back safely. Session snapshots keep running underneath as a second net. Nothing pushes anywhere unless they ever ask.

## Rules

- Consent first. The install command runs only after an explicit yes, and the founder sees the exact command before agreeing.
- Local only. `git init`, local config, local commits. Never push, never sign anything up. The only remote change ever made is defensive: renaming the public update source to `founderos-upstream` and disabling its push URL so nothing can flow out. Never add a new remote here (the backup skill owns that, separately consent-gated).
- Never bypass the privacy guard. It is wired before the first commit so no version predates it.
- Honest failure. If any step cannot complete (no winget, no sudo, PATH not refreshed), say exactly where it stopped and what still works. Session snapshots are unaffected either way.
- No em dashes or en dashes in anything you write. Hyphens only.
