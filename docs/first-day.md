# Your first day with Founder OS

The OS is files. Skills read those files. The more files you fill, the more skills come alive.

This page maps the cascade. You don't need to do all of it on day one - but knowing the order means you stop wondering why a writing skill sounds generic.

---

## The 35-minute first run

Three steps. Each step unlocks the skills underneath it.

### Step 1 - Setup wizard (15 min)

```
/founder-os:setup
```

Asks you 15-20 questions about who you are, what you run, what tools you use. From your answers it generates: identity, priorities, decisions, cadence, brain layer, role files, network stubs.

After this step, the OS knows who you are. These skills now work end to end:
- `/today`, `/next`
- weekly-review, priority-triage
- brain-log, decision-framework
- meeting-prep, knowledge-capture, sop-writer
- founder-coaching, unit-economics, strategic-analysis
- session-handoff, pre-send-check
- business-context-loader

Anything you write through these comes out in a neutral tone. The next step fixes that.

### Step 2 - Voice interview (10 min)

```
/founder-os:voice-interview
```

Asks for two writing samples plus a few shaping questions. Writes `core/voice-profile.yml`.

After this step, the writing skills speak as you, not as Claude:
- email-drafter
- linkedin-post
- client-update
- content-repurposer
- your-voice
- proposal-writer (voice half)

If you skip this, those skills warn you and fall back to a neutral tone.

### Step 3 - Brand interview (10 min)

```
/founder-os:brand-interview
```

Asks for colors, fonts, logo path. Writes `core/brand-profile.yml`. If you have an existing brand kit, paste hex codes and font names. If you don't, the wizard helps you pick.

After this step, branded outputs render in your visual identity:
- your-deliverable-template (CV, deck, one-pager, PDF reports)
- proposal-writer (when output is a branded PDF/DOCX, not plain text)
- client-update (when output is a branded PDF, not an email)

### Step 4 - Audit anytime

```
/founder-os:status
```

Read-only. Returns a 0-100% readiness score across Core, Voice and Brand, Cadence, Business Context, Brain Layer. Names the next 3 high-leverage moves.

Run this whenever you want to see where the OS is and what to fill next.

---

## The cascade map

| Fill once | Skills it lights up |
|---|---|
| `core/identity.md` (setup wizard) | Almost all skills generically. |
| `core/voice-profile.yml` (voice-interview) | email-drafter, linkedin-post, client-update, content-repurposer, your-voice, sop-writer voice. proposal-writer voice half. |
| `core/brand-profile.yml` (brand-interview) | your-deliverable-template. proposal-writer brand half. client-update branded variant. |
| `context/companies/<x>.md` (business-context-loader) | Per-business scoping for proposal-writer, meeting-prep, priority-triage, unit-economics, weekly-review. |

Pattern: a small one-time fill cascades into many skills. If a writer feels generic, the upstream profile is the gap.

---

## After the first day

**Daily**

```
/today          # one-screen view of what matters today
/next           # one recommended next action
```

**Weekly**

```
/founder-os:weekly-review     # via skill-name (no slash command yet for this one)
```

In Claude Code, just say "run weekly review" - the skill auto-triggers.

**When you make a commitment**: Claude logs it to `brain/log.md` and tracks it.

**When you make a decision**: Claude routes it into `context/decisions.md` (open / parked / resolved).

**When you take an outreach action**: log it. The session-close hook checks that outreach signals match `context/clients.md` updates - the revenue loop stays honest.

---

## When something feels off

**A writing skill sounds generic** -> voice profile not filled. Run `/founder-os:voice-interview`.

**A branded doc looks wrong** -> brand profile not filled or has placeholders. Run `/founder-os:brand-interview`.

**Claude doesn't know what's important this week** -> priorities or weekly commitments are stale. Refresh `cadence/weekly-commitments.md` or run a weekly-review.

**The OS feels off-track in general** -> run `/founder-os:status`. The score and the next-3-moves block tell you exactly what's missing.

**You want to remove the OS** -> `/founder-os:uninstall`. Default mode preserves your data; pass `--purge` to wipe everything.

If any of the above doesn't work cleanly, email `solutions@arcassystems.com` with what you tried and the error you hit.
