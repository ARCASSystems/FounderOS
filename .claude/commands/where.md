---
description: Find work you cannot find. Say "where is my work", "where did that go", "where did you save it", or run /founder-os:where. Answers with the project and folder in your own words instead of a list of paths, says plainly whether a second copy exists anywhere, and names any folder that would be gone tomorrow if this laptop died. Read-only - it opens nothing and moves nothing.
argument-hint: "[what you are looking for]"
---

Run the `where` skill.

Looking for: $ARGUMENTS

Run `python scripts/where.py --days 14` first, passing their words through a quoted block so nothing they typed is read as shell code (an apostrophe, `;`, backticks or `$(...)` would otherwise run):

```bash
python scripts/where.py --days 14 "$(cat <<'FOUNDER_OS_W_END'
<their words, exactly as written, on this one line>
FOUNDER_OS_W_END
)"
```

Every line starts at the left edge with no spaces in front. If their words have a line that reads exactly `FOUNDER_OS_W_END`, reply `Refusing to forward that as written. Say it again without the line FOUNDER_OS_W_END.` and stop.

With no words, run `python scripts/where.py --days 14` alone. The words they gave you surface matching folders first; then answer in two or three plain sentences leading with the work, not the location. Widen the window if nothing looks familiar. If any folder comes back NOT BACKED UP, say so even though they did not ask - that is the more urgent finding. Close by offering to open the folder; on a yes, open it with `python scripts/open_folder.py` and the folder from the scan passed through the same kind of quoted block (a folder name can hold an apostrophe, a backtick or `$(...)`), never with a raw explorer / open / xdg-open command:

```bash
python scripts/open_folder.py "$(cat <<'FOUNDER_OS_F_END'
<folder from the scan>
FOUNDER_OS_F_END
)"
```

If the folder name has a line that reads exactly `FOUNDER_OS_F_END`, do not run it. Give the full path on its own line instead.

Never explain the folder architecture to someone who has just told you they cannot find their work.
