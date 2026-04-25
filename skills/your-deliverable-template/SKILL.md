---
name: your-deliverable-template
description: >
  Master template for ALL personal-branded documents. Every output that carries the user's name and visual identity (CV, cover letter, proposal, pitch deck, one-pager, portfolio, PDF, DOCX, PPTX, HTML) MUST read this skill first. Reads `core/brand-profile.yml` for the user's specific brand. Trigger when the user says "make a CV", "write a proposal", "build a pitch deck", "create a one-pager", "branded doc", "in my brand", "use my colors", or asks to produce any visual deliverable. If in doubt about whether a document should be branded, it should be branded.
allowed-tools: ["Read", "Write", "Edit", "Bash"]
---

# Your Deliverable Template - Master Brand Standard

Every document that carries the user's name and visual identity follows the rules in this file plus the brand-specific values in `core/brand-profile.yml`. No exceptions.

Read this entire file before writing any document-producing code. Then read `core/brand-profile.yml` to load the user's brand.

If `core/brand-profile.yml` is missing or contains the template placeholders (the `[BRACKETED]` values), stop and tell the user:

> Your brand profile is not set up. Run `/founder-os:setup` and complete the brand interview, or edit `core/brand-profile.yml` directly. I can produce the document with placeholder branding if you confirm, but the result will look generic.

Do not silently default to generic styling. The whole point of this skill is the user's specific visual identity.

After loading the brand profile, also load the `your-voice` skill for the writing voice on any text inside the document.

---

## Page setup (universal defaults)

These can be overridden per-document if the brand profile specifies, but the defaults are:

- **Page size:** A4 (595.27 x 841.89 pt). The brand profile may switch to US Letter (612 x 792 pt) if the user's market needs it.
- **Margins:** 52pt left, 52pt right. 60pt top and bottom (adjust for header/footer space).
- **Orientation:** Portrait default. Landscape only when a table or diagram needs it.

---

## Brand profile (read this every time)

`core/brand-profile.yml` contains:

- **identity.display_name** - the name that goes on the cover and footer
- **identity.tagline** - optional one-liner under the name
- **identity.support_contact** - email or URL for "get in touch" lines
- **colors** - 5 named colors with hex codes and usage rules
- **fonts** - 1 to 2 font families with weight/size mapping for the document elements
- **logo** - logomark file path + full logo file path + usage rules
- **footer** - default footer text
- **assets_dir** - directory for the user's brand assets (defaults to `core/brand-assets/`)

Each setting below explains how to use that part of the brand profile.

---

## Color palette

Read `colors` from the brand profile. The structure is 5 named slots:

```yaml
colors:
  primary:    { hex: "#XXXXXX", usage: "section headers + emphasis" }
  secondary:  { hex: "#XXXXXX", usage: "accents + CTAs" }
  dark:       { hex: "#XXXXXX", usage: "body text + dark backgrounds" }
  light:      { hex: "#XXXXXX", usage: "light backgrounds + dividers" }
  accent:     { hex: "#XXXXXX", usage: "highlights only - use sparingly" }
```

### Accessibility rules (always)

- Never use a light color (e.g. mint, pale yellow) as text on a white or light background. Invisible.
- Never use the accent color for body text. Accents only.
- Verify contrast ratios. Body text on its background must hit at least 4.5:1.
- If the brand profile color choices fail accessibility, warn the user and suggest a darker alternative.

---

## Font stack

Read `fonts` from the brand profile. The structure is:

```yaml
fonts:
  primary:   { family: "FontName", source: "google_fonts | local | system" }
  secondary: { family: "FontName", source: "google_fonts | local | system" }
  weights:
    section_header: { font: "primary", weight: "Bold",   size_pt: 15 }
    subsection:     { font: "primary", weight: "Medium", size_pt: 11 }
    body:           { font: "primary", weight: "Light",  size_pt: 9 }
    emphasis:       { font: "primary", weight: "Regular", size_pt: 10 }
    footer:         { font: "primary", weight: "Light",  size_pt: 8 }
    cover_title:    { font: "primary", weight: "Bold",   size_pt: 26 }
    cover_subtitle: { font: "primary", weight: "Medium", size_pt: 15 }
```

### Font handling

- If `source` is `google_fonts`, install if not present:
  ```bash
  pip install fonttools --break-system-packages 2>/dev/null || true
  # Or download directly from Google Fonts API
  ```
- For ReportLab (PDF), register all weights with `pdfmetrics.registerFont()`.
- For python-docx (DOCX), set font name in run properties.
- For python-pptx (PPTX), set font name in text frame runs.
- If the font cannot be installed, fall back to the closest system font (e.g. Inter for Poppins, Helvetica for Arial) and warn the user.

---

## Logo placement

Read `logo` from the brand profile. The structure is:

```yaml
logo:
  logomark: { path: "core/brand-assets/logomark.png", description: "icon only" }
  full:     { path: "core/brand-assets/full-logo.png", description: "icon + name text" }
  white:    { path: "core/brand-assets/full-logo-white.png", description: "for dark backgrounds" }
```

Placement rules:

