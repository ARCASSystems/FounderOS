# UAE Legal & Compliance References

This is the worked reference set for the `legal-compliance` skill. It is also the template every other jurisdiction should mirror.

## When to use this folder

The skill loads this folder when `core/identity.md` has one of:

- `jurisdiction: UAE`
- `jurisdiction: UAE-Dubai-Mainland`
- `jurisdiction: UAE-Dubai-Freezone-<zone>` (e.g., `DMCC`, `IFZA`, `RAKEZ`, `in5`)
- `jurisdiction: UAE-Abu-Dhabi-Mainland`
- `jurisdiction: UAE-DIFC` (separate regime — see DIFC sections in each file)
- `jurisdiction: UAE-ADGM` (separate regime — see ADGM sections in each file)

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

## Disclaimer

This reference set is general guidance based on publicly available UAE law as of the dates noted. For decisions with significant financial or legal consequences, confirm with a qualified UAE lawyer or registered tax agent. The skill flags 🟢/🟡/🔴 escalation level on every response — 🟡 means "the rule is clear but specific circumstances could change the outcome" and 🔴 means "professional counsel required, do not act on this skill alone".

## Maintenance

Re-verify the index of cabinet/ministerial decisions monthly. The biggest sources of drift in UAE law:

- **MOHRE / Emiratisation thresholds** — reset annually at calendar year-end
- **FTA / tax** — Cabinet/Ministerial Decisions roughly monthly
- **ICP / visas** — quarterly shifts in visa categories and thresholds
- **DIFC / ADGM** — separate amendments, check both portals
- **VARA / virtual assets** — fastest-moving area, web search before every answer
