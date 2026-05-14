# Tools, MCPs, and surfaces

Founder OS does not assume your stack. The OS is a set of files and skills. Each skill declares which Model Context Protocol (MCP) servers it can use, and degrades gracefully when those MCPs are not available.

You connect only the MCPs you actually need. A founder with zero MCPs can still complete setup and run most of the 45 skills end-to-end. The four skills that produce noticeably better output with the relevant MCP connected are `email-drafter`, `meeting-prep`, `knowledge-capture`, and `session-handoff`. They still function without one, but with reduced context.

This doc covers three things: which MCPs activate which skills, which editors and surfaces (Obsidian, Claude Cowork, claude-mem) pair well with the OS, and what works under each surface.

---

## What is an MCP?

An MCP (Model Context Protocol) server is an integration that lets Claude Code talk to an external tool - your email, calendar, Notion, Apollo, Supabase, and so on. MCPs are configured at the Claude Code level, not inside Founder OS. You install them once and any project can use them.

Read the Claude Code docs for how to add MCP servers: [docs.claude.com/claude-code](https://docs.claude.com/en/docs/claude-code).

---

## Capability catalog

| Capability | Recommended MCP | Alternatives | Skills that use it | Required for launch? |
|---|---|---|---|---|
| Email | Gmail MCP | Outlook MCP, manual paste | email-drafter, capture-meeting | No - works without |
| Calendar | Google Calendar MCP | Outlook MCP, manual paste | meeting-prep, /today | No - degrades to "no calendar event" line |
| Knowledge base | Notion MCP | Local markdown, Obsidian | knowledge-capture, session-handoff | No - skills work locally without it |
| Sales / CRM | Apollo MCP | HubSpot MCP, manual entry | proposal-writer (pricing context only) | No |
| Design and decks | Canva MCP, Gamma MCP | None - skill produces text spec | (no deck skills shipped yet) | No |
| Code repos | GitHub MCP | None - if no GitHub, skip | (future build-related skills) | No |
| Database | Supabase MCP | None | (advanced users only) | No |
| Web research | Web search (built-in) | None | strategic-analysis, knowledge-capture | No - usually built into Claude Code |

---

## What works with zero MCPs

If you install Founder OS and add no MCPs, all of these skills work end-to-end on your local files:

- founder-os-setup
- readiness-check (`/founder-os:status`)
- audit
- voice-interview
- brand-interview
- your-voice
- your-deliverable-template
- linkedin-post
- client-update
- proposal-writer
- weekly-review
- priority-triage
- decision-framework
- brain-log
- brain-snapshot
- brain-pass
- founder-coaching
- bottleneck-diagnostic
- unit-economics
- content-repurposer
- strategic-analysis (without web search, less useful but still runs)
- pre-send-check
- blind-spot-review
- ship-deliverable
- sop-writer
- forcing-questions
- approval-gates
- handoff-protocol
- context-persistence
- data-security
- business-context-loader
- ingest
- lint
- wiki-build
- query

The four remaining skills (`email-drafter`, `meeting-prep`, `knowledge-capture`, `session-handoff`) function without MCPs but produce noticeably better output with the relevant integration connected.

---

## What each MCP adds

### Gmail MCP
- `email-drafter` can read your inbox to draft replies in context.
- `capture-meeting` can route follow-up emails directly to a draft.

### Google Calendar MCP
- `/today` shows the next scheduled event.
- `meeting-prep` reads attendee list and meeting metadata.

### Outlook MCP (Email + Calendar)
- Same as Gmail + Google Calendar but on the Microsoft stack.

### Notion MCP
- `knowledge-capture` can write captured insights directly into a Notion database.
- `session-handoff` can post a session summary to a Notion page.
- Useful if you already live in Notion. Skip if you don't.

### Apollo MCP
- `proposal-writer` can pull prospect company data when writing a proposal.
- Useful only if you do enough cold outreach to justify Apollo's pricing.

### Supabase MCP
- For advanced founders who want to wire database state into the OS. Not needed for the default skills.

---

## Declaring MCP requirements per skill

Every skill in `skills/` includes a `mcp_requirements:` field in its frontmatter:

- `mcp_requirements: []` - works with no MCPs.
- `mcp_requirements: [optional: gmail, optional: gcal]` - degrades gracefully if the MCP is missing.
- `mcp_requirements: [required: notion]` - hard-fails without the named MCP, with a friendly message.

If you add a third-party skill or build your own, follow the same convention so the readiness check (`/founder-os:status`) can report what's wired up correctly.

---

## When something doesn't work

If a skill says it needs an MCP you don't have, it will tell you. Two options:

1. **Install the MCP.** See [docs.claude.com/claude-code](https://docs.claude.com/en/docs/claude-code) for adding MCP servers.
2. **Skip that skill.** Use the local-file alternative the skill suggests (e.g. paste calendar events manually, write Notion exports as markdown into `brain/log.md`).

If you get stuck, email `solutions@arcassystems.com` with the skill name and the error.

---

## Editor and surface compatibility

Founder OS is plain markdown plus Python and shell scripts. Anything that reads markdown can read it. Three pairings worth knowing.

### Obsidian (recommended companion editor)

Open your founder-os folder as an Obsidian vault. Everything that uses Obsidian's `[[wikilink]]` convention is honoured because the OS already speaks Obsidian's syntax.

What works:
- `[[file.md]]`, `[[file.md#anchor]]`, `[[target|alias]]` all resolve in Obsidian's graph view.
- `wiki-build` extracts the same wikilinks into `brain/relations.yaml`. Open the YAML in Obsidian as a regular note. Nothing breaks.
- Frontmatter (the `---` blocks at the top of brain entries, knowledge files, raw sources) parses correctly in Obsidian's properties panel.
- Obsidian's backlinks pane gives you the inverse view of what the lint skill audits.

What does not work:
- Obsidian does not run skills, hooks, or slash commands. Use it as a viewer / editor, not an OS surface.
- Obsidian's auto-rename of wikilinks on file move can race with `wiki-build` if both run at the same time. Run wiki-build after Obsidian-driven renames, not during.

Setup: Obsidian → Open folder as vault → point at your founder-os install. The `.obsidian/` config folder it creates is gitignored.

#### Bare-slug ambiguity

If the same bare slug matches multiple files (e.g. `[[index]]` matching `brain/index.md`, `network/index.md`, and `roles/index.md`), Obsidian prompts you to pick at link-creation time. The lint skill (`/founder-os:lint`) flags ambiguous slugs, names every candidate, and names the deterministic pick.

The pick rule: scan directories in the order declared in `scripts/wiki-build.py:INCLUDE_PREFIXES` (`core/`, `context/`, `cadence/`, `brain/`, `network/`, `companies/`, `roles/`, `rules/`), then alphabetical within the first matching directory. First match wins. So `[[index]]` resolves to `brain/index.md` because `brain/` comes before `network/` and `roles/` in `INCLUDE_PREFIXES`. Disambiguate explicitly by writing the path form: `[[brain/index.md]]`.

#### Day-0 expectations

When you first open the founder-os folder as an Obsidian vault, the graph view will be empty. Every seeded file is an isolated node by design. The wikilink convention is forward-only: existing template files are not retrofitted with cross-references. The graph fills in as you write `[[wikilinks]]` between files (a flag references a decision, a meeting note references a client, a knowledge note references a pattern). Run `/founder-os:wiki-build` after a session that added cross-references to refresh `brain/relations.yaml`.

### Claude Cowork (Anthropic's desktop knowledge-work surface)

Cowork is Anthropic's desktop agent for non-coding work. It can open local folders, read markdown, run MCPs, and execute scheduled tasks. Pair it with FounderOS for knowledge-work execution while keeping Claude Code as the OS layer.

What works in Cowork:
- Reading the file tree, CLAUDE.md as context (manually attached or via Cowork's "Folder instructions").
- MCP connectors at the account level.
- Scheduled tasks via `/schedule`.
- Markdown reads and writes.

What does not work in Cowork (yet):
- SessionStart and Stop hooks. The session-start-brief and revenue-loop check do not fire.
- Custom slash commands from `.claude/commands/`. The plugin marketplace tags plugins per-surface, and FounderOS is not yet tagged "Works with: Cowork."
- The fabric trio (`/today`, `/pre-meeting`, `/capture-meeting`) and the `/founder-os:*` namespace.

Recommended pattern: use Cowork for execution work (drafting, scheduled briefs, file ops) pointed at the FounderOS folder. Keep Claude Code in terminal for any commit, ship, hook-driven, or cadence-refresh work. Track the [plugins directory](https://claude.com/plugins) for when FounderOS gains a "Works with: Cowork" tag.

### claude-mem (complementary tool-call telemetry)

[claude-mem](https://github.com/thedotmack/claude-mem) is a separate Claude Code plugin that auto-captures tool calls into a SQLite + vector store and re-injects relevant context on session start. Different problem from FounderOS:

- claude-mem captures *tool-call telemetry* (what files did I touch, what commands ran).
- FounderOS curates *founder thinking* (decisions, clients, voice rants, behavioural guards).

You can install both on the same machine without conflict. claude-mem runs a Bun-managed worker on port 37777. FounderOS is plain markdown with no daemon. Audit claude-mem's `<private>` tag usage before installing in client repos - it ships private tool-call telemetry to its worker by default.

Note: claude-mem is AGPL-3.0. We cannot vendor any of its code into FounderOS without licensing the public repo AGPL.

---

## Surface compatibility table

| Surface | Reads markdown | Skills | Slash commands | Hooks | MCPs | Auto-memory |
|---|---|---|---|---|---|---|
| Claude Code (terminal) | Yes | Yes | Yes | Yes | Yes | `~/.claude/projects/<slug>/memory/MEMORY.md` |
| Claude Cowork (desktop) | Yes | Partial | Partial | No | Yes (account-level) | Separate Cowork memory, not shared with Claude Code |
| Obsidian | Yes (viewer) | No | No | No | No | No |
| claude-mem | Reads via tool-call telemetry only | No (separate plugin) | No | Yes (own hooks) | Yes (own MCP server) | Own SQLite + Chroma store |

Use Claude Code as the OS layer. Use Obsidian as the viewer. Use Cowork for desktop knowledge-work pointed at the same folder. Add claude-mem if you want tool-call telemetry on top.
