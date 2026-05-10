# Adding Your Jurisdiction's Reference Set

This is the scaffold for any jurisdiction the Founder OS legal-compliance skill doesn't ship with. The UAE reference set (`../uae/`) is the worked example — your folder should mirror its shape.

The skill is **principally right** but **specifically empty** until you load it. It knows the *shape* of business compliance (tax, employment, contracts, IP, data protection, dispute resolution, industry permits) and can ask the right follow-up questions. It just won't quote your jurisdiction's law until you give it sources.

---

## Step 1: Create your jurisdiction folder

Pick a folder name that matches your `jurisdiction:` field in `core/identity.md`. Examples:

- `references/us-delaware-llc/`
- `references/uk-ltd/`
- `references/in-karnataka-pvt-ltd/`
- `references/sg-pte-ltd/`
- `references/au-pty-ltd/`

The string is jurisdiction-country-state-entity-type, dash-separated, lowercase. The skill matches your `jurisdiction:` field to a folder name.

Run `/founder-os:legal-setup` and the wizard will:
1. Ask what jurisdiction you operate in
2. Write the field to `core/identity.md`
3. Create the matching folder by copying this `_template/` scaffold
4. Walk you through adding your first three priority sources (tax authority, business law, labour law)

You can also do it manually: copy this `_template/` folder to `references/<your-jurisdiction>/`, then start populating.

---

## Step 2: Add at least 3 priority sources

These three sources unlock most legal questions. Add them first.

1. **Tax authority** — your country's IRS / HMRC / FBR / IRAS / ATO equivalent. Add the URL of their main legal/regulations page.
2. **Business law / Companies act** — your gazetted Companies Act or equivalent. PDF URL or government portal page.
3. **Labour law / Employment code** — your gazetted Employment Act / Labour Code / Fair Work Act. PDF URL or government portal page.

Add each via:

```
/founder-os:legal-add-source <url-or-pdf-path>
```

The command asks: which domain does this cover? Which jurisdiction folder? It then drops the link into `sources.yml` with today's `last_checked_on:` date and creates a stub domain file (e.g., `tax-vat.md`) if one doesn't exist.

---

## Step 3: Populate the domain files (over time, not all at once)

The UAE folder ships with 9 domain files because that's a complete reference set. You don't need all 9 on day one. Most founders use 3-4 in regular practice:

- `employment.md` — when hiring or letting people go
- `tax-vat.md` — at filing deadlines and registration thresholds
- `contracts-commercial.md` — for service agreements, NDAs, MOUs
- `data-protection.md` — for privacy policy, DPAs, cross-border transfers

Add domain files as questions come up. The skill will tell you which file is missing the first time you ask a question it can't answer.

For each domain file, mirror the UAE structure:
- `## Last Verified:` header (today's date when you write it)
- `## Material Changes Since <baseline>:` list of recent amendments
- `## Table of Contents`
- Domain-specific sections
- `## Escalation` block at the end (🟢 / 🟡 / 🔴)

Read `../uae/employment.md` as a reference for tone, depth, and structure.

---

## Step 4: Maintain freshness

Run `/founder-os:legal-update` quarterly (or before any client-facing legal memo). The skill flags any source where `last_checked_on:` is >6 months old.

When a material legal change happens (new ministerial decision, gazette notification, regulator announcement), add it via `/founder-os:legal-add-source` with the source URL/PDF and update the relevant domain file's "Material Changes" block.

---

## What this folder should NOT contain

- **Your filings.** Your VAT TRN, license numbers, fiscal year end go in `context/compliance.md`, not here. This folder is the law; that file is your obligations.
- **Your clients' legal data.** Client license details, NDAs you've signed, employment contracts you've signed — those belong in private project folders, not here.
- **Secondary commentary as authority.** Big 4 guides, law firm articles, blog posts can be added as `notes:` fields in `sources.yml` for context, but the `url:` should always point to a primary source.
- **AI-generated summaries.** Don't add ChatGPT or similar outputs as a source. The skill's job is to ground answers in primary law, not aggregate other AI's interpretations.

---

## Files in this scaffold

| File | What to do |
|---|---|
| `README.md` | This file — keep as-is in your jurisdiction folder, or delete |
| `sources.yml.template` | Rename to `sources.yml` and start populating |

Domain files are not pre-created in this scaffold. The `/founder-os:legal-add-source` command creates them as you add sources, or you can manually create `<domain>.md` files mirroring the UAE structure.
