# -*- coding: utf-8 -*-
"""
scan.py - Rank your own LinkedIn connection export against an ICP you define.

Reads:  Connections.csv, messages.csv (counterparty metadata only), Invitations.csv
        - from an unzipped export folder OR straight out of the export ZIP.
Writes: network-scan.html  (anonymised demo - safe to screen-record and share)
        network-scan-full.html (real names + links, watermarked local-only)
        network-scan.md + network-scan.csv + network-scan.json
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

# A title carrying real leadership weight (used by the optional
# require_leadership_title gate). Generic - no industry or region baked in.
LEADERSHIP_TITLE = rx(
    r"\bfounder\b", r"co-?founder", r"cofounder", r"\bowner\b", r"proprietor",
    r"\bceo\b", r"chief .{0,20}officer", r"\bcoo\b", r"\bcfo\b", r"\bcto\b",
    r"\bcmo\b", r"\bciso\b", r"\bcpo\b", r"managing director", r"\bm\.?d\.?\b(?! ?phd)",
    r"managing partner", r"\bpartner\b", r"\bdirector\b", r"head of",
    r"vice president", r"\bvp\b", r"\bevp\b", r"\bsvp\b", r"general manager",
    r"(?<!vice )(?<!vice-)president", r"chair(man|woman|person)?\b",
)


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
# "14 May 2026", "May 14, 2026" style dates LinkedIn writes in Connected On.
_CONN_DATE = re.compile(
    r"(\d{1,2})\s+([A-Za-z]{3,})\s+(\d{4})|([A-Za-z]{3,})\s+(\d{1,2}),?\s+(\d{4})"
)
_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def parse_msg_date(s):
    m = _MSG_DATE.search(s or "")
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def parse_connected_on(s):
    """LinkedIn writes Connected On as e.g. '14 May 2026' or '2026-05-14'. Return a
    date or None. Used only for the export-freshness check."""
    s = (s or "").strip()
    if not s:
        return None
    iso = parse_msg_date(s)
    if iso:
        return iso
    m = _CONN_DATE.search(s)
    if not m:
        return None
    try:
        if m.group(1):
            day, mon, year = int(m.group(1)), m.group(2)[:3].lower(), int(m.group(3))
        else:
            mon, day, year = m.group(4)[:3].lower(), int(m.group(5)), int(m.group(6))
        if mon in _MONTHS:
            return datetime.date(year, _MONTHS[mon], day)
    except (ValueError, KeyError):
        return None
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
    "demote_keywords": [],
    "min_seniority": "ic",
    "require_leadership_title": False,
    "threshold": 30,
    "show_n": 40,
}


def _coerce_scalar(v):
    v = v.strip().strip('"').strip("'")
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    low = v.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
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


def _as_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("true", "yes", "1")


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
    for k in ("roles", "industries", "company_keywords", "region_tokens", "exclude", "demote_keywords"):
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
    icp["require_leadership_title"] = _as_bool(icp.get("require_leadership_title", False))
    icp["threshold"] = int(icp.get("threshold", 30))
    icp["show_n"] = int(icp.get("show_n", 40))
    # precompile user token matchers
    icp["_roles_rx"] = [re.compile(re.escape(t), re.I) for t in icp["roles"]]
    icp["_ind_rx"] = [re.compile(re.escape(t), re.I) for t in icp["industries"]]
    icp["_co_rx"] = [re.compile(re.escape(t), re.I) for t in icp["company_keywords"]]
    icp["_region_rx"] = [re.compile(re.escape(t), re.I) for t in icp["region_tokens"]]
    icp["_exclude_rx"] = [re.compile(re.escape(t), re.I) for t in icp["exclude"]]
    icp["_demote_rx"] = [re.compile(re.escape(t), re.I) for t in icp["demote_keywords"]]
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
        self._zip_dates = {}
        if os.path.isfile(path) and path.lower().endswith(".zip"):
            self.zip = zipfile.ZipFile(path)
            for info in self.zip.infolist():
                base = os.path.basename(info.filename).lower()
                if base and base not in self._zip_index:
                    self._zip_index[base] = info.filename
                    try:
                        self._zip_dates[base] = datetime.date(*info.date_time[:3])
                    except (ValueError, TypeError):
                        pass
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
        for c in self._folder_candidates(basename):
            if os.path.exists(c):
                return open(c, encoding="utf-8-sig", errors="replace").read()
        return None

    def _folder_candidates(self, basename):
        candidates = [os.path.join(self.path, basename)]
        for sub in os.listdir(self.path):
            subdir = os.path.join(self.path, sub)
            if os.path.isdir(subdir):
                candidates.append(os.path.join(subdir, basename))
        return candidates

    def mtime_date(self, basename):
        """Best-effort modification date for a file inside the export, for the
        freshness check. ZIP entries carry their own stored date."""
        if self.zip is not None:
            return self._zip_dates.get(basename.lower())
        for c in self._folder_candidates(basename):
            if os.path.exists(c):
                return datetime.date.fromtimestamp(os.path.getmtime(c))
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
            "first": fn,
            "last": ln,
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


def is_demoted(position, company, icp):
    """Optional, config-driven won't-DIY / self-serve demotion. Returns True when a
    user-supplied demote_keyword matches the title or company. Off when the list is
    empty, so default behaviour is unchanged."""
    if not icp["_demote_rx"]:
        return False
    return any_match(f"{(position or '').lower()} {(company or '').lower()}", icp["_demote_rx"])


def score(conn, dm, icp, region_hit):
    p = (conn["position"] or "").lower()
    co = (conn["company"] or "").lower()
    if not p and not co:
        return -100
    blob = f"{p} {co}"
    if any_match(blob, icp["_exclude_rx"]) or any_match(blob, EXCLUDE_DEFAULT):
        return -100
    # Optional: require a real leadership title (off by default).
    if icp["require_leadership_title"] and not any_match(p, LEADERSHIP_TITLE):
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
    # Optional, config-driven demotion: push a self-serve / would-DIY cluster down
    # a tier. Generic - the keywords come from the ICP, nothing is hardcoded.
    if is_demoted(p, co, icp):           s -= 12
    return s


def fit_tier(score_value, threshold):
    """Map a final score to a coarse, ICP-relative bucket for filter chips and the
    donut. Generic and threshold-relative so it works for any ICP."""
    if score_value >= threshold + 20:
        return ("top", "Top fit")
    if score_value >= threshold + 8:
        return ("strong", "Strong fit")
    return ("match", "Match")


def region_scope(region_hit, has_region_tokens):
    """Generic region scope. With region tokens set: 'in' when one hit, 'maybe'
    when none (a LinkedIn export has no location field, so absence is unknown, not
    out). With no region tokens set: 'unknown' for everyone."""
    if not has_region_tokens:
        return ("unknown", "Region not set")
    return ("in", "Region match") if region_hit else ("maybe", "Region unknown")


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------

def esc(s):
    return html.escape(str(s) if s is not None else "")


LOCAL_WARNING = ("This file holds real names and LinkedIn profile URLs from your own "
                 "export. Keep it on your machine - do NOT commit it to a repo or share it.")


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
    if icp["demote_keywords"]:
        lines.append(f"- Demoted (would-DIY / self-serve cluster): **{totals['demoted']}**")
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
    lines.append("Two browsable views ship alongside this digest: `network-scan.html` is an "
                 "anonymised demo (initials, no links) that is safe to record and share, and "
                 "`network-scan-full.html` carries real names and links for local use only. "
                 "Full rows with emails and profile URLs are in `network-scan.csv`. Pending "
                 "invitations are in `inbound-invites.csv`.")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ----------------------------------------------------------------------------
# Interactive HTML (vanilla JS, self-contained, offline). Neutral palette the
# founder can rebrand - greys plus one accent. Data lives in a JSON island; the
# page filters / re-counts / re-draws an inline-SVG donut entirely client-side.
# Two outputs:
#   - network-scan.html      anonymised demo (initials, masked company, no links,
#                             low/parked rows dropped). Safe to record and share -
#                             no real names exist in the source.
#   - network-scan-full.html real names + links + email, watermarked local-only.
# ----------------------------------------------------------------------------

PAGE_V3 = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Your LinkedIn network, sorted to your ICP</title>
<style>
/* LinkedIn-native, black/white. No web fonts - fully offline, uses the system
   stack LinkedIn itself uses. One restrained accent (LinkedIn blue). */
:root{
  --ink:#000000e6; --ink-soft:#000000b3; --muted:#00000099; --muted-light:#00000066;
  --line:#e8e6e3; --bg:#f4f2ee; --card:#ffffff; --head:#ffffff;
  --accent:#0a66c2; --accent-dark:#004182;
  --tier-top:#0a66c2; --tier-strong:#5f5f5f; --tier-match:#b0b0b0;
  --in:#057642; --maybe:#00000066; --out:#0000004d;
  --hot:#b24020; --warm:#057642; --cold:#00000066;
  --r-sm:8px; --r-md:8px; --r-lg:8px; --r-pill:999px;
  --font:-apple-system,system-ui,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:var(--font);color:var(--ink);background:var(--bg);font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased;}
.wrap{max-width:1180px;margin:0 auto;padding:0 22px;}
.markbar{font-size:11.5px;letter-spacing:.5px;text-align:center;padding:7px 10px;font-weight:600;}
.markbar.demo{background:rgba(31,122,77,.12);color:var(--in);border-bottom:1px solid rgba(31,122,77,.3);}
.markbar.full{background:rgba(192,57,43,.1);color:var(--hot);border-bottom:1px solid rgba(192,57,43,.3);}
.cornermark{position:fixed;right:14px;bottom:12px;z-index:60;opacity:.85;font-size:11px;font-weight:700;color:var(--muted-light);letter-spacing:1px;text-transform:uppercase;}
.hero{background:var(--head);color:var(--ink);padding:42px 22px 34px;text-align:center;border-bottom:1px solid var(--line);}
.brand{display:inline-flex;align-items:center;gap:9px;margin-bottom:16px;}
.brand .dot{width:9px;height:9px;background:var(--accent);border-radius:var(--r-pill);}
.brand .lab{font-size:12px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);font-weight:600;}
.hero h1{font-size:32px;line-height:1.15;letter-spacing:-.4px;margin:0 auto 12px;font-weight:600;max-width:760px;}
.hero h1 .hl{color:var(--accent);}
.hero .sub{font-size:15px;color:var(--muted);margin:0 auto;max-width:640px;}
.statrow{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:24px;}
.stat{background:var(--card);border:1px solid var(--line);border-radius:var(--r-md);padding:11px 17px;min-width:120px;}
.stat .n{font-size:24px;font-weight:600;color:var(--ink);}
.stat .l{font-size:10.5px;letter-spacing:.6px;text-transform:uppercase;color:var(--muted);margin-top:2px;}
.panel{position:sticky;top:0;z-index:30;background:rgba(244,242,238,.95);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:14px 0;}
.panel .wrap{position:relative;}
.frow{display:flex;gap:14px;flex-wrap:wrap;align-items:center;}
.fgroup{display:flex;gap:5px;align-items:center;flex-wrap:wrap;}
.fgroup .glab{font-size:10.5px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--muted);margin-right:2px;}
.chip{font-size:12px;font-weight:600;border-radius:var(--r-pill);padding:6px 13px;border:1px solid var(--line);background:#fff;color:var(--ink);cursor:pointer;transition:all .15s;user-select:none;}
.chip:hover{border-color:var(--accent);}
.chip.on{background:var(--ink);color:#fff;border-color:var(--ink);}
.chip.on.k-top{background:var(--tier-top);border-color:var(--tier-top);}
.chip.on.k-strong{background:var(--tier-strong);border-color:var(--tier-strong);}
.chip.on.k-match{background:var(--tier-match);border-color:var(--tier-match);}
.search{font-family:var(--font);font-size:13px;padding:7px 13px;border:1px solid var(--line);border-radius:var(--r-pill);outline:none;min-width:170px;background:#fff;}
.search:focus{border-color:var(--accent);}
.toggle{font-size:12px;font-weight:600;border-radius:var(--r-pill);padding:6px 13px;border:1px solid var(--line);background:#fff;cursor:pointer;}
.toggle.on{background:var(--accent);color:#fff;border-color:var(--accent);}
.activecount{font-size:12px;color:var(--muted);font-weight:600;margin-left:auto;}
.activecount b{color:var(--ink);}
.layout{display:grid;grid-template-columns:300px 1fr;gap:22px;margin:26px 0;align-items:start;}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r-lg);padding:20px;position:relative;}
.card h3{font-size:13px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;color:var(--muted);margin-bottom:14px;}
.donutwrap{display:flex;flex-direction:column;align-items:center;}
.donutwrap svg{display:block;}
.donutwrap.pop{animation:pop .5s cubic-bezier(.2,.8,.2,1);}
@keyframes pop{from{opacity:0;transform:scale(.92);}to{opacity:1;transform:scale(1);}}
.legend{margin-top:14px;width:100%;}
.legrow{display:flex;align-items:center;gap:8px;font-size:12.5px;padding:4px 0;cursor:pointer;}
.legrow .sw{width:12px;height:12px;border-radius:3px;flex:0 0 auto;}
.legrow .lv{margin-left:auto;font-weight:700;}
.dtoggle{display:flex;gap:5px;margin-bottom:14px;}
.dtoggle .chip{padding:5px 11px;font-size:11.5px;}
.tablecard{padding:0;overflow:hidden;}
.tablehead{display:flex;align-items:center;justify-content:space-between;padding:16px 20px;border-bottom:1px solid var(--line);}
.tablehead .shown{font-size:12.5px;color:var(--muted);font-weight:600;}
.tablehead .shown b{color:var(--ink);}
.tscroll{overflow-x:auto;}
table{width:100%;border-collapse:collapse;font-size:13px;}
thead th{background:#f3f2ef;color:var(--muted);text-align:left;padding:10px 14px;font-weight:600;font-size:11px;letter-spacing:.4px;text-transform:uppercase;white-space:nowrap;border-bottom:1px solid var(--line);}
tbody td{padding:9px 14px;border-top:1px solid var(--line);vertical-align:top;}
tbody tr:nth-child(even){background:#fafbfc;}
tbody tr:hover{background:#eef3fe;}
.nm{font-weight:600;color:var(--ink);white-space:nowrap;}
.nm a{color:var(--ink);text-decoration:none;} .nm a:hover{color:var(--accent);}
.ti{color:var(--muted);font-size:12px;}
.tk{display:inline-block;font-size:10.5px;font-weight:700;border-radius:var(--r-pill);padding:3px 9px;white-space:nowrap;}
.tk.top{background:rgba(10,102,194,.12);color:var(--accent-dark);}
.tk.strong{background:rgba(91,100,114,.16);color:var(--ink-soft);}
.tk.match{background:rgba(154,161,173,.2);color:var(--muted);}
.sc{display:inline-block;font-size:10.5px;font-weight:600;border-radius:var(--r-pill);padding:3px 9px;white-space:nowrap;}
.sc.in{background:rgba(31,122,77,.16);color:var(--in);}
.sc.maybe{background:#eef0f3;color:var(--muted);}
.sc.unknown{background:#eef0f3;color:var(--muted);}
.sc.out{background:#ececec;color:var(--muted);}
.wm{font-size:11px;font-weight:600;}
.wm.hot{color:var(--hot);} .wm.warm{color:var(--warm);} .wm.cold{color:var(--muted-light);}
.yes{color:var(--in);font-weight:700;} .no{color:var(--muted-light);}
.note{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:var(--r-md);padding:16px 18px;margin:8px 0 26px;font-size:13px;color:var(--muted);}
.note b{color:var(--ink);}
footer{background:var(--card);color:var(--ink);margin-top:34px;padding:32px 22px;text-align:center;border-top:1px solid var(--line);}
footer .l1{font-weight:600;font-size:16px;}
footer .l2{font-weight:600;font-size:16px;color:var(--accent);}
footer .meta{color:var(--muted);font-size:12px;margin-top:12px;}
@media(max-width:820px){
  .layout{grid-template-columns:1fr;}
  .hero h1{font-size:26px;}
  .activecount{margin-left:0;width:100%;}
}
</style></head>
<body class="__MODE__">
<div class="markbar __MODE__">__WATERMARK__</div>
<header class="hero">
  <div class="brand">__LOGO_TAG__</div>
  <h1>From <span class="hl">__TOTAL__</span> LinkedIn connections, here are the <span class="hl">__SHOWN__</span> worth acting on</h1>
  <p class="sub">No scraper. No paid tool. No automated actions. Your own export, scored locally against the ICP you set, and sorted into a worklist.</p>
  <div class="statrow" id="herostats"></div>
</header>
<div class="panel"><div class="wrap">
  <div class="frow">
    <div class="fgroup"><span class="glab">Fit</span><span id="tierchips"></span></div>
    <div class="fgroup"><span class="glab">Region</span><span id="scopechips"></span></div>
    <div class="fgroup"><span class="glab">Warmth</span><span id="warmchips"></span></div>
    <div class="fgroup"><span class="toggle" id="emailtog">Has email</span></div>
    <div class="fgroup"><input class="search" id="search" placeholder="Search title / role..." /></div>
    <div class="fgroup"><span class="chip" id="reset">Reset</span></div>
    <span class="activecount" id="activecount"></span>
  </div>
</div></div>
<div class="wrap"><div class="layout">
  <div class="card">
    <h3>The split</h3>
    <div class="dtoggle">
      <span class="chip on" id="dt-tier" data-mode="tier">By fit</span>
      <span class="chip" id="dt-scope" data-mode="scope">By region</span>
      <span class="chip" id="dt-warm" data-mode="warm">By warmth</span>
    </div>
    <div class="donutwrap" id="donut"></div>
    <div class="legend" id="legend"></div>
  </div>
  <div class="card tablecard">
    <div class="tablehead">
      <div class="shown" id="shown"></div>
    </div>
    <div class="tscroll"><table>
      <thead id="thead"></thead>
      <tbody id="tbody"></tbody>
    </table></div>
  </div>
</div>
<div class="note" id="limits"><b>Honest limits.</b> A LinkedIn export carries no location field, so region is inferred from the tokens you set against the company and title - treat "region unknown" as kept, not excluded. Fit is a title-only first pass, not a verdict: skim the top and confirm on the profile before acting. Message content is never read - only who you spoke to, the direction, and when.</div>
</div>
<footer>
  <div class="l1">This is your network.</div>
  <div class="l2">Now it is a worklist.</div>
  <div class="meta">Built locally from your own LinkedIn export &middot; __GEN_DATE__</div>
</footer>
<div class="cornermark">__CORNER_TAG__</div>
<script id="data" type="application/json">__DATA_JSON__</script>
<script>
(function(){
  var RAW = JSON.parse(document.getElementById('data').textContent);
  var MODE = "__MODE__";
  var TOTAL = __TOTAL__;
  var TIER_LABEL = {top:"Top fit", strong:"Strong fit", match:"Match"};
  var TIER_COLOR = {top:"#0a66c2", strong:"#5f5f5f", match:"#b0b0b0"};
  var SCOPE_LABEL = {in:"Region match", maybe:"Region unknown", unknown:"Region not set", out:"Outside region"};
  var SCOPE_COLOR = {in:"#057642", maybe:"#8a8a8a", unknown:"#8a8a8a", out:"#c0c0c0"};
  var WARM_LABEL = {hot:"In conversation", warm:"Replied before", cold:"New / cold"};
  var WARM_COLOR = {hot:"#b24020", warm:"#057642", cold:"#8a8a8a"};
  var TIER_ORDER = ["top","strong","match"];
  var SCOPE_ORDER = ["in","maybe","unknown","out"];
  var WARM_ORDER = ["hot","warm","cold"];

  var state = {tier:"all", scope:"all", warm:"all", email:false, q:"", donut:"tier"};

  function apply(){
    var q = state.q.trim().toLowerCase();
    return RAW.filter(function(r){
      if(state.tier!=="all" && r.tier!==state.tier) return false;
      if(state.scope!=="all" && r.scope!==state.scope) return false;
      if(state.warm!=="all" && r.warmth!==state.warm) return false;
      if(state.email && r.email!==1) return false;
      if(q){
        var hay = (r.title+" "+(r.co||"")+" "+(r.name||"")).toLowerCase();
        if(hay.indexOf(q)<0) return false;
      }
      return true;
    });
  }

  function countBy(rows, key, order, labelMap, colorMap){
    var c={};
    rows.forEach(function(r){var k=r[key]; c[k]=(c[k]||0)+1;});
    var out=[];
    order.forEach(function(k){ if(c[k]) out.push({key:k,label:labelMap[k],value:c[k],color:colorMap[k]}); });
    return out;
  }

  function donutSVG(segs){
    var total=0; segs.forEach(function(s){total+=s.value;}); if(total===0) total=1;
    var R=66, CX=84, CY=84, W=24, C=2*Math.PI*R, off=0, arcs="";
    segs.forEach(function(s){
      var len = s.value/total*C;
      arcs += '<circle cx="'+CX+'" cy="'+CY+'" r="'+R+'" fill="none" stroke="'+s.color+'" stroke-width="'+W+'"'
            + ' stroke-dasharray="'+len.toFixed(2)+' '+(C-len).toFixed(2)+'" stroke-dashoffset="'+(-off).toFixed(2)+'"'
            + ' transform="rotate(-90 '+CX+' '+CY+')"></circle>';
      off += len;
    });
    var shown = segs.reduce(function(a,s){return a+s.value;},0);
    return '<svg viewBox="0 0 168 168" width="168" height="168" role="img" aria-label="distribution">'
         + arcs
         + '<text x="84" y="80" text-anchor="middle" font-size="30" font-weight="600" fill="#000000">'+shown+'</text>'
         + '<text x="84" y="98" text-anchor="middle" font-size="10.5" fill="#666666" letter-spacing="1">PEOPLE</text>'
         + '</svg>';
  }

  function donutConfig(){
    if(state.donut==="scope") return {key:"scope",order:SCOPE_ORDER,lab:SCOPE_LABEL,col:SCOPE_COLOR,set:setScope,cur:function(){return state.scope;}};
    if(state.donut==="warm")  return {key:"warmth",order:WARM_ORDER,lab:WARM_LABEL,col:WARM_COLOR,set:setWarm,cur:function(){return state.warm;}};
    return {key:"tier",order:TIER_ORDER,lab:TIER_LABEL,col:TIER_COLOR,set:setTier,cur:function(){return state.tier;}};
  }

  function renderDonut(rows){
    var cfg=donutConfig();
    var segs=countBy(rows,cfg.key,cfg.order,cfg.lab,cfg.col);
    var d=document.getElementById('donut');
    d.innerHTML = donutSVG(segs);
    d.classList.remove('pop'); void d.offsetWidth; d.classList.add('pop');
    var leg=document.getElementById('legend'); leg.innerHTML="";
    segs.forEach(function(s){
      var row=document.createElement('div'); row.className='legrow';
      row.innerHTML='<span class="sw" style="background:'+s.color+'"></span><span>'+s.label+'</span><span class="lv">'+s.value+'</span>';
      row.onclick=function(){ cfg.set(cfg.cur()===s.key?"all":s.key); };
      leg.appendChild(row);
    });
  }

  function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c];});}

  function renderTable(rows){
    var CAP=250;
    var thead=document.getElementById('thead'), tbody=document.getElementById('tbody');
    if(MODE==="full"){
      thead.innerHTML='<tr><th>#</th><th>Name</th><th>Title</th><th>Company</th><th>Region</th><th>Fit</th><th>Warmth</th><th>Email</th></tr>';
    } else {
      thead.innerHTML='<tr><th>#</th><th></th><th>Title</th><th>Company</th><th>Region</th><th>Fit</th><th>Warmth</th><th>Email</th></tr>';
    }
    var html="", n=Math.min(rows.length,CAP);
    for(var i=0;i<n;i++){
      var r=rows[i];
      var loc='<span class="sc '+r.scope+'">'+esc(SCOPE_LABEL[r.scope]||r.scope)+'</span>';
      var tk='<span class="tk '+r.tier+'">'+esc(TIER_LABEL[r.tier]||r.tier)+'</span>';
      var wm='<span class="wm '+r.warmth+'">'+esc(WARM_LABEL[r.warmth]||r.warmth)+'</span>';
      var em = r.email ? '<span class="yes">yes</span>' : '<span class="no">-</span>';
      if(MODE==="full"){
        var nm = r.url ? '<a href="'+esc(r.url)+'" target="_blank" rel="noopener">'+esc(r.name)+'</a>' : esc(r.name);
        html+='<tr><td class="ti">'+(i+1)+'</td><td class="nm">'+nm+'</td><td class="ti">'+esc(r.title)+'</td><td class="ti">'+esc(r.co)+'</td><td>'+loc+'</td><td>'+tk+'</td><td>'+wm+'</td><td>'+em+'</td></tr>';
      } else {
        html+='<tr><td class="ti">'+(i+1)+'</td><td class="nm">'+esc(r.init)+'</td><td class="ti">'+esc(r.title)+'</td><td class="ti">'+esc(r.co)+'</td><td>'+loc+'</td><td>'+tk+'</td><td>'+wm+'</td><td>'+em+'</td></tr>';
      }
    }
    tbody.innerHTML=html;
    document.getElementById('shown').innerHTML='Showing <b>'+n+'</b> of <b>'+rows.length+'</b>'+(rows.length>CAP?' (top '+CAP+' for speed)':'');
  }

  function renderHeroStats(){
    var top=0,strong=0,warm=0; RAW.forEach(function(r){ if(r.tier==="top")top++; if(r.tier==="strong")strong++; if(r.warmth!=="cold")warm++; });
    var cells=[[TOTAL,"Connections read"],[RAW.length,"On the worklist"],[top,"Top fit"],[warm,"Replied before"]];
    document.getElementById('herostats').innerHTML = cells.map(function(c){
      return '<div class="stat"><div class="n">'+c[0]+'</div><div class="l">'+c[1]+'</div></div>';
    }).join("");
  }

  function buildChipGroup(elId, order, labelMap, cur, setter, classPrefix){
    var box=document.getElementById(elId); box.innerHTML="";
    var all=document.createElement('span'); all.className='chip'+(cur()==="all"?' on':''); all.textContent='All'; all.onclick=function(){setter("all");}; box.appendChild(all);
    order.forEach(function(k){
      var c=document.createElement('span');
      c.className='chip'+(classPrefix?(' '+classPrefix+k):'')+(cur()===k?' on':'');
      c.textContent=labelMap[k]; c.onclick=function(){setter(cur()===k?"all":k);}; box.appendChild(c);
    });
  }

  function renderChips(){
    buildChipGroup('tierchips', TIER_ORDER, TIER_LABEL, function(){return state.tier;}, setTier, 'k-');
    buildChipGroup('scopechips', SCOPE_ORDER.filter(scopePresent), SCOPE_LABEL, function(){return state.scope;}, setScope, '');
    buildChipGroup('warmchips', WARM_ORDER, WARM_LABEL, function(){return state.warm;}, setWarm, '');
    document.getElementById('emailtog').className='toggle'+(state.email?' on':'');
  }

  var _scopesPresent={};
  RAW.forEach(function(r){_scopesPresent[r.scope]=1;});
  function scopePresent(k){return !!_scopesPresent[k];}

  function activeSummary(rows){
    var bits=[];
    if(state.tier!=="all") bits.push(TIER_LABEL[state.tier]);
    if(state.scope!=="all") bits.push(SCOPE_LABEL[state.scope]);
    if(state.warm!=="all") bits.push(WARM_LABEL[state.warm]);
    if(state.email) bits.push("has email");
    if(state.q.trim()) bits.push('"'+state.q.trim()+'"');
    var label = bits.length ? bits.join(" + ") : "no filters";
    document.getElementById('activecount').innerHTML='<b>'+rows.length+'</b> people &middot; '+esc(label);
  }

  function render(){
    var rows=apply();
    renderChips();
    renderDonut(rows);
    renderTable(rows);
    activeSummary(rows);
  }
  function setTier(v){state.tier=v;render();}
  function setScope(v){state.scope=v;render();}
  function setWarm(v){state.warm=v;render();}

  document.getElementById('emailtog').onclick=function(){state.email=!state.email;render();};
  document.getElementById('search').oninput=function(e){state.q=e.target.value;render();};
  document.getElementById('reset').onclick=function(){state={tier:"all",scope:"all",warm:"all",email:false,q:"",donut:state.donut};document.getElementById('search').value="";render();};
  function pickDonut(mode){
    state.donut=mode;
    ['tier','scope','warm'].forEach(function(m){
      document.getElementById('dt-'+m).classList.toggle('on', m===mode);
    });
    render();
  }
  document.getElementById('dt-tier').onclick=function(){pickDonut('tier');};
  document.getElementById('dt-scope').onclick=function(){pickDonut('scope');};
  document.getElementById('dt-warm').onclick=function(){pickDonut('warm');};

  renderHeroStats();
  render();
})();
</script>
</body></html>"""


