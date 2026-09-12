---
why: "Sooner or later you want your OS to do something it has no idea how to do - produce video, design, run deep research. The two obvious moves both go badly: copy the outside tool into your OS, or wire yourself so tightly into it that swapping is a rebuild. This names the layering that avoids both, the five things your own layer has to carry, and the preflight that keeps the answer honest when the tool is only half installed."
---

# Adding a big outside capability

Your brain is the asset. The hands swap out. That is easy to say when the hand is a recorder or a mail integration. It gets harder when the hand is a whole system with its own skills, its own pipelines, and more files than your OS has.

The instinct at that point is to absorb it. Do not.

## The two wrong moves

**Copying it in.** You clone the tool's skills into your OS so everything is in one place. Now your repo is mostly someone else's project, their next release is a merge conflict, and if their licence differs from yours you have a problem that is not fixable by deleting the folder later.

**Wiring into it.** You write your OS around that tool's specific commands and file layout. Now switching costs a rebuild, and you have quietly given one vendor a veto over a capability you thought you owned.

## The three layers

Think of any capability as three layers, and be strict about which one is yours.

| Layer | Who owns it | What it answers |
|---|---|---|
| 1 - the tools | the outside tool | what exists, what it costs, what is installed right now |
| 2 - **how YOUR OS uses it** | **you** | when to reach for it, what to do first, what is allowed |
| 3 - how the tool works | the outside tool | provider quirks, parameters, the craft of that domain |

You own layer 2 and nothing else. Read layers 1 and 3 in place, in the tool's own folder. Never copy them.

Layer 2 is small. It is usually one skill file. And it is the only layer that knows anything worth knowing about you.

## The five things your layer must carry

A general-purpose tool cannot know these. That is the whole reason your layer exists.

1. **Preflight, and an honest verdict.** Before anything else, check what is actually installed and say so in one line. A tool with no credentials configured is not broken, it is limited, and those are different sentences. Name what the limited version genuinely does. Say the verdict before you plan, not after you have described work the install cannot do. This is the same habit as [hands resilience](hands-resilience.md), applied at a bigger size.

2. **Routing.** Half the requests that reach the new capability belong somewhere you already have. Write the routing table before you write anything else: this ask goes to the thing you already built, that one goes to the outside tool. Naming the cheaper path you already own is a better answer than a plan.

3. **A money gate.** If the tool spends, every paid call names the tool, the provider, the model, and the cost estimate before it runs. Then one rule above all others: **sample before batch.** One cheapest-viable attempt, shown to you, before anything that multiplies that cost. Discovering the style was wrong on attempt twelve is how a budget disappears.

4. **A privacy line.** A cloud call sends your input off the machine. Write down what may never go into one: client names, anything from your client folders, your own numbers. If real client work is genuinely in scope, the brief goes in anonymized and the real details go in locally at the end. Decide this before the first run, not during it.

5. **Where finished work lands.** The outside tool writes into its own working folder. Nothing is delivered while it lives only there. Name the folder in your OS where the finished pieces belong, and copy them there as the closing act.

## Where the outside tool lives

**Beside your OS, not inside it.** A sibling folder next to your OS repo, cloned from its own source, updated with its own `git pull`.

Three reasons, and any one of them is enough. Licences differ and copying files across that line is not something you can undo later. Their release cadence stays theirs. And when you swap the tool for a better one next year, you delete a folder and rewrite one skill, rather than picking their files out of yours.

Your OS refers to it by path. That is the entire coupling.

## Split the seats

A capability that spends money or produces something public wants three jobs, not one. This is the [digital employees](digital-employees.md) pattern at work.

- **The one who plans.** Intake, picks the approach, writes the plan and what it costs. Proposes only. Never spends, ever.
- **The one who runs it.** Works only from a plan you approved by name. Samples before batching. Stops at every paid step.
- **The one who checks it.** Looks at the actual output, against your voice and your standards. Changes nothing, recommends everything.

Keeping the planner away from the spending is what makes the plan honest. A job that can both propose and pay will find reasons to pay.

## Recommended tool - video production

For video, the one worth pointing at is **OpenMontage**: <https://github.com/calesthio/OpenMontage>

It is an instruction-driven video production system, which is to say it is built the same way this OS is: manifests and markdown skills carry the intelligence, and its code holds only tools and saved state. It ships pipelines for explainers, talking-head, screen demos, clip extraction from long recordings, and dubbing. It has a real zero-credential path - free stock footage, local transcription, ffmpeg, and a browser-based renderer - so it clears the floor this OS holds itself to.

Two things to know before you install it. It is licensed AGPL-3.0 and this OS is MIT, so it is a tool you install beside your OS and never a folder you copy from. And it can spend real money through paid providers once you add credentials, which is what the money gate above is for.

This repo ships no bridge to it and no vendored copy. Write your own layer 2 skill using the five points above, and the pattern works the same for any other outside capability you add later.
