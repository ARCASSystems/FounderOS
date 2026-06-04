# Setup - Phase 0.0 and Phase 0: Frame and Discovery

Load this when you start the wizard. It covers the framing contract and the full discovery interview. Ask ONE question at a time and wait for the answer. Return to the router (`SKILL.md`) for the phase order.

---

## Phase 0.0: Frame what you're getting (always run first)

Open with this in one short turn before any discovery questions. Without it, users who arrived via "help me set up my second brain" leave the wizard with a mental model the product does not deliver.

Say (verbatim, or close paraphrase matching the user's tone):

> "Founder OS is your personal second brain. Your files, on your machine, queryable by you across sessions. It captures the judgment that currently lives only in your head.
>
> What it is NOT, by design: not team-shared (your team would install their own, the files do not merge), not always-on (no background agents, no notifications while you sleep). Both could ship later. Neither ships today.
>
> Want to keep going?"

Routing:

- If the user says "yes" / "go" / "continue" / any positive signal: proceed to Phase 0.1.
- If the user asks a question first: answer it briefly, then ask the framing question again. Do not start Phase 0.1 until you have a clean yes.
- If the user says they wanted team-shared or always-on: name the gap honestly. "That's not what Founder OS ships today. The personal version installs in 15 minutes. Want that, or stop here?" Respect a stop.

Do not skip this phase. Users who arrived via "set up Founder OS" benefit from the reset too - "Founder OS" is ambiguous to a first-time reader and the rest of the wizard assumes a clean expectation contract.

---

## PHASE 0: DISCOVERY

Ask these questions one at a time. Record answers internally.

### 0.1 Who Are You?
Ask: "Let's set up your Founder OS. First - what's your name, and what do you do? Give me the one-sentence version of your business (or businesses if you run more than one)."

### 0.2 Business Map
If they mentioned multiple businesses, ask for each: "For each business, tell me: name, what it does in one sentence, and who else is involved (co-founders, key team members, or just you)."

If they have one business, move to 0.2.1.

### 0.2.1 Your Role

Ask: "What best describes your role?
1. Founder - you own the business
2. Operator - you run operations for someone else's business
3. Team-of-one - solo creator, freelancer, or independent professional (no employees, no investors)

Pick the closest. The OS adapts to your role - it does not assume you are a founder."

Record the answer as `role` internally. Map to a token:

- "1" / "founder" / "own" / "my business" / "I run it" → `founder`
- "2" / "operator" / "working for" / "reporting to" / "not my company" → `operator`
- "3" / "freelancer" / "solo" / "creator" / "independent" / "team of one" → `team_of_one`
- Unclear or no answer → `founder` (safe default)

Store `role:` in `core/identity.md` under a `## Role` field. This value drives downstream question phrasing and the bootloader `{{role_noun}}` substitution in Phase 2.2.

### 0.2.2 Meet you where you are

Before the rest of discovery, take one read on WHO is using this OS and say it back. This is the moment the OS adapts to the person instead of assuming everyone is a founder. Keep it to one line and one question. Do not turn it into a form.

From the name, business, and role captured so far, infer a provisional variant using the `profile-router` skill's signal table (founder / career-mover / builder / student / team-internal). State the pick and the lead it implies, then ask for a yes or an adjustment.

Phrasing examples (match the user's tone):

- founder: "Sounds like you run the business and carry most of it yourself. I will lead with your pipeline, your week, and the decisions you are sitting on. That right?"
- career-mover: "Sounds like you are moving between roles. I will lead with your positioning and a record of your wins you can carry anywhere. That right?"
- builder: "Sounds like you are heads-down building something. I will lead with one-thing-at-a-time focus and a finish line. That right?"
- student: "Sounds like you are here to learn and remember. I will lead with capture and recall. That right?"
- team-internal: "Sounds like you want this for a team. Founder OS installs per person today, so I will set you up as an individual operator and note the team interest. That work?"

Record the provisional variant internally. Do NOT write any file yet. The priorities (0.4) and work-style (0.7) answers may refine it; you finalise and write `core/profile.md` in Phase 1.1.5. If the user corrects your read, take the correction as the variant.

This is a soft touch, not a gate. If the user does not engage, keep the provisional read and move on. Never block discovery on it.

### 0.2.5 Positioning

Ask three short positioning questions in sequence. One question, one line. Each is skip-able. Wait for the answer before moving to the next unless the user dumps all three answers at once.

Use the role captured in Phase 0.2.1 to branch the phrasing of each question:

**Q1 - "Who do you sell to?"**
- founder / team_of_one: "Who do you sell to in one sentence? You can say skip."
- operator: "Who does your company sell to in one sentence? You can say skip."

**Q2 - "What do you sell?"**
- founder / team_of_one: "What do you sell in one sentence? You can say skip."
- operator: "What does your company sell in one sentence? You can say skip."

**Q3 - "What pain does your buyer feel?"**
- founder / team_of_one: "What visible pain does your buyer feel before they come to you? You can say skip."
- operator: "What pain does your company's typical buyer feel before they come to you? You can say skip."

These answers populate `core/identity.md` under `## Positioning`, which `linkedin-post`, `proposal-writer`, `client-update`, and `business-context-loader` read before drafting. If the user says "skip", write `[NOT SET]` for that line and continue.

**Backward compatibility (parse-everything-at-once path).** If the founder answers with all three in one reply ("I sell to UAE SMEs, I sell brand and web projects, they feel embarrassed by a website that no longer matches the business"), parse all three, mark the section answered, and skip the remaining prompts in this phase. Confirm what was captured in one line. Do not re-ask.

### 0.3 Active Workstreams
For EACH business: "What are you actively working on right now in [business name]? Examples: website, email campaigns, lead generation, content, product development, client delivery, hiring."

Each workstream becomes a potential project folder.

### 0.4 Immediate Priorities
Ask: "Of everything you just listed, what are the top 3 things you need Claude helping with THIS WEEK? Be specific."

These get built first. Everything else is structure for later.

### 0.5 Tool Stack

Ask four short multi-choice prompts in sequence. One question, one line of options. No preamble between them. Wait for the answer before moving to the next.

1. "Where do you store written knowledge? Notion / Obsidian / Google Drive / local files only / other / skip."
2. "What email do you use for work? Gmail / Outlook / Apple Mail / other / none / skip."
3. "What calendar do you use? Google Calendar / Outlook / Apple Calendar / other / none / skip."
4. "Where do you track customers, subscribers, or your pipeline? Notion DB / HubSpot / Airtable / subscriber list (Mailchimp, Klaviyo, ConvertKit) / spreadsheet / nothing yet / skip."

5. "What's your main channel for reaching customers or your audience? LinkedIn / Instagram / YouTube / email newsletter / other / skip."

Map each answer to the exact lowercase token from `stack.json`'s `_allowed_values`:

- Knowledge base -> `knowledge_base` (notion / obsidian / google_drive / local). "other" or unrecognised tool -> `null` and log the actual name in the backlog.
- Email -> `email_platform` (gmail / outlook / apple_mail). "none" or "other" -> `null`.
- Calendar -> `calendar` (google_calendar / outlook_calendar). Apple Calendar / "other" / "none" -> `null` and log to backlog.
- CRM or pipeline -> `crm` (notion_db / hubspot / airtable / none). "spreadsheet" -> `null` with a backlog note. "nothing yet" -> `none`. "subscriber list" or any email marketing platform (Mailchimp, Klaviyo, ConvertKit) -> `crm: null` and log to backlog: "Subscriber platform: <tool_name>. B2C audience tool - not a sales CRM."
- Primary channel (Q5) -> `primary_channel` (linkedin / instagram / youtube / email_newsletter). "other" -> `null` and log the actual platform name in the backlog. "skip" -> `null`.

"skip" on any prompt records `null` for that field and continues. No "are you sure?" follow-up. No re-ask later in the wizard.

The other eight `stack.json` fields (`automation_platform`, `file_storage`, `meeting_notes`, `voice_input`, `server`, `prospecting_db`, `video_tool`, `booking`) stay `null` by default. If the founder dumps additional tool names in any earlier or later phase ("I use n8n and Granola"), parse them into the matching fields. They are not asked individually because they are not load-bearing for first-run output skills.

**Backward compatibility (parse-everything-at-once path).** If the founder replies to the first prompt with multiple tools in one shot ("Notion, Gmail, Google Calendar, no CRM"), parse all of it, populate every matching field, and skip the remaining prompts in this phase. Confirm what was captured in one line. Do not re-ask.

These fields populate `stack.json`, which sop-writer, meeting-prep, email-drafter, and other skills read at runtime to tailor output to the founder's actual stack. The full write happens in Phase 5.0.

### 0.6 Existing Setup Audit
Before proceeding, scan the filesystem silently:
- Read `~/.claude/CLAUDE.md` if it exists
- Read `~/.claude/settings.json` if it exists
- Check common project folder locations for existing CLAUDE.md files

Report what you found. This prevents duplication.

### 0.7 How You Work

Ask four short multi-choice prompts in sequence. One question, one line of options. No preamble between them. Wait for the answer before moving to the next.

1. "When do you do your best deep work? Morning / afternoon / evening / variable / skip."
2. "How do you usually make decisions? Gut / data / dialogue with someone / mixed / skip."
3. "How do you prefer Claude to communicate with you? Direct and short / detailed and explanatory / skip."
4. "What overwhelms you most? Too many open loops / unclear next step / context switching / decision fatigue / other / skip."

"skip" on any prompt records `null` for that field and continues. No "are you sure?" follow-up.

**Backward compatibility (parse-everything-at-once path).** If the founder dumps all four answers in one reply ("morning, gut, direct, too many open loops"), parse them, mark all four as answered, and skip the remaining prompts in this phase. Confirm what was captured in one line.

These answers personalize the operating rules and identity file.

**Encoding (mandatory).** Map the answers to these structured tokens. Skills downstream read the tokens, not the prose. "skip" on any prompt records `null` for that field.

Deep work time:

- "morning" -> `morning`
- "afternoon" -> `afternoon`
- "evening" -> `evening`
- "variable" / unclear -> `variable`

Decision style:

- "gut" / "gut feel" / "instinct" / "feel" -> `gut`
- "data" / "spreadsheets" / "numbers" / "math first" -> `data`
- "dialogue" / "talk it through" / "out loud" / "sounding board" -> `dialogue`
- "mixed" / unclear -> `mixed`

Communication style:

- "direct" / "short" / "lead with the answer" / "no filler" -> `direct`
- "detailed" / "thorough" / "context first" / "build up" / "explanatory" -> `detailed`

What overwhelms you:

- "too many open loops" -> `open_loops`
- "unclear next step" -> `unclear_next`
- "context switching" -> `context_switching`
- "decision fatigue" -> `decision_fatigue`
- "other" -> capture the prose verbatim

When you write `core/identity.md` in Phase 1.1, populate `**Decision style:**` with the token. When you write `rules/operating-rules.md` in Phase 2.2, populate `**Communication style:**` with the token. Use the prose answer (or the `other` capture) for the descriptive paragraph that follows. Deep work time and overwhelm token go into `core/identity.md` under their respective sections.

### 0.8 Privacy Layers
Ask: "Last setup question. Some information is private to you, some you'd share with a co-founder or team member. Any businesses where someone else might see the project files? And anything that should ONLY live in your private global config?"

### 0.9 Observation Logging (opt-in)

Ask: "Optional: do you want Claude Code to log every tool call into a daily JSONL? Useful if you want a forensic record of what was touched in each session. Off by default. (yes / no / later)"

This is the `FOUNDER_OS_OBSERVATIONS` opt-in. The PostToolUse hook ships disabled. It only writes when the env var is set to `1`.

- If `no` or `later`: log to backlog as "Observation logging not enabled. Set `FOUNDER_OS_OBSERVATIONS=1` if you want it later." Move on.
- If `yes`:
  1. Create the `brain/observations/` folder at the Founder OS root.
  2. Copy `templates/brain/observations/README.md` to `brain/observations/README.md`. Do not edit the contents.
  3. Tell the user how to set the env var in their shell. Do NOT modify their shell config without explicit approval. Suggested copy:

     > "Add this to your shell config so the hook fires in new sessions:
     > - Bash / Zsh: `export FOUNDER_OS_OBSERVATIONS=1` in `~/.bashrc` or `~/.zshrc`
     > - PowerShell: `$env:FOUNDER_OS_OBSERVATIONS = '1'` in `$PROFILE`
     > - Windows (system-wide): run `setx FOUNDER_OS_OBSERVATIONS 1` once
     >
     > Restart your shell after editing. The hook stays silent until the variable is set."

  4. Append a one-line note to `core/setup-backlog.md` reminding them to set the env var. If the file does not exist, create it with the heading `## Setup Backlog` followed by the note. Example note: `- [ ] Set FOUNDER_OS_OBSERVATIONS=1 in shell env to enable observation logging.`