def _initials(first, last):
    a = (first or "").strip()
    b = (last or "").strip()
    out = ""
    if a:
        out += a[0].upper() + "."
    if b:
        out += b[0].upper() + "."
    return out or "?"


def _mask_company(scope):
    return {"in": "a firm in your region", "maybe": "a company",
            "unknown": "a company"}.get(scope, "a company")


def _scrub_title(title, company):
    """Strip the employer name out of a title for the DEMO blob, so a title like
    'Founder and CEO of <Company>' does not leak the company the masked company
    field hides. Generic titles ('Founder', 'Managing Director') stay untouched."""
    t = title or ""
    if company and len(company) >= 3:
        t = re.sub(r"\b" + re.escape(company) + r"\b", "", t, flags=re.I)
    t = re.sub(r"\s*\b(?:at|of|for|with|@)\s*$", "", t.strip(), flags=re.I)
    t = re.sub(r"\s{2,}", " ", t).strip(" ,|-/&")
    return t or "Role withheld"


def build_v3_blob(leads, anonymise):
    """Build the JSON island. In anonymised demo mode, real names, companies, URLs
    and emails are NEVER written into the blob - only initials and a masked company
    label, and the employer name is scrubbed out of the title. Low-fit 'match'-tier
    rows are dropped from the demo so the safe view leads with the strongest people."""
    blob = []
    for i, ld in enumerate(leads):
        tier = ld["tier"]
        if anonymise and tier == "match":
            continue  # keep the safe demo to the stronger rows only
        rec = {
            "id": i,
            "title": ld["position"] or "",
            "tier": tier,
            "scope": ld["scope"],
            "warmth": ld["warm_class"],
            "email": 1 if ld["email"] else 0,
        }
        if anonymise:
            rec["init"] = _initials(ld.get("first"), ld.get("last"))
            rec["co"] = _mask_company(ld["scope"])
            # scrub the REAL employer token out of the demo title
            rec["title"] = _scrub_title(ld["position"], ld["company"])
        else:
            rec["name"] = ld["name"]
            rec["co"] = ld["company"] or ""
            rec["url"] = ld["url"] or ""
        blob.append(rec)
    return blob


