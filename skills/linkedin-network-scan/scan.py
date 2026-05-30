# -*- coding: utf-8 -*-
"""
scan.py - Rank your own LinkedIn connection export against an ICP you define.

Reads:  Connections.csv, messages.csv (counterparty metadata only), Invitations.csv
        - from an unzipped export folder OR straight out of the export ZIP.
Writes: network-scan.html + network-scan.md + network-scan.csv + network-scan.json
        + inbound-invites.csv  - all into an output folder you choose.

No AI calls. No third-party APIs. No pip installs - Python standard library only
(zipfile, csv, json, re, html, datetime, argparse). Message CONTENT is never read;
only the counterparty name, the direction (who sent it), the count, and the date.

The ranked output is small on purpose: the assistant reads the compact summary, never
the raw 2,000-row CSV. Your real names and profile URLs stay in the output files on
your disk - those files are NOT meant to be committed or shared.

Usage:
    python scan.py <export.zip | export-folder> <output-folder> [--icp icp.yaml]

If --icp is omitted, a permissive default ICP is used (any decision-maker, no region
or industry filter) and that is stated in the output so you know nothing was narrowed.
"""

import argparse
import csv
import datetime
import html
import json
import os
import re
import sys
import zipfile
from collections import defaultdict

# ----------------------------------------------------------------------------
# Title taxonomy (generic - no industry or region is baked in here; ICP filters
# come from the user's config). This layer only maps a title string to a rough
# seniority signal, with demotions so individual contributors and front-line
# "advisor/consultant" titles do not get read as decision-makers.
# ----------------------------------------------------------------------------

def rx(*pats):
    return [re.compile(p, re.I) for p in pats]

FOUNDER_CORE = rx(
    r"\bfounder\b", r"co-?founder", r"cofounder", r"\bowner\b",
    r"proprietor", r"entrepreneur", r"\bfounding\b",
)
C_SUITE = rx(
    r"\bceo\b", r"chief executive", r"\bcoo\b", r"chief operating",
    r"\bcfo\b", r"\bcmo\b", r"\bcto\b", r"\bciso\b", r"\bcpo\b",
    r"chief .{0,20}officer", r"managing director", r"\bm\.?d\.?\b(?! ?phd)",
    r"chair(man|woman|person)?\b", r"(?<!vice )(?<!vice-)president",
    r"managing partner",
)
VP_TIER = rx(r"vice president", r"\bvp\b", r"\bevp\b", r"\bsvp\b", r"head of", r"\bgeneral manager\b")
DIRECTOR_TIER = rx(r"\bdirector\b")
MANAGER_TIER = rx(r"\bmanager\b", r"\blead\b", r"\bprincipal\b")

# Individual-contributor / junior titles that should NOT score as decision-makers
# even when they contain a senior-ish word (analyst, associate consultant...).
JUNIOR_IC = rx(
    r"\banalyst\b", r"\bresearcher\b", r"research associate", r"\bcoordinator\b",
    r"\bassociate\b(?! partner| director| vice)", r"\bassistant\b(?! vice)",
    r"\bjunior\b", r"\bintern\b", r"\btrainee\b",
    r"\bexecutive\b(?! director| officer| chair| vice| vp)",
)
# Real-estate agents write "consultant/advisor" but are sales, not advisory.
# "intellectual property" guarded so IP advisors are not caught.
RE_POS = rx(r"real[\s-]?estate", r"\brealtor\b", r"\bbroker\b",
            r"property (consultant|advisor|adviser|agent|specialist|manager|sales)")
