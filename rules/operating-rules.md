# Operating Rules

Behavioral rules for Founder OS. These supplement the skill bodies and apply across all writing-side operations.

---

## `<private>` exclusion tag

Any text wrapped in `<private>...</private>` is excluded from all persistent writes. This applies to:

- `brain/log.md` (the brain-log skill)
- `brain/rants/*.md` (the rant command - wrapped content is dropped before the file is written)
- `brain/patterns.md`, `brain/flags.md`, `brain/decisions-parked.md` (the dream command - distilled content from rant processing)
- `brain/knowledge/*.md` (the knowledge-capture skill)
- Auto-memory `MEMORY.md` (the auto-memory write path)
- Any future skill that writes to a persistent file the user did not explicitly request a write to

The tag does not apply to ephemeral context - text the model holds in-conversation but does not persist.

The tag is case-insensitive: `<PRIVATE>`, `<Private>`, `<private>` all work. The closing tag must match the opening tag case-insensitively.

### Why this exists

The user may share context in a rant, log entry, or knowledge capture that is useful in the moment but should not survive the session. The `<private>` tag gives a lightweight way to mark that content without having to split it into a separate message.

### How the filter runs

Each writing skill or command that persists user content must run this check before writing:

1. Scan the source text for `<private>...</private>` blocks (case-insensitive regex).
2. Remove every matched block, including the opening and closing tags, from the text.
3. Trim leading and trailing whitespace from the result.
4. If the entire input is wrapped in `<private>` (nothing remains after removal), write nothing and report: "skipped - content was tagged private."
5. Write the cleaned text.

The user is not notified of the filter step unless the entire input was private.