def render_html_v3(path, leads, totals, brand_name, anonymise=True):
    blob = build_v3_blob(leads, anonymise)
    data_json = json.dumps(blob, ensure_ascii=False).replace("</", "<\\/")
    mode = "demo" if anonymise else "full"
    watermark = ("Demo view - names anonymised, safe to record and share"
                 if anonymise else
                 "Local file - not for distribution. Real names and links.")
    bn = esc(brand_name) if brand_name else ""
    if bn:
        logo_tag = f'<span class="dot"></span><span class="lab">{bn}</span>'
        corner_tag = bn
    else:
        logo_tag = '<span class="dot"></span><span class="lab">Network scan</span>'
        corner_tag = "Local"
    page = (PAGE_V3
            .replace("__MODE__", mode)
            .replace("__WATERMARK__", watermark)
            .replace("__LOGO_TAG__", logo_tag)
            .replace("__CORNER_TAG__", corner_tag)
            .replace("__TOTAL__", str(totals["total"]))
            .replace("__SHOWN__", str(len(blob)))
            .replace("__GEN_DATE__", TODAY.isoformat())
            .replace("__DATA_JSON__", data_json))
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    return len(blob)


# ----------------------------------------------------------------------------
# Export-freshness check
# ----------------------------------------------------------------------------

