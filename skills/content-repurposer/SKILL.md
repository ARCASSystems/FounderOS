---
name: content-repurposer
description: >
  Reformat one piece of content across many channels. Trigger on "repurpose this", "turn this into", "adapt this for", "convert this to", "make versions of this for", or any variation. Also fires when the user shares content and wants it reformatted for different platforms. Works across LinkedIn, YouTube, Instagram, email newsletters, website copy, Twitter/X, and internal docs. Reads `core/voice-profile.yml` and applies the founder's voice.
mcp_requirements: []
---

# Content Repurposer

You take one piece of content and transform it for multiple channels while keeping the founder's voice consistent. Apply the voice and writing rules from `core/identity.md`, `rules/writing-style.md`, and `core/voice-profile.yml` (via the `your-voice` skill) to all output.

## Voice profile

Before writing, run: `python scripts/check-voice-ready.py`

If exit code is 1, read the output line and surface it to the user verbatim. Do not produce any draft. Stop.

If the user explicitly chooses to proceed with defaults after seeing that message, repurpose the content using the universal anti-AI baseline from `your-voice` and clearly label that the voice profile was not applied. Do not pretend the outputs are voice-coupled.

Then read `core/voice-profile.yml` so the rest of this skill can apply it.

After producing a draft and before returning it, run the anti-examples filter:

1. Read the `anti_examples.pairs` block in `core/voice-profile.yml`.
2. For each line in your draft, scan for matches against any `bad:` pattern (literal substrings, structural markers like negation-contrast, or rule-of-three lists).
3. If a line matches, rewrite it using the `good:` pattern as the model and the `rule:` line as the constraint.
4. Also reject any line that uses an `aesthetic_crimes` phrase or a `red_flags` pattern.
5. Return the cleaned draft.

Do not surface this filter to the user as a separate step. The user sees only the cleaned draft.

## Runtime context

Before drafting, read `brain/.snapshot.md` if it exists. Use the open-flags block to avoid topics that contradict current operator stance. Use the must-do block to lean the draft toward what the operator is actively working on. Use the voice and brand blocks (if present) to set tone. If `brain/.snapshot.md` does not exist, proceed without it - the snapshot is optional context, not a hard prerequisite.

## How It Works

1. Read the source content
2. Identify the core insight (what's the ONE thing this is really about?)
3. Identify supporting stories, data points, and examples
4. Adapt for each requested channel

## Channel Specifications

### LinkedIn Post
- 100-300 words, line breaks between thoughts, hook first, no hashtags, arrows for lists

### YouTube Script
- 3-5 minutes, conversational, Hook/Story/Framework/Takeaway, [B-ROLL] markers

### Instagram Caption
- 50-150 words, scroll-stopper first line, short lines, no hashtags

### Email Newsletter
- 200-500 words, lead with the point, one insight, casual direct tone

### Twitter/X Thread
- 3-7 tweets, first tweet standalone value, one idea per tweet

### Website Copy
- Clear hierarchy, scannable, SEO-aware not SEO-driven

### Internal Doc / SOP
- Clear, direct, industry terms when they serve clarity, anti-AI check relaxed

## Repurposing Rules

1. **Don't just shorten.** Each platform has a different angle.
2. **Preserve the core insight.** It should survive every adaptation.
3. **Match the energy.** LinkedIn = thought leadership. Instagram = personal. YouTube = teaching. Email = intimate.
4. **Don't repeat yourself across channels.** Find a different angle for each.
5. **Apply the founder's voice to every output.** Run anti-AI self-check on public content.

## Output Format

```
SOURCE: [Brief description of original content]
CORE INSIGHT: [One sentence]
---
LINKEDIN POST
[content]
---
YOUTUBE SCRIPT
[content]
---
INSTAGRAM CAPTION
[content]
```
