# Tools and MCPs

Founder OS does not assume your stack. The OS is a set of files and skills. Each skill declares which Model Context Protocol (MCP) servers it can use, and degrades gracefully when those MCPs are not available.

You connect only the MCPs you actually need. A founder with zero MCPs can still complete setup and run most of the 24 skills end-to-end.

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
| Design and decks | Canva MCP, Gamma MCP | None - skill produces text spec | (future creative-deck-style skills) | No - v1.2 has no deck skills |
| Code repos | GitHub MCP | None - if no GitHub, skip | (future build-related skills) | No |
| Database | Supabase MCP | None | (advanced users only) | No |
| Web research | Web search (built-in) | None | strategic-analysis, knowledge-capture | No - usually built into Claude Code |

---

## What works with zero MCPs

If you install Founder OS and add no MCPs, all of these skills work end-to-end on your local files:

- founder-os-setup
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
- founder-coaching
- unit-economics
- content-repurposer
- strategic-analysis (without web search, less useful but still runs)
- pre-send-check
- sop-writer
- business-context-loader
- readiness-check (`/founder-os:status`)

That is 20 of the 24 skills. The remaining four (`email-drafter`, `meeting-prep`, `knowledge-capture`, `session-handoff`) function without MCPs but produce noticeably better output with the relevant integration connected.

---

## What unlocks with each MCP

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
- For advanced founders who want to wire database state into the OS. Not needed for v1.2 default skills.

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
