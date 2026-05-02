# Install paths

Three ways to install Founder OS. Pick the one that matches your stack. None of them lock you in - if you outgrow one path, you can move to another without losing your data.

If you get stuck, email `solutions@arcassystems.com` with the path you tried and the error you hit.

---

## Path A - Claude Code plugin (cleanest)

Two slash commands. Auto-updates available. Cleanest first-run experience.

**Best for:** Anyone with a Claude Pro or Max plan who already uses Claude Code in their terminal or IDE.

**Steps:**

```
/plugin marketplace add ARCASSystems/FounderOS
/plugin install founder-os@founder-os-marketplace
/founder-os:setup
```

**Pros**
- Two commands and you're set up.
- Plugin updates flow through `/plugin update`.
- Slash commands and hooks register automatically.

**Cons**
- Requires Claude Code with a paid Claude plan.
- Plugin marketplace behaviour can vary by Claude Code version. If the install does not work, fall back to Path B.

**Verifying it worked:** Run `/plugin list`. You should see `founder-os` listed as installed. Then `/founder-os:setup` should be available in the slash command palette.

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

Open Claude Code in that folder, then run:

```
/founder-os:setup
```

**Pros**
- Works regardless of plugin marketplace state.
- You own the local copy. Nothing magical happens behind the scenes.
- Standard git update path: `git pull` to refresh.

**Cons**
- Requires git installed.
- Updates are manual via `git pull`.
- Slightly longer first install than Path A.

**Verifying it worked:** From the Claude Code session opened in the cloned folder, run `/founder-os:setup`. The setup wizard should start its questions. If the slash command does not appear, confirm Claude Code's working directory is the FounderOS root (the folder containing `CLAUDE.md` and `.claude-plugin/`).

---

## Path C - Cloud Claude (no Claude Code required)

Use Claude.ai web or desktop with this repo as context.

**Best for:** Founders who do not have Claude Code installed and want to talk to the OS in the Claude app.

**Honest limit:** Cloud Claude cannot run slash commands or write to your local disk. Path C is currently a read-only operating mode. The setup wizard cannot complete here. The Notion Starter Kit (which would unlock a writable cloud path) is in development.

**Steps:**

1. Open [Claude.ai](https://claude.ai).
2. Start a new Project.
3. Attach the repo's `README.md` and `CLAUDE.md` as Project context. (Optional: also attach `core/identity.md` after you have run setup somewhere else.)
4. Use the safe fallback prompt below to start the conversation:

```
Use this repo as the Founder OS system layer. Read README.md and CLAUDE.md first.
If the founder context files are missing, stop and tell me to run /founder-os:setup
or use the Notion quickstart. Do not invent identity, clients, priorities, decisions,
revenue, or commitments.
```

**Pros**
- Works without Claude Code.
- Useful as a read-only thinking partner if you have set up elsewhere.

**Cons**
- Read-only. No setup wizard. No slash commands. No file writes.
- You'll get the "operating layer" experience without the persistence.

**Recovery:** If you decide you want write access, run Path A or Path B on your laptop. Your Cloud Claude project can stay where it is.

---

## Picking the right path

| You have... | Pick |
|---|---|
| Claude Code + Pro/Max plan | Path A |
| Claude Code, plugin install failed | Path B |
| No Claude Code, want to try the OS in the Claude app | Path C |
| Notion-only workflow, no terminal access | Wait for Notion Starter Kit (in development) |

You can switch paths anytime. The OS is your files - they're the same regardless of how Claude reads them.

---

## After install

All three paths converge on the same six files. Whichever path you picked, the next steps are:

1. Run `/founder-os:setup` (Path A or B). Path C: skip until you've set up locally.
2. Run `/founder-os:voice-interview` to capture how you write.
3. Run `/founder-os:brand-interview` to capture how your work looks.
4. Use the OS for a week on real work before tweaking templates.

If anything breaks in the first 24 hours, email `solutions@arcassystems.com` with what you tried. We read every email.

---

## Known platform notes

**Windows users.** The session-close revenue-loop hook is wired through `bash`. If you installed Claude Code without git-bash, the hook will not fire. Two fixes:

1. Install [Git for Windows](https://git-scm.com/download/win), which includes git-bash. This is the recommended path - most Windows founders running Claude Code already have it.
2. Or wire the PowerShell mirror manually. Edit `.claude/settings.json` and replace the Stop hook's command with:
   ```
   "command": "powershell -ExecutionPolicy Bypass -File \"$env:CLAUDE_PROJECT_DIR\\.claude\\hooks\\session-close-revenue-check.ps1\""
   ```

The hook is a soft warning, not a blocker. If it does not fire, the OS still works - you just lose the revenue-loop nudge.

**Mac, Linux.** Hooks run through bash with no extra setup.

**Cloud Claude (Path C).** Hooks do not fire in cloud-only mode. They are Claude Code-specific.
