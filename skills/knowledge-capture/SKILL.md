---
name: knowledge-capture
description: >
  Captures and structures knowledge from books, podcasts, conversations, conferences, articles, and experiences. Use this skill when the user says "capture notes from", "what I learned from", "book notes for", "takeaways from", "save this insight", "I just read", "I just listened to", "key points from", or any variation of knowledge capture and learning extraction. Also trigger when the user shares raw notes or highlights and wants them organized.
mcp_requirements: [optional: notion]
---

# Knowledge Capture - Learning System

You help the founder capture, structure, and connect what they learn.

## Storage Convention

Every captured knowledge piece writes to `brain/knowledge/<topic-slug>.md`. If the file exists, append a dated section. If it does not exist, create it with frontmatter. Every new knowledge file gets a stable ID per `rules/entry-conventions.md` (channel: `know`).

```yaml
---
id: know-YYYY-MM-DD-NNN
topic: <slug>
captured: <YYYY-MM-DD>
sources: [source title or URL]
tags: [book, podcast, article, conversation, experiment]
---

# <Topic>

## Takeaways

- <point>

## How this applies to my work

- <application>
```

Also update `brain/knowledge/README.md` index table with one row. The columns are fixed:

```
| ID | Topic | Captured | Tags | Source |
|---|---|---|---|---|
| know-YYYY-MM-DD-NNN | <slug> | <YYYY-MM-DD> | <comma-separated tags> | <source title or URL> |
```

Insert the new row directly under the header. Do not invent additional columns. Ask for a topic slug if it is not obvious from the source title.

Use `raw/` only when preserving the full source matters. Use `brain/knowledge/` for distilled notes that future skills should read.

## ID Stamping

Every new knowledge file gets a stable ID at write time. Convention spec: `rules/entry-conventions.md`.

### Procedure (run before creating any new knowledge file)

1. Compute today's date in `YYYY-MM-DD`.
2. Read every existing file under `brain/knowledge/` plus the `README.md` index. Find every ID that matches `know-<today>-<NNN>`.
3. Take the highest `<NNN>`. If none exist for today, start at `001` (the first ID of the day for this channel) and skip to step 5.
4. Increment by 1. Format as 3-digit zero-padded.
5. The result is the new file's ID. Stamp it in the file's frontmatter and in the index row.

### Counter rules

- Per channel, per day. Resets to `001` each new day.
- IDs are stamped at write time, never retroactively.
- IDs are case-sensitive lowercase only.
- If a knowledge file already exists and you are appending a new dated section to it, do not change the file's existing ID. The ID belongs to the file, not to each appended section.

## Book / Long-Form Content

```
BOOK: [Title]
Author: [Name]
Date captured: [Date]

---

CORE THESIS
[One paragraph. What is this book really saying?]

KEY IDEAS
1. [Idea] - [Why it matters to the founder's work]
2. [Idea] - [Why it matters]
3. [Idea] - [Why it matters]

QUOTES WORTH KEEPING
- "[Quote]" (p. XX)

DISAGREE / QUESTION
[Anything that didn't land or needs more thinking]

APPLY TO
-> Business: [How this connects to the company or model]
-> Clients: [How this helps in client conversations]
-> Content: [Could this become a post, video, or playbook chapter?]
-> Personal: [Does this change how you work or lead?]
```

## Podcast / Talk / Conversation

```
SOURCE: [Podcast name / Speaker / Event]
Date: [Date]

---

KEY TAKEAWAYS
1. [Takeaway]
2. [Takeaway]

MEMORABLE MOMENTS
- [Something that stood out]

APPLY TO
-> [Same structure as book notes]
```

## Quick Insight Capture

```
INSIGHT: [Date]
[The insight in one to three sentences]

TRIGGERED BY: [What prompted this]

CONNECTS TO: [Existing work, a project, a content idea]
```

## Connection Mapping

Always ask:
- Does this challenge something the founder currently believes?
- Does this support or challenge the current business model?
- Could this become a playbook chapter or framework?
- Would a specific client benefit from hearing this?
- Is there a content opportunity here?

## Formatting

- Simple hyphens (-) not em or en dashes
- Arrows (->) for application mapping
- Quotes in quotation marks with page numbers when available
