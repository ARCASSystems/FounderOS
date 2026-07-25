---
why: "Documentation rots the moment the thing it describes moves. A harness does not: it stays readable to the next session, catches its own failures, learns from what keeps going wrong, and fits the person running it. Naming those four properties in one place keeps them maintained together instead of drifting apart as four unrelated habits."
---

# OS as harness - the four self-maintenance properties

A harness is not documentation. Documentation gets read by a human and goes stale silently. A harness keeps itself legible to the next session, catches its own failures, learns from repeated ones, and fits the human running it.

Your OS already does all four in small ways. This page names them as one doctrine so they stay wired to each other and get applied on every build, instead of being rediscovered as four separate good ideas.

**The standing guardrail on all four:** this is a self-observing harness, not a self-modifying one. Every property below notices, names, and proposes. None of them edits a rule, sends anything, or overwrites a file you own without your yes. The loop proposes. You decide.

---

## 1. Why-first markdown - the OS explains itself to the next session

**The property:** every doctrine file says why it exists before it says what it does, so a session opening it cold can tell load-bearing doctrine from a scratch note without being told.

- **The form:** a one-line `why:` in the frontmatter. For a file without frontmatter, a `## Why this exists` heading near the top.
- **Why `description:` is not enough:** description says what a skill does and when to fire it. Why says what breaks without it. Different questions, and only the second one survives a rewrite.
- **The check:** `python scripts/selfdoc_check.py why` names the files still missing it. Surfaced by `/founder-os:lint` as one advisory line.
- **Adoption is forward-only.** Files written before the convention adopt it the next time you touch them. Nobody backfills.

## 2. Self-documenting code - the OS explains itself to the next builder

**The property:** every substantial script opens with a docstring stating the problem it solves, the rules it holds to, and how it is invoked. The next person to touch it reads the contract instead of working it out from the code.

- **The bar:** the problem in plain words, the invariants (what must always stay true), and a usage block showing how to run it.
- **The check:** `python scripts/selfdoc_check.py code` grades every substantial script in `scripts/`. Thin wrappers are exempt by design - a ten-line helper needs no essay.
- **This is a warning, never a failure.** A thin docstring makes a file harder to read. It does not break the machine.

## 3. The self-healing loop - fix the engine, not the symptom

**The property:** when the OS keeps failing at the same thing, that is a bug in the engine, not a task for you. A correction you have made twice should change a file, not get made a third time.

Four stages:

1. **Surface.** Failures get written down where they can be seen. Hooks and background jobs fail silently by design, so `system/quarantine.md` is the catch-net, and the session brief counts what is sitting in it.
2. **Detect.** When the same failure shows up twice, name the surface that owns the durable fix - the skill body, the prompt, the script that generates the wrong thing.
3. **Prescribe.** `/founder-os:os-evolve` turns those findings into a dated plan: gaps with evidence, numbered prompts to execute, and reconcile lines. The planner never executes its own prompts.
4. **Close.** Each prompt gets a reconcile line naming what observably moved. A fix that lands with no reconcile line is debt, and becomes gap number one of the next cycle.

**The input most people miss:** today the loop learns from failures - things killed, things marked needs-work, corrections. The richer signal is what you decline to decide. What you skip, repeatedly, is a preference you have not written down yet. A skip is not an answer, so nothing should ever act on one automatically. But a pattern of skips is worth surfacing to you as a question about the system, not the task.

## 4. Per-person adaptation - the OS fits the human, and each human runs their own

**The property:** the OS adapts to who is operating it, and that adaptation is per person, never shared.

- **The profile.** `core/profile.md` and `core/identity.md` are what make the same machine behave differently for a different human. They are read at session start, and they are the reason the OS opens with what your situation needs.
- **The behavioral layer.** `core/avatar.md` holds how you actually work - where you default, where you stretch - and skills load it when behavioral context matters. The framing is "the system is set to your profile", never "take our assessment".
- **The boundary.** Adapting to a person is not absorbing them. If someone else works alongside you, they run their own install. There is no shared multi-person OS here. What passes between two OSes is shared work items, never personal data and never commercial terms.

---

## How the four compound

Properties 1 and 2 keep the OS **readable**: any session or any builder can pick up a file cold. Property 3 keeps it **honest**: failures surface and get fixed at the engine instead of papered over. Property 4 keeps it **fitted**: the same machine serves a different human without a rewrite, and without merging two people who should stay separate.

Together they are what lets the OS grow past the size any one session can hold. The harness carries the legibility, the failure-catching, and the personal fit that you would otherwise have to hold in your own head.

A build lands under the harness when it satisfies all four: its doctrine says why, its script documents its contract, a repeated failure in it has somewhere to surface, and it respects whose profile and whose OS it touches.

## Cross-reference

- `rules/entry-conventions.md` - the why-first convention and the per-entry data conventions
- `system/quarantine.md` - the failure catch-net (stage 1 of the loop)
- `rules/digital-employees.md` - the org chart doctrine and the person boundary
- `rules/approval-gates.md` - the write-side law every property obeys
- `scripts/selfdoc_check.py` - the checker behind properties 1 and 2
