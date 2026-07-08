# Install paths

Five ways to install FounderOS. The ZIP download (Path 0) needs nothing installed and comes first; pick whichever matches how you work. None of them lock you in - if you outgrow one path, you can move to another without losing your data.

**Not comfortable in a terminal?** Use Path 0 (ZIP download) or Path A (Claude Code plugin). Both run without a single terminal command.

If you get stuck, email `solutions@arcassystems.com` with the path you tried and the error you hit.

---

## Path 0 - Download ZIP (nothing to install, no git, no terminal)

Three steps, nothing typed. The gentlest path there is.

**Best for:** Anyone who wants to own the system in ten minutes with nothing new installed. Anyone who does not have git and does not want to think about it.

**Requirements:** Claude Code with a paid Claude plan, and Python 3.11+ (most machines have it; the setup wizard checks and tells you plainly if not).

**Steps:**

1. [Download the ZIP](https://github.com/ARCASSystems/FounderOS/archive/refs/heads/main.zip).
2. Right-click the file and choose **Extract All** (Windows) or double-click it (Mac). Move the extracted folder wherever you keep your work and rename it if you like (`founder-os` is a good name).
3. Open the folder in Claude Code and say **"set up Founder OS"** (or run `/setup`).

Commands use bare names on this path (`/setup`, `/today`), same as the git-clone path.

**Updates:** say "update Founder OS" (or run `/update`). The OS re-downloads the ZIP itself, refreshes only its own engine files (skills, commands, scripts, docs), and never touches your data. You approve before anything is applied.

**Version history on this path:** off at first, by design - there is no git on the machine yet. You are still covered: the OS snapshots every file it touches, every session, and `/changes` shows exactly what changed with a one-command restore per file. When you want full history ("undo to before this morning", a complete timeline), say **"own my history"** - with your yes, the OS installs git itself, turns the folder into a repository, and wires the privacy guard. You never type a git command.

**Pros**
- Nothing to install first. No git, no curl, no terminal.
- The folder is yours from the first second - plain markdown, no hidden state.
- Updates and version history are both one sentence away, handled for you.

**Cons**
- Version history starts off until you graduate it on (session snapshots cover you meanwhile).
- Slash commands use bare names (`/setup`), not the `/founder-os:` namespace.

**Verify the install:** Say "verify the OS" (or run `/verify`).

---

## Path A - Claude Code plugin (no terminal, cleanest)

Two commands, typed inside Claude Code. No terminal needed. Auto-updates available. Cleanest first-run experience.

**Best for:** Anyone not comfortable in a terminal, and anyone with a Claude Pro or Max plan who already uses Claude Code.

**Steps:**

```
/plugin marketplace add ARCASSystems/FounderOS
/plugin install founder-os@founder-os-marketplace
```

If `/founder-os:setup` is not recognised after install, run `/reload-plugins` (or restart Claude Code) so the plugin namespace activates, then try again.

**Pros**
- Two commands and you are set up, with no terminal install step.
- Plugin updates flow through `/plugin update`.
- Slash commands and hooks register automatically, across every project.

**Cons**
- Requires Claude Code with a paid Claude plan.
- Plugin marketplace behaviour can vary by Claude Code version. If the install does not work, fall back to Path B or Path E.

**Verifying it worked:** Open `/plugin` and check the Installed tab. You should see `founder-os` listed. Then `/founder-os:setup` should appear in the slash command palette. If the command is missing, run `/reload-plugins` first.

**Where your files live.** The plugin is the engine - it installs under `~/.claude/plugins/` where Claude Code manages it, updates through `/plugin update`, and you never have to open it. When you run setup, it builds your actual OS in a folder you own (default `~/founder-os/`): priorities, decisions, brain log, the lot. That folder is plain markdown and yours to keep, back up, or fork. If you ever remove the plugin, your OS folder stays exactly where it is. Engine and data are separate on purpose: the engine is swappable, your files are not.

**Verify the install:** Say "verify the OS" (or run `/founder-os:verify`).

---

## Path E - One-line curl (fastest if you live in a terminal)

One command. Works on macOS, Linux, and git-bash on Windows.

**Best for:** Anyone comfortable in a terminal who wants the fastest path to a working install.

**Requirements:** bash, git, and Python 3.11+.

**Steps:**

```bash
curl -fsSL https://raw.githubusercontent.com/ARCASSystems/FounderOS/main/install.sh | bash
```

The installer:

1. Checks that bash, git, and Python 3.11+ are present. If any are missing, it prints install instructions for that specific tool and exits.
2. Clones FounderOS to `~/founder-os/` (override with `--target <path>`). This is one folder you own - your data, the hooks, and the commands all live together. It is a plain git repo: back it up, move it, fork it. Nothing phones home.
3. Prints a one-screen confirmation with the next step (`cd` into `~/founder-os`, open Claude Code, say "set up Founder OS"). Hooks register through the `.claude/settings.json` inside that folder - see "How hooks fire on Path E" below.

If FounderOS is already installed, re-running the same command asks whether to update instead of cloning again. (Installs from before v1.37 that still live at `~/.claude/plugins/founder-os` are detected and kept in place, so you are never left with two copies.)

**How hooks fire on Path E.** Claude Code discovers hooks through a `.claude/settings.json` file in the working directory. The curl install lands one inside `~/founder-os/`, so the SessionStart brief and Stop revenue-check fire when you open Claude Code IN your OS folder. If you open Claude Code in a different project folder, those hooks do not fire there. To get hooks across every project, also add Path A (the Claude Code plugin) - the plugin engine activates the commands and hooks globally and stays out of your OS folder.

**Pros**
- One command, no decisions.
- Works whether or not you have the Claude Code plugin marketplace.
- Re-runnable as an update path.

**Cons**
- Requires bash. On Windows, install git-bash first.
- The install script requires internet access for the initial clone.
- Hooks fire only when Claude Code is opened in the cloned folder. Use Path A for hooks that activate everywhere.

**Verify the install:** Say "verify the OS" (or run `/founder-os:verify`).

---

## Path B - Manual git clone (most reliable)

Standard git workflow. Works regardless of plugin system state.

**Best for:** Anyone who wants full control of the local copy, anyone whose plugin install on Path A failed, anyone running on a Claude Code version where the plugin marketplace is flaky.

**Mac, Linux, or git-bash on Windows:**

```bash
git clone --depth 1 https://github.com/ARCASSystems/FounderOS.git ~/founder-os
cd ~/founder-os
```

**PowerShell on Windows:**

```powershell
git clone --depth 1 https://github.com/ARCASSystems/FounderOS.git "$HOME\founder-os"
cd "$HOME\founder-os"
```

Open Claude Code in that folder, then say "set up Founder OS" (or run `/setup`).

> **Note:** Commands in the manual clone path use bare names (`/setup`, `/status`, `/today`, etc.) because the plugin namespace is not active. The plugin install path (Path A) uses the `/founder-os:` prefix. The commands are identical underneath.

**Pros**
- Works regardless of plugin marketplace state.
- You own the local copy. Nothing magical happens behind the scenes.
- Standard git update path: `git pull` to refresh.

**Cons**
- Requires git installed.
- Updates are manual via `git pull`.
- Commands use bare names, not the `/founder-os:` namespace.

**Verifying it worked:** From the Claude Code session opened in the cloned folder, say "set up Founder OS" (or run `/setup`). The setup wizard should start its questions. If the slash command does not appear, confirm Claude Code's working directory is the FounderOS root (the folder containing `CLAUDE.md` and `.claude-plugin/`).

**Verify the install:** Say "verify the OS" (or run `/verify`).

---

## Path D - Claude Cowork (partial, desktop knowledge work)

Claude Cowork is Anthropic's desktop surface for non-coding work. It reads markdown, runs MCPs, and runs timed jobs - but hooks and the `/founder-os:*` slash command namespace do not fire there. Pair it with FounderOS for drafting and timed execution. Keep Claude Code as the OS layer.

**Best for:** Founders who already have FounderOS installed via Path 0, A, B, or E, and want Cowork available as a drafting surface with OS context.

**Note:** Cowork is not a setup surface. Install via one of the paths above first.

**Setup recipe:**

1. Install via Path 0, A, B, or E first.
2. In Cowork, open the FounderOS folder you set up.
3. Attach `CLAUDE.md` as folder instructions (or use Cowork's "Folder instructions" if available on your version).
4. If `brain/.snapshot.md` exists, attach it too. Skills produced this snapshot from your current state - it is the cheapest way to give Cowork live context.
5. Talk to Cowork in natural language. "What is on my plate today?" "Draft a follow-up to the call with X." Cowork reads markdown and writes markdown.
6. Return to Claude Code for any of: SessionStart brief, Stop revenue-check, slash commands, commits, cadence refresh, or the natural-language weekly review skill.

**Honest limits in Cowork:**

- The SessionStart brief does not fire. You will not see flags, stale cadence, or decay items unless you ask.
- The Stop revenue-check does not fire. Outreach actions captured in Cowork must be logged manually until you return to Claude Code.
- The fabric trio (`/today`, `/pre-meeting`, `/capture-meeting`) and the `/founder-os:*` namespace do not run.
- Cowork memory is separate from Claude Code's auto-memory. Behavioural guards in `~/.claude/projects/<slug>/memory/MEMORY.md` do not load in Cowork.

Full surface-by-surface compatibility detail in [docs/tools-and-mcps.md](tools-and-mcps.md).

---

## Picking the right path

| You have... | Pick |
|---|---|
| Nothing but Claude Code + a Pro/Max plan, and you want the fastest ownership path | Path 0 (ZIP) |
| Claude Code + Pro/Max plan, and you want commands and hooks active across every project | Path A (plugin) |
| bash + git + Python 3.11+ and you like the terminal | Path E (curl) |
| Claude Code, plugin install failed | Path B (git clone) |
| FounderOS installed, want Cowork too | Path D (Cowork) |

You can switch paths anytime. The OS is your files - they are the same regardless of how Claude reads them.

---

## After install

All paths converge on the same six files. Whichever path you picked, the next steps are the same. You can run the slash command or ask Claude in plain English - both work.

1. **Start the wizard.** Say "set up Founder OS" (or run `/founder-os:setup` on Path A, `/setup` on Path 0 and Path B). Path D: skip until you have set up locally.
   If your install uses git (Paths B and E, or Path 0 after "own my history"), run `./scripts/install-git-hooks.sh` to activate the privacy pre-commit hook (operator-only). On a fresh ZIP install there is no git yet, so this step waits until you turn version history on.
2. **Add your voice.** Say "set up my voice profile" (or run `/founder-os:voice-interview` on Path A, `/voice-interview` on Path B). Captures how you write so every writing skill sounds like you.
3. **Add your brand.** Say "set up my brand profile" (or run `/founder-os:brand-interview` on Path A, `/brand-interview` on Path B). Captures colors, fonts, logo so every branded deliverable looks like you.
4. **See your day.** Ask "what's on for today?" (or run `/today`). Ask "what should I focus on next?" (or run `/next`).
5. Use the OS for a week on real work before tweaking templates.

If anything breaks in the first 24 hours, email `solutions@arcassystems.com` with what you tried.

---

## Known platform notes

**Windows users.** Every hook ships with bash and PowerShell variants. `.claude/settings.json` wires both automatically. If you have PowerShell installed (all modern Windows systems do), the full hook set fires without any extra setup - no bash, no git-bash required. If you also have git-bash, both variants run - they fail gracefully if the other shell is absent, so there is no double-output risk.

**Git-less installs (Path 0).** Every hook degrades quietly when git is absent: the session brief still runs, the auto-save hook stays silent instead of erroring, and the per-session change snapshots do not need git at all. Nothing errors, nothing nags. Version history activates when you say "own my history".

**Mac, Linux.** Hooks run through bash with no extra setup.

**Cloud Claude (web, desktop).** Cloud Claude cannot run slash commands or write to local disk. It is a read-only surface. If you want the OS to remember your context across sessions, you need one of the local paths above.
