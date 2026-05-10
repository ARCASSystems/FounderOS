# FounderOS v1.20.3 post anti-examples trace

- Trace date: 2026-05-10
- Product state traced: v1.20.3 working tree after anti-examples
- Persona: Marcus Adler, founder of Linebreak Labs, a 12-person Berlin developer-tools startup selling code review and release workflow software to engineering managers. Four years in, technical writer background.
- Topic tested: what AI tools are doing to the engineering-manager job

## Voice interview run

The same Marcus profile from `traces/v1203-pre-anti-examples.md` was re-run through the upgraded voice interview. Phase 2.5 captured the new contrastive fields.

### Anti-example blocks captured

```yaml
anti_examples:
  pairs:
    - bad: "AI will not replace engineering managers."
      good: "The review queue got a second mouth this year. It still does not have an owner."
      rule: "Start from the concrete object, not the broad prediction."
    - bad: "It is not just about managing people - it is about protecting focus."
      good: "The job changed at the handoff, not the org chart."
      rule: "Cut negation-contrast setup. Name the handoff."
    - bad: "Engineering managers are part therapist, part project manager, part technical translator."
      good: "The manager is the person who has to ask why ready means three different things."
      rule: "Replace tidy role labels with one concrete responsibility."
    - bad: "AI tools can summarize pull requests, draft status updates, find blockers, and turn tickets into plans."
      good: "If a tool can name the stale review before standup, the meeting has to justify itself."
      rule: "Name one painful handoff instead of listing features."
    - bad: "That sounds like a gift. It is also a trap."
      good: "The trap is quieter than that."
      rule: "Avoid stock contrast pairs. Make the turn colder and shorter."
  contrarian_takes:
    - "Most engineering managers do not need more visibility. They need fewer fake definitions of ready."
  aesthetic_crimes:
    - "It is not just about X - it is about Y"
    - "part X, part Y, part Z"
  red_flags:
    - "A list of tool abilities with no named handoff"
    - "A confident prediction before one concrete queue is named"
```

## LinkedIn post output after anti-examples

```text
The review queue got a second mouth this year.

It still does not have an owner.

AI can read pull requests, tickets, and standup notes faster than an engineering manager can open the tabs.

Useful.

Also not the job.

The job is deciding which stuck thing deserves interruption.

If a tool can name the stale review before standup, the meeting has to justify itself.

If it can draft the update, the manager still has to decide whether the update is honest.

If it can say three tickets are blocked, someone still has to ask why "ready" meant three different things.

That is where the job gets narrower.

Less status gathering.
More ownership of the merge decision.

The bad version of this future is an engineering manager with better dashboards and the same old queue.

The useful version is smaller:

Cancel the meeting when the tool already knows the answer.
Name the handoff hiding behind the polite label.

AI can make the queue visible.

It cannot decide whether the queue is honest.

That is still the job.
```

## Side-by-side cleanup

| Pre-trace drift line | Post-filter rewrite | Confirmed |
|---|---|---|
| "AI will not replace engineering managers." | "The review queue got a second mouth this year. It still does not have an owner." | Yes - starts from the concrete queue. |
| "But it will change what the job is really about." | "The job is deciding which stuck thing deserves interruption." | Yes - removes negation-contrast setup. |
| "part therapist, part project manager, part technical translator." | "The manager is the person who has to ask why ready means three different things." | Yes - replaces tidy labels with one responsibility. |
| "summarize pull requests, draft status updates, find blockers, and turn messy tickets into cleaner plans." | "If a tool can name the stale review before standup, the meeting has to justify itself." | Yes - swaps feature pile for one painful handoff. |
| "That sounds like a gift. It is also a trap." | "Useful. Also not the job." | Yes - colder, shorter, less stock. |

## Result

- Anti-example pairs captured in profile: yes.
- LinkedIn post cleaner of negation-contrast: yes.
- LinkedIn post cleaner of rule-of-three labels: yes.
- LinkedIn post cleaner of generic openers: yes.
- Each pre-trace drift line has a visible rewrite in the final post: yes.

The remaining deliberate rough edge is "Useful. Also not the job." It is short and a little abrasive, which fits Marcus's samples better than the smoother v1.20.2 contrast pair.
