# Install paths

Four ways to install FounderOS. Pick the one that matches your stack. None of them lock you in - if you outgrow one path, you can move to another without losing your data.

If you get stuck, email `solutions@arcassystems.com` with the path you tried and the error you hit.

---

## Path E - One-line curl (simplest)

One command. Works on macOS, Linux, and git-bash on Windows.

**Best for:** Anyone who wants the fastest path to a working install without reading install docs.

**Requirements:** bash, git, and Python 3.11+.

**Steps:**

```bash
curl -fsSL https://raw.githubusercontent.com/ARCASSystems/FounderOS/main/install.sh | bash
```

The installer:

1. Checks that bash, git, and Python 3.11+ are present. If any are missing, it prints install instructions for that specific tool and exits.
2. Clones FounderOS to `~/.claude/plugins/founder-os/` (override with `--target <path>`).
3. Copies hook files to `~/.claude/hooks/` as a backup location. (Hooks register through the plugin's own `.claude/settings.json` - see "How hooks fire" below.)
4. Prints a one-screen confirmation and the natural-language next step.

If FounderOS is already installed, re-running the same command asks whether to update instead of cloning again.

**How hooks fire on Path E.** Claude Code discovers hooks through a `.claude/settings.json` file in the working directory. The curl install lands one inside `~/.claude/plugins/founder-os/`, so the SessionStart brief and Stop revenue-check fire when you open Claude Code IN that folder. If you open Claude Code in a different project folder, those hooks do not fire there. To get hooks across every project, use Path A (Claude Code plugin) - the plugin namespace activates the hooks globally.

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

## Path A - Claude Code plugin (cleanest)

Two commands. Auto-updates available. Cleanest first-run experience inside Claude Code.

**Best for:** Anyone with a Claude Pro or Max plan who already uses Claude Code in their terminal or IDE.

**Steps:**

```
/plugin marketplace add ARCASSystems/FounderOS
/plugin install founder-os@founder-os-marketplace
```

If `/founder-os:setup` is not recognised after install, run `/reload-plugins` (or restart Claude Code) so the plugin namespace activates, then try again.

**Pros**
- Two commands and you are set up.
- Plugin updates flow through `/plugin update`.
- Slash commands and hooks register automatically.

**Cons**
- Requires Claude Code with a paid Claude plan.
- Plugin marketplace behaviour can vary by Claude Code version. If the install does not work, fall back to Path B or Path E.

**Verifying it worked:** Open `/plugin` and check the Installed tab. You should see `founder-os` listed. Then `/founder-os:setup` should appear in the slash command palette. If the command is missing, run `/reload-plugins` first.

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

Claude Cowork is Anthropic's desktop surface for non-coding work. It reads markdown, runs MCPs, and executes scheduled tasks - but hooks and the `/founder-os:*` slash command namespace do not fire there. Pair it with FounderOS for drafting and scheduled execution. Keep Claude Code as the OS layer.

**Best for:** Founders who already have FounderOS installed via Path A, B, or E, and want Cowork available as a drafting surface with OS context.

**Note:** Cowork is not a setup surface. Install via one of the three paths above first.

**Setup recipe:**

1. Install via Path A, B, or E first.
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
| bash + git + Python 3.11+ | Path E (curl) |
| Claude Code + Pro/Max plan | Path A (plugin) |
| Claude Code, plugin install failed | Path B (git clone) |
| FounderOS installed, want Cowork too | Path D (Cowork) |

You can switch paths anytime. The OS is your files - they are the same regardless of how Claude reads them.

---

## After install

All paths converge on the same six files. Whichever path you picked, the next steps are the same. You can run the slash command or ask Claude in plain English - both work.

1. **Start the wizard.** Say "set up Founder OS" (or run `/founder-os:setup` on Path A, `/setup` on Path B). Path D: skip until you have set up locally.
2. **Add your voice.** Say "set up my voice profile" (or run `/founder-os:voice-interview` on Path A, `/voice-interview` on Path B). Captures how you write so every writing skill sounds like you.
3. **Add your brand.** Say "set up my brand profile" (or run `/founder-os:brand-interview` on Path A, `/brand-interview` on Path B). Captures colors, fonts, logo so every branded deliverable looks like you.
4. **See your day.** Ask "what's on for today?" (or run `/today`). Ask "what should I focus on next?" (or run `/next`).
5. Use the OS for a week on real work before tweaking templates.

If anything breaks in the first 24 hours, email `solutions@arcassystems.com` with what you tried.

---

## Known platform notes

**Windows users.** Both hooks ship with bash and PowerShell variants. `.claude/settings.json` wires both automatically. If you have PowerShell installed (all modern Windows systems do), both the SessionStart brief and the Stop revenue-check will fire without any extra setup. If you also have git-bash, both variants run - they fail gracefully if the other shell is absent, so there is no double-output risk.

**Mac, Linux.** Hooks run through bash with no extra setup.

**Cloud Claude (web, desktop).** Cloud Claude cannot run slash commands or write to local disk. It is a read-only surface. If you want the OS to remember your context across sessions, you need one of the local paths above.
