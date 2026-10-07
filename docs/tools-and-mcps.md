# Tools, MCPs, and surfaces

Founder OS does not assume your stack. The OS is a set of files and skills. Each skill declares which Model Context Protocol (MCP) servers it can use, and degrades gracefully when those MCPs are not available.

You connect only the MCPs you actually need. A founder with zero MCPs can still complete setup and run most of the 97 skills end-to-end. The four skills that produce noticeably better output with the relevant MCP connected are `email-drafter`, `meeting-prep`, `knowledge-capture`, and `session-handoff`. They still function without one, but with reduced context.

This doc covers three things: which MCPs activate which skills, which editors and surfaces (Obsidian, Claude Cowork, claude-mem) pair well with the OS, and what works under each surface.

---

## What is an MCP?

An MCP (Model Context Protocol) server is an integration that lets Claude Code talk to an external tool - your email, calendar, Notion, Apollo, Supabase, and so on. MCPs are set up outside Founder OS, in one of two places. The easier one for most founders: connect Gmail, Google Calendar or Drive once as a connector on your claude.ai account. When you sign in to Claude Code with that same account, those connectors are available there too. Or add an MCP server to Claude Code itself, once, and any project can use it.

Anthropic's guide to both: [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp).

---

## Capability catalog

| Capability | Recommended MCP | Alternatives | Skills that use it | Required for launch? |
|---|---|---|---|---|
| Email | Gmail MCP | Outlook MCP, manual paste | email-drafter, capture-meeting | No - works without |
| Calendar | Google Calendar MCP | Outlook MCP, manual paste | meeting-prep, /today | No - degrades to "no calendar event" line |
| Knowledge base | Notion MCP | Local markdown, Obsidian | knowledge-capture, session-handoff | No - skills work locally without it |
| Sales / CRM | Apollo MCP | HubSpot MCP, manual entry | proposal-writer (pricing context only) | No |
| Design and decks | Canva MCP, Gamma MCP | None - skill produces text spec | pitch-deck (uses no MCP. Its markdown spec pastes into Canva or Gamma, or renders to `.pptx` with `python-pptx`) | No |
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

Four skills in particular (`email-drafter`, `meeting-prep`, `knowledge-capture`, `session-handoff`) function without MCPs but produce noticeably better output with the relevant integration connected.

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

Most skills in `skills/` carry a `mcp_requirements:` field in their frontmatter:

- `mcp_requirements: []` - works with no MCPs.
- `mcp_requirements: [optional: gmail, optional: gcal]` - degrades gracefully if the MCP is missing.
- `mcp_requirements: [required: notion]` - hard-fails without the named MCP, with a friendly message.

If you add a third-party skill or build your own, follow the same convention so the readiness check (`/founder-os:status`) can report what's wired up correctly.

---

## When something doesn't work

If a skill says it needs an MCP you don't have, it will tell you. Two options:

1. **Install the MCP.** Connect it once as a connector on your claude.ai account, or see [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp) to add it to Claude Code directly.
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

Going the other direction - installing FounderOS into a vault you already have - is the adopt path: setup moves the OS in next to your notes and never touches an existing file. See [adopt-existing-notes.md](adopt-existing-notes.md).

#### Bare-slug ambiguity

If the same bare slug matches multiple files (e.g. `[[index]]` matching `brain/index.md`, `network/index.md`, and `roles/index.md`), Obsidian prompts you to pick at link-creation time. The lint skill (`/founder-os:lint`) flags ambiguous slugs, names every candidate, and names the deterministic pick.

The pick rule: scan directories in the order declared in `scripts/_common.py:WIKI_LAYER_PREFIXES` (`core/`, `context/`, `cadence/`, `brain/`, `network/`, `companies/`, `roles/`, `rules/`), then alphabetical within the first matching directory. First match wins. So `[[index]]` resolves to `brain/index.md` because `brain/` comes before `network/` and `roles/` in `WIKI_LAYER_PREFIXES`. Disambiguate explicitly by writing the path form: `[[brain/index.md]]`.

#### Day-0 expectations

When you first open the founder-os folder as an Obsidian vault, the graph view will be empty. Every seeded file is an isolated node by design. The wikilink convention is forward-only: existing template files are not retrofitted with cross-references. The graph fills in as you write `[[wikilinks]]` between files (a flag references a decision, a meeting note references a client, a knowledge note references a pattern). Run `/founder-os:wiki-build` after a session that added cross-references to refresh `brain/relations.yaml`.

### Claude Cowork (Anthropic's agent for non-coding work)

Cowork is Anthropic's agent for knowledge work. From 16 September 2026 it has been merging into the main Claude app alongside chat, Pro and Max plans first. It reads the connectors, skills and plugins on your claude.ai account, not your local `~/.claude` folder.

What changes on 6 October 2026, on Pro and Max plans:
- New Cowork tasks run in Anthropic's cloud. A cloud task reaches a folder on your computer only while the Claude desktop app is open and connected to it.
- Anthropic's help pages disagree on scheduled tasks. One says they cannot be tied to a folder on your computer, another says a task that uses local files needs the desktop app open. Either way, a timed job that needs your OS folder is safer in Claude Code.

