# Brain Log

> Running log of what happens. Cap: 300 lines. When full, archive to `archive/log-[YYYY-MM].md` and start fresh.
> Use three modes: `#context` (log and move), `#xref:[target]` (log and connect), `#acted` (log and confirm action taken).
> Most recent entries at the top. Every new entry gets a stable ID per `rules/entry-conventions.md` (channel: `log`).

Revenue loop: every outreach action must log here with `#acted [S]` AND update `context/clients.md` in the same session. The session-close hook warns if outreach signals appear here without a matching client update.

## Format

Each entry carries an ID line. The ID is `log-<YYYY-MM-DD>-<NNN>` where NNN is a per-day counter starting at 001. The trailing-parenthetical form on the heading is the canonical fallback for one-line entries.

```
### [YYYY-MM-DD] #[tag] [entry] (log-YYYY-MM-DD-NNN)
```

For multi-line entries, put the ID on its own frontmatter line under the heading:

```
### [YYYY-MM-DD] #[tag] [short title]
id: log-YYYY-MM-DD-NNN
[body of the entry]
```

---

<!-- Examples (delete once you have your first three real entries):

### [YYYY-MM-DD] #context Closed week with three meetings booked for next week. (log-YYYY-MM-DD-001)

### [YYYY-MM-DD] #xref:decisions Reviewed pricing options for the diagnostic tier. Routed to context/decisions.md as an open decision pending margin model. (log-YYYY-MM-DD-002)

### [YYYY-MM-DD] #acted [S] Sent proposal to <Prospect>. Updated context/clients.md row with status "proposal sent" and follow-up date. (log-YYYY-MM-DD-003)

-->
