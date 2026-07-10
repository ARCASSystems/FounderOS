# Why local-first - the security story, with receipts

You are about to give an AI system your priorities, your clients, your numbers, and your half-formed decisions. "Is that safe?" is the right question. This page answers it with the 2026 record, not with adjectives.

## What happened when this went wrong elsewhere

In early 2026 the most popular open-source AI agent framework, OpenClaw, produced the year's defining AI security incident. The public record, from independent security researchers:

- **135,000+ instances exposed to the public internet** across 82 countries, roughly 12,800 of them exploitable by remote code execution ([The Register](https://www.theregister.com/2026/02/05/openclaw_skills_marketplace_leaky_security/)).
- **API keys in plaintext files** (`.env` files and credential folders on disk) readable by anything that could read the machine, and around **1.5 million API tokens exposed** through one companion-service database misconfiguration.
- **A poisoned skills marketplace.** An audit found roughly **12% of marketplace skills were malicious**, and separate research found 283 more that leaked credentials by design - functional, popular skills instructing the agent to pass keys and passwords through logs in plaintext ([Snyk](https://snyk.io/blog/openclaw-skills-credential-leaks-research/), [Backslash](https://www.backslash.security/blog/openclaw-security-risks-explained)).

Read the failure modes closely. Every one of them required at least one of three things: **a server listening on a port**, **a stored API key file**, or **a third-party skill registry** pulling unreviewed code onto the machine.

## Founder OS has none of the three

Not because it is better-audited. Because the attack surface is not there.

- **No server.** Nothing listens. The OS runs only when you open a session and stops when you close it. There is no port to scan, no exposed instance to find, no process running while you sleep. (This is also why the OS never claims background behavior - the honesty and the security are the same design decision.)
- **No API key file.** The OS runs on your Claude subscription through Claude Code's own sign-in. There is no `.env` with a model key, because there is no model key. The one guard that handles names (`scripts/private-name-patterns.txt`) is gitignored and contains no secrets. Optional extras that DO need a key (a realtime voice tier, a Telegram connector) store it gitignored-only, ask first, and are never defaults.
- **No marketplace supply chain.** Every skill ships in this repo as readable markdown. You can open any of them and read exactly what it does before it ever runs - there is no registry, no auto-installed third-party skill, no code you did not choose. The privacy pre-commit guard blocks secrets, private names, and AI-attribution from ever leaving in a commit.
- **Your data lives on your laptop.** The brain is plain markdown files on your disk. Reading them into a session sends them to the model under your subscription's terms, the same as any Claude conversation - but no product server, no telemetry, no sync service ever sees them. Deleting the OS is deleting a folder.

Same file-based brain the agent frameworks promise. None of the three doors the 2026 incident walked through.

## The honest limits

Local-first is a smaller attack surface, not a force field.

- **Your laptop is the perimeter.** Disk encryption, OS updates, and screen locks matter more than anything in this repo.
- **MCP connectors are your choice.** Each tool you connect (calendar, email, notes) extends what a session can reach. The OS treats every write path behind a connector as gated - but connect only what you use, and read `rules/approval-gates.md` for what auto-runs versus what always asks.
- **A cloud session is a different posture.** Claude Code's cloud path runs in a remote sandbox on a branch. Useful when you are away from the machine; it is opt-in per use, and the local path stays the default.

## For the power user: the repo is the sync contract

If you ever run the OS on more than one machine, or hand execution to another agent (a home server doing video renders, a second laptop, a coding agent doing builds), you do not need a sync product. The repo itself is the contract: any agent that can run git can pull the brain, do its work, and push the result back. Transport costs zero tokens, works over plain git remotes you own, and keeps the same audit trail as everything else. That is a documentation-tier pattern, not a product feature - nothing in the OS phones a server, including this.

---

Sources: [The Register, Feb 2026](https://www.theregister.com/2026/02/05/openclaw_skills_marketplace_leaky_security/) - [Snyk Research](https://snyk.io/blog/openclaw-skills-credential-leaks-research/) - [Backslash Security](https://www.backslash.security/blog/openclaw-security-risks-explained). Figures are the researchers' published counts at the time of writing; the pattern, not the precise numbers, is the lesson.