RE_CO = rx(r"real[\s-]?estate", r"\bproperties\b", r"\brealty\b")
# Retail / front-line sales roles that borrow "advisor/consultant" - not buyers.
SALES_RETAIL = rx(
    r"client advisor", r"lifestyle advisor", r"sales advisor", r"sales consultant",
    r"customer[\s\w]{0,15}advisor", r"travel (consultant|advisor)", r"sports? advisor",
    r"home[\s\w]{0,12}advisor", r"beauty advisor", r"fashion advisor",
    r"retail (advisor|sales)", r"showroom",
)
# HR/enablement "business partner" titles - mid-level employees, not equity partners.
HR_BP = rx(r"(people|culture|\bhr\b|human resources|business|learning|talent|enablement)\s+partner")
# Advisory / professional-services seniors (real ones, after the demotions above).
ADVISORY = rx(
    r"consultant", r"consulting", r"consultancy", r"advisor", r"advisory",
    r"\bcoach\b", r"coaching", r"mentor", r"fractional", r"strategist",
    r"lawyer", r"attorney", r"legal counsel", r"solicitor",
    r"accountant", r"\bcpa\b", r"professional services", r"facilitator",
)
PARTNER = rx(r"\bpartner\b")

EXCLUDE_DEFAULT = rx(
    r"\bstudent\b", r"\bintern\b", r"\binternship\b", r"graduate(?!d)",
    r"\btrainee\b", r"aspiring", r"seeking", r"looking for (work|opportunit)",
    r"\bunemployed\b", r"\bretired\b", r"open to work",
)

# Named seniority tiers a user can set as `min_seniority` in the ICP, mapped to the
# floor on the seniority score below. Documented in icp.example.yaml.
SENIORITY_FLOORS = {
    "ic": 0, "manager": 10, "director": 20, "vp": 22,
    "c_suite": 36, "founder": 45,
}


def any_match(text, regexes):
    return any(r.search(text) for r in regexes)


def is_realestate_agent(position, company):
    p, co = (position or "").lower(), (company or "").lower()
    if "intellectual property" in p:
        return False
    return any_match(p, RE_POS) or any_match(co, RE_CO)


def seniority_points(position, company=""):
    """Title -> rough seniority signal (0-45). Demotions applied first so a
    front-line 'advisor' or an analyst does not score like a decision-maker."""
    p = (position or "").lower()
    co = (company or "").lower()
    if any_match(p, FOUNDER_CORE):                 return 45
    if any_match(p, JUNIOR_IC):                    return 8
    if any_match(p, SALES_RETAIL):                 return 12
    if any_match(p, HR_BP):                        return 12
    if is_realestate_agent(p, co) and not any_match(p, rx(r"\bdirector\b", r"head of", r"\bpartner\b")):
        return 12
    if any_match(p, rx(r"\bceo\b", r"chief executive", r"managing director",
                       r"\bm\.?d\.?\b", r"chair", r"(?<!vice )president", r"managing partner")):
        return 40
    if any_match(p, rx(r"\bcoo\b", r"\bcfo\b", r"\bcto\b", r"\bcmo\b", r"chief .{0,20}officer")):
        return 36
    if any_match(p, ADVISORY):                     return 30
    if any_match(p, PARTNER):                      return 30
    if any_match(p, rx(r"general manager")):       return 28
    if any_match(p, VP_TIER):                      return 22
    if any_match(p, DIRECTOR_TIER):                return 20
    if any_match(p, MANAGER_TIER):                 return 10
    return 4


# ----------------------------------------------------------------------------
# Dates and names
# ----------------------------------------------------------------------------

TODAY = datetime.date.today()
_MSG_DATE = re.compile(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})")
YEAR_RX = re.compile(r"(\d{4})")


def parse_msg_date(s):
    m = _MSG_DATE.search(s or "")
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def rel_ago(days):
    if days is None:   return ""
    if days < 14:      return f"{days}d ago"
    if days < 60:      return f"{days // 7}w ago"
    if days < 365:     return f"{days // 30}mo ago"
    return f"{days // 365}y ago"


def norm_name(n):
    """First+last, stripped of credentials/emoji, for fuzzy warmth matching."""
    n = re.sub(r"[^A-Za-z\s'-]", " ", n or "")
    toks = [t for t in n.lower().split() if len(t) > 1]
    if len(toks) >= 2:
        return f"{toks[0]} {toks[-1]}"
    return toks[0] if toks else ""


