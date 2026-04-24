---
description: Run the Founder OS setup wizard. Generates your identity, priorities, decisions, cadence, and brain files from a guided interview. Takes 15 to 20 minutes.
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

   Read the setup skill at `skills/founder-os-setup/SKILL.md` and execute it end to end. The skill owns the wizard flow: Discovery, Identity, Founder OS root, company folders, first project, remaining projects, validation. Follow its phases IN ORDER. Do not shortcut.

   If `$ARGUMENTS` contains `reset`, pass that signal into the skill so it knows to scan for and reconcile existing files rather than assume a clean slate.

## Rules

- This command is a thin trigger. All logic lives in the skill. Do not duplicate wizard steps here.
- If the skill file is missing, reply: `Setup skill not found at skills/founder-os-setup/SKILL.md. This install is incomplete. Re-install the plugin.` and stop.
- No em dashes or en dashes. Hyphens only with spaces.
- Never overwrite existing files without the explicit re-run confirmation above.
