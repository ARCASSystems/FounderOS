---
name: where
description: Find work you cannot find. Say "where is my work", "where did that go", "where did you save it", "I cannot find the supplier list", "what have I been working on", or run /founder-os:where. Answers with the project and the folder in your own words, not a list of paths, and says plainly whether a second copy of it exists anywhere. Also names the folders that would be gone tomorrow if this laptop died.
why: "A founder said: I have been on three different chats for this project but somehow it is nowhere to be found, it does things and saves somewhere else. Nothing was lost - the work sat in a folder git had been told to ignore, so it appeared in no status, no backup, and no answer she could use. When she asked where it went she got a wall of paths back and said she could not understand any of it. Losing track of your own work is the fastest way to stop trusting a system, and the answer has to be readable by the person asking."
enhance: "Ask it the moment something feels missing rather than opening three chats to look. It is read-only, costs nothing, and it names unbacked-up folders even when you did not ask - that is usually the more urgent finding."
allowed-tools: ["Read", "Glob", "Bash(python scripts/where.py:*)"]
---

# Where is my work

Runs on: local-exec - it runs one read-only script over your own folder. Nothing is opened, moved, renamed, or deleted, ever.

## When this fires

Any version of "I cannot find it". The words are rarely "where is my work" - they are "where did that go", "you saved it somewhere else", "I have been through four chats and it is nowhere", "what happened to the vendor list". Treat all of it as this skill.

Also fire it, without being asked, when the founder says work has gone missing and you are about to explain how the folder structure works. That explanation is the failure, not the fix.

## Step 1 - run the scan

```
python scripts/where.py --days 14
```

Widen with `--days 60` or `--all` if the first pass finds nothing they recognise. Use `--json` if you need to reason over the result rather than read it.

If the script is missing (an install that predates it), fall back to `Glob` over the root for recently modified files and answer in the same shape below. Never skip the answer because the tool is absent.

## Step 2 - answer in their words, not the file system's

The script's output is already close to shippable. Your job is to turn it into two or three sentences a person can act on, leading with the thing they asked about.

**The shape that works:**

> The supplier work for the March event is in `Events/march-pitch/` - 12 files, last touched today. The supplier longlist and the tracker are both in there.
>
> One thing worth knowing: that folder has no backup. It exists on this laptop and nowhere else.

**The shape that failed a real person:**

> This isn't in your OS at all - it's in a separate project folder sitting inside your directory but deliberately excluded from it, git-tracked to a different remote. Three pieces: benchmarking research, inspiration research, and the project brief. The actual chat transcripts can't be retrieved...

Both are true. Only one is usable. Rules that keep you in the first shape:

- **Lead with the work, not the location.** "The supplier list is in X" beats "X contains the vendor list".
- **One folder per thing they asked about.** If work is genuinely in two places, say "two places" and name both in one line each. Never a table.
- **No layer names.** Never "System Layer", "User Layer", "the install root", "gitignored", "untracked", "the remote". These are true and they are not English.
- **Say what you cannot do, once and briefly.** If they ask for the chat history rather than the files, the honest line is: "I can find the files. The conversations themselves are in the assistant's own history on whichever machine ran them, and I have no way to reach into that." One sentence, then back to what you did find.
- **Never end on a list of options.** Ask one question or state one next step.

## Step 3 - the backup line is not optional

If the scan reports any folder as NOT BACKED UP, say so even when they did not ask, and say it in the second person: "this exists only on this computer". A founder who does not know that cannot decide to fix it. This is the one line to volunteer.

Then offer the fix in one sentence: `own-your-history` turns an install with no version history into one with full undo and a second copy, on a single yes. Do not run it here, and do not turn a "where is it" question into an install project. Offer it and move on.

If everything is backed up, say that in four words and stop.

## Step 4 - offer to open it, do not lecture

Close with the smallest useful action:

> Want me to open that folder?

On a yes, open it with the platform command (`explorer` on Windows, `open` on macOS, `xdg-open` on Linux). If you cannot, give the full path on its own line so it can be pasted into Explorer or Finder, and say that is what it is for.

## What this skill never does

- Never moves, renames, consolidates, or "tidies" anything it found. A founder asking where something is has not asked you to reorganize it, and a reorganization is the one action that makes the next search harder.
- Never proposes a folder restructure in the same breath as the answer. If the layout is genuinely a problem, say so in one line and let them raise it.
- Never claims work is lost. Work that is not in the scan is work outside this folder, which is a different sentence: "not in your OS folder - it may be in another project directory, and I can only see this one."

## Rules

- Read-only. No writes, no moves, no opens without a yes.
- Plain language. Writing rules apply, and the register bar here is higher than anywhere else in the OS: assume the person asking is frustrated and is not a developer.
- No em dashes. Hyphens with spaces.
