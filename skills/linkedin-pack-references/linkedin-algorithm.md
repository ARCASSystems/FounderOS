---
title: LinkedIn algorithm reference (shared, dated)
last_verified: 2026-06-07
re_verify_after_days: 90
sources:
  - "AuthoredUp - large-sample LinkedIn post study (format and engagement)"
  - "Richard van der Blom - Algorithm Insights Report (annual reverse-engineering)"
---

# LinkedIn algorithm reference

The single source of algorithm truth for the LinkedIn pack. The brand and content skills read this file and cite it; they do not restate it inline and drift. If a fact is not here, do not assert it.

## Freshness rule (read first)

LinkedIn's ranking is reverse-engineered from public studies, not documented by LinkedIn. It shifts. This file carries a `last_verified` date. **If today is more than `re_verify_after_days` (90) past `last_verified`, web-check the specifics before asserting them**, and prefer the conservative reading until you have re-verified. A consumer skill that cannot find this file degrades gracefully: it says "algorithm reference not found, using conservative defaults" and falls back to format-and-cadence basics only.

## Data-backed facts (assert these)

These are supported by repeated large-sample external studies. State them plainly.

- **Dwell time is the hidden primary driver.** How long a reader stops on a post matters more than the like. The practical threshold is around 30+ seconds of attention. Posts built to be read slowly (a strong first line, white space, a reason to expand "see more") out-perform posts built to be skimmed.
- **Comments weigh roughly 2x likes.** Engagement is not flat. A thoughtful comment and a save outweigh a like; the like is the weakest signal. Reply to comments in the first hour to compound it.
- **The golden hour gates expansion.** Early engagement in roughly the first 60 to 90 minutes decides whether the post is shown more widely. Post when your audience is active and be present to reply during that window.
- **Format ladder (strongest to weakest):** document carousels (PDF-style) top the reach table, native short video next, polls strong, plain image mid, **text-only weakest** for reach (though text can still win on dwell if the writing holds). Pick the format the message deserves, but know the ladder.
- **Body links cut reach by around 60%.** An external link in the post body suppresses distribution. The old "put the link in the first comment" workaround is now throttled too, so it is not a clean escape. If a link must go out, accept the reach cost or put it in the post later as an edit.
- **Cadence: 3 to 5 times a week, never more than once per 24 hours.** Posting more than once a day splits your own reach. Consistency over volume.
- **Length: around 800 to 1000 characters, simple language, max 3 hashtags.** Short, plain sentences read by a wide audience beat dense expert prose. Hashtags past three add nothing.
- **The interest graph amplifies topic lanes.** LinkedIn increasingly shows posts to people interested in the topic, not just your followers. Posting consistently in one lane trains the graph to carry you to the right strangers. Lane discipline compounds; topic-hopping resets it.

## Tool-blog color (do NOT assert as fact; label it)

These circulate in tool-vendor blogs and talks. They are plausible directional color, not study-backed. If you mention any of them, label them as unverified mechanism, never as a number to act on.

- LLM-embedding mechanics behind topic matching ("the feed reads your post with a language model").
- "Your post starts with ~300M potential reach and the algorithm narrows it to ~2,000."
- "A comment is worth 15x a like."

Use the data-backed comment-weighting (~2x) for any real recommendation. The 15x figure is color.

## Source disagreements (kept conservative)

Where studies disagree, design for the worse case:

- **External-link reach penalty:** estimates range; treat it as a real and meaningful suppression (~60% is the working figure) rather than debating the exact percent.
- **Export email coverage:** sources cite anywhere from ~3% to 30 to 50% of connections having an email in the export. Design every downstream skill for **mostly blank** email - never assume the email column is populated.

## Primary sources to re-check on a refresh

- AuthoredUp's large-sample post study (format and engagement breakdowns).
- Richard van der Blom's Algorithm Insights Report (annual, reverse-engineered).

When re-verifying, update `last_verified` and reconcile any fact that moved. Forward-only: do not silently rewrite history, note what changed.

## Known-limitation line (consumer skills paste this)

> Algorithm facts are reverse-engineered and dated. If this reference's `last_verified` stamp is over ~90 days old, re-verify before trusting specifics.
