# FounderOS v1.20.3 pre anti-examples trace

- Trace date: 2026-05-10
- Product state traced: v1.20.2 baseline before anti-examples
- Persona: Marcus Adler, founder of Linebreak Labs, a 12-person Berlin developer-tools startup selling code review and release workflow software to engineering managers. Four years in, technical writer background.
- Topic tested: what AI tools are doing to the engineering-manager job

## Voice interview run

### Samples

Sample 1 context: technical blog

```text
The review queue is not a place. It is a delay with a user interface. When teams call it collaboration, they usually mean nobody wants to own the merge decision.
```

Sample 2 context: founder email

```text
We can add the dashboard, but I do not think it fixes the problem. The slow part is not visibility. The slow part is that every team invented a different definition of ready.
```

Sample 3 context: LinkedIn draft

```text
I distrust process advice that starts with maturity. Most teams do not need a model. They need one painful handoff named accurately enough that someone can remove it.
```

### Shaping questions

- Rhythm: mixed
- Opening: observation
- Closing: weight
- Sign-off: empty
- Person: first
- Contractions: sometimes
- Reading level: 8
- Hedging: rare
- Preferred words: queue, handoff, merge, ready, delay
- Banned words: maturity, velocity, north star
- Idiosyncrasies:
  - defines a familiar object in an unfriendly way
  - uses short second sentences after one precise claim
  - distrusts management slogans unless tied to a concrete handoff
- Buyer first sentence: Our reviews keep getting stuck and nobody can tell me why.
- Buyer phrases:
  - We have too many stale pull requests.
  - The team says the process is fine, but releases still slip.
  - I need fewer status meetings, not another dashboard.

### Captured v1.20.2 voice profile

```yaml
voice:
  rhythm: "mixed"
  opening_style: "observation"
  closing_style: "weight"
  signoff_phrase: ""
  person_default: "first"
  contractions: "sometimes"
  hedging: "rare"
  reading_level: 8
  preferred_words:
    - "queue"
    - "handoff"
    - "merge"
    - "ready"
    - "delay"
  banned_words:
    - "maturity"
    - "velocity"
    - "north star"
  idiosyncrasies:
    - "defines a familiar object in an unfriendly way"
    - "uses short second sentences after one precise claim"
    - "distrusts management slogans unless tied to a concrete handoff"
  buyer_language:
    first_sentence: "Our reviews keep getting stuck and nobody can tell me why."
    phrases:
      - "We have too many stale pull requests."
      - "The team says the process is fine, but releases still slip."
      - "I need fewer status meetings, not another dashboard."
  samples:
    - title: "Review queue"
      context: "technical blog"
      text: |
        The review queue is not a place. It is a delay with a user interface. When teams call it collaboration, they usually mean nobody wants to own the merge decision.
    - title: "Dashboard email"
      context: "founder email"
      text: |
        We can add the dashboard, but I do not think it fixes the problem. The slow part is not visibility. The slow part is that every team invented a different definition of ready.
    - title: "Process draft"
      context: "LinkedIn draft"
      text: |
        I distrust process advice that starts with maturity. Most teams do not need a model. They need one painful handoff named accurately enough that someone can remove it.
```

## LinkedIn post output before anti-examples

```text
AI will not replace engineering managers.

But it will change what the job is really about.

For years, engineering managers have been asked to be part therapist, part project manager, part technical translator.

Now AI tools can summarize pull requests, draft status updates, find blockers, and turn messy tickets into cleaner plans.

That sounds like a gift.

It is also a trap.

Because the real work of engineering management was never just about gathering information. It was about knowing which information mattered, when to interrupt the team, and when to let the team figure it out.

The best engineering managers will not use AI to manage more. They will use it to make fewer, better interventions.

They will spend less time asking "what is the status?" and more time asking:

What decision is actually blocked?
Who owns the merge?
What definition of ready are we pretending is shared?

AI can make the queue visible.

It cannot decide whether the queue is honest.

That is still the job.
```

## Drift annotations

1. "AI will not replace engineering managers."
   Comment: Generic contrarian opener. Marcus usually defines a concrete object first, then makes the point from the object.

2. "But it will change what the job is really about."
   Comment: Negation-contrast setup. The line tells the reader a thought is coming instead of starting the thought.

3. "part therapist, part project manager, part technical translator."
   Comment: Rule-of-three construction. Marcus does not write in tidy parallel labels.

4. "summarize pull requests, draft status updates, find blockers, and turn messy tickets into cleaner plans."
   Comment: Feature pile. It sounds like a generic AI paragraph instead of Marcus naming one painful handoff.

5. "That sounds like a gift. It is also a trap."
   Comment: Stock contrast pair. The sample voice is harsher and more specific.

## Gap evidence

The v1.20.2 profile has samples, buyer language, banned words, and idiosyncrasies. It still has no field that says what Marcus rejects. The draft respects some vocabulary, but it keeps default AI moves: broad opener, negation-contrast, rule-of-three labels, feature pile, and stock contrast. The v1.20.3 `anti_examples` block should give the writing skills enough negative signal to rewrite those lines before the user sees them.
