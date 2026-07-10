# Setup - Phase 6: Validate and Orient

Load this last. It commits the build, detects the command prefix, opens with the operator's profile, walks the natural-language orientation, and saves the backlog. The personalization principle that governs the whole wizard sits at the end. Return to the router (`SKILL.md`) for the phase order.

---

## PHASE 6: VALIDATE + ORIENT

### 6.1 Final Commit
Commit all company and project folders: "Add company folders and first project setup."

If version history is off (no git on the machine - Phase 2.3 already said so), skip the commit silently. The tour below makes the one graduation offer; do not nag about git anywhere else.

### 6.2.0 Post-setup tour (show them what they now own)

Setup just created a few dozen files silently. A non-technical founder will not go looking for them and will not trust a system they cannot see. Before the longer orientation, run a short tour that makes the new OS visible and proves the brain captured something real. Keep it warm and concrete. Do not list all forty files - list the handful they will actually touch.

**1. Reflect the Founder Snapshot back (founder / team_of_one only).** If Phase 0.2.6 ran, read the four fields you just wrote to `core/identity.md` `## Founder Snapshot` and say them back in plain language. This is the moment the founder sees their own brain on the page:

> "Here is what your OS now knows about you and your venture:
> - Venture: [venture one-liner]
> - Customer: [customer]
> - Where you are: [stage in plain words]
> - Biggest blocker: [biggest blocker]
>
> That is enough for the OS to start proposing real moves. It gets sharper every time you use it."

If any of the four is `[NOT SET]`, say so honestly and offer the one-line fix: "Your biggest blocker is still blank - tell me in one line any time and I will add it." Do not paper over a blank with a guess. For non-founder variants (no Founder Snapshot), skip this point.

**1.5 Run the first real proposal, in the flow (founder / team_of_one only).** Do not hand them an artifact to open somewhere else - the value is in the flow they are already in. Run the `founder-next-move` skill now: it reads the snapshot you just wrote and names the single highest-leverage move toward a paying customer, closing with one big and two small steps. This is the founder's first taste of the actual product - their own brain producing a decision, thirty seconds after it was born. Then say one line about how it compounds, because compounding IS the product:

> "That move came from four lines your brain holds right now. Every session adds to it - what you did, what stalled, what you decided - and the moves get sharper because they are read from your real state, not guessed. Six months from now this same question reads a brain that knows your whole business."

If the snapshot is too thin for a real move (no customer set), the skill already handles that by asking for the missing field - that ask is the move. For non-founder variants, skip this point entirely.

**2. Show the six files they now own.** Name them with a one-line, plain-English purpose each. These are the files a founder actually opens, not the engine files:

> "Six files run your day. They are plain text on your machine - yours to read, edit, back up, or move:
> - `core/identity.md` - who you are and your venture snapshot
> - `context/priorities.md` - what matters right now
> - `cadence/weekly-commitments.md` - this week's plan
> - `brain/log.md` - your running journal, the OS's memory
> - `context/clients.md` - your customers and pipeline
> - `brain/flags.md` - open loops and things to come back to
>
> You never have to edit these by hand. Just talk to the OS and it keeps them current. But they are there, in the open, whenever you want to look."

**2.5 Own your history (only when version history is off).** If the machine has no git (Phase 2.3 skipped init), make the graduation offer exactly once, here, in the tour - warm, consent-gated, zero pressure:

> "One optional thing, whenever you are ready: full version history. Right now every change the OS makes is snapshotted per session, so undo works. If you also want a permanent timeline - 'undo to before this morning', a full history of every save - just say 'own my history'. I will install the version tool quietly and set it all up myself. One yes, nothing for you to type, and the whole history lives in this folder on your disk - version history sends nothing anywhere. No rush; the OS is complete either way."

If they say yes on the spot, run the `own-your-history` skill now and return to the tour when it finishes. If they say nothing or move on, drop it - the offer stays available as a plain sentence forever.

**3. The three things to say next.** Give the founder exactly three next moves, in natural language, so they leave with something to do instead of a blank screen:

> "Three things to try right now:
> 1. Ask 'what should I focus on next?' (or run `/next`) - the OS gives you one recommended move toward your next paying customer.
> 2. Ask 'what's on for today?' (or run `/today`) - a one-screen view of your day.
> 3. Say 'set up my voice' - a 10-minute step so every post, email, and proposal the OS writes sounds like you, not like a robot. (The exact command is in the next message.)"

Keep the three to three. More than three next steps is the overwhelm this OS exists to remove. The voice step is also covered in 6.2 Step 1 with the path-correct command, so here it stays natural-language only and does not need the prefix.

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

### 6.2.9 Prove it worked (automatic health check - do not skip)

Setup just built a few dozen files, copied the Python hook dispatcher and its helper scripts, and wired all six hook events through it. A non-technical founder cannot see whether any of that actually landed, and the hooks fail silently by design - so a half-copied script or a missing Python would stay invisible until a skill breaks days later mid-task. Do not let the founder leave on trust. Run the `verify` skill now, automatically, before the finish line. This is the product living its own rule: no "you are ready" without a check that says so.

Run `verify` and show the founder its one-screen report (the eight substrate checks, each `[PASS]` / `[WARN]` / `[FAIL]`). Then read the result out loud in one plain line:

- **All PASS (or PASS with benign WARNs like no MCPs configured or the opt-in observation hook off):** "Checked it end to end - your OS is wired correctly and working." Then go to 6.3.
- **Any FAIL:** name it plainly and fix it before declaring the finish line. A `[FAIL] Scripts present` usually means a script did not copy (re-run the Phase 2 hook/script copy) or Python is not installed (none of `python --version`, `python3 --version`, `py -3 --version` answers - point them at [python.org/downloads](https://www.python.org/downloads/), 3.11+, then re-run `verify`). A `[FAIL] Hooks installed` means the settings/hook copy did not complete. Do not paper over a FAIL with reassurance - a silent partial install is the one failure this whole OS exists to prevent.

Keep it to the report plus one or two lines of plain reading. Do not turn a clean result into a lecture.

### 6.3 Backlog and finish line
Show any skipped or deferred items from the setup. Save them to `core/setup-backlog.md` as a simple markdown list under the heading `## Setup Backlog`. Create the file if it does not exist. Do not scatter deferred items across other files.

Echo the backlog back in the session, split so the founder knows what actually blocks them versus what can wait:

> "A few things we skipped, saved to `core/setup-backlog.md`:
> - **Worth doing before your first proposal or post:** [any `[NOT SET]` positioning, voice, or brand items]
> - **Whenever you like:** [observation logging, the private-name guard, other optional items]"

If nothing was skipped, say so in one line and move on. Do not invent backlog items to fill the list.

**Then close with an explicit finish line.** A non-technical founder needs to be told they are done, or they wait for a next step that never comes:

> "That is setup, and it checked out - the health check above confirms the OS is wired correctly. Your Founder OS is live. Next time you open Claude Code in this folder, the SessionStart brief surfaces your week in one screen. You are ready to work - ask 'what should I focus on next?' whenever you are."

---

## Personalization Approach

Templates are structural guides, not copy-paste sources. When you read a template, understand its structure and sections, then generate a personalized version using the founder's discovery answers.

Adapt phrasing to match the founder's communication style from 0.7. Skip sections that don't apply (e.g., if they have no team, skip team-related sections in operating rules). Add context-specific content where the template has placeholders.
