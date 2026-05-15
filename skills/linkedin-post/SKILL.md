---
name: linkedin-post
description: >
  Write a LinkedIn post in the founder's voice. Trigger on "write a LinkedIn post", "draft a post", "post about this", "make this a LinkedIn post", "turn this into a post", "I want to share this on LinkedIn", or any mention of "LinkedIn" in the context of creating content. Also fires when the user shares an idea, insight, or experience and wants it shaped into a post. Covers founder stories, leadership insights, hiring perspectives, AI commentary, systems thinking, and business-related content. Reads `core/voice-profile.yml`.
allowed-tools: ["Read", "Write", "Edit"]
mcp_requirements: []
---

# LinkedIn Post

You are writing LinkedIn posts for the founder whose voice profile lives in `core/voice-profile.yml`. Every post must apply that profile. Before drafting, read `skills/your-voice/SKILL.md` and apply its universal rules in full. Then pass the LinkedIn-specific self-check at the bottom of this file.

## Before you write

Before writing, run: `python scripts/check-voice-ready.py`

If exit code is 1, read the output line and surface it to the user verbatim. Do not produce any draft. Stop.

If the user explicitly chooses to proceed with defaults after seeing that message, draft the post using the universal anti-AI baseline from `your-voice` and clearly label that the voice profile was not applied. Do not pretend the post is voice-coupled.

Then read `core/voice-profile.yml` so the rest of this skill can apply it.

After producing a draft and before returning it, run the anti-examples filter:

1. Read the `anti_examples.pairs` block in `core/voice-profile.yml`.
2. For each line in your draft, scan for matches against any `bad:` pattern (literal substrings, structural markers like negation-contrast, or rule-of-three lists).
3. If a line matches, rewrite it using the `good:` pattern as the model and the `rule:` line as the constraint.
4. Also reject any line that uses an `aesthetic_crimes` phrase or a `red_flags` pattern.
5. Return the cleaned draft.

Do not surface this filter to the user as a separate step. The user sees only the cleaned draft.

## Brain context (default)

Before producing output, read `brain/.snapshot.md` if it exists.

If `brain/.snapshot.md` does not exist: check whether `scripts/brain-snapshot.py` exists. If it does, run:

    python scripts/brain-snapshot.py --write

Then read `brain/.snapshot.md`. If neither the snapshot nor the script exists (older install), proceed using only the profile files. Do not block.

The snapshot tells you what flags are open, what the user is working on this week, and what the latest staleness state is. Apply this context to your output where it is relevant. Do not surface every snapshot field in every output - use judgment. For LinkedIn, open flags often hint at honest, post-worthy tension the founder is sitting with right now, and recent decisions are usually richer post material than abstract theory.

## Positioning and buyer language

Before drafting, also read `core/identity.md` and the `buyer_language:` block in `core/voice-profile.yml` if present.

Use `core/identity.md` `## Positioning` to understand who the founder sells to, what they sell, and the visible buyer pain. Use `buyer_language` for the buyer's actual words. If these fields exist, the post should speak to that buyer instead of a generic founder audience.

## Brain pass (auto)

Before invoking brain-pass, run: `python scripts/check-log-has-history.py`

If exit code is 1, skip brain-pass entirely and proceed directly to drafting. This prevents a fresh-install user's first post request from triggering a "no content found" search loop.

If exit code is 0, invoke the `brain-pass` skill (`skills/brain-pass/SKILL.md`) with this question:

> What has the user posted on LinkedIn recently? What themes are stale? What recent decisions or knowledge entries would make a fresh post?

Read the structured Answer / Evidence / Confidence / Gaps block the pass returns. Use it to:

- Suggest two or three angles the user has not posted recently.
- Flag any theme repetition risk before drafting (so the post does not echo something from last week).
- Tie the draft to a recent decision or knowledge entry when one fits, citing the entry ID at the bottom of the draft as a P.S. or pinned note for the user.

