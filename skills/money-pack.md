# Money Pack

A logical pack, not a folder. Claude Code discovers skills as top-level directories under `skills/`, so the pack is held together by convention and by the links in this manifest rather than by nesting. The members do not share a name prefix; this manifest reads them as one connected unit.

This is the finance function for a founder who does their own numbers. It covers the path from "is this worth it" to a defensible answer: pricing, margins, break-even, and where the business actually leaks time or money.

## The front door

[unit-economics](unit-economics/SKILL.md) is the entry. Unlike the other packs, the Money pack has no separate wedge skill; the front door is the workhorse itself. Say "run the numbers", "what should I charge", "is this profitable", or "what's the break-even". It runs the business math and routes to the other members when a question needs a finance import or a bottleneck read first.

## What the pack is

You bring a pricing question, a deal to test, a hire to weigh, or a finance export to make sense of. The pack gives you the math: CAC, LTV, margins, break-even, pricing models, and an honest read of where you are the bottleneck. Everything runs locally and free, on plain arithmetic the OS shows its working for. No black-box number, no invented benchmark.

## The outcomes and the skills behind them

| Outcome | Skill | Status |
| --- | --- | --- |
| Front door (run the numbers) | [unit-economics](unit-economics/SKILL.md) | Ready |
| Turn a finance export into a summary | [finance-import](finance-import/SKILL.md) | Ready |
| Find where you are the bottleneck | [bottleneck-diagnostic](bottleneck-diagnostic/SKILL.md) | Ready |
| Load context for a company you run | [business-context-loader](business-context-loader/SKILL.md) | Ready |

## The shared input

The pack's shared input is your own data. [finance-import](finance-import/SKILL.md) parses a finance CSV export into a normalised summary at `finance/<period>/summary.md`, which `unit-economics` then reads instead of asking you to type numbers from memory. Feeding real figures in is what turns a generic model into your actual economics.

## Honest about the limits

The OS does the math and shows its working; it does not connect to your bank, pull live figures, or invent an industry benchmark you did not give it. A number is only as good as the inputs you provide, and the pack says so rather than dressing up a guess as a forecast. Its strength is fast, honest, transparent business math on your real figures.

## Dependencies between members

- `unit-economics` reads `finance/<period>/summary.md` when `finance-import` has produced one; without it, you supply the figures inline.
- `bottleneck-diagnostic` is a self-assessment that needs no prior file; it pairs with `unit-economics` when the question is "where is the money or time going".
- `business-context-loader` supplies company context so the math is grounded in a real operation, not an abstract one.
