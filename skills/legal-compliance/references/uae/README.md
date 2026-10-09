# UAE Legal & Compliance References

This is the worked reference set for the `legal-compliance` skill. It is also the template every other jurisdiction should mirror.

## When to use this folder

The skill loads this folder when `core/identity.md` has one of:

- `jurisdiction: UAE`
- `jurisdiction: UAE-Dubai-Mainland`
- `jurisdiction: UAE-Dubai-Freezone-<zone>` (e.g., `DMCC`, `IFZA`, `RAKEZ`, `in5`)
- `jurisdiction: UAE-Abu-Dhabi-Mainland`
- `jurisdiction: UAE-DIFC` (separate regime - see DIFC sections in each file)
- `jurisdiction: UAE-ADGM` (separate regime - see ADGM sections in each file)

If you operate across mainland and a free zone, or both DIFC/ADGM and federal, the skill will surface the relevant section automatically.

## What's in this folder

| File | Covers |
|---|---|
| `quick-reference.md` | Most-asked questions answered directly without loading a full domain file |
| `company-formation.md` | Mainland vs free zone vs offshore, entity types, license types, free zone matrix |
| `employment.md` | Federal Decree-Law 33/2021, MOHRE, Emiratisation, gratuity, WPS, termination |
| `tax-vat.md` | VAT, Corporate Tax, QFZP, ESR, transfer pricing, FTA filings |
| `visas-immigration.md` | Employment / Golden / Green / Investor / Freelancer / Family visas |
| `contracts-commercial.md` | Commercial contracts, NDAs, governing law, e-signatures, commercial agency |
| `ip-trademarks.md` | Trademarks, copyright, patents, trade secrets, IP holding structures |
| `data-protection.md` | PDPL, DIFC DP Law, ADGM DP Regulations, cross-border transfers |
| `dispute-resolution.md` | Courts, MOHRE binding authority, arbitration, debt collection, enforcement |
| `industry-specific.md` | Events, education, tech, fintech, e-commerce, F&B, healthcare permits |
| `templates/` | Contract, employment, and data-protection document templates |
| `sources.yml` | All primary government sources with `last_checked_on:` dates |

## How freshness works

Each domain file has a `## Last Verified:` header. Each source in `sources.yml` has a `last_checked_on:` field. The skill flags the answer with a freshness warning if either is >90 days old (file) or >6 months (source).

To refresh: `/founder-os:legal-update`. Walks you through which sources are stale, prompts you to web-search them, updates the dates and any material changes.

### Freshness at a glance (as of 9 Oct 2026)

| File | Last verified | State on 9 Oct 2026 |
|---|---|---|
| `company-formation.md` | 2026-04-25 (header refresh only) | Past the 90-day rule. One ESR line corrected 8 Oct |
| `contracts-commercial.md` | 2026-04-25 | Past the 90-day rule. The abolished DIFC-LCIA option corrected 9 Oct |
| `data-protection.md` | 2026-04-25 | Past the 90-day rule. One DIFC fine line corrected 8 Oct and made exact 9 Oct |
| `dispute-resolution.md` | 2026-04-25 | Past the 90-day rule. DIFC-LCIA and ADCCAC rows corrected 9 Oct |
| `employment.md` | 2026-04-25 | Past the 90-day rule. Contract-length and conversion-deadline lines corrected 8 Oct, the grace-period step 9 Oct |
| `industry-specific.md` | 2026-04-25 (header refresh only) | Past the 90-day rule |
| `ip-trademarks.md` | 2026-04-25 (header refresh only) | Past the 90-day rule |
| `quick-reference.md` | 2026-05-14 | Past the 90-day rule. One contract-length line corrected 8 Oct, the grace-period lines 9 Oct |
| `tax-vat.md` | 2026-05-14 | Past the 90-day rule. ESR section corrected 8 Oct |
| `visas-immigration.md` | 2026-04-25 | Past the 90-day rule. One visa line clarified 8 Oct. Grace-period and absence lines corrected 9 Oct |
| `templates/employment-templates.md`, `templates/contract-templates.md` | not dated | The blanket grace-period line and the DIFC-LCIA and ADCCAC options corrected 9 Oct |

Every file is past its 90-day rule, so every answer from this pack carries the freshness warning until a full refresh runs. A corrected line is not a full re-verification of its file.

**Not covered:** any other country, India included. Outside the UAE the skill declines until a jurisdiction is set up with its own sources. A founder who sells from or into another country should take the legal question to a qualified adviser there.

## Disclaimer

This reference set is general guidance based on publicly available UAE law as of the dates noted. For decisions with significant financial or legal consequences, confirm with a qualified UAE lawyer or registered tax agent. The skill flags 🟢/🟡/🔴 escalation level on every response - 🟡 means "the rule is clear but specific circumstances could change the outcome" and 🔴 means "professional counsel required, do not act on this skill alone".

## Maintenance

Re-verify the index of cabinet/ministerial decisions monthly. The biggest sources of drift in UAE law:

- **MOHRE / Emiratisation thresholds** - reset annually at calendar year-end
- **FTA / tax** - Cabinet/Ministerial Decisions roughly monthly
- **ICP / visas** - quarterly shifts in visa categories and thresholds
- **DIFC / ADGM** - separate amendments, check both portals
- **VARA / virtual assets** - fastest-moving area, web search before every answer
