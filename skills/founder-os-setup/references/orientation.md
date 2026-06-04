# Setup - Phase 6: Validate and Orient

Load this last. It commits the build, detects the command prefix, opens with the operator's profile, walks the natural-language orientation, and saves the backlog. The personalization principle that governs the whole wizard sits at the end. Return to the router (`SKILL.md`) for the phase order.

---

## PHASE 6: VALIDATE + ORIENT

### 6.1 Final Commit
Commit all company and project folders: "Add company folders and first project setup."

### 6.2 Orient the User
Show the user what they have AND the next two profile steps. The wizard creates the operating layer, but the writing skills are gated on the voice and brand profiles - tell them this directly.

**Detect the command prefix first.** Path A (plugin install) uses the `/founder-os:` namespace. Path B (manual git clone) uses bare command names because the plugin namespace is not active. The orientation must show the right form for the path the user actually used:

- Check whether `.claude-plugin/marketplace.json` exists at the user's current working directory.
- If it exists, treat this as Path B and set `<prefix>` to a single forward slash `/`. The orientation below uses `<prefix>voice-interview`, which substitutes to `/voice-interview` (a real command on Path B).
- If it does not exist, treat this as Path A and set `<prefix>` to `/founder-os:`. The orientation below uses `<prefix>voice-interview`, which substitutes to `/founder-os:voice-interview`.
- A small set of commands are always bare on both paths and never take the prefix: `/today`, `/next`, `/pre-meeting`, `/capture-meeting`. Render those as written.
- If the heuristic is ambiguous (both signals present, or neither), default to Path A and add a one-line note in the orientation: "If a command is not recognised, drop the `/founder-os:` prefix - you are on the manual-clone path."

When you render the orientation block below, substitute every `<prefix>` literally with the detected value before showing it to the user. Do not show the placeholder text. Verify the rendered output before sending: every backtick-wrapped command must start with a `/` and must match a real file in `.claude/commands/` (Path B) or a namespaced plugin command (Path A).

**Voice and pattern in the orientation: lead with natural language.** Real users will not memorize a 20-command surface. The orientation tells the founder how to talk to Claude in plain English. Slash commands appear in parentheses as optional shortcuts for power users. Do not invert this. Anti-pattern: "Run `<prefix>voice-interview` to set up your voice." Pattern: "Say 'set up my voice' (or run `<prefix>voice-interview` if you prefer slash commands)."

**Open with their profile.** Read `core/profile.md` (written in Phase 1.1.5). Open the orientation with the operator's `frame` in one line, then point them at their `lead surfaces` first - the files and skills their variant needs - before the generic walkthrough below. A career-mover should hear about their positioning and proof-of-value record before they hear about pipeline cadence; a student should hear about capture and recall first. The generic block below still applies to everyone; the profile only decides what leads. Say once that the variant changes nothing about what is available - every skill works for them - and that they can change it any time by saying "update my profile".

"Your Founder OS is set up. The operating layer is live. Two more 10-minute steps activate the writing skills:

**Step 1 - Voice profile.** Say "set up my voice profile" (or run `<prefix>voice-interview`). The interview captures how you write. After this, linkedin-post, client-update, proposal-writer, email-drafter, content-repurposer, sop-writer, and your-voice all write as you instead of as Claude. ~10 minutes.

**Step 2 - Brand profile.** Say "set up my brand profile" (or run `<prefix>brand-interview`). Captures your visual brand (colors, fonts, logo). After this, your-deliverable-template, branded proposals, and branded client updates render in your visual identity. ~10 minutes.

**Step 3 - Check readiness.** Say "check my OS readiness" (or run `<prefix>status`). Returns a 0-100% score across Core, Voice and Brand, Cadence, Business Context, and Brain Layer. Names the next 3 high-impact moves.

**Optional - Legal compliance.** If your business has regulatory, tax, or employment compliance requirements, say "set up legal compliance" (or run `<prefix>legal-setup`). This activates jurisdiction-aware legal guidance and deadline tracking in the SessionStart brief. ~5 minutes.

Then start using it. You do not need to memorize commands - just talk to Claude.

**Your words map to OS files. Use whichever you prefer.**

- "my journal", "diary", "notes to self" → `brain/log.md` (the brain log)
- "my schedule", "this week's plan", "what I'm working on this week" → `cadence/weekly-commitments.md` (the weekly sprint)
- "my goals", "what matters this quarter" → `context/priorities.md`
- "my customers", "prospects", "leads" → `context/clients.md`
- "rants", "dumps", "vents" → `brain/rants/`
- "ideas to follow up on" → `brain/flags.md` (the open-loop flag channel)

You never need to use the OS terms. Say what feels natural.

**Daily:** Open Claude Code in your Founder OS folder. Ask "what's on for today?" (or run `/today`) for a one-screen view, or ask "what should I focus on next?" (or run `/next`) for one recommended action.

**Weekly:** Say "run my weekly review." Claude rolls the sprint, does the retro, and sets the next week.

**When overwhelmed:** Say "I'm overwhelmed" or "what should I focus on" - Claude triages your priorities.

**When you learn something:** Say "capture this" or "log this" - goes into your brain system.

**When you've been dumping rants:** Say "process my rants" (or run `<prefix>dream`). The OS distils your rants into patterns, flags, parked decisions, and one recommended action. The SessionStart brief will also nudge you when 3 or more rants pile up.

**Before meetings:** Say "prep me for my call with [name]" - Claude builds a brief.

**When you have a post / email / proposal to write:** Just ask. After the voice profile is filled, every output is in your voice.

**When making decisions:** Say "help me decide" - Claude walks you through a structured framework.

**When the OS gives you an opinion:** It comes with a counter-case and a confidence level on purpose. The OS argues the other side of your own plan so you decide with the counter in front of you, the way a good advisor disagrees with you sometimes. That is the OS working, not the OS being difficult. To turn that lens on any claim or decision yourself, say "play devil's advocate" (or run `<prefix>devil`).

**End of every session:** Claude commits changes. Your repo is your memory.

**To audit anytime:** Say "audit the OS" (or run `<prefix>audit`) for the composite health report across readiness, lint, wiki, brain staleness, and voice.

**To remove cleanly:** Say "uninstall Founder OS" (or run `<prefix>uninstall`). Default preserves your data; add --purge to wipe everything.

**Your folder structure:**
- Open `[founder-os-root]/` for strategic work
- Open `[company]/[project]/` for execution work
- Claude loads the right context based on where you are."

### 6.3 Backlog
Show any skipped or deferred items from the setup. Save them to `core/setup-backlog.md` as a simple markdown list under the heading `## Setup Backlog`. Create the file if it does not exist. Do not scatter deferred items across other files.

---

## Personalization Approach

Templates are structural guides, not copy-paste sources. When you read a template, understand its structure and sections, then generate a personalized version using the founder's discovery answers.

Adapt phrasing to match the founder's communication style from 0.7. Skip sections that don't apply (e.g., if they have no team, skip team-related sections in operating rules). Add context-specific content where the template has placeholders.
