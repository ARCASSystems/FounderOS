# Install paths

Five ways to install FounderOS. The ZIP download (Path 0) needs no Git and no terminal and comes first; pick whichever matches how you work. None of them lock you in - if you outgrow one path, you can move to another without losing your data.

**Not comfortable in a terminal?** Use Path 0 (ZIP download) or Path A (Claude Code plugin). Both run without a single terminal command.

If you get stuck, email `solutions@arcassystems.com` with the path you tried and the error you hit.

---

## Path 0 - Download ZIP (no Git or terminal required)

Three steps and one sentence typed. The gentlest path there is.

**Best for:** Anyone who wants to own the system in ten minutes with nothing new installed. Anyone who does not have git and does not want to think about it.

**Requirements:** Claude Code with a paid Claude plan (Pro, Max, Team or Enterprise - it does not run on the free plan), and Python 3.11+ (the setup wizard checks for it before asking anything and tells you plainly if it is missing).

**Steps:**

1. [Download the ZIP](https://github.com/ARCASSystems/FounderOS/releases/download/v1.55.1/FounderOS-1.55.1.zip).
2. Right-click the file and choose **Extract All** (Windows) or double-click it (Mac). Windows puts a folder inside a folder - open the inner one, called **Founder OS**, the one that contains `CLAUDE.md`. Move it wherever you keep your work. It is already named, so there is nothing to rename.
3. Open the folder in Claude Code and say **"set up Founder OS"**. Two ways in:
   - **No terminal - the Claude desktop app.** Download it from [claude.com/download](https://claude.com/download), sign in, open the **Code** tab, choose **Local**, click **Select folder**, and pick the Founder OS folder. The desktop app includes Claude Code, so nothing else is installed. This route follows Anthropic's docs, and we have not yet watched a fresh install run it.
   - **With the Claude Code terminal tool.** Double-click **Start Founder OS** (the file ending `.bat` on Windows, the one ending `.command` on a Mac). It opens Claude Code in the folder and starts the setup wizard for you. After setup, the same double-click just opens your OS - it is the standing front door, not a one-time installer.

First-run notes, so nothing surprises you:

- **Windows** may show a security note about a downloaded script. Choose to run it - the file is plain text; right-click it and choose Edit to read everything it does before running, if you like.
- **Mac**: right-click the file and choose **Open** the first time. That is how macOS treats any downloaded script, not an error in the file.
- **If the Claude Code terminal tool is not installed**, the start file says so, explains the desktop-app route, and opens the Claude download page - nothing breaks. The desktop app does not add the terminal tool, so if you only have the app, open the folder from its Code tab instead of double-clicking.
- **Prefer no scripts?** The spoken way works identically: open the folder in Claude Code and say **"set up Founder OS"** (or run `/setup`).
- **The folder icon** appears on Windows the first time you double-click **Start Founder OS**. Windows only reads a folder's icon setting once the folder is marked as customised, and extracting a ZIP does not mark it, so the launcher does it. On a Mac, run `bash scripts/set_folder_icon.sh` from the folder once if you want the same thing (it ships with the ZIP and the clone, which are the paths where there is a folder to brand); it needs Xcode Command Line Tools and says so plainly if they are missing. Either way it is cosmetic. Nothing about the OS depends on it.

Commands use bare names on this path (`/setup`, `/today`), same as the git-clone path.

**Already have notes?** If you keep an Obsidian vault or a folder of markdown, setup can move the OS in next to your notes instead of starting a fresh folder - your existing files are never touched, and the wizard asks before anything that would collide. Say "set up Founder OS inside my vault". Full picture, including what your old notes can and cannot do afterwards, in [adopt-existing-notes.md](adopt-existing-notes.md).

**Updates:** say "update Founder OS" (or run `/update`). The OS re-downloads the ZIP itself, refreshes only its own engine files (skills, commands, scripts, docs), and never touches your data. You approve before anything is applied.

**Version history on this path:** off at first, by design - there is no git on the machine yet. You are still covered: the OS snapshots every file it touches, every session, and `/changes` shows exactly what changed with a one-command restore per file. When you want full history ("undo to before this morning", a complete timeline), say **"own my history"** - with your yes, the OS installs git itself, turns the folder into a repository, and wires the privacy guard. You never type a git command. This is the recommended steady state: once git is on, updates flow through it instead of ZIP re-downloads, and git maintains itself - the ZIP was the door, not the destination.

**Pros**
- No Git, no curl, no terminal.
- The folder is yours from the first second - plain markdown, no hidden state.
- Updates and version history are both one sentence away, handled for you.

**Cons**
- Version history starts off until you graduate it on (session snapshots cover you meanwhile).
- Slash commands use bare names (`/setup`), not the `/founder-os:` namespace.

**Verify the install:** Say "verify the OS" (or run `/verify`).

---

## Path A - Claude Code plugin (no terminal, cleanest)

Two commands, typed inside Claude Code. No terminal needed. Cleanest first-run experience. Updates are manual unless you turn auto-update on (see Pros).

**Best for:** Anyone not comfortable in a terminal, and anyone with a Claude Pro or Max plan who already uses Claude Code.

**Steps:**

```
/plugin marketplace add ARCASSystems/FounderOS
/plugin install founder-os@founder-os-marketplace
```

If `/founder-os:setup` is not recognised after install, run `/reload-plugins` (or restart Claude Code) so the plugin namespace activates, then try again.

**Pros**
- Two commands and you are set up, with no terminal install step.
- Updates are one click, but manual by default: Claude Code leaves auto-update off for third-party marketplaces like this one. Update from `/plugin` (Installed tab, Update now), or turn auto-update on once (`/plugin`, Marketplaces tab, Enable auto-update).
- Slash commands register automatically and are available in every project you open.

**Cons**
- Requires Claude Code with a paid Claude plan.
- Plugin marketplace behaviour can vary by Claude Code version. If the install does not work, fall back to Path B or Path E.

**Verifying it worked:** Open `/plugin` and check the Installed tab. You should see `founder-os` listed. Then `/founder-os:setup` should appear in the slash command palette. If the command is missing, run `/reload-plugins` first.

**How hooks fire on Path A.** The plugin registers the slash commands. It does not register hooks - the setup wizard does, by writing a `.claude/settings.json` into the OS folder it builds for you. So the session brief, the revenue check, and the auto-save fire when you open Claude Code in your OS folder, and nowhere else. That is deliberate rather than a gap: every one of them reads your OS files, and firing them inside an unrelated project would be noise at best.

**Where your files live.** The plugin is the engine - it installs under `~/.claude/plugins/` where Claude Code manages it, updates from `/plugin` (manual unless you turn auto-update on), and you never have to open it. When you run setup, it builds your actual OS in a folder you own (default `~/founder-os/`): priorities, decisions, brain log, the lot. That folder is plain markdown and yours to keep, back up, or fork. If you ever remove the plugin, your OS folder stays exactly where it is. Engine and data are separate on purpose: the engine is swappable, your files are not.

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

If FounderOS is already installed, the installer never overwrites it. Run from a terminal (`bash install.sh`), it asks whether to update. Piped straight from curl, as the command above does, nothing can read your answer, so it leaves the install untouched and prints how to update on purpose: re-run with `FOUNDER_OS_UPDATE=1`. (Installs from before v1.37 that still live at `~/.claude/plugins/founder-os` are detected and kept in place, so you are never left with two copies.)

**How hooks fire on Path E.** Claude Code discovers hooks through a `.claude/settings.json` file in the working directory. The curl install lands one inside `~/founder-os/`, so the SessionStart brief and Stop revenue-check fire when you open Claude Code IN your OS folder. If you open Claude Code in a different project folder, those hooks do not fire there. Adding the plugin (Path A) does not change that - the plugin carries the slash commands, not the hooks. Hooks are read from the folder you open, on every path, by design: they all read your OS files.

**Pros**
- One command, no decisions.
- Works whether or not you have the Claude Code plugin marketplace.
- Re-runnable as an update path.

**Cons**
- Requires bash. On Windows, install git-bash first.
- The install script requires internet access for the initial clone.
- Hooks fire only when Claude Code is opened in the cloned folder. That is true on every install path.

**Verify the install:** Say "verify the OS" (or run `/verify`). This path clones the repo, so commands use bare names, not the `/founder-os:` namespace.

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
- Updates work the same as every path: say "update Founder OS". `git pull` also works if you prefer raw git.

**Cons**
- Requires git installed.
- Commands use bare names, not the `/founder-os:` namespace.

**Verifying it worked:** From the Claude Code session opened in the cloned folder, say "set up Founder OS" (or run `/setup`). The setup wizard should start its questions. If the slash command does not appear, confirm Claude Code's working directory is the FounderOS root (the folder containing `CLAUDE.md` and `.claude-plugin/`).

**Verify the install:** Say "verify the OS" (or run `/verify`).

---

## Path D - Claude Cowork (partial, desktop knowledge work)

Claude Cowork is Anthropic's agent for non-coding work. From 16 September 2026 it has been merging into the main Claude app alongside chat, Pro and Max plans first. Two platform facts shape how it pairs with Founder OS:

- **From 6 October 2026, new Cowork tasks on Pro and Max plans run in Anthropic's cloud.** A cloud task reaches a folder on your computer only while the Claude desktop app is open and connected to it.
- **Anthropic's help pages disagree on scheduled tasks.** One says they cannot be tied to a folder on your computer. Another says a task that uses local files needs the desktop app open. Either way, a timed job that reads or writes your OS folder is safer in Claude Code.

Founder OS hooks live in the folder's own settings, not in the plugin, and whether Cowork reads them is not yet tested. Pair Cowork with FounderOS for drafting while the desktop app is open. Keep Claude Code as the OS layer.

**Best for:** Founders who already have FounderOS installed via Path 0, A, B, or E, and want Cowork available as a drafting surface with OS context.

**Note:** Cowork is not a setup surface. Install via one of the paths above first.

**Setup recipe:**

1. Install via Path 0, A, B, or E first.
2. Open the Claude desktop app and keep it open while you work, because Cowork reaches your folder only through it.
3. Connect the FounderOS folder you set up, and attach `CLAUDE.md` as its instructions.
4. If `brain/.snapshot.md` exists, attach it too. Skills produced this snapshot from your current state - it is the cheapest way to give Cowork live context.
5. Talk to Cowork in natural language. "What is on my plate today?" "Draft a follow-up to the call with X."
6. Return to Claude Code for any of: SessionStart brief, Stop revenue-check, saves, cadence refresh, anything on a timer, or the weekly review.

**Honest limits in Cowork:**

- Do not count on the SessionStart brief. You will not see flags, stale cadence, or decay items unless you ask.
- Do not count on the Stop revenue-check. Log outreach actions captured in Cowork by hand until you return to Claude Code.
- The fabric trio (`/today`, `/pre-meeting`, `/capture-meeting`) is a set of folder commands. Cowork can run a plugin's commands when the plugin is on your claude.ai account, but installing Founder OS there is not yet tested, so say what you want in words instead.
- Cowork does not read Claude Code's auto-memory. Behavioural guards in `~/.claude/projects/<slug>/memory/MEMORY.md` do not load in Cowork.

Full surface-by-surface compatibility detail in [docs/tools-and-mcps.md](tools-and-mcps.md).

---

## Picking the right path

| You have... | Pick |
|---|---|
| Nothing but Claude Code + a Pro/Max plan, and you want the fastest ownership path | Path 0 (ZIP) |
| Only the Claude desktop app, no terminal | Path 0 (ZIP), opened from the Code tab |
| Claude Code + Pro/Max plan, and you want the slash commands available in every project | Path A (plugin) |
| bash + git + Python 3.11+ and you like the terminal | Path E (curl) |
| Claude Code, plugin install failed | Path B (git clone) |
| FounderOS installed, want Cowork too | Path D (Cowork) |

You can switch paths anytime. The OS is your files - they are the same regardless of how Claude reads them.

---

## Updating, and what stays yours

Say "update Founder OS" whenever you like. No git needed: a ZIP install updates over a plain download, and every other path uses the same command. The update draws a hard line between the OS's machinery and your data:

- **The OS's, replaced freely by an update:** `skills/`, `scripts/`, `templates/`, `docs/`, `updates/`, the commands, and the reference docs at the root.
- **Yours, never written by an update:** `core/`, `context/`, `cadence/`, `brain/`, `capture/`, `network/`, `brands/`, `clients/`, `companies/`, `roles/` (your employee registry and its review record), `system/` (this install's quarantine record), any company or project folders setup created at the root, plus `stack.json`, `os-config.yaml`, and `MEMORY.md` with its `memory/` directory. Your identity, your log, your pipeline, and your decisions survive every update by design.
- **In between, proposed never imposed:** `CLAUDE.md`, `rules/`, and `.claude/settings.json`. An update shows you each change as a diff and you say yes or no per file. Declining leaves your version in place.

---

## After install

All paths converge on the same six files. Whichever path you picked, the next steps are the same. You can run the slash command or ask Claude in plain English - both work.

1. **Start the wizard.** Say "set up Founder OS" (or run `/founder-os:setup` on Path A, `/setup` on Path 0 and Path B). Path D: skip until you have set up locally.
   If your install uses git (Paths B and E, or Path 0 after "own my history"), the setup wizard wires the privacy guard for you as part of setup. If you ever need to re-wire it by hand later (say the folder moved machines), `./scripts/install-git-hooks.sh` does it. On a fresh ZIP install there is no git yet, so this waits until you turn version history on.
2. **Add your voice.** Say "set up my voice profile" (or run `/founder-os:voice-interview` on Path A, `/voice-interview` on Path B). Captures how you write so every writing skill sounds like you.
3. **Add your brand.** Say "set up my brand profile" (or run `/founder-os:brand-interview` on Path A, `/brand-interview` on Path B). Captures colors, fonts, logo so every branded deliverable looks like you.
4. **See your day.** Ask "what's on for today?" (or run `/today`). Ask "what should I focus on next?" (or run `/next`).
5. Use the OS for a week on real work before tweaking templates.

If anything breaks in the first 24 hours, email `solutions@arcassystems.com` with what you tried.

---

## Known platform notes

**Windows users.** Every hook event runs through one cross-platform Python dispatcher (`scripts/hooks/dispatch.py`), wired by `.claude/settings.json`. There is no shell to be missing - no bash, no PowerShell, no git-bash required. Python 3.11+ (already a prerequisite of the OS) is the only thing the hooks need. Out of the box each hook command tries the three interpreter spellings in order (`python`, `python3`, `py -3`), so the hooks fire even before setup on a machine where bare `python` is not on PATH; setup then writes the one interpreter it discovered into the hook commands for you.

**Git-less installs (Path 0).** Every hook degrades quietly when git is absent: the session brief still runs, the auto-save hook stays silent instead of erroring, and the per-session change snapshots do not need git at all. Nothing errors, nothing nags. Version history activates when you say "own my history".

**Mac, Linux.** Same Python dispatcher, no extra setup.

**Claude in the cloud.** Three different things share the name. Claude Code on the web (claude.ai/code) runs a full session in Anthropic's cloud on a GitHub copy of a repo, so it never sees a folder that lives only on your computer. claude.ai chat can load a plugin's skills but never runs hooks. Cowork reaches a folder on your computer only while the Claude desktop app is open. For the OS to work on your own files, with the session brief and saves, open the folder in Claude Code on your machine: the terminal tool, or per Anthropic's docs an IDE extension or the desktop app's Code tab (not yet tested by us).