# ----------------------------------------------------------------------------
# ICP config: JSON, or a small, explicitly-documented YAML subset (so the script
# stays standard-library-only - no PyYAML dependency, free-tier safe).
# Supported YAML grammar: blank lines, `# comments`, `key: scalar`, and a key
# followed by indented `- item` list lines. Nothing else. Anything richer should
# be written as JSON instead (the script reads either by file extension).
# ----------------------------------------------------------------------------

ICP_DEFAULT = {
    "label": "default (permissive: any decision-maker, no industry/region filter)",
    "roles": [],
    "industries": [],
    "company_keywords": [],
    "region_tokens": [],
    "exclude": [],
    "min_seniority": "ic",
    "threshold": 30,
    "show_n": 40,
}


def _coerce_scalar(v):
    v = v.strip().strip('"').strip("'")
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def _strip_inline_comment(s):
    """Cut a whitespace-preceded inline '#' comment, but never one inside quotes,
    so a value like `label: "Founders #1"` keeps its '#' instead of being truncated."""
    quote = None
    for i, ch in enumerate(s):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or s[i - 1].isspace()):
            return s[:i].rstrip()
    return s.rstrip()


def parse_simple_yaml(text):
    """Parse the documented YAML subset only. Raises ValueError on a construct it
    does not understand, rather than silently mis-reading the ICP."""
    data = {}
    cur_key = None
    for raw in text.splitlines():
        if raw.strip().startswith("#"):
            continue
        line = _strip_inline_comment(raw)
        if not line.strip():
            continue
        if re.match(r"^\s+-\s", line):  # list item under the current key
            if cur_key is None:
                raise ValueError(f"list item with no parent key: {raw!r}")
            data.setdefault(cur_key, [])
            if not isinstance(data[cur_key], list):
                raise ValueError(f"key {cur_key!r} got both a scalar and list items")
            data[cur_key].append(_coerce_scalar(line.strip()[1:].strip()))
            continue
        m = re.match(r"^([A-Za-z0-9_]+)\s*:\s*(.*)$", line)
        if not m:
            raise ValueError(f"unsupported line (not 'key:' or '- item'): {raw!r}")
        cur_key, val = m.group(1), m.group(2).strip()
        data[cur_key] = _coerce_scalar(val) if val else []
    return data


def load_icp(path):
    if not path:
        parsed = {}
    else:
        if not os.path.exists(path):
            raise SystemExit(f"ICP config not found: {path}")
        raw = open(path, encoding="utf-8-sig").read()
        parsed = json.loads(raw) if path.lower().endswith(".json") else parse_simple_yaml(raw)
    icp = dict(ICP_DEFAULT)
    icp.update({k: v for k, v in parsed.items() if v not in (None, "")})
    # normalise list fields to lists of lowercased strings
    for k in ("roles", "industries", "company_keywords", "region_tokens", "exclude"):
        val = icp.get(k) or []
        if isinstance(val, str):
            val = [val]
        icp[k] = [str(x).lower() for x in val]
    if path and "label" not in parsed:
        icp["label"] = os.path.basename(path)
    ms = str(icp.get("min_seniority", "ic")).lower()
    if ms not in SENIORITY_FLOORS:
        raise SystemExit(
            f"min_seniority must be one of {list(SENIORITY_FLOORS)}, got {ms!r}"
        )
    icp["min_seniority"] = ms
    icp["threshold"] = int(icp.get("threshold", 30))
    icp["show_n"] = int(icp.get("show_n", 40))
    # precompile user token matchers
    icp["_roles_rx"] = [re.compile(re.escape(t), re.I) for t in icp["roles"]]
    icp["_ind_rx"] = [re.compile(re.escape(t), re.I) for t in icp["industries"]]
    icp["_co_rx"] = [re.compile(re.escape(t), re.I) for t in icp["company_keywords"]]
    icp["_region_rx"] = [re.compile(re.escape(t), re.I) for t in icp["region_tokens"]]
    icp["_exclude_rx"] = [re.compile(re.escape(t), re.I) for t in icp["exclude"]]
    return icp


# ----------------------------------------------------------------------------
# CSV loading - from a folder OR straight out of a ZIP (LinkedIn may double-zip
# or nest one level; we match by basename anywhere in the archive).
# ----------------------------------------------------------------------------

