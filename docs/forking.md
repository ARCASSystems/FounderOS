# Forking FounderOS

FounderOS v1.23 is feature-complete. If you need something beyond what ships, fork it.

This guide explains when to fork, what the extension points are, which rules to preserve, and how to keep your fork sync-able with future breakage patches.

---

## Why fork

Fork when the baseline does not fit your situation. Common reasons:

- You want a skill the baseline does not ship (a specific industry, role, or tool integration).
- You want to add automation the baseline deliberately skipped (crons, Notion sync, embeddings).
- You are building a team or company layer on top of the single-user core.

You do not need to fork to add your own skills, voice profile, or brand profile. Those are user-layer files the setup wizard generates for you. Fork when you want to change the system layer.

---

## The five extension points

**1. Skills.** Drop a `skills/<your-skill>/SKILL.md` file. The plugin loader picks it up automatically. The setup wizard's final phase asks whether to enable additional skills, so your fork can include them in the install flow. Copy an existing skill folder as a starting point - the frontmatter structure and body format are self-documenting.

**2. Slash commands.** Drop a `.claude/commands/<your-command>.md` file. Use the existing commands in `.claude/commands/` as templates. Commands run on invocation; they do not need to be registered anywhere else.

**3. Hooks.** Drop a script in `.claude/hooks/` and register the event and path in `.claude/settings.json`. Ship bash and PowerShell variants using the `session-start-brief.*` pair as the reference pattern. Hooks fail silently by design - add a quarantine write if you want failures to be visible.

**4. Templates.** Edit or add files in `templates/`. The setup wizard reads from there when generating a user's operating files. If you change a template, update the corresponding skill or wizard phase that references it.

**5. Runtime payloads.** Write a Python script that emits a markdown file to a known path (`brain/.snapshot.md` is the v1.10 reference). Any skill that needs live context reads the file at task time. Keep the script stdlib-only and idempotent.

---

## The three rules to preserve

**Free-tier accessibility floor.** No paid API key required for core function. This is load-bearing: it is why embeddings, hosted vector DBs, and cloud-only integrations were not shipped. If your fork adds something that requires a paid key, gate it behind a user opt-in and make the opt-out path fully functional. A user who cannot afford or does not want a paid key should still get a useful OS.

**Local-first.** No mandatory external service. Data stays on the user's machine unless they explicitly send it somewhere. Cloud writes should always be opt-in. The system works fully offline once installed.

**Markdown-first.** No proprietary format. Every file the OS reads and writes is plain markdown or YAML. This keeps the OS readable in any editor, diff-able in any git client, and portable when the user moves machines or tools.

---

## Keeping your fork sync-able with breakage patches

Tag your customizations with `# fork:` comments in skill bodies and hook scripts. When a breakage patch lands on the baseline (`v1.23.0`, for example), you can `git rebase` or cherry-pick against the upstream and your tagged lines make it clear what is yours versus what is system layer.

Example in a skill body:
```
# fork: added buyer-journey stage to intake questions - remove if upstreaming
```

Example in a hook script:
```bash
# fork: added Slack notification on stale cadence
```

This convention costs nothing to add and makes a future rebase straightforward.

---

## Where to get help

- **GitHub Discussions** - open a discussion thread in the FounderOS repo. If your fork is public, link it there. We don't merge into this repo, but we'll point others to your work.
- **Community fork list** - linked from the README once forks are registered via the discussion thread.
- **The baseline itself** - every skill body is prose describing the behavior. Read the ones closest to what you want to build before writing your own.