What Cowork loads from a plugin on your claude.ai account, per Anthropic's plugin docs: skills, commands (run as `/plugin-name:command`), agents and hooks. Founder OS keeps its hooks in the folder's own settings, not in the plugin, and adding Founder OS to a claude.ai account is not yet tested. Whether Cowork reads a connected folder's own hooks is not yet tested either.

Recommended pattern: use Cowork for drafting against the FounderOS folder while the desktop app is open. Keep Claude Code for anything hook-driven, on a timer, saved, or cadence-related.

### claude-mem (complementary tool-call telemetry)

[claude-mem](https://github.com/thedotmack/claude-mem) is a separate Claude Code plugin that auto-captures tool calls into a SQLite + vector store and re-injects relevant context on session start. Different problem from FounderOS:

- claude-mem captures *tool-call telemetry* (what files did I touch, what commands ran).
- FounderOS curates *founder thinking* (decisions, clients, voice rants, behavioural guards).

You can install both on the same machine without conflict. claude-mem runs a Bun-managed local worker, on a port you can configure. FounderOS is plain markdown with no daemon. Audit claude-mem's `<private>` tag usage before installing in client repos - it ships private tool-call telemetry to its worker by default.

Note: claude-mem is Apache-2.0 (its GitHub page, checked 6 Oct 2026). FounderOS does not vendor it. The two stay separate tools.

---

## Surfaces and the runtime-capability matrix

What changes by surface is per-skill capability, not whether the OS works. Every skill declares its runtime class on a `Runs on:` line (see the `Runs on:` contract in `CLAUDE.md`): `reasoning` (read and reason), `local-writes` (create or edit OS files), `local-exec` (run a local script). Surfaces fall into three buckets:

- **Local Claude Code** - runs scripts, writes files, fires slash commands and hooks. That covers the terminal tool, the IDE extensions, and the Claude desktop app's Code tab with a local folder selected, which Anthropic documents as the same engine reading the same settings files. Codex and other local CLIs are covered by the bridge-file redirect (`AGENTS.md`, `GEMINI.md`).
- **Desktop folder-attached** - reads and writes the files through a connected folder. Cowork does this only while the Claude desktop app is open. Antigravity does it when opened in the folder. Folder hooks and folder commands are not yet tested on either, so do not count on them.
- **Cloud and web** - Claude Code on the web runs scripts and a repo's own hooks in Anthropic's cloud, on a GitHub copy of a repo, never on a folder that lives only on your computer. claude.ai chat loads a plugin's skills (commands arrive as skills) and never runs hooks, and a browser LLM can only read and reason over what you give it.

Only the terminal row below is validated by a real run. The other rows describe what each bucket's capability implies through the bridge-file redirect. They are covered by design, not separately tested per agent.

| Surface (bucket) | `reasoning` | `local-writes` | `local-exec` | Slash commands | Hooks |
|---|---|---|---|---|---|
| Claude Code terminal tool (local) - validated | Yes | Yes | Yes | Yes | Yes |
| Claude desktop app, Code tab, local folder - per Anthropic's docs, not yet validated by us | Yes | Yes | Yes | Yes | Yes |
| Cowork, Antigravity (desktop folder-attached) - not separately validated | Yes | Yes, through a connected folder (Cowork: only while the desktop app is open) | Depends on the surface; with no script-exec it reads the produced artifacts | Not tested - say what you want in words | Not tested - do not count on them |
| Claude Code on the web (claude.ai/code) - not separately validated | Yes | Yes, on a GitHub copy in the cloud, saved to a branch there, never your local folder | Yes, on that cloud copy | A repo's own commands | A repo's own hooks, on the cloud copy |
| claude.ai chat, browser LLM - not separately validated | Yes | No - drafts the change for you to apply | No - reads the produced artifacts and helps you act | Chat: plugin commands arrive as skills | No |

Apply the honest-degradation rule from `CLAUDE.md`: on a surface that cannot do what a skill's `Runs on:` class needs, say so in one sentence and offer the path you can do. Never claim a slash command, script run, hook, or local write happened where it did not.

**Auto-memory:** Claude Code reads `~/.claude/projects/<slug>/memory/MEMORY.md` at session start. claude.ai has its own account memory, on every plan including free since March 2026, and Cowork in the cloud shares it. Whether that account memory reaches Claude Code is not yet tested, so keep anything the OS must know in your files. Obsidian has no memory layer and only reads the files.

**Obsidian and claude-mem** are not agent surfaces. Obsidian reads and edits the markdown but runs no skills, slash commands, or hooks (see the Obsidian section above). claude-mem is a separate tool-call telemetry plugin (see above).

Use Claude Code as the OS layer. Use Obsidian as the viewer. Use Cowork or Antigravity for desktop knowledge-work pointed at the same folder. Add claude-mem if you want tool-call telemetry on top.