class ExportSource:
    """Abstracts a folder vs a ZIP so the rest of the code just asks for a file."""

    def __init__(self, path):
        self.path = path
        self.zip = None
        self._zip_index = {}
        if os.path.isfile(path) and path.lower().endswith(".zip"):
            self.zip = zipfile.ZipFile(path)
            for name in self.zip.namelist():
                base = os.path.basename(name).lower()
                if base and base not in self._zip_index:
                    self._zip_index[base] = name
        elif not os.path.isdir(path):
            raise SystemExit(f"export path is neither a folder nor a .zip: {path}")

    def read_text(self, basename):
        """Return file text (utf-8-sig tolerant) or None if absent."""
        if self.zip is not None:
            name = self._zip_index.get(basename.lower())
            if not name:
                return None
            data = self.zip.read(name)
            return data.decode("utf-8-sig", errors="replace")
        # folder: search top level then one level down (some unzippers nest)
        candidates = [os.path.join(self.path, basename)]
        for sub in os.listdir(self.path):
            subdir = os.path.join(self.path, sub)
            if os.path.isdir(subdir):
                candidates.append(os.path.join(subdir, basename))
        for c in candidates:
            if os.path.exists(c):
                return open(c, encoding="utf-8-sig", errors="replace").read()
        return None

    def has(self, basename):
        return self.read_text(basename) is not None


def read_rows(src, basename):
    """Read a LinkedIn CSV, skipping any 'Notes:' preamble before the header."""
    text = src.read_text(basename)
    if text is None:
        return []
    lines = text.splitlines(keepends=True)
    hdr = 0
    for i, ln in enumerate(lines):
        first = ln.split(",")[0].strip().strip('"')
        if first in ("First Name", "From", "FROM", "CONVERSATION ID"):
            hdr = i
            break
    reader = csv.DictReader(lines[hdr:])
    return [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader]


def load_connections(src):
    out = []
    for r in read_rows(src, "Connections.csv"):
        fn, ln = r.get("First Name", ""), r.get("Last Name", "")
        if not (fn or ln):
            continue
        m = YEAR_RX.search(r.get("Connected On", ""))
        out.append({
            "name": f"{fn} {ln}".strip(),
            "company": r.get("Company", ""),
            "position": r.get("Position", ""),
            "url": r.get("URL", ""),
            "email": r.get("Email Address", ""),
            "connected_on": r.get("Connected On", ""),
            "year": m.group(1) if m else "",
        })
    return out


def load_warm_names(src, owner):
    """Return {lowercased name: {total, in, out, last}}. Direction-aware so 'warm'
    means they actually REPLIED, not just that one message went out. Names + the
    direction flag + the date only - message CONTENT is never read.

    `owner` is inferred (most frequent FROM sender) when not supplied, so a generic
    user does not have to hardcode their own name."""
    rows = read_rows(src, "messages.csv")
    if not rows:
        return {}
    if not owner:
        senders = defaultdict(int)
        for r in rows:
            frm = (r.get("FROM", "") or r.get("From", "")).strip()
            if frm:
                senders[frm] += 1
        owner = max(senders, key=senders.get) if senders else ""
    owner_l = owner.lower()
    data = {}
    for r in rows:
        frm = (r.get("FROM", "") or r.get("From", "")).strip()
        to = (r.get("TO", "") or r.get("To", "")).strip()
        folder_f = (r.get("FOLDER", "") or "").upper()
        if frm.lower() == owner_l or folder_f == "SENT":
            cp, direction = to, "out"
        else:
            cp, direction = frm, "in"
        cp = re.split(r"[;,]", cp)[0].strip()
        if not cp or cp.lower() == owner_l:
            continue
        d = data.setdefault(cp.lower(), {"total": 0, "in": 0, "out": 0, "last": None})
        d["total"] += 1
        d[direction] += 1
        dt = parse_msg_date(r.get("DATE", ""))
        if dt and (d["last"] is None or dt > d["last"]):
            d["last"] = dt
    return data


