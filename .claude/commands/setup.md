---
description: Set up Founder OS from scratch. Fires on any natural-language onboarding ask, including "set up Founder OS", "install Founder OS", "set up my second brain", "help me set up my second brain", "help me onboard", "onboard me", "what do I do", "where do I start", "how does this work", "I'm new", "get me started", "run the setup wizard" (or run /founder-os:setup). Guided interview generates your identity, priorities, decisions, cadence, and brain files. Takes 15 to 20 minutes.
argument-hint: "[--reset]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
---

# Founder OS setup

Entry point for the Founder OS setup wizard. Triggers the `founder-os-setup` skill, which runs a guided interview and generates every file the OS needs to operate: identity, priorities, decisions, cadence, brain, roles.

Argument: `$ARGUMENTS` - optional. Pass `--reset` (or `reset`) to force a re-run on an existing install.

## Procedure (in order)

1. Check whether `core/identity.md` exists at the repo root.

2. If it exists AND `$ARGUMENTS` does NOT contain `reset`:

   Ask the founder, as a single message, nothing else:

   ```
   Founder OS appears to be set up already (core/identity.md exists). Re-run setup? (yes / no)
   ```

   Wait for the reply.
   - If the reply is a clear `no` (or anything that is not a clear `yes`), reply: `Setup dismissed. Existing files left untouched.` and stop.
   - If the reply is a clear `yes`, proceed to step 3.

3. If `core/identity.md` does NOT exist, OR the founder confirmed re-run, OR `$ARGUMENTS` contains `reset`:

   **Find the setup skill before trying to read it.** The skill ships with the engine, and the engine is not always in the folder you are standing in. On a plugin install the working directory is the founder's own folder, which is empty on purpose - the engine lives where Claude Code keeps plugins. Resolving against the working directory alone fails there, on a correct install.

   Take the first of these that exists and use it for the rest of the run:

   1. `${CLAUDE_PLUGIN_ROOT}/skills/founder-os-setup/SKILL.md`. Claude Code sets `CLAUDE_PLUGIN_ROOT` for a plugin's own components; read it with `echo "$CLAUDE_PLUGIN_ROOT"` if it has not already been substituted into this file. An empty value only means this is not a plugin install - move on without saying anything.
   2. `skills/founder-os-setup/SKILL.md` relative to the working directory. This is the git clone, curl, and ZIP case.
   3. The newest match for `~/.claude/plugins/**/skills/founder-os-setup/SKILL.md`. Plugin managers move their folder layout between versions, so search rather than assume one.

   Read the skill from wherever it resolved and execute it end to end. The skill owns the wizard flow: Discovery, Identity, Founder OS root, company folders, first project, remaining projects, validation. Follow its phases IN ORDER. Do not shortcut.

   If `$ARGUMENTS` contains `reset`, pass that signal into the skill so it knows to scan for and reconcile existing files rather than assume a clean slate.

## Rules

- This command is a thin trigger. All logic lives in the skill. Do not duplicate wizard steps here.
- If all three lookups in step 3 come back empty, do NOT tell the founder to re-install. On the path this fails hardest, a plugin install, they did everything right and the engine is sitting on their machine. Reply exactly:

  ```
  I could not find the setup instructions that came with Founder OS, so I cannot start the wizard yet. Restarting Claude Code fixes this most of the time, because it reloads what is installed. If it happens again after a restart, email solutions@arcassystems.com and say setup could not find its own instructions.
  ```

  Then stop.
- No em dashes or en dashes. Hyphens only with spaces.
- Never overwrite existing files without the explicit re-run confirmation above.
