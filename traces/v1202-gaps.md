# FounderOS v1.20.2 gap analysis

Trace: `traces/v1202-first-60-min.md`

- **Gap: setup captures business facts but not a Positioning block.**
  - Downstream skill that suffers: `linkedin-post`, `proposal-writer`, `client-update`, and `business-context-loader`.
  - Missing intake question: "Who do you sell to in one sentence?", "What do you sell in one sentence?", and "What visible pain does your buyer feel before they come to you?"
  - Smallest patch: add a skip-able positioning phase after the current business map, store the answers in `core/identity.md` under `## Positioning`, and tell the wizard that these answers are read by writing and proposal skills.

- **Gap: voice interview captures Sara's words but not her buyer's words.**
  - Downstream skill that suffers: `linkedin-post`, `email-drafter`, `proposal-writer`, `client-update`, and `your-voice`.
  - Missing intake question: "When your buyer describes the problem to you, what is the first sentence out of their mouth?" and "What phrase does your buyer say that makes you nod every time?"
  - Smallest patch: add two buyer-language questions after the six voice shaping questions, store them in `core/voice-profile.yml` under `buyer_language:`, and include the block in the confirm step.

- **Gap: brand interview hears that assets exist but drops where they live.**
  - Downstream skill that suffers: `your-deliverable-template`.
  - Missing intake question: "Do you have an existing deck, website, logo folder, or other visual reference? Where is it?"
  - Smallest patch: ask one visual-proof question in each brand path, store the answer under `existing_assets:` in `core/brand-profile.yml`, and keep `brand_assets/` for actual logo files.

- **Gap: `/rant` captures only, even when the rant contains an obvious action need.**
  - Downstream skill that suffers: `decision-framework`, `linkedin-post`, `email-drafter`, `proposal-writer`, `priority-triage`, and `brain-log`.
  - Missing intake question: "Does this need a decision, a draft, a plan, or just to be captured?"
  - Smallest patch: change `.claude/commands/rant.md` from dump-only to one-question qualification. Route "decision" to `decision-framework`, "draft" to the right writing skill, "plan" to `priority-triage`, and "capture" or skipped answers to the existing rants file path.

- **Gap: writing skills warn on empty voice data but keep drafting from defaults.**
  - Downstream skill that suffers: `linkedin-post`, `client-update`, `proposal-writer`, `email-drafter`, and `content-repurposer`.
  - Missing intake question or gate: none in the wizard. The gate belongs in the writing skills before output.
  - Smallest patch: each writing skill reads `core/voice-profile.yml` first and stops if the profile is missing or still contains template defaults. Ask whether to run the interview or proceed with defaults.
