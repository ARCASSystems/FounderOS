# Auto-memory

The `MEMORY.md` template in this folder lives as a template until `/founder-os:setup` writes it into the right place on disk.

## Where it lands

Claude Code reads auto-memory from a per-project location:

- **macOS / Linux**: `~/.claude/projects/<project-slug>/memory/MEMORY.md`
- **Windows**: `%USERPROFILE%\.claude\projects\<project-slug>\memory\MEMORY.md`

The `<project-slug>` is derived by Claude Code from the absolute path of your working directory. The setup wizard determines the slug, creates the folder, and seeds `MEMORY.md` with the template content.

## What goes in it

Four sections, in this order:

1. **Behavioral Guards** - permanent corrections ("never do X", "always do Y"). Load every session.
2. **Active Project Context** - facts that are true right now. Load conditionally on task.
3. **Review Due** - entries past their decay date awaiting triage. Do not auto-load.
4. **Expired** - reference only, never loaded.

## Why it matters

The Founder OS files in `core/`, `context/`, and `cadence/` hold operating state - priorities, decisions, clients, daily anchors. The auto-memory layer holds *behavioral memory* - how you have corrected Claude, patterns you do not want repeated, project facts that span sessions.

Without auto-memory, Claude forgets your corrections after every session. With it, behavioral guards persist as a small, fast-loading layer the harness reads automatically.

## Maintenance

- Add a guard whenever you correct Claude on something that would otherwise come up again.
- Move expired entries down rather than deleting them. Reference history matters.
- Keep the file under 200 lines. Anything larger should be a linked detail file in the same folder.