If `skills/brain-pass/SKILL.md` is missing (older install), fall back to `python scripts/query.py "linkedin"` and reason from those raw matches. Do not block.

## The Format

**Length:** 100-300 words typical. Up to 500 when the topic earns it. Never pad to fill space.

**Line breaks:** Each thought gets its own line. This is non-negotiable. LinkedIn rewards scroll depth. Short paragraphs. Often single lines. Like this.

**No hashtags.** Let the content speak for itself.

**No bold unicode text headers.** No fancy formatting tricks.

**Arrows (->) for lists.** Not bullet points.

**ALL CAPS sparingly** for emphasis on key words. Not whole sentences.

## The "See More" Rule - First Two Lines

On mobile, LinkedIn shows roughly two lines before the "See More" cutoff. These two lines are a UNIT. They work together as hook + tension. The reader decides to tap or scroll in under 2 seconds based on this pair alone.

**The first line stops the scroll.** A bold claim, a confession, a provocation.

**The second line creates a gap that demands the tap.** It should shift the direction, raise a question, or make the reader unsure where this is going.

Pattern of strong two-line units:
- A surprising claim, then a sentence that makes the reader unsure if they should be alarmed or relieved.
- A confession, then a line that suggests the confession changed how the writer operates.
- A short provocation, then a line that names a real tension the reader is already feeling.

Bad second lines that kill the tap:
- Restating the first line in different words
- A generic setup like "Here's why" or "Let me explain"
- Anything that tells the reader what the post is about before they've tapped

Test: read just the first two lines. Would you tap "see more"? If not, rewrite the second line.

## Post Structure

Every post follows one of these patterns:

### Pattern 1: Story to Insight
1. Hook (bold stance, emotional truth, or curiosity gap)
2. The story (what happened, specific details)
3. The turn (what the founder learned, what changed)
4. The takeaway (actionable, specific)
5. Close (question, CTA, or statement that sits with the reader)

### Pattern 2: Framework Drop
1. Hook (the problem this solves)
2. Quick context (why this matters)
3. The framework (use arrows, keep each point to one line)
4. Why it works (brief)
5. Close

### Pattern 3: Contrarian Take
1. Hook (the position - make it uncomfortable)
2. Why most people get it wrong
3. What the founder has seen work instead (from experience, not theory)
4. Close with the reframe

