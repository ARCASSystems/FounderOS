---
why: "Once the OS runs more than a handful of recurring jobs, you stop being able to hold what each one does, whether it is any good, and what it is allowed to touch. Naming them as employees with a job description, a review, and a written grant makes capability something you can manage in role language instead of remembering in workflow language."
---

# Digital employees - the org chart doctrine

One page deciding how recurring capability is organized, monitored, and improved inside your OS. It sits on top of the roles in `roles/index.md` (which decide who owns what) and the gates in `rules/approval-gates.md` (which decide what is allowed to happen without you).

You do not need this on day one. Reach for it the moment you have two or three recurring jobs running and you can no longer remember what each one covers.

## The core principle

**The org chart is the interface. The workflow is the implementation.**

People understand roles. You will monitor, correct, and trust your OS in role language ("the follow-up job missed two weeks"), not in workflow language ("the second stage of the chain skipped"). So every digital employee carries two faces, and both are required:

- **Human face:** a job title, a plain-language job description that states the narrow scope truthfully (what it does AND what it does not do), one measure of whether it is working, and a review written in role language.
- **Machine face:** the chain of skills it runs, its inputs, exactly one output surface, how it gets triggered, and where its runs are recorded.

A role is a stance and a charter. An employee is one recurring job inside that role. The role speaks for its function when you review the week. The employee is what actually runs.

The metaphor must not overpromise. A digital employee does exactly its chain and nothing else. Its job description says so out loud.

## Hard rules (every employee, no exceptions)

1. **Propose only, by default.** An employee drafts, ranks, flags, and files. It does not send, approve, or overwrite a file you own. Graduating it to any acting verb is a decision you make once per verb, never trust that accumulated quietly.
2. **One interchange to you.** Everything an employee wants from you arrives the same way: as an item on your queue (`cadence/queue.md`). No side channels, no separate inbox to check.
3. **Hiring has a test.** Create an employee only if it beats you on both speed AND accuracy, for a job that genuinely recurs. No on either count means do not create it. Most ideas fail here, and that is the point.
4. **The narrowest tool grant its chain needs.** A job that only reads files does not get write access. A job that only proposes does not get the ability to send. Wide grants are debt you wrote down, not a default.
5. **Scoped reading, not the whole brain.** An employee reads `brain/.snapshot.md` plus the specific files named in its row. Your identity file loads only for employees whose output a human will read as prose.
6. **Monitoring speaks role language. Upgrades speak workflow language.** You mark a run ok, needs work, or failed, with one line of why. The review turns those verdicts into a shown diff on the employee's definition. It proposes. You approve.

## The charter IS the grant (the rule worth stating twice)

The most common way this doctrine fails: the boundary is written in the job description as prose, and the actual permission handed to the run is far wider. "Propose only, never send" as a sentence in a prompt is not a boundary. It is a wish.

So every employee row carries three fields, and the middle one is the only one that constrains anything:

- `may_write` - every file or store it is allowed to change, in plain language
- `never` - the prohibitions, so the shape of the job reads in one line
- `tools` - the exact grant handed to the run

Whatever dispatches the employee reads `tools` from that row. There is no second list somewhere in the code to drift from. An employee with no `tools` field does not run at all. An employee asking for a blanket "run anything" grant on a propose-only job is refused, not warned.

`may_write` and `never` are for you to read. `tools` is what actually holds. Keep them consistent, and treat narrowing `tools` as the real control.

Your own verbs are a different thing and stay deliberately wide. When you run a task yourself, the grant is your hands, not a job acting on standing authority.

## The performance loop (small, and it compounds)

- **Verdicts.** After a run you actually saw, record one line: ok, needs work, or failed, plus why. That is the cheapest possible act of management and the whole input to everything below.
- **Review.** Read one employee's row, its verdicts, and its runs, then propose changes to its definition as a shown diff. Trigger it monthly, or as soon as three needs-work verdicts land in thirty days. The review never applies its own diff.
- **Registry.** `roles/employees.yaml` is the org chart. One row per employee, both faces. Seeded honestly with only what exists.

## Honest status, always

A row exists only for something that exists. Three states:

- `active` - runs today, and there is evidence (runs recorded, or items it filed)
- `stale` - exists but is not currently earning its seat. Say why in the description.
- `gated` - defined and approved, but not yet wired to anything that triggers it

The failure this prevents: an org chart full of impressive-sounding jobs, none of which have ever run. An empty registry is honest. A full one that lies is worse than no registry.

## Change protocols (so the registry stays true)

**This doctrine** changes only through a diff you approved, the same gate as any other rule.

**The registry** changes through exactly three doors:

1. **Hire** - a new row, only after the hiring test above.
2. **Review diff** - the review proposes, you approve, the row is edited and its review date stamped.
3. **Retirement** - below.

Anything else (a quick field tweak mid-session, a bulk rewrite) is drift.

**Retirement keeps the row.** A retired employee keeps its row with `status: retired` plus a one-line why and date at the front of its job description. It is never silently deleted. The row is the provenance. Its verdicts stay in the ledger. The org chart stays honest about what used to work here.

## What crosses between people, and what never does

If anyone else runs their own OS alongside yours, adapting to a person is not absorbing them into one system. Each person runs their own. What passes between two OSes is shared work items only.

What never crosses, in either direction: pay and commercial terms, one person's private profile reaching another person's system, and personal data about anyone. Keep those out of any file a second person can open, whatever the convenience argument is that day.

## Start here

You do not fill this in at setup. When a job has recurred three times and you have corrected it twice, that is the job worth writing a row for. Start with one. Give it a review after a month. Add a second only if the first one earned its place.
