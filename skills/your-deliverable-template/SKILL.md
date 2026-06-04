---
name: your-deliverable-template
description: >
  Build a branded document inheriting the founder's colors, fonts, and logo. Say "make a CV", "write a proposal", "build a pitch deck", "create a one-pager", "branded doc", "in my brand", or "use my colors". Master template for ALL personal-branded documents (CV, cover letter, proposal, pitch deck, one-pager, portfolio, PDF, DOCX, PPTX, HTML). Reads `core/brand-profile.yml`. If in doubt about whether a document should be branded, it should be branded.
why: "Ensures every document that carries your name inherits your visual identity rather than defaulting to generic black-and-white formatting that does not represent you."
enhance: "Place logo files at the paths recorded in core/brand-profile.yml before generating any HTML or PDF - the skill checks for real files and stops rather than silently substituting a placeholder."
allowed-tools: ["Read", "Write", "Edit", "Bash"]
mcp_requirements: []
---

# Your Deliverable Template

Every document that carries a name and visual identity follows the rules in this file plus the brand-specific values from a visual brand profile. There are two visual layers:

- **Operator brand** at `core/brand-profile.yml` - the user's personal visual identity. Default for personal output (CV, personal proposals, your one-pager).
- **Brand visual** at `brands/<slug>/visual.yml` - a brand the operator runs. Used when output represents that brand (brand deck, brand proposal, brand collateral).

An operator can have one or many brands. If `brands/` does not exist, this skill behaves exactly as it did before the brand layer existed - operator brand only.

Read this file before writing any document-producing code. The full visual specs (page setup, brand-profile schema, color palette, font stack, logo placement, HTML inlining, headers, footers, cover templates, section/body/table styling, and per-document-type defaults) live in `references/styling-spec.md`. Load it once you have routed to the right profile and are ready to generate.

If the active profile is missing or contains the template placeholders (the `[BRACKETED]` values), stop and tell the user:

> Your brand profile is not set up. Run `/founder-os:setup` and complete the brand interview, or edit the relevant brand profile directly. I can produce the document with placeholder branding if you confirm, but the result will look generic.

Do not silently default to generic styling. The whole point of this skill is the user's specific visual identity.

After loading the brand profile, also load the `your-voice` skill for the writing voice on any text inside the document.

---

## Brand routing - operator or brand?

Before loading any profile, decide which visual brand this document should use.

### Step 1 - Check if brands are set up

Run: `python scripts/list-brands.py`

If the script exits 0 with no output, OR the script does not exist, OR the `brands/` directory does not exist: skip to operator brand. No routing decision needed.

If the script lists 1+ brands: continue.

### Step 2 - Infer the brand from task context

Look at how the user phrased the task. Apply these signals in order:

1. **Explicit brand mention** - the user said "for `<brand>`", "as `<brand>`", "in `<brand>`'s brand", or named a brand display_name that matches a slug. Use that brand's visual.
2. **Explicit personal mention** - the user said "for me", "my personal", "my CV", "my one-pager". Use operator brand.
3. **Document implies brand** - "brand deck", "customer proposal for `<brand>`", "ad collateral" + a known brand = brand visual. "My CV" = operator. "Cover letter" = operator.
4. **Ambiguous** - ask once: "Whose brand for this? (you / `<brand 1>` / `<brand 2>` / ...)"

If only one brand is set up and the task is clearly brand-oriented (brand deck, brand collateral, customer-facing proposal for the brand), it is safe to pick that brand without asking - but still mention which brand was chosen in the output preamble so the user can correct.

If multiple brands are set up and the task could plausibly belong to any of them, ALWAYS ask. Do not guess.

### Step 3 - Load the chosen profile

- Operator: read `core/brand-profile.yml`.
- Brand: read `brands/<slug>/visual.yml`.

The schema is the same in both files. The styling spec in `references/styling-spec.md` applies uniformly regardless of which profile was loaded.

---

## Workflow before shipping any document

1. Run brand routing (above). Read the chosen profile - `core/brand-profile.yml` for operator, `brands/<slug>/visual.yml` for a named brand. If not set up, stop and ask.
2. Read the matching voice profile via `your-voice` (operator `core/voice-profile.yml` or brand `brands/<slug>/voice.yml`). If not set up, the document will use anti-AI defaults for any prose - warn the user.
3. Read `references/styling-spec.md` and generate the document using those rules + the brand profile values.
4. Run the self-check below.
5. Save the file to the right location.

### Self-check

- All section headers in `colors.primary`.
- No `colors.accent` used for body text.
- Logomark on cover page (and closing page if applicable).
- Footer carries `display_name` and `support_contact`.
- All HTML assets inlined (if HTML).
- Voice profile applied to any prose inside the document.
- Page count appropriate for the document type.

If any check fails, fix before declaring done.

---

## Save locations

- Drafts: `core/drafts/<document-type>-<YYYY-MM-DD>-<slug>.<ext>`
- Final outputs: `core/outputs/<document-type>-<YYYY-MM-DD>-<slug>.<ext>`

If those folders don't exist, create them. Both are gitignored by default.
