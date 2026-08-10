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

So every employee row carries three fields:

- `may_write` - every file or store it is allowed to change, in plain language
- `never` - the prohibitions, so the shape of the job reads in one line
- `tools` - the exact grant the run is meant to carry

Be honest about what the grant is, because it is not a sandbox. The grant lives in two places by construction: the row's `tools` field, which you read, and the `allowed-tools` list in the seat skill's own frontmatter - the skill's declared runtime list. Claude Code today reads that list as pre-approval (the listed commands run without a prompt), not as a wall that blocks everything else; a restrictive mode is an open request upstream. So the boundary is a written contract plus a tripwire: the two lists are kept identical, the charter audit (`python scripts/employee_verdict.py charters`) names drift between them in either direction, and anything outside the grant still lands in your normal permission prompts rather than running silently. An employee with no `tools` field does not run at all. An employee asking for a blanket "run anything" grant on a propose-only job is refused, not warned.

`may_write` and `never` are for you to read. `tools` is the declared surface the audit holds both files to. Keep them consistent, and treat narrowing `tools` as the real control. Tools that arrive through MCP (a calendar, a meeting-notes reader) ride the same permission prompts and belong in the row's `inputs`, not in `tools`.

Your own verbs are a different thing and stay deliberately wide. When you run a task yourself, the grant is your hands, not a job acting on standing authority.

## The performance loop (small, and it compounds)

- **Run records.** The job writes one line about itself when it finishes: what it read, what it produced, how it ended, and what it could not do. `python scripts/agent_runs.py record --seat <id> --trigger "<what set it off>" --outcome ok|refused|failed`. This is the job's own closing act, not something you remember to do.
- **Verdicts.** After a run you actually saw, record one line: ok, needs work, or failed, plus why. That is the cheapest possible act of management.
- **Review.** Read one employee's row, its verdicts, and its runs, then propose changes to its definition as a shown diff. Trigger it monthly, or as soon as three needs-work verdicts land in thirty days. The review never applies its own diff.
- **Registry.** `roles/employees.yaml` is the org chart. One row per employee, both faces. Seeded honestly with only what exists.

### Why the runner records the run, and not you

Before the run log existed, `run_record_source` on every row held a sentence naming a place, and nothing wrote there. So the only trace a job left was a verdict you typed, and a verdict only exists for a run you were watching. That makes the whole ledger a sample biased toward the runs you happened to see, and the review reads that sample as if it were the record. A job that misbehaves quietly, in the runs you were not watching, is invisible to the exact machinery built to catch it.

One line per run fixes it, and it is the smallest thing that could: `brain/agent-runs.jsonl`, append-only, standard library, no key. `python scripts/employee_verdict.py render` shows runs beside verdicts, so the gap between them is readable - fourteen runs, three graded. `drift` reports an `active` row that the log has never seen, which is the check `active` always claimed to mean.

Two honest limits, worth stating so nobody over-trusts it. A run line says a run happened, never that the output was any good - that is still your verdict. And a job that does not record cannot be told apart from a job that did not run, which is why the drift check names the two possibilities rather than picking one.

`refused` is a first-class outcome, not a failure. A propose-only job that declined because the charter said no is the charter working, and a log that could not say so would push every honest refusal into the failed bucket and teach you to distrust your own restraint rules.

### The read-list grows, or the seat stays as ignorant on run 50 as on run 1

A seat's read-list is the `inputs:` string on its row, and left alone that string never changes. Meanwhile the brain accumulates beside it: notes from books, calls, and articles, filed by `knowledge-capture`, read by nobody on the chart. Two stores in one folder, learning nothing from each other.

The fix is one optional field, and the smallness is the point. Any note in `brain/knowledge/` may carry `seats:`, and every seat it names gets a POINTER folded into its read-list - id, topic, path. Never the note's body: the seat opens the file itself when it runs, which is the same do-not-hard-parse-bodies rule the knowledge layer has always had. `python scripts/agents_sync.py apply` is what makes it real, and the field has three states rather than two:

| Value | Meaning |
|---|---|
| absent | never reviewed - the morning loop may raise it once, when a slot is free |
| `seats: <ids>` | routed to those seats |
| `seats: none` | reviewed and deliberately routed to nobody - the tombstone |

**The third state is the one that earns its place.** A "no" that leaves no record is a question you get asked again tomorrow, and the morning after that, until you stop reading the mornings at all. Writing `seats: none` closes the question permanently, so a decline costs you one answer rather than one answer per day forever.