# ----------------------------------------------------------------------------
# Scoring + warmth
# ----------------------------------------------------------------------------

def warmth_tier(dm, days_since=None):
    """'Warm' requires a real reply (in>0). 'In conversation' also requires the
    thread to be RECENT (<=90d) - a two-way thread that last moved a year ago is
    dormant, not hot."""
    if not dm:
        return ("New / cold", "cold")
    recent = days_since is not None and days_since <= 90
    if dm["in"] >= 2 and dm["total"] >= 4 and recent:
        return ("In conversation", "hot")
    if dm["in"] >= 1:
        return ("Replied before", "warm")
    return ("You reached out", "cold")


def score(conn, dm, icp, region_hit):
    p = (conn["position"] or "").lower()
    co = (conn["company"] or "").lower()
    if not p and not co:
        return -100
    blob = f"{p} {co}"
    if any_match(blob, icp["_exclude_rx"]) or any_match(blob, EXCLUDE_DEFAULT):
        return -100
    sp = seniority_points(p, co)
    if sp < SENIORITY_FLOORS[icp["min_seniority"]]:
        return -100  # below the seniority floor the user asked for
    s = sp
    if icp["_roles_rx"] and any_match(p, icp["_roles_rx"]):     s += 15
    if icp["_ind_rx"] and any_match(blob, icp["_ind_rx"]):      s += 8
    if icp["_co_rx"] and any_match(co, icp["_co_rx"]):          s += 10
    yr = conn["year"]
    if yr == "2026":   s += 6
    elif yr == "2025": s += 3
    elif yr == "2024": s += 1
    if dm:
        s += 12 if dm["in"] > 0 else 4  # a real reply beats outbound-only
    if region_hit:                       s += 8
    if conn["email"]:                    s += 3
    return s


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------

def esc(s):
    return html.escape(s or "")