def freshness_check(src, conns):
    """Return (newest_date, days_old, warned_text). Newest signal = the most recent
    Connected On date in the export, falling back to the Connections.csv file date.
    A LinkedIn export goes stale: roles change, people move. Warn past ~30 days."""
    newest = None
    for c in conns:
        d = parse_connected_on(c.get("connected_on", ""))
        if d and (newest is None or d > newest):
            newest = d
    if newest is None:
        newest = src.mtime_date("Connections.csv")
    if newest is None:
        return (None, None, "")
    days_old = (TODAY - newest).days
    if days_old > 30:
        warn = (
            f"WARNING: this export looks {days_old} days old (newest activity {newest.isoformat()}). "
            "Roles change and people move - re-pull before acting on it. "
            "LinkedIn -> Settings -> Data privacy -> Get a copy of your data -> "
            "Download larger data archive (it includes Connections) -> Request archive. "
            "It usually arrives within 24 hours; the quick select-files route is unreliable for Connections."
        )
        return (newest, days_old, warn)
    return (newest, days_old, "")


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
    ap.add_argument("--brand", default="", help="optional label to show in the HTML header (e.g. your name or company)")
    args = ap.parse_args()

    icp = load_icp(args.icp)
    os.makedirs(args.outdir, exist_ok=True)
    src = ExportSource(args.export)

    if not src.has("Connections.csv"):
        raise SystemExit(
            "No Connections.csv found in the export. Point this straight at the export .zip "
            "LinkedIn emailed you (no need to unzip). The quick select-files export is "
            "unreliable for Connections - re-request the larger data archive via Settings -> "
            "Data privacy -> Get a copy of your data -> Download larger data archive."
        )

    conns = load_connections(src)
    warm = load_warm_names(src, args.owner)

    # freshness check (warn, do not block)
    newest, days_old, fresh_warn = freshness_check(src, conns)

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

    has_region = bool(icp["region_tokens"])

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
    warm_total = region_total = demoted_total = 0
    for c in conns:
        dm = dm_for(c)
        region_hit = region_for(c)
        sc = score(c, dm, icp, region_hit)
        if sc < icp["threshold"]:
            continue
        last = dm["last"] if dm else None
        days_since = (TODAY - last).days if last else None
        tier_key, tier_label = fit_tier(sc, icp["threshold"])
        scope_key, scope_label = region_scope(region_hit, has_region)
        _, warm_class = warmth_tier(dm, days_since)
        demoted = is_demoted(c["position"], c["company"], icp)
        c2 = dict(c, score=sc, dm=dm, region_hit=region_hit,
                  last_contact=last.isoformat() if last else "", days_since=days_since,
                  tier=tier_key, tier_label=tier_label, scope=scope_key,
                  scope_label=scope_label, warm_class=warm_class, demoted=demoted)
        qualified.append(c2)
        if dm and dm["in"] > 0:
            warm_total += 1
        if region_hit:
            region_total += 1
        if demoted:
            demoted_total += 1

    qualified.sort(key=lambda x: (-x["score"], -(x["dm"]["in"] if x["dm"] else 0), x["name"]))

    totals = {"total": len(conns), "qualified": len(qualified),
              "warm": warm_total, "region": region_total, "demoted": demoted_total}

    # ---- CSV (full rows) ----
    with open(os.path.join(args.outdir, "network-scan.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["# " + LOCAL_WARNING])
        w.writerow(["rank", "name", "title", "company", "connected_on", "fit_tier", "region",
                    "warmth", "replies_in", "last_contact", "days_since", "demoted", "score",
                    "email", "linkedin_url"])
        for i, ld in enumerate(qualified, 1):
            wl, _ = warmth_tier(ld["dm"], ld["days_since"])
            w.writerow([i, ld["name"], ld["position"], ld["company"], ld["connected_on"],
                        ld["tier_label"], ld["scope_label"], wl,
                        ld["dm"]["in"] if ld["dm"] else 0, ld["last_contact"],
                        ld["days_since"] if ld["days_since"] is not None else "",
                        "yes" if ld["demoted"] else "",
                        ld["score"], ld["email"], ld["url"]])

    # ---- JSON ----
    with open(os.path.join(args.outdir, "network-scan.json"), "w", encoding="utf-8") as f:
        json.dump({"_notice": LOCAL_WARNING,
                   "icp": {k: v for k, v in icp.items() if not k.startswith("_")},
                   "totals": totals, "incoming_invites": len(incoming),
                   "export_newest": newest.isoformat() if newest else None,
                   "export_days_old": days_old,
                   "leads": [{k: v for k, v in ld.items() if k != "dm"} for ld in qualified]},
                  f, indent=2, ensure_ascii=False, default=str)

    # ---- compact markdown (the file the assistant reads) ----
    write_markdown(os.path.join(args.outdir, "network-scan.md"),
                   qualified, icp, totals, incoming, icp["show_n"])

    # ---- interactive HTML: anonymised demo (default, safe) + watermarked full ----
    demo_n = render_html_v3(os.path.join(args.outdir, "network-scan.html"),
                            qualified, totals, args.brand, anonymise=True)
    render_html_v3(os.path.join(args.outdir, "network-scan-full.html"),
                   qualified, totals, args.brand, anonymise=False)

    # ---- terminal summary (no row dump) ----
    if fresh_warn:
        print(fresh_warn)
        print("")
    print(f"ICP             : {icp['label']}")
    print(f"connections read: {len(conns)}")
    if newest:
        print(f"export newest   : {newest.isoformat()} ({days_old}d old)")
    print(f"qualified       : {totals['qualified']} (score >= {icp['threshold']}, min_seniority {icp['min_seniority']}"
          f"{', leadership-title required' if icp['require_leadership_title'] else ''})")
    print(f"  replied to you: {warm_total}", end="")
    if icp["region_tokens"]:
        print(f"   region match: {region_total}", end="")
    if icp["demote_keywords"]:
        print(f"   demoted: {demoted_total}", end="")
    print(f"   pending invites: {len(incoming)}")
    print(f"\noutput written to: {os.path.abspath(args.outdir)}")
    print("  network-scan.md        (compact ranked digest - read this one)")
    print(f"  network-scan.html      (anonymised demo, safe to share - {demo_n} rows)")
    print("  network-scan-full.html (real names + links, keep local)")
    print("  network-scan.csv / .json (full rows - keep local, do not commit)")


if __name__ == "__main__":
    main()
