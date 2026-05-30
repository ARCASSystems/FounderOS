---
name: linkedin-network-scan
description: >
  Rank your own LinkedIn network against an ICP you define, without burning context on raw CSVs. Point it at your LinkedIn data-export ZIP; a deterministic local script scores every connection (seniority with demotions, ICP role/industry/company match, connection recency, reply-warmth, optional region) and writes a compact ranked worklist. The assistant reads only the small ranked digest, never the 2,000-row export. Free plan only - no scrapers, no paid tools, no API calls. Message content is never read. Use when someone says "scan my linkedin network", "who in my network fits my ICP", "build my outreach list from my connections", or shares a LinkedIn export ZIP for targeting.
why: "A LinkedIn connections export is tens of thousands of tokens; reading it raw wastes context and money. A deterministic script collapses it to a ranked top-N first, so the model only ever sees a small worklist - and real names and URLs never leave the machine."
enhance: "Write a real ICP file before running (roles, industries, company keywords, min seniority, optional region) instead of taking the permissive default - a narrowed ICP turns a long flat list into a short, ranked, actually-actionable worklist."
allowed-tools: ["Bash", "Read"]
mcp_requirements: []
---

# LinkedIn Network Scan

Turn your own LinkedIn connections export into a ranked outreach worklist scored against an ICP you control. Deterministic, local, free-plan only. The raw CSVs never enter the conversation - the script collapses them to a compact ranked digest first.

## When to use

- A user wants to find who in their existing network matches a target customer / hiring / partnership profile.
- They have (or can request) their LinkedIn data export.
- They want a manual-outreach worklist, not automated sending.

## When NOT to use

- To analyse someone else's export they did not personally download. Refuse on consent grounds.
- To write the outreach messages. That is a separate writing task.
- To scrape LinkedIn or use a paid Sales Navigator seat. This skill is export-only, free-plan only.

## Step 1 - the ZIP gate (do this FIRST, before anything else)

Ask: **"Do you have your LinkedIn data export downloaded?"**

If no, walk them through requesting it and STOP - do not ingest anything yet:

> LinkedIn Settings -> Data Privacy -> "Get a copy of your data" -> pick the full archive
> (the "Download larger data archive") -> Request archive. LinkedIn emails a download link.
> The basic file arrives in minutes; the complete archive (with messages and invitations)
> can take up to 24 hours. Download it, then come back - you can point me at the ZIP directly,
> no need to unzip.

Only continue once they have the file.

## Step 2 - get the ICP

Ask whether they have an ICP config, or want to define one now. Offer the template at `icp.example.yaml` in this skill folder - they copy it, edit the lists (roles, industries, company keywords, min seniority, optional region tokens, exclusions), and save it as their own file.

If they have no ICP and do not want to build one, run with the permissive default (any decision-maker, no industry/region filter) and tell them explicitly that nothing was narrowed, so the ranking is seniority + warmth only.

## Step 3 - run the scan

```
python scan.py <export.zip OR export-folder> <output-folder> --icp <their-icp.yaml>
```

- `<export.zip>` can be the ZIP itself or an unzipped folder. The script reads `Connections.csv`, `messages.csv` (metadata only), and `Invitations.csv` from inside it.
- `<output-folder>` MUST be outside any git repo - it holds real names and profile URLs. A folder in their home directory or Desktop is fine.
- `--icp` is optional; omit it for the permissive default.

The script is Python standard-library only - no `pip install`, nothing to set up, works on a free plan. If `python` is not found, try `python3`.

## Step 4 - read ONLY the compact digest

When the script finishes, **read only `network-scan.md`** from the output folder. It is the ranked top-N digest, a few hundred lines at most.

**Do NOT read `network-scan.csv`, `network-scan.json`, the export's `Connections.csv`, or `messages.csv`** - those are the full raw rows and reading them is exactly the token waste this skill exists to avoid. They are deliverables for the user to open, not for the model to ingest.

Then summarise in one or two sentences: how many connections were read, how many qualified for their ICP, how many have actually replied to them before (warm), and how many pending inbound invitations are waiting. Point them at `network-scan.html` to browse and `network-scan.csv` for the full list with emails and URLs.

## What the script outputs (all in the output folder)

- `network-scan.md` - compact ranked digest (the only file the assistant reads).
- `network-scan.html` - browsable ranked worklist with warmth and region chips.
- `network-scan.csv` - every qualified row with email + LinkedIn URL.
- `network-scan.json` - the same data plus the ICP used, for tooling.
- `inbound-invites.csv` - people who sent a connection request still pending (warm inbound).

Every file carries a header reminding the user not to commit or share it.

## Privacy

- Message **content** is never read. The script uses only metadata: who messaged whom, the direction, the count, and the date - enough to tell a real two-way relationship from a one-way cold send.
- Nothing leaves the machine. No API calls, no scrapers, no third-party services.
- The output holds real names and URLs. The script writes a "keep this local, do not commit" warning into every file; repeat it to the user.

## Honest limitations (state these, do not hide them)

- **Seniority and region are inferred from one title string.** A serious-consultancy founder and a side-hustle "founder" can score alike; a UAE company that does not say "Dubai" in its name will miss a `dubai` region token. The ranking is a strong first cut, not a verdict - skim the top of the list before acting on it.
- **Warmth only sees export metadata.** A thread that moved off LinkedIn (to email or WhatsApp) looks cold here even if the relationship is warm.
- **Nothing is sent.** This produces a worklist. The outreach is manual, by design.

## Files

- `scan.py` - the deterministic scanner (stdlib only).
- `icp.example.yaml` - documented ICP template to copy and edit.
