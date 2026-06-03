---
name: web-fetch-extract
description: >
  Generic web-data primitive. Fetches a URL via scripts/scrape.py and extracts structured data inline using the model's own reasoning over the fetched HTML. Use when any other skill or task needs data from a public web page - bios, leadership teams, prices, OpenGraph tags, page titles, recent posts, or "what does this page say about X". Triggered by /founder-os:scrape and by other skills as a sub-step. Falls back to the WebFetch tool if scrape.py is missing or fails.
why: "Pulls a page into context and extracts the answer without an LLM API call - extraction is the model's reasoning over the fetched text, so it works on a free plan and never sends the page to a paid endpoint."
enhance: "Pick the lightest extract mode for the goal (meta, og, links, text) instead of dumping full HTML - it keeps the payload small and the extraction sharp, and only escalate to render mode when a first attempt comes back near-empty."
summary: "Fetch a public web page and extract structured data from it inline."
allowed-tools: ["Bash", "Read", "WebFetch"]
mcp_requirements: []
---

# Web Fetch + Extract

Generic skill for pulling a URL into context and extracting whatever the calling skill or user asked for. No LLM API call - extraction is the model's reasoning over the fetched HTML or text. Works on a free plan.

## Dependencies

`scripts/scrape.py` needs three Python packages for the default path, and one optional package for JS-rendered pages:

```
pip install httpx selectolax tenacity
```

Optional, only for `--render` (JS-walled pages):

```
pip install playwright
python -m playwright install chromium
```

The script imports Playwright lazily, so the three core packages are enough unless you actually pass `--render`. If a required package is missing, the script errors clearly and this skill falls back to the `WebFetch` tool.

## Pre-flight

If `scripts/scrape.py` does not exist, fall back to the `WebFetch` tool for the whole flow and tell the user the script is missing.

## Inputs

The skill receives two things:

1. **URL** - a single fully-qualified URL.
2. **Extraction goal** - natural language describing what to pull. Examples: "bio + role + recent posts", "leadership team names and titles", "title + meta description", "the three pricing tiers and what is in each".

## Procedure

1. **Decide render mode.**
   Default to no JS render. Add `--render` only if the user explicitly says the page is JS-heavy or a first attempt returns near-empty HTML or text. Playwright is not installed by default. If `--render` is requested and Playwright is missing, the script errors clearly - fall back to `WebFetch` and note the gap.

2. **Pick the lightest extraction mode for the goal.**
   - Title + description / OG tags only: `python scripts/scrape.py <url> --extract meta`
   - OG-only payload: `python scripts/scrape.py <url> --extract og`
   - All outbound links (for example discovering a sitemap or About page): `python scripts/scrape.py <url> --extract links`
   - Text body (cleaned): `python scripts/scrape.py <url> --extract text` (optionally `--selector "main"` or similar)
   - Full HTML for messy parsing: `python scripts/scrape.py <url>`

3. **Run the script via the Bash tool.** Capture stdout. If the script exits non-zero, read stderr and either retry with a different mode or fall back to `WebFetch`.

4. **If the captured payload is larger than ~50KB, summarise as you read.** Do not echo the whole HTML back. Pull only the spans the goal needs.

5. **Apply the natural-language extraction inline.** Read the captured text. Match content to the goal. Resolve simple ambiguity (for example, "leadership team" - look for sections titled About, Team, Leadership, Our People; pull name + title pairs).

6. **Return structured output** in the format the calling skill needs. If the caller did not specify, default to:
   - JSON when the goal asks for fields (bio, role, links, prices, dates).
   - Markdown table when the goal asks for a list (team members, posts, products).
   - Short prose paragraph when the goal is a single open question ("what does this page say about X").

## Robots and politeness

`scrape.py` checks `robots.txt` and warns on disallow. It proceeds unless `--strict` is set. Do not pass `--strict` by default. Surface the warning to the user if it fires and let them decide.

Never scrape a URL the user did not supply. Never follow links beyond the page the user asked about unless the goal explicitly says "follow X link" or "find the team page".

## Fallback

If `scripts/scrape.py` returns an error twice (different modes), or if the page clearly needs JS and Playwright is unavailable, switch to the `WebFetch` tool for that URL and note the fallback in the response.

## Output rules

- No em dashes or en dashes. Hyphens only.
- No banned words.
- Cite the URL once at the top of the response.
- If the goal could not be fully answered (for example, the team page only had two of an expected larger list), say so explicitly in a one-line caveat at the end. Do not fabricate.

## Edge cases

- **404 or 403.** Report the status code and stop. Do not retry indefinitely.
- **Page returns a near-empty body.** Re-run with `--render` if Playwright is available; otherwise fall back to `WebFetch`.
- **Goal references a field not on the page.** State that explicitly in the caveat. Never invent values.
- **URL is a PDF or other non-HTML.** Tell the user scrape.py is HTML-only and suggest a different approach (download + read).
