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

If `/founder-os:setup` is not recognised after the install, run `/reload-plugins` (or restart Claude Code) so the plugin namespace activates, then try again.

**Pros**
- Two commands and you're set up.
- Plugin updates flow through `/plugin update`.
- Slash commands and hooks register automatically.

**Cons**
- Requires Claude Code with a paid Claude plan.
- Plugin marketplace behaviour can vary by Claude Code version. If the install does not work, fall back to Path B.

**Verifying it worked:** Open `/plugin` and check the Installed tab. You should see `founder-os` listed. Then `/founder-os:setup` should appear in the slash command palette. If the command is missing, run `/reload-plugins` first.

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
/setup
```

> **Note:** Commands in the manual clone path use bare names (`/setup`, `/status`, `/today`, etc.) because the plugin namespace is not active. The plugin install path (Path A) uses the `/founder-os:` prefix. The commands are identical underneath.

**Pros**
- Works regardless of plugin marketplace state.
- You own the local copy. Nothing magical happens behind the scenes.
- Standard git update path: `git pull` to refresh.

**Cons**
- Requires git installed.
- Updates are manual via `git pull`.
- Slightly longer first install than Path A.
- Commands use bare names, not the `/founder-os:` namespace.

**Verifying it worked:** From the Claude Code session opened in the cloned folder, run `/setup`. The setup wizard should start its questions. If the slash command does not appear, confirm Claude Code's working directory is the FounderOS root (the folder containing `CLAUDE.md` and `.claude-plugin/`).

---

## Path C - Cloud Claude (no Claude Code required)

Use Claude.ai web or desktop with this repo as context.

**Best for:** Founders who do not have Claude Code installed and want to talk to the OS in the Claude app.

**Honest limit:** Cloud Claude cannot run slash commands or write to your local disk. Path C is **preview mode, not install mode**. The setup wizard cannot complete here. The Notion Starter Kit (which would enable a writable cloud path) is in development. If you want a working install, choose Path A or Path B.

**Steps:**

1. Open [Claude.ai](https://claude.ai).
2. Start a new Project.
3. Attach the repo's `README.md` and `CLAUDE.md` as Project context. (Optional: also attach `core/identity.md` after you have run setup somewhere else.)
4. Use this fallback prompt to start the conversation:

```
Use this repo as the Founder OS system layer. Read README.md and CLAUDE.md first.
If you cannot find core/identity.md, treat the OS as not yet set up: do not invent
identity, clients, priorities, decisions, revenue, or commitments. Tell me which
setup path you recommend (Claude Code Path A or Path B) and why. Do not instruct
me to run /founder-os:setup here - it will not work in this surface.
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

All three paths converge on the same six files. Whichever path you picked, the next steps are below. You can run the slash command OR ask Claude in plain English - both work. Real users do not memorize a 20-command surface; talking to Claude is the default, slash commands are optional shortcuts for power users.

1. Start the wizard. Say "set up Founder OS" or run `/founder-os:setup` on Path A, `/setup` on Path B. Path C: skip until you have set up locally.
2. Add your voice. Say "set up my voice profile" or run `/founder-os:voice-interview` on Path A, `/voice-interview` on Path B. Captures how you write so every writing skill sounds like you.
3. Add your brand. Say "set up my brand profile" or run `/founder-os:brand-interview` on Path A, `/brand-interview` on Path B. Captures colors, fonts, logo so every branded deliverable looks like you.
4. See your day. Ask "what's on for today?" or run `/today`, then ask "what should I focus on next?" or run `/next`. Both bare on either path.
5. Use the OS for a week on real work before tweaking templates.

If anything breaks in the first 24 hours, email `solutions@arcassystems.com` with what you tried. We read every email.

---

## Cowork mode (partial, desktop knowledge work)

Claude Cowork is Anthropic's desktop surface for non-coding work. It reads markdown, runs MCPs, and executes scheduled tasks - but hooks and the `/founder-os:*` slash command namespace do not fire there. Pair it with FounderOS for drafting and scheduled execution. Keep Claude Code as the OS layer.

**Setup recipe:**

1. Install via Path A or Path B first. Cowork is not a setup surface.
2. In Cowork, open the FounderOS folder you set up.
3. Attach `CLAUDE.md` as folder instructions (or use Cowork's "Folder instructions" if available on your version).
4. If `brain/.snapshot.md` exists, attach it too. Skills produced this snapshot from your current state - it is the cheapest way to give Cowork live context.
5. Talk to Cowork in natural language. "What is on my plate today?" "Draft a follow-up to the call with X." Cowork reads markdown and writes markdown. It can also run scheduled tasks - say "schedule this" or use `/schedule` directly - useful for automated briefs while you are not in Claude Code.
6. Return to Claude Code for any of: SessionStart brief, Stop revenue-check, slash commands (`/today`, `/next`, `/founder-os:status` on Path A or `/status` on Path B, `/founder-os:wiki-build` on Path A or `/wiki-build` on Path B), commits, cadence refresh, or the natural-language weekly review skill (`run my weekly review`).

**Honest limits in Cowork:**

- The SessionStart brief does not fire. You will not see flags, stale cadence, or decay items unless you ask.
- The Stop revenue-check does not fire. Outreach actions captured in Cowork must be logged manually until you return to Claude Code.
- The fabric trio (`/today`, `/pre-meeting`, `/capture-meeting`) and the `/founder-os:*` namespace do not run.
- Cowork memory is separate from Claude Code's auto-memory. Behavioural guards in `~/.claude/projects/<slug>/memory/MEMORY.md` do not load in Cowork.

Full surface-by-surface compatibility detail in [docs/tools-and-mcps.md](tools-and-mcps.md).

---

## Known platform notes

**Windows users.** Both hooks ship with bash and PowerShell variants. `.claude/settings.json` wires both automatically. If you have PowerShell installed (all modern Windows systems do), both the SessionStart brief and the Stop revenue-check will fire without any extra setup. If you also have git-bash, both variants run - they fail gracefully if the other shell is absent, so there is no double-output risk.

**Mac, Linux.** Hooks run through bash with no extra setup.

**Cloud Claude (Path C).** Hooks do not fire in cloud-only mode. They are Claude Code-specific.