Two rules carried over unchanged, because they are what keep the chart honest. **Nothing auto-tags** - a session proposes at most one seat in one line, and only your yes writes the field, exactly as the registry itself works. And **a tag adds no ownership rule**: the fold happens inside the render, so the body digest already in each agent file's marker covers it. Tag a note and the seat reads `[stale]`; `apply` converges it; a seat file you edited by hand stays `[modified]` and is never overwritten. An install where nothing is tagged renders precisely the files it rendered before.

## Honest status, always

A row exists only for something that exists. Three states:

- `active` - runs today, and there is evidence (runs recorded, or items it filed)
- `stale` - exists but is not currently earning its seat. Say why in the description.
- `gated` - defined and approved, but not yet wired to anything that triggers it

The failure this prevents: an org chart full of impressive-sounding jobs, none of which have ever run. A registry that lies is worse than no registry.

This is why the five starter roles the OS installs all arrive `gated`, and why none of them may be marked `active` by anything except you, after you have seen a run. A gated row makes a claim you can check in ten seconds: open the skill it names and it is there. An active row makes a claim about the past, and only a run can back that. Seeding the first kind is an introduction. Seeding the second would be the lie this section exists to stop.

## Propose-only and draft-only are different constraints

Two shapes of restraint get called the same thing and the difference decides the tool grant.

A **propose-only** job writes nothing. It hands you a ranked list, a diff, or a recommendation, and you act on it. It holds no write tool at all, and the charter audit treats a write tool on a job that calls itself propose-only as a finding rather than a preference.

A **draft-only** job writes a file - a client update, a filed capture, an answer landing in the file that owns it - and stops before anything leaves your machine. It needs a write tool to do its job. What constrains it is `may_write` naming the exact files and `never` naming the delivery it must not do.

Both are real constraints. Say in the job description which one a row is, then grant to match. A row that claims the stricter one and takes the looser grant is how "never sends" quietly becomes a wish, which is the failure the section above already warned about, arriving through the other door.

One seam worth naming. When you approve a propose-only job's diff, the edit that lands is yours: applied in your session, on your yes, with your tools. The role never held the pen. Approval moved the act to you, which is why a reviewer that "writes nothing" can still end with the registry updated - you updated it.

## How a job gets created (the shape ladder)

The Chief of Staff's door is the `hire` skill, and the discipline behind it fits in one line: **pick the smallest shape that removes the job, and say what the next size up would have bought.** Six shapes, cheapest first: an answer, a preference line, a skill, a script, a chartered seat, a team. Most recurring pains die at rung 1 to 4 and never needed a team - and a founder who is told that, with the reason, trusts the one hire that IS proposed.

Two rules ride the ladder. Split the job into stages before picking, because most real workflows are a deterministic spine (code, rung 4) with one or two judgment stages (rung 5) - paying model tokens to re-decide a solved filing step is how a team gets expensive without getting better. And manual-first at rung 5 and 6: a job nobody has run by hand gets run by hand once or twice before a seat takes it over. Effectiveness before efficiency.

**A team is a workflow whose handoffs you can read.** One seat per judgment stage, one job per seat, and the relationship between specialists is the handoff artifact: stage B's read-list names stage A's output, so the run log reads back as a relay - who did what, in what order, where the baton was dropped. The operator manages the team the same way they manage one seat: talk to a seat by name (its agent file), change its standing instructions by editing its row, judge it by its runs and verdicts, fire it by retiring the row. There is no second management surface to learn.

Every proposed hire carries an informed-choice passport before the yes: what it may touch, what it never does, what it costs to run, what leaves the machine (nothing, unless a connector is named), and how to fire it. The passport exists because the person hiring is often new to all of this, and a yes given without knowing those five things is not consent, it is hope.

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

Setup installs five roles and every one of them is `gated`. They are not a roster you built, they are the jobs this OS already knows how to do, written in role language so you can see what you have: someone who runs your morning, someone who names your next move, someone who files what you captured, someone who writes the client update, and someone who reviews the other four.

Run one. Record a verdict on what you saw. Move it to `active` when there is a run behind it, mark it `stale` with a reason when there is not, or delete a starter row you know you will never use. Any of those three is honest; leaving five rows sitting `gated` for six months is also honest, just idle.

Adding a sixth is the older rule and it has not changed. When a job has recurred three times and you have corrected it twice, that is the job worth writing your own row for.
