---
description: Query the OS for a topic. Say "find the file about [topic]" or "search my OS for [topic]" (or run /founder-os:query <question>). Three modes (index, timeline, full) for progressive disclosure. Read-only.
argument-hint: <question> | --mode timeline --anchor <slug> | --mode full --ids <id1,id2>
allowed-tools: ["Read", "Bash"]
---

# Founder OS query

Run the query skill at `skills/query/SKILL.md` end to end.

## Procedure

1. If `$ARGUMENTS` is empty, reply `What should I query? Re-run as /founder-os:query <question>.` and stop.
2. If `core/identity.md` does not exist, reply `Founder OS not set up here. Say "set up Founder OS" first.` and stop.
3. If `skills/query/SKILL.md` is missing, reply `Query skill not found at skills/query/SKILL.md. Restarting Claude Code fixes this most of the time, because it reloads what is installed. If it happens again after a restart, say "update Founder OS".` and stop.
4. If `scripts/query.py` exists, invoke it via the **Bash** tool using the quoted-block form below so user input is never read as shell code. The user's `$ARGUMENTS` may contain an apostrophe, `;`, `|`, backticks, or `$(...)`. Inside single quotes an apostrophe ends the string and whatever follows runs, so never put the question inside quotes on the command line.

   **Plain question (no `--` flags in `$ARGUMENTS`):** put the question on its own line between the two marker lines, exactly as the user wrote it, with nothing escaped. The quoted marker (`'FOUNDER_OS_Q_END'`) makes bash read every character in between as plain text. Run it exactly as shown, every line starting at the left edge with no spaces in front, or bash will not see the end marker:

```bash
python scripts/query.py "$(cat <<'FOUNDER_OS_Q_END'
__QUESTION__
FOUNDER_OS_Q_END
)"
```

   If the question itself contains a line that reads exactly `FOUNDER_OS_Q_END`, reply `Refusing to forward that question as written. Rephrase it without the line FOUNDER_OS_Q_END.` and stop.

   **Argument string contains flags (`--mode`, `--ids`, `--anchor`, `--root`, `--from`, `--to`):** split the user's argument string on whitespace. Each flag, and the value right after it, must match this pattern in full, every character and not only the first: `^[A-Za-z0-9_./,:=-]+$`. Bash reads each of those characters as plain text, so a checked token cannot run anything. If a flag or its value has any other character (an apostrophe, `<`, `(`, `$`, `{`, `~`, `*`, `?`, `;`, `|`, `&`, `>` or a backtick), reply `Refusing to forward potentially unsafe argument token: <token>` and stop. Write the checked tokens after `python scripts/query.py`, separated by single spaces, for example `python scripts/query.py --mode timeline --anchor log-2026-05-07-001`. Anything left over that is not a flag or its value is the question: pass it through the quoted block above, after the flags, never as bare words.

   If neither form fits, stop and reply: `Could not parse arguments safely. Re-run as /founder-os:query "<your question>" or with explicit flags.`

The underlying script also accepts `--root <path>` for direct CLI use. The flag and its path go before the quoted block, and the path follows the same pattern.

5. Print stdout verbatim. If the script exits non-zero, print stderr and stop.
6. If the script is missing, follow the manual procedure in the skill file.

## Forms

- `/founder-os:query <question>` - default `index` mode. Returns ~10 candidate nodes with IDs.
- `/founder-os:query --mode timeline --anchor <slug-or-id>` - returns entries within 7 days either side of the anchor, ordered chronologically.
- `/founder-os:query --mode full --ids <id1,id2,...>` - returns full bodies for the listed IDs.

Examples:

- `/founder-os:query outreach stalled`
- `/founder-os:query --mode timeline --anchor brain/flags.md`
- `/founder-os:query --mode timeline --anchor log-2026-05-07-001`
- `/founder-os:query --mode full --ids log-2026-05-07-001,log-2026-05-07-002`

## Progressive Flow

Recommended for any non-trivial question:

1. Start with `index` to see candidate nodes.
2. Pick one and run `timeline` anchored on it for surrounding context.
3. Pull specific IDs with `full` to read bodies end to end.

## Rules

- Read-only.
- No external dependencies.
- No em dashes or en dashes.
- No banned words.