- **Cover pages:** logomark top-left, 68x68pt
- **Closing pages:** logomark bottom-right, 36x36pt
- **Internal pages (PDF/DOCX):** not required unless the brand profile says otherwise
- **Dark background headers/slides:** white full logo if available, else full logo on a light box behind it
- **HTML topbar:** logomark, 36x36px
- **HTML footer (dark background):** white full logo, ~120px wide, centered above signature

### Hard rule

Never substitute a styled letter for the user's logomark. If the logomark file doesn't exist at the path in the brand profile, ask the user before shipping. Don't generate a placeholder letter-mark and ship.

---

## HTML asset inlining (HARD RULE)

HTML deliverables must be self-contained before they leave the user's machine. Relative paths to logos, images, or fonts break the moment the file is sent via email, WhatsApp, or downloaded elsewhere.

### Workflow

1. Build HTML using relative paths during development.
2. Before declaring ready to share, base64-encode every `<img src="...">` with a relative or local-absolute path. Resize logos to <= 360px wide before encoding to keep the file size reasonable.
3. Verify by opening the file from a different directory. Logos must still render.
4. If you don't have a script to inline assets, do it inline in your HTML generation code.

Never declare an HTML deliverable "ready to share" if it has relative asset paths.

---

## Header format (internal pages)

For multi-page PDFs and DOCX:

- **Left:** brand profile `identity.display_name`
- **Right:** document title + page number (e.g. "Proposal | p.3")
- **Font:** primary, Light, 8pt, in `colors.dark`
- **Bottom border:** 0.5pt line in `colors.light`

---

## Footer format

- **Left:** `footer.text` from brand profile (default: `<display_name> | <support_contact>`)
- **Right:** date in YYYY-MM-DD format
- **Font:** primary, Light, 7-8pt, in `colors.dark`
- **Top border:** 0.5pt line in `colors.light`

---

## Cover page templates

### Standard cover (CV, proposal, one-pager)

- Logomark top-left, 68x68pt
- Title centered, cover_title weight, in `colors.primary`
- Subtitle below title, cover_subtitle weight, in `colors.dark`
- Date and recipient name (if applicable) bottom-left, body weight, in `colors.dark`
- Optional accent bar (4pt tall) across the bottom in `colors.secondary`

### Pitch deck cover (PPTX)

- Logomark top-left, 80x80pt
- Title centered vertically and horizontally, cover_title weight scaled to 36pt
- Subtitle below, cover_subtitle weight scaled to 18pt
- Date and audience bottom-right, body weight, 12pt
- Background: white default, or `colors.dark` with white text if the brand profile specifies a dark cover

---

## Section headers

- **Format:** colors.primary, primary font, Bold, 15pt
- **Spacing:** 24pt above, 12pt below
- **Optional accent:** 3pt left border in `colors.secondary` if the brand profile enables it

---

## Body text

- **Color:** `colors.dark`
- **Font:** primary, Light, 9pt
- **Line height:** 1.4
- **Paragraph spacing:** 6pt below

### Emphasis

- **Bold:** primary, Bold, 10pt, `colors.dark`
- **Italic:** primary, Light Italic, 9pt, `colors.dark`
- **Inline code:** monospace fallback (Courier, Menlo, Consolas), 8.5pt, on `colors.light` background

---

## Tables

- **Header row:** `colors.primary` background, white text, primary font Bold 9pt
- **Body rows:** alternating white and `colors.light` (very subtle)
- **Borders:** 0.5pt in `colors.light`
- **Padding:** 6pt all sides

---

## Document type defaults

The brand profile may define per-document overrides. If not, use these defaults.

### CV (PDF)

- 1-2 pages
- Cover header: name + tagline + contact details (right-aligned)
- Sections: Summary | Experience | Education | Skills | (optional) Certifications | (optional) Side Projects
- No cover page (waste of a page on a CV)

### Cover letter (PDF or DOCX)

- 1 page
- Header: name + contact details (right-aligned)
- Date + recipient name and address (left-aligned, separate blocks)
- Body: the cover letter, written via `your-voice` skill
- Sign-off: `voice.signoff_phrase` from voice profile

### Proposal (PDF)

- 4 to 8 pages
- Cover page (full)
- Sections: Summary | What You Get | Approach | Timeline | Pricing | Next Steps
- Closing page with logomark and contact

### Pitch deck (PPTX)

- 8 to 15 slides
- Cover slide (full)
- Sections: Problem | Solution | Why You | Proof | Pricing | Ask
- Closing slide with logomark and contact

### One-pager (PDF or HTML)

- 1 page
- Cover header (compact)
- 3 to 5 sections in a single column or 2-column grid
- Closing footer with contact

### Portfolio piece (HTML)

- Single self-contained HTML file
- Hero section with project title and 1-line summary
- Sections: Context | Role | Approach | Result | (optional) Visuals
- Footer with brand and contact

---

## Workflow before shipping any document

1. Read `core/brand-profile.yml`. If not set up, stop and ask.
2. Read `core/voice-profile.yml`. If not set up, the document will use anti-AI defaults for any prose - warn the user.
3. Generate the document using the rules above + brand profile values.
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
