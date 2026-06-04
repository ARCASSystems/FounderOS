---
name: voice-interview
description: >
  Set up the writing-voice profile. Say "set up my voice profile", "set up my voice", "voice interview", or "capture my voice" (or run /founder-os:voice-interview). Interactive interview that captures rhythm, openings, closings, contractions, idiosyncrasies, and writes the result to `core/voice-profile.yml`. Asks for samples first because samples beat self-description, then asks shaping questions to fill the gaps. Extracts intent from messy real-world answers, never asks the user to be structured.
why: "Builds the voice profile that gates every writing skill - without it linkedin-post, email-drafter, proposal-writer, and client-update all produce generic output that does not sound like you."
enhance: "Paste at least three real samples you have already written before answering shaping questions - samples are the ground truth and override the rules when they conflict, so more specific samples mean a sharper profile."
allowed-tools: ["Read", "Write", "Edit"]
mcp_requirements: []
---

# Voice Interview

You are running an interactive interview to capture the user's writing voice. The output is `core/voice-profile.yml`. The voice-profile feeds the `your-voice` skill, which then writes everything as the user from that point on.

Internal phase numbers in markdown H2 headers are for the maintainer; the operator sees a three-part frame (Part 1 of 3 - Samples, Part 2 of 3 - Shaping questions, Part 3 of 3 - Confirm and save) inside model utterances. Setup (Phase 1) and Final message (Phase 5) sit outside the three-part frame because they are pre-interview onboarding and post-save confirmation respectively.

Cross-skill asymmetry note: this skill has 5 phases. The sibling `brand-voice-interview` has 6 because it captures positioning (who-the-brand-sells-to) before voice (how-the-brand-speaks). Operator voice does not need a positioning phase because operator positioning lives in `core/identity.md` (captured by `founder-os-setup`). Do not collapse positioning into voice when editing the sibling skill.

<Instruction-gate>
Do not generate `core/voice-profile.yml` until you have collected at least 2 reference samples (pasted in chat OR sourced from existing session artifacts: `brain/rants/*.md`, `context/decisions.md`, `brain/log.md` recent entries, or `clients/*/communications/`) AND walked the shaping questions, including buyer-language questions and anti-example questions. Samples are the ground truth. If the user has no existing artifacts and refuses to paste samples, ask them to write 2 short pieces in the chat right now (a 2-sentence work email and a LinkedIn-style hook). Don't proceed without samples - the profile without samples is a stereotype.

Do not invent answers. If the user skips a question, leave the field as `[NOT SET]` and tell them they can re-run the interview later.
</Instruction-gate>

## Phase map - load the reference when you reach the phase

Run the phases in order. When you reach a heavy phase, read its reference file for the full procedure, then execute it. Load only the phase you are in.

| Phase | What it does | Load |
|-------|--------------|------|
| 1 | Setup - operator vs brand, then welcome (inline below) | - |
| 2 | Samples - scan for existing artifacts, paste flow (the ground truth) | `references/samples-and-questions.md` |
| 3 | Shaping questions - Q1 to Q12 including anti-examples | `references/samples-and-questions.md` |
| 4 | Confirm and save - the recap block + `core/voice-profile.yml` output | `references/confirm-and-save.md` |
| 5 | Final message (inline below) | - |

---

## Phase 1 - Setup (operator vs brand, then welcome)

Say exactly:

> Quick check. There are two voice layers in this OS:
>
> 1. **Your personal voice** - how YOU write as a person. Personal LinkedIn, your CV, emails from you, anything where your name is on the output. This is what we are about to capture.
> 2. **A brand voice** - how a brand you run writes. Customer comms, brand social, ads. Captured separately with `/founder-os:brand-voice-interview`.
>
> If you are running a founder-led brand the two overlap, but the brand voice should still be captured separately so it survives after employees other than you start writing for the brand.
>
> Is this for you personally, or for a brand you run? (personal / brand)

If they say "brand", stop and dispatch to `brand-voice-interview` instead.

If they say "personal" or "both", continue with this skill for personal voice. (If "both", note at the end that they should also run brand-voice-interview separately.)

Then say exactly:

> Voice interview. About 10 minutes. The output is your personal voice profile - it will write everything as you from now on: emails, posts, scripts, cover letters, whatever you generate. We'll do it in three parts: paste a few samples of your writing, walk a few shaping questions, then you confirm and we save. Ready?

Wait for confirmation.

---

## Phase 2 - Samples (the ground truth)

Read `references/samples-and-questions.md`. Scan for existing artifacts first, then run the paste flow. Open with "Part 1 - samples." Collect 3 short pieces (or 2 written in chat if the user refuses to paste).

---

## Phase 3 - Shaping questions (Q1-Q12)

Continue in `references/samples-and-questions.md`. Walk Q1 to Q12 (including the anti-example questions Q9 to Q12), ONE at a time. Open with "Part 2 of 3 - 12 shaping questions."

---

## Phase 4 - Confirm and save

Read `references/confirm-and-save.md`. Show the recap block (Part 3 of 3), then on a "yes" write `core/voice-profile.yml` using the exact structure in that reference.

---

## Phase 5 - Final message

Say exactly:

> Voice profile saved to core/voice-profile.yml. From now on, anything I generate for you will use this voice - emails, posts, scripts, cover letters, whatever. If something I write doesn't sound like you, tell me and we'll refine the profile.
>
> One more note: this is your PERSONAL voice. If you run a brand (or multiple brands), they have their own voice that should be captured separately. Run `/founder-os:brand-voice-interview` when you are ready. The two layers stay independent and writing skills route to the right one based on what you ask for.

Stop. Do not do anything else.

---

## Re-run behavior

If the user runs this skill and `core/voice-profile.yml` already has real values (not template placeholders), ask:

> A voice profile already exists. Want to start over from scratch, or just update specific fields? (start-over / update)

If `update`, ask which fields, then walk only those questions.
If `start-over`, run the full interview.

---

## Rules

- One question at a time. Wait for answer.
- Real users ramble. Extract intent. Don't ask them to be more structured.
- Never tell the user to be more concise. The volume is the thinking.
- Never invent samples. Never invent vocabulary.
- Plain language. The user is not a linguist.
