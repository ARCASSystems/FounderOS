---
name: sop-writer
description: >
  Write a delegation-ready SOP. Trigger on "write an SOP", "document this process", "create a procedure", "process documentation", "how-to guide", "write up the steps for", "create a runbook", or any request to turn a process into a reusable document. Also fires when the user describes how something works and wants it captured for someone else to follow.
mcp_requirements: []
---

# SOP Writer

The goal: someone who has never done this task before should be able to complete it by following this document. No phone calls to the founder.

## Before You Write

Read three files first so the SOP is specific to the user's stack and voice, not generic.

1. **`stack.json`** at the Founder OS root. Maps the user's placeholder tools to actual products (e.g. `knowledge_base: notion`, `email_platform: outlook`, `automation_platform: n8n`). When you populate the TOOLS NEEDED section, name the user's actual tool. Do not write "your CRM" if `stack.json` says `crm: hubspot`. If a relevant field is null, use the generic label and append `[VERIFY]`.
2. **`core/identity.md`** for the founder's name and primary business. Use these for the Owner field. Do not invent.
3. **`core/voice-profile.yml`** via the `your-voice` skill. Apply `voice.rhythm` and `voice.reading_level` to the prose inside steps. SOPs that read at level 12 for an ops-focused founder who speaks at level 8 do not get followed.

Before drafting, read `brain/.snapshot.md` if it exists. Use the open-flags block to avoid topics that contradict current operator stance. Use the must-do block to lean the draft toward what the operator is actively working on. Use the voice and brand blocks (if present) to set tone. If `brain/.snapshot.md` does not exist, proceed without it - the snapshot is optional context, not a hard prerequisite.

## SOP Structure

```
SOP: [Process Name]
Owner: [Who is responsible]
Last updated: [Date]

---

PURPOSE
[One sentence. Why does this process exist?]

WHEN TO USE
[What triggers this process?]

TOOLS NEEDED
[Software, access, templates required]

---

STEPS

1. [Action verb] [what to do]
   - [Detail if needed]
   Expected result: [What should happen]

2. [Action verb] [what to do]
   Expected result: [What should happen]

---

IF SOMETHING GOES WRONG
-> [Problem]: [Fix]
-> [Problem]: [Fix]
-> [Problem]: Escalate to [Person/Role]

---

QUALITY CHECK
-> [How you know it was done correctly]
-> [Checkpoint]
```

## Writing Rules

- Start every step with a verb. "Open the CRM" not "The CRM should be opened."
- One action per step. If it has "and", split it.
- Include expected results after each step.
- Write for a smart person who has never done this.
- Handle exceptions. The "if something goes wrong" section is what makes an SOP useful.
- Simple hyphens (-) not em or en dashes
- Numbered steps, arrows (->) for sub-items

## What to Ask

1. Walk me through it step by step
2. What tools or systems do you use? (cross-check with `stack.json`; only ask if missing or ambiguous)
3. What goes wrong most often?
4. Who does this currently? Who should be able to do it?
5. How do you know it's done correctly?
