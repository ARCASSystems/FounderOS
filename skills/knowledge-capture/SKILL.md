---
name: knowledge-capture
description: >
  Captures and structures knowledge from books, podcasts, conversations, conferences, articles, and experiences. Use this skill when the user says "capture notes from", "what I learned from", "book notes for", "takeaways from", "save this insight", "I just read", "I just listened to", "key points from", or any variation of knowledge capture and learning extraction. Also trigger when the user shares raw notes or highlights and wants them organized.
mcp_requirements: [optional: notion]
---

# Knowledge Capture - Learning System

You help the founder capture, structure, and connect what they learn.

## Storage Convention

Every captured knowledge piece writes to `brain/knowledge/<topic-slug>.md`. If the file exists, append a dated section. If it does not exist, create it with frontmatter:

```yaml
---
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
| Topic | Captured | Tags | Source |
|---|---|---|---|
| <slug> | <YYYY-MM-DD> | <comma-separated tags> | <source title or URL> |
```

Insert the new row directly under the header. Do not invent additional columns. Ask for a topic slug if it is not obvious from the source title.

Use `raw/` only when preserving the full source matters. Use `brain/knowledge/` for distilled notes that future skills should read.

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