LOCAL_WARNING = ("This file holds real names and LinkedIn profile URLs from your own "
                 "export. Keep it on your machine - do NOT commit it to a repo or share it.")

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>LinkedIn network, ranked to your ICP</title>
<style>
  :root {{ --ink:#1d2330; --muted:#5b6472; --line:#e4e7ec; --bg:#fbfcfd;
           --accent:#2f6df0; --hot:#c0392b; --warm:#1f7a4d; --cold:#8a909c; }}
  * {{ box-sizing:border-box; }} html,body {{ margin:0; padding:0; }}
  body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
          color:var(--ink); background:var(--bg); font-size:15px; line-height:1.6; }}
  .wrap {{ max-width:1040px; margin:0 auto; padding:0 24px; }}
  header {{ background:#161b26; color:#fff; padding:48px 24px 40px; text-align:center; }}
  header h1 {{ font-size:32px; margin:0 0 10px; font-weight:650; }}
  header .sub {{ color:rgba(255,255,255,.78); max-width:680px; margin:0 auto; }}
  .stats {{ display:flex; gap:10px; flex-wrap:wrap; justify-content:center; margin-top:22px; }}
  .stat {{ background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.16);
           border-radius:10px; padding:10px 16px; min-width:96px; }}
  .stat .n {{ font-size:22px; font-weight:700; }}
  .stat .l {{ font-size:11px; letter-spacing:.5px; text-transform:uppercase; color:rgba(255,255,255,.6); }}
  .note {{ background:#fff; border:1px solid var(--line); border-left:3px solid var(--accent);
           border-radius:10px; padding:16px 18px; margin:26px 0; font-size:13.5px; color:var(--muted); }}
  .note b {{ color:var(--ink); }}
  table {{ width:100%; border-collapse:collapse; background:#fff; border:1px solid var(--line);
           border-radius:10px; overflow:hidden; font-size:13.5px; }}
  thead th {{ background:#161b26; color:#fff; text-align:left; padding:10px 12px; font-size:12px; }}
  tbody td {{ padding:10px 12px; border-top:1px solid var(--line); vertical-align:top; }}
  tbody tr:nth-child(even) {{ background:#f7f9fb; }}
  .rk {{ color:var(--cold); font-weight:700; width:30px; }}
  .nm {{ font-weight:650; }} .nm a {{ color:var(--ink); text-decoration:none; }}
  .nm a:hover {{ color:var(--accent); }}
  .ti {{ color:var(--muted); font-size:12.5px; }}
  .em {{ font-size:11.5px; color:var(--accent); }}
  .chip {{ display:inline-block; font-size:11px; font-weight:600; border-radius:999px;
           padding:3px 9px; white-space:nowrap; }}
  .chip.hot {{ background:rgba(192,57,43,.12); color:var(--hot); }}
  .chip.warm {{ background:rgba(31,122,77,.12); color:var(--warm); }}
  .chip.cold {{ background:#eef0f3; color:var(--cold); }}
  .chip.region {{ background:rgba(47,109,240,.12); color:var(--accent); }}
  .open {{ font-weight:600; color:var(--accent); text-decoration:none; white-space:nowrap; }}
  footer {{ color:var(--muted); font-size:12px; text-align:center; padding:36px 24px 48px; }}
</style>
</head>
<body>
  <header>
    <h1>Your LinkedIn network, ranked to your ICP</h1>
    <div class="sub">{total_conn} connections read. {qualified} match the ICP "{icp_label}", ranked by fit. Nothing is sent - this is a manual-outreach worklist.</div>
    <div class="stats">{stat_cells}</div>
  </header>
  <div class="wrap">
    <div class="note">
      <b>How this was scored.</b> Each connection got a seniority signal from its title (with demotions so analysts, front-line "advisors", and property agents do not read as decision-makers), plus a bonus for matching your ICP roles, industries, and company keywords, how recently you connected, whether they have actually replied to you, and {region_clause}. <b>Two honest limits:</b> seniority and region are inferred from a single title string, so a serious-consultancy founder and a side-hustle founder can score alike - this is a strong first cut, not a verdict; and warmth only sees export metadata (who messaged whom, how often, when), never the message text.{inbound_note}
      <br><br><b>Keep this local.</b> {local_warning}
    </div>
    {section}
  </div>
  <footer>Generated from your LinkedIn export &middot; {gen_date} &middot; Personal worklist, not for distribution</footer>
</body>
</html>
"""


def render_table(leads, show_n):
    rows = []
    for i, ld in enumerate(leads[:show_n], 1):
        wlabel, wclass = warmth_tier(ld["dm"], ld.get("days_since"))
        name_cell = f'<div class="nm"><a href="{esc(ld["url"])}" target="_blank" rel="noopener">{esc(ld["name"])}</a></div>'
        name_cell += f'<div class="ti">{esc(ld["position"])}</div>'
        if ld["email"]:
            name_cell += f'<div class="em">{esc(ld["email"])}</div>'
        ago = rel_ago(ld.get("days_since"))
        wtext = f"{wlabel} &middot; {ago}" if (ago and wclass != "cold") else wlabel
        chips = f'<span class="chip {wclass}">{wtext}</span>'
        if ld.get("region_hit"):
            chips += ' <span class="chip region">Region match</span>'
        open_cell = (f'<a class="open" href="{esc(ld["url"])}" target="_blank" rel="noopener">Open &rarr;</a>'
                     if ld["url"] else "")
        rows.append(
            f'<tr><td class="rk">{i}</td><td>{name_cell}</td>'
            f'<td>{esc(ld["company"])}</td><td>{esc(ld["connected_on"])}</td>'
            f'<td>{chips}</td><td>{open_cell}</td></tr>'
        )
    body = "\n".join(rows) if rows else '<tr><td colspan="6" style="padding:18px;color:#8a909c;">No connections matched this ICP.</td></tr>'
    return (
        '<table><thead><tr><th>#</th><th>Name &amp; title</th><th>Company</th>'
        '<th>Connected</th><th>Status</th><th>Link</th></tr></thead>'
        f'<tbody>{body}</tbody></table>'
    )


def write_markdown(path, leads, icp, totals, incoming, show_n):
    """Compact ranked digest - this is the file the assistant reads (small),
    NOT the raw CSV."""
    lines = []
    lines.append(f"# LinkedIn network scan - ICP: {icp['label']}")
    lines.append("")
    lines.append(f"> {LOCAL_WARNING}")
    lines.append("")
    lines.append(f"- Connections read: **{totals['total']}**")
    lines.append(f"- Qualified for this ICP (score >= {icp['threshold']}): **{totals['qualified']}**")
    lines.append(f"- Replied to you (warm): **{totals['warm']}**")
    if icp["region_tokens"]:
        lines.append(f"- Region-token match ({', '.join(icp['region_tokens'])}): **{totals['region']}**")
    lines.append(f"- Pending incoming invitations (warm inbound): **{len(incoming)}**")
    lines.append("")
    lines.append(f"## Top {min(show_n, len(leads))} ranked (of {totals['qualified']})")
    lines.append("")
    lines.append("| # | Name | Title | Company | Connected | Warmth | Score |")
    lines.append("|---|------|-------|---------|-----------|--------|-------|")
    for i, ld in enumerate(leads[:show_n], 1):
        wlabel, _ = warmth_tier(ld["dm"], ld.get("days_since"))
        nm = ld["name"].replace("|", "/")
        ti = (ld["position"] or "").replace("|", "/")[:50]
        cot = (ld["company"] or "").replace("|", "/")[:30]
        lines.append(f"| {i} | {nm} | {ti} | {cot} | {ld['connected_on']} | {wlabel} | {ld['score']} |")
    lines.append("")
    lines.append("Full rows with emails + profile URLs are in `network-scan.csv`. "
                 "Pending invitations are in `inbound-invites.csv`.")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="Rank a LinkedIn export against your ICP.")
    ap.add_argument("export", help="path to the export ZIP or unzipped export folder")
    ap.add_argument("outdir", help="folder to write the ranked output into (keep it OUTSIDE any repo)")
    ap.add_argument("--icp", default="", help="path to an ICP config (.yaml or .json). Omit for a permissive default.")
    ap.add_argument("--owner", default="", help="your own name as it appears in messages.csv (auto-detected if omitted)")
    args = ap.parse_args()

    icp = load_icp(args.icp)
    os.makedirs(args.outdir, exist_ok=True)
    src = ExportSource(args.export)

    if not src.has("Connections.csv"):
        raise SystemExit(
            "No Connections.csv found in the export. Point this at your unzipped LinkedIn "
            "export folder or the export .zip (Settings -> Data Privacy -> Get a copy of your data)."
        )

    conns = load_connections(src)
    warm = load_warm_names(src, args.owner)
    # normalized warmth index so credentials/emoji in a name still match
    warm_norm = {}
    for nm, d in warm.items():
        n = norm_name(nm)
        acc = warm_norm.setdefault(n, {"total": 0, "in": 0, "out": 0, "last": None})
        for k in ("total", "in", "out"):
            acc[k] += d[k]
        if d["last"] and (acc["last"] is None or d["last"] > acc["last"]):
            acc["last"] = d["last"]

    def dm_for(c):
        return warm.get(c["name"].lower()) or warm_norm.get(norm_name(c["name"]))

    def region_for(c):
        if not icp["_region_rx"]:
            return False
        return any_match(f"{c['position']} {c['company']}", icp["_region_rx"])

    # incoming connection requests = warm inbound (no title in the export, so a
    # names list, not part of the scored worklist)
    inv_rows = read_rows(src, "Invitations.csv")
    incoming = [r for r in inv_rows if (r.get("Direction", "") or "").upper() == "INCOMING"]
    with open(os.path.join(args.outdir, "inbound-invites.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["# " + LOCAL_WARNING])
        w.writerow(["name", "sent_at", "profile_url"])
        for r in incoming:
            w.writerow([r.get("From", ""), r.get("Sent At", ""), r.get("inviterProfileUrl", "")])

    qualified = []
    warm_total = region_total = 0
    for c in conns:
        dm = dm_for(c)
        region_hit = region_for(c)
        sc = score(c, dm, icp, region_hit)
        if sc < icp["threshold"]:
            continue
        last = dm["last"] if dm else None
        days_since = (TODAY - last).days if last else None
        c2 = dict(c, score=sc, dm=dm, region_hit=region_hit,
                  last_contact=last.isoformat() if last else "", days_since=days_since)
        qualified.append(c2)
        if dm and dm["in"] > 0:
            warm_total += 1
        if region_hit:
            region_total += 1

    qualified.sort(key=lambda x: (-x["score"], -(x["dm"]["in"] if x["dm"] else 0), x["name"]))

    totals = {"total": len(conns), "qualified": len(qualified),
              "warm": warm_total, "region": region_total}

    # ---- CSV (full rows) ----
    with open(os.path.join(args.outdir, "network-scan.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["# " + LOCAL_WARNING])
        w.writerow(["rank", "name", "title", "company", "connected_on", "region_match",
                    "warmth", "replies_in", "last_contact", "days_since", "score", "email", "linkedin_url"])
        for i, ld in enumerate(qualified, 1):
            wl, _ = warmth_tier(ld["dm"], ld["days_since"])
            w.writerow([i, ld["name"], ld["position"], ld["company"], ld["connected_on"],
                        "yes" if ld["region_hit"] else "", wl,
                        ld["dm"]["in"] if ld["dm"] else 0, ld["last_contact"],
                        ld["days_since"] if ld["days_since"] is not None else "",
                        ld["score"], ld["email"], ld["url"]])

    # ---- JSON ----
    with open(os.path.join(args.outdir, "network-scan.json"), "w", encoding="utf-8") as f:
        json.dump({"_notice": LOCAL_WARNING,
                   "icp": {k: v for k, v in icp.items() if not k.startswith("_")},
                   "totals": totals, "incoming_invites": len(incoming),
                   "leads": qualified}, f, indent=2, ensure_ascii=False, default=str)

    # ---- compact markdown (the file the assistant reads) ----
    write_markdown(os.path.join(args.outdir, "network-scan.md"),
                   qualified, icp, totals, incoming, icp["show_n"])

    # ---- HTML deliverable ----
    stat_cells = "".join([
        f'<div class="stat"><div class="n">{totals["qualified"]}</div><div class="l">Qualified</div></div>',
        f'<div class="stat"><div class="n">{warm_total}</div><div class="l">Replied</div></div>',
        f'<div class="stat"><div class="n">{len(incoming)}</div><div class="l">Inbound</div></div>',
    ])
    region_clause = (f"whether a region token ({', '.join(icp['region_tokens'])}) appears in their company or title"
                     if icp["region_tokens"] else "no region filter (you set none)")
    inbound_note = (f" Separately, {len(incoming)} people sent you a connection request that is still pending "
                    f"(warm inbound); they carry no title in the export, so they are listed by name in "
                    f"<b>inbound-invites.csv</b>.") if incoming else ""
    page = PAGE_TEMPLATE.format(
        total_conn=len(conns), qualified=totals["qualified"], icp_label=esc(icp["label"]),
        stat_cells=stat_cells, region_clause=region_clause, inbound_note=inbound_note,
        local_warning=LOCAL_WARNING, section=render_table(qualified, icp["show_n"]),
        gen_date=TODAY.isoformat(),
    )
    with open(os.path.join(args.outdir, "network-scan.html"), "w", encoding="utf-8") as f:
        f.write(page)

    # ---- terminal summary (no row dump) ----
    print(f"ICP             : {icp['label']}")
    print(f"connections read: {len(conns)}")
    print(f"qualified       : {totals['qualified']} (score >= {icp['threshold']}, min_seniority {icp['min_seniority']})")
    print(f"  replied to you: {warm_total}", end="")
    if icp["region_tokens"]:
        print(f"   region match: {region_total}", end="")
    print(f"   pending invites: {len(incoming)}")
    print(f"\noutput written to: {os.path.abspath(args.outdir)}")
    print("  network-scan.md   (compact ranked digest - read this one)")
    print("  network-scan.html (open in a browser)")
    print("  network-scan.csv / .json (full rows - keep local, do not commit)")


if __name__ == "__main__":
    main()