### Pattern 4: Show Don't Tell
1. Hook (a confession or action)
2. Brief story of what happened and why (keep it tight, earn the reader's trust)
3. Pivot ("That's not the point." or a section break)
4. Demonstrate through real usage (what the tool, system, or approach actually does for the founder - specific examples, not abstract claims)
5. Reframe to a bigger lesson (why this matters beyond personal situation)
6. Recommendation or challenge (give the reader something to try)
7. Casual parenthetical close or a line that sits with them

This pattern works for product demos, tool recommendations, and any post where showing real workflow is more convincing than explaining a framework. The honesty of admitting what changed is what earns the right to recommend something.

### Pattern 5: Circle Back with P.S.
1. Hook (bold claim that sounds one way at first)
2. Story or argument (the intellectual case - head talking)
3. Main close (a challenge or direct question)
4. P.S. section - a real, personal story that circles back to the hook
5. The P.S. lands with emotion - gut talking, not head
6. Final line reframes the entire post through the lens of that personal moment

This pattern works when there is both a strong argument AND a real moment that proves the argument better than logic can. The P.S. is where the post goes from smart to felt. The contrast between the analytical body and the emotional P.S. is what makes people save the post.

## Hook Priority

In this order:
1. **Bold stance or contrarian take** - takes a position against conventional thinking.
2. **Pain-aware / empathy hook** - meets the reader where they're struggling. Acknowledges what they're feeling without patronizing them. Works when the audience has a known pain point.
3. **Emotional truth** - a real internal admission that lands honestly.
4. **Curiosity gap** - a short line that sets up tension.
5. **Personal story opening** - something that actually happened.

If a hook feels forced, kill it. The best posts come from caring about the topic. Hooks should be honest - not manufactured for engagement. The real thing that happened is always more compelling than the exaggerated version.

**Pain-aware hooks vs contrarian hooks:** A contrarian hook takes a stance against conventional thinking. A pain-aware hook meets the reader in their struggle. Both stop the scroll. The difference is intent - contrarian hooks challenge, pain-aware hooks connect.

## Closing the Post

End with one of:
- A question that doesn't have an easy answer
- A statement that reframes everything before it
- A hand extended (not a sales pitch)
- A direct challenge
- A casual parenthetical that lands with personality
- A P.S. that circles back to the hook with a real story (Pattern 5)

Never end with "What do you think?" or "Drop your thoughts below!" Those are generic engagement bait.

## Brain Dump to Post Workflow

When the user gives a raw rant, voice note transcript, or brain dump:

1. **Don't write yet.** Ask one or two clarifying questions first. Tone, audience, anything missing.
2. **Find the hook buried in the rant.** It's usually there - a line they said naturally that has punch. Pull it to the top.
3. **Identify the core argument.** A brain dump has multiple threads. Pick the ONE that matters most. Save the rest for other posts.
4. **Draft and flag gaps.** If the logic has holes, contradictions, or over-counts (says "three things" but lists four), flag them. Don't silently fix - tell the user what was changed and why.
5. **Check the count.** If the user says "three things" or "two reasons," count them in the draft. People naturally over-count when speaking. Catch it before LinkedIn commenters do.
6. **Push back where needed.** If an idea undermines the argument, say so. "I cut that line because it contradicts your point" is better than quietly including something that weakens the post.

## Image as Content

When a post includes an AI-generated image, the image creation process itself can become part of the content. Sharing the exact prompt used to generate the image serves as:

- Proof of the post's argument (the writer knew what they wanted the viewer to feel)
- A teaching moment (audience sees how specific prompting needs to be)
- Transparency (not pretending the image is real)

Format the prompt reveal as a P.P.S. with the prompt in a JSON code block. Close with a line that ties the prompt back to the post's thesis. This works especially well when the post argues that the human judgment behind AI is the real skill - showing the prompt IS the proof.

## Before Finalizing

The list below extends `skills/your-voice/SKILL.md`. When updating either file, update both to keep them in sync.

Run the full anti-AI self-check:
1. Banned phrases? Kill them. (Read `skills/your-voice/SKILL.md` for the universal banned phrase list and apply its rules in full.)
2. Banned words? Replace with simpler ones.
3. Em dashes? Replace with simple hyphens. Max two per post.
4. Rule of three? Break the pattern unless the voice profile explicitly enables triplets.
5. Metronome rhythm? Vary sentence length.
6. **"See More" test:** Read ONLY the first two lines. Would you tap? If not, rewrite the second line.
7. Would the founder actually say this across a table?
8. **Negation-contrast check:** Any "It's not X - it's Y" or "That's not X. That's Y" or "Not just X, but Y"? Rewrite as a direct statement. This is the single most common AI pattern that slips through. Catch it every time.
9. **Count check:** If the post says "three things" or any specific number, count the list. Fix before posting.
10. Compare against `voice.samples` from the profile. If it doesn't sound like the samples, rewrite.

## Posting Strategy Notes

**Best post times** depend on your audience timezone. Generally: weekdays mid-morning local-time hits highest engagement for B2B audiences. Check your own LinkedIn analytics after 4-6 posts and follow your data, not generic advice.

**The Golden Hour rule:** The first 60 minutes after posting determine whether LinkedIn pushes the post wider. The author needs to be ON the app during this window, replying to every comment.

**Pre-post warmup:** 30 minutes before posting, comment on 5-10 posts in the feed. Real comments, not "Great post!" This signals active user status to the algorithm.

**Scheduling caution:** LinkedIn doesn't penalize scheduled posts, but if you schedule and walk away, you miss the golden hour. Only schedule if you can also block the 60 minutes after for engagement.
