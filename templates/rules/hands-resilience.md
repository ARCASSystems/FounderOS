---
why: "A tool the OS depends on will die without warning - an integration drops, an auth expires, a connector stops appearing in the session. Without a written fallback the work stops and nobody notices until the value is already lost. This names every hand the OS leans on, what breaks when it dies, and the ladder that keeps the work moving."
---

# Hands resilience - your tools, and what happens when one dies

Your brain is the asset. The mouths and hands around it swap out. This file is the hands half: which outside tools your OS depends on, what each one is for, what breaks when it stops working, and the fallback ladder that keeps the work moving without paying for anything new.

Write this file once, then update the registry when something actually breaks. A dead recorder is an outage, not weather.

## The fallback ladder (every critical hand has one, in this order)

1. **The integration** - the normal path. An MCP connector, an app link.
2. **A command line tool or a local script** - same job, no integration.
3. **Export or paste** - the vendor's own export, or you paste it into the OS by hand. This is a first-class path, not an apology. Most outages are survived here.
4. **Manual capture** - a voice note to yourself, a photo of a whiteboard, paper. Whatever works in the room you are standing in.

Two laws sit on top of the ladder.

**Every failure gets written down the same day.** Log it in `system/quarantine.md`. Silent failures compound for weeks. A session that finds a critical hand missing writes the entry before working around it, not after.

**Preflight before any work that depends on a tool.** Before a meeting you are counting on the recorder for, before a send you are counting on the mail integration for, check the tool is actually there and say which fallback you will use if it is not. Finding out mid-meeting is the failure. Finding out at minute zero is a plan.

## Being honest about proxies

You can only build a proxy where an export or an API exists. Where the vendor gives you neither, the free proxy IS the export-and-paste rung plus a second tool covering the same event. Where a free API or command line tool exists, the proxy is a small script in `scripts/`.

Whether to build a proxy at all is the same test as any capability: something that saves you minutes every week is worth building. Something that covers a tool failing twice a year is not.

## Your hands registry

Fill this in with the tools you actually run. Tier CRITICAL if a capture path or a recurring job depends on it, SUPPORT if the work continues without it.

The Verified column is evidence, not memory: a live check, a run that worked, a tool showing up in the session, with the date you saw it. Never write "working" because it worked last month.

| Hand | Job in your OS | Tier | Fallback ladder | Verified state |
|---|---|---|---|---|
| `{meeting_recorder}` | Meeting capture and transcripts | CRITICAL | second recorder, then export/paste into `capture/inbox/`, then a voice note | (not yet checked) |
| `{email_platform}` | Inbox reading and drafts | CRITICAL | the web client plus paste into `/log-reply` | (not yet checked) |
| `{calendar}` | Schedule and reminders | CRITICAL | the web client, entered by hand | (not yet checked) |
| `{knowledge_base}` | Mirrors and registries | SUPPORT | your markdown files are the source of truth, the mirror can wait | (not yet checked) |
| `{comms_tool}` | Team and client messages | SUPPORT | paste the thread into `/log-reply` | (not yet checked) |
| `{automation_platform}` | Jobs that fire while you sleep | SUPPORT | run it by hand at your desk | (not yet checked) |
| `{crm}` | Pipeline data | SUPPORT | `context/clients.md` is the source of truth | (not yet checked) |

Add a row when you connect a tool. Keep rows for tools you dropped, with a date and a one-line why, so the history stays readable.

## Keeping it true

- **A Verified cell needs evidence with a date.** The tool answered a live call, or a job it runs produced a record. Not a memory, not an assumption.
- **Check the CRITICAL rows when something feels wrong.** If a capture did not land or a send did not go, read this table first. The answer is usually a dead hand, not a bug.
- **Re-authorizing is always your job.** Login flows need a human. The OS's job is to say clearly that a hand is down and name what still works meanwhile.

## The line that makes this worth keeping

When a tool dies, the question is never "is it broken". It is "what do I do in the next ten minutes". This file answers that in advance, once, so you are not solving it during the meeting you are trying to capture.
