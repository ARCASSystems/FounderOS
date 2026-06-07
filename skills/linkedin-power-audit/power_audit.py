# -*- coding: utf-8 -*-
"""
power_audit.py - deep, deterministic read of your own LinkedIn data export.

A Python port of the LinkedIn Power Audit deterministic layer. Reads an UNZIPPED
LinkedIn export folder and writes audit.json: profile, metrics, network composition
(role clusters, stakeholder buckets, industry buckets, top companies, founder pool),
message warmth, invitations, content themes, skills, positions, education. Plus an
optional network-gap read (over/under-representation of the roles your goal needs).

No AI. No third-party calls. No message CONTENT is read - metadata only (who, the
direction, the count, the date). Python standard library only - no pip install.

Single runtime: Python, matching the rest of the LinkedIn pack. A tech founder who
prefers Node can add their own; this is the free-tier floor and needs nothing extra.

Usage:
    python power_audit.py <unzipped-export-folder> <output-folder> [--goal-buckets a,b]

Writes <output-folder>/audit.json. Keep the output folder OUTSIDE any git repo - it
holds real names. linkedin-warm-revival and linkedin-brand-direction read audit.json.
"""

import argparse
import csv
import datetime
import io
import json
import os
import re
import sys
from collections import OrderedDict

SCHEMA_VERSION = "1.0"
NOW = datetime.datetime.now(datetime.timezone.utc)

HERE = os.path.dirname(os.path.abspath(__file__))

LOCAL_WARNING = ("This file holds real names from your own LinkedIn export. Keep it on "
                 "your machine - do NOT commit it to a repo or share it.")


# ----------------------------------------------------------------------------
# CSV (port of lib/csv.js): tolerant of a Notes preamble before the header,
# quoted multi-line fields, and "" escaped quotes. Stdlib csv handles the quoting.
# ----------------------------------------------------------------------------

def read_csv(path):
    if not os.path.exists(path):
        return {"headers": [], "rows": [], "present": False}
    raw = open(path, encoding="utf-8-sig", errors="replace").read()
    all_rows = list(csv.reader(io.StringIO(raw)))
    header_idx = 0
    for i in range(min(len(all_rows), 10)):
        r = all_rows[i]
        if len(r) > 1 and all(len(c) < 60 and "\n" not in c for c in r):
            header_idx = i
            break
    headers = [h.strip() for h in (all_rows[header_idx] if header_idx < len(all_rows) else [])]
    rows = []
    for r in all_rows[header_idx + 1:]:
        if len(r) == len(headers) and any((c or "").strip() for c in r):
            rows.append({h: r[idx] for idx, h in enumerate(headers)})
    return {"headers": headers, "rows": rows, "present": True}


def clean_line_quotes(text):
    if not text:
        return text
    out = []
    for line in text.split("\n"):
        t = line.strip()
        if t in ('"', '""'):
            out.append("")
            continue
        if t.startswith('"') and t.endswith('"') and len(t) >= 2:
            t = t[1:-1]
        elif t.endswith('"') and not t.startswith('"'):
            t = t[:-1]
        elif t.startswith('"') and not t.endswith('"'):
            t = t[1:]
        out.append(t)
    joined = "\n".join(out)
    joined = re.sub(r"\n{3,}", "\n\n", joined)
    return joined.strip()


def g(row, key):
    return (row.get(key, "") or "").strip()


# ----------------------------------------------------------------------------
# Dates (port of extract.js parseDate - every LinkedIn export format we have seen)
# ----------------------------------------------------------------------------

_MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
           "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


def _utc(y, mo, d, hh=0, mm=0, ss=0):
    try:
        return datetime.datetime(y, mo, d, hh, mm, ss, tzinfo=datetime.timezone.utc)
    except ValueError:
        return None


def parse_date(s):
    if not s:
        return None
    t = str(s).strip()
    if not t:
        return None

    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})", t)
    if m:
        return _utc(int(m[1]), int(m[2]), int(m[3]), int(m[4]), int(m[5]), int(m[6]))
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", t)
    if m:
        return _utc(int(m[1]), int(m[2]), int(m[3]))
    m = re.match(r"^(\d{4})/(\d{2})/(\d{2})\s+(\d{2}):(\d{2}):(\d{2})", t)
    if m:
        return _utc(int(m[1]), int(m[2]), int(m[3]), int(m[4]), int(m[5]), int(m[6]))
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$", t)
    if m:
        mo = _MONTHS.get(m[2].lower())
        return _utc(int(m[3]), mo, int(m[1])) if mo else None
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{2,4}),?\s*(\d{1,2}):(\d{2})\s*([AP]M)?$", t, re.I)
    if m:
        mo, dy, yr, hh, mm, ap = m.groups()
        yr = int(yr)
        if yr < 100:
            yr += 2000
        h = int(hh)
        if ap:
            if ap.upper() == "PM" and h != 12:
                h += 12
            if ap.upper() == "AM" and h == 12:
                h = 0
        return _utc(yr, int(mo), int(dy), h, int(mm))
    m = re.match(r"^[A-Za-z]{3}\s+([A-Za-z]{3})\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})\s+(?:UTC\s+)?(\d{4})$", t)
    if m:
        mo = _MONTHS.get(m[1].lower())
        return _utc(int(m[6]), mo, int(m[2]), int(m[3]), int(m[4]), int(m[5])) if mo else None
    m = re.match(r"^([A-Za-z]{3})\s+(\d{4})$", t)
    if m:
        mo = _MONTHS.get(m[1].lower())
        return _utc(int(m[2]), mo, 1) if mo else None
    m = re.match(r"^(\d{4})$", t)
    if m:
        return _utc(int(m[1]), 1, 1)
    return None


def ym_key(d):
    return f"{d.year:04d}-{d.month:02d}" if d else None


def y_key(d):
    return str(d.year) if d else None


# ----------------------------------------------------------------------------
# Regex helpers (taxonomy uses string patterns, JS-compatible)
# ----------------------------------------------------------------------------

def compile_patterns(patterns):
    return [re.compile(p, re.I) for p in patterns]


def matches_any(text, regexes):
    if not text:
        return False
    return any(rx.search(text) for rx in regexes)


def round1(x):
    # match JS +(n).toFixed(1): one decimal, trailing-zero-trimmed to a number
    return round(x + 1e-9, 1)


# ----------------------------------------------------------------------------
# Per-CSV processors (faithful port of extract.js)
# ----------------------------------------------------------------------------

def process_profile(rows):
    if not rows:
        return None
    r = rows[0]
    summary = g(r, "Summary")
    return {
        "first_name": g(r, "First Name"),
        "last_name": g(r, "Last Name"),
        "headline": g(r, "Headline"),
        "summary_word_count": len([w for w in re.split(r"\s+", summary) if w]) if summary else 0,
        "industry": g(r, "Industry") or None,
        "location": g(r, "Geo Location") or None,
    }


def process_positions(rows):
    out = [{
        "company": g(r, "Company Name"),
        "title": g(r, "Title"),
        "started_on": g(r, "Started On"),
        "finished_on": g(r, "Finished On"),
        "location": g(r, "Location") or None,
    } for r in rows]
    out = [p for p in out if p["company"] or p["title"]]

    def key(p):
        d = parse_date(p["started_on"])
        return d.timestamp() if d else float("-inf")
    out.sort(key=key, reverse=True)
    return out


def process_education(rows):
    out = [{
        "school": g(r, "School Name"),
        "degree": g(r, "Degree Name") or None,
        "start_date": g(r, "Start Date") or None,
        "end_date": g(r, "End Date") or None,
    } for r in rows]
    return [e for e in out if e["school"]]


def process_skills(rows):
    return [g(r, "Name") for r in rows if g(r, "Name")]


def process_endorsements(rows):
    accepted = [r for r in rows if g(r, "Endorsement Status").upper() == "ACCEPTED"]
    by_skill = OrderedDict()
    for r in accepted:
        skill = g(r, "Skill Name")
        if not skill:
            continue
        by_skill[skill] = by_skill.get(skill, 0) + 1
    return {"total": len(accepted), "by_skill": by_skill}


def process_connections(rows, taxonomy):
    all_c = [{
        "first_name": g(r, "First Name"),
        "last_name": g(r, "Last Name"),
        "company": g(r, "Company"),
        "position": g(r, "Position"),
        "connected_on": g(r, "Connected On"),
    } for r in rows]
    conns = [c for c in all_c if c["first_name"] or c["last_name"]]
    private_count = len(all_c) - len(conns)
    total = len(conns)

    role_regex = {k: compile_patterns(v) for k, v in taxonomy["role_clusters"].items()}
    role_counts = {k: 0 for k in taxonomy["role_clusters"]}
    for c in conns:
        pos = c["position"].lower()
        for k, regs in role_regex.items():
            if matches_any(pos, regs):
                role_counts[k] += 1
    role_clusters = sorted([{
        "cluster": k, "label": taxonomy["role_cluster_labels"].get(k, k),
        "count": cnt, "share": round1(cnt / total * 100) if total else 0,
    } for k, cnt in role_counts.items()], key=lambda x: -x["count"])

    stakeholder_regex = [(k, compile_patterns(pats)) for k, pats in taxonomy["stakeholder_priority"]]
    stakeholder_counts = {k: 0 for k, _ in taxonomy["stakeholder_priority"]}
    for c in conns:
        pos = c["position"].lower()
        bucket = "other_unclear"
        for k, regs in stakeholder_regex:
            if regs and matches_any(pos, regs):
                bucket = k
                break
        stakeholder_counts[bucket] += 1
    stakeholder_buckets = sorted([{
        "bucket": k, "label": taxonomy["stakeholder_priority_labels"].get(k, k),
        "count": cnt, "share": round1(cnt / total * 100) if total else 0,
    } for k, cnt in stakeholder_counts.items()], key=lambda x: -x["count"])

    industry_regex = OrderedDict((k, compile_patterns(v)) for k, v in taxonomy["industry_buckets"].items())
    industry_counts = OrderedDict()
    industry_counts["other_mixed"] = 0
    for k in taxonomy["industry_buckets"]:
        industry_counts[k] = 0
    for c in conns:
        co = c["company"].lower()
        matched = None
        for k, regs in industry_regex.items():
            if matches_any(co, regs):
                matched = k
                break
        industry_counts[matched or "other_mixed"] += 1
    industry_buckets = sorted([{
        "bucket": k, "label": taxonomy["industry_bucket_labels"].get(k, k),
        "count": cnt, "share": round1(cnt / total * 100) if total else 0,
    } for k, cnt in industry_counts.items()], key=lambda x: -x["count"])

    company_map = OrderedDict()
    for c in conns:
        co = c["company"].strip()
        if not co:
            continue
        company_map[co] = company_map.get(co, 0) + 1
    company_clusters = [{"company": co, "count": cnt} for co, cnt in
                        sorted(company_map.items(), key=lambda kv: -kv[1])[:30]]

    strict_regex = compile_patterns(taxonomy["founder_pool_keywords"]["strict"])
    broad_extra_regex = compile_patterns(taxonomy["founder_pool_keywords"]["broad_extra"])
    excluded = [s.lower() for s in taxonomy["founder_pool_excluded_companies"]]
    use_regex = OrderedDict((k, compile_patterns(v)) for k, v in taxonomy["commercial_use_buckets"].items())
    use_counts = {k: 0 for k in taxonomy["commercial_use_buckets"]}
    ind_counts_founders = OrderedDict()
    ind_counts_founders["other_mixed"] = 0
    for k in taxonomy["industry_buckets"]:
        ind_counts_founders[k] = 0

    strict = broad = 0
    founder_records = []
    for c in conns:
        pos = c["position"].lower()
        co = c["company"].lower()
        is_excluded = any(x in co for x in excluded)
        strict_match = matches_any(pos, strict_regex)
        broad_match = strict_match or (not is_excluded and matches_any(pos, broad_extra_regex))
        if strict_match:
            strict += 1
        if broad_match:
            broad += 1
            for k, regs in use_regex.items():
                if matches_any(f"{pos} {co}", regs):
                    use_counts[k] += 1
            matched = None
            for k, regs in industry_regex.items():
                if matches_any(co, regs):
                    matched = k
                    break
            ind_counts_founders[matched or "other_mixed"] += 1
            if len(founder_records) < 30:
                founder_records.append({
                    "name": f"{c['first_name']} {c['last_name']}".strip(),
                    "company": c["company"], "title": c["position"],
                    "connected_on": c["connected_on"],
                })

    founder_pool = {
        "strict_count": strict,
        "broad_count": broad,
        "by_use": sorted([{"bucket": k, "label": taxonomy["commercial_use_labels"].get(k, k), "count": cnt}
                          for k, cnt in use_counts.items()], key=lambda x: -x["count"]),
        "by_industry": sorted([{"bucket": k, "label": taxonomy["industry_bucket_labels"].get(k, k), "count": cnt}
                               for k, cnt in ind_counts_founders.items()], key=lambda x: -x["count"]),
        "sample_records": founder_records,
    }

    month_map = OrderedDict()
    for c in conns:
        k = ym_key(parse_date(c["connected_on"]))
        if k:
            month_map[k] = month_map.get(k, 0) + 1
    connections_by_month = [{"month": k, "count": v} for k, v in sorted(month_map.items())]

    return {
        "total": total, "total_in_export": len(all_c), "private_count": private_count,
        "role_clusters": role_clusters, "stakeholder_buckets": stakeholder_buckets,
        "industry_buckets": industry_buckets, "company_clusters": company_clusters,
        "founder_pool": founder_pool, "connections_by_month": connections_by_month,
    }


def process_messages(rows, owner_name):
    owner_low = owner_name.lower().strip()
    counter_map = OrderedDict()
    conversation_set = set()
    month_map = OrderedDict()
    total = 0
    for r in rows:
        conv = g(r, "CONVERSATION ID")
        from_name = g(r, "FROM")
        to_raw = g(r, "TO")
        d = parse_date(g(r, "DATE"))
        folder = g(r, "FOLDER").upper()
        total += 1
        if conv:
            conversation_set.add(conv)
        if d:
            k = ym_key(d)
            if k:
                month_map[k] = month_map.get(k, 0) + 1
        if from_name.lower() == owner_low or folder == "SENT":
            direction = "OUT"
        else:
            direction = "IN"
        counterparty = to_raw if direction == "OUT" else from_name
        if not counterparty or counterparty.lower() == owner_low:
            continue
        parts = [s.strip() for s in re.split(r"[;,]", counterparty) if s.strip() and s.strip().lower() != owner_low]
        counterparty = parts[0] if parts else counterparty
        ts = d.timestamp() if d else 0
        cur = counter_map.get(counterparty) or {"name": counterparty, "in": 0, "out": 0,
                                                "total": 0, "last_touch": 0, "conv": set()}
        cur["total"] += 1
        if direction == "OUT":
            cur["out"] += 1
        else:
            cur["in"] += 1
        if ts > cur["last_touch"]:
            cur["last_touch"] = ts
        if conv:
            cur["conv"].add(conv)
        counter_map[counterparty] = cur

    def days(ts):
        return int((NOW.timestamp() - ts) // 86400)

    counterparties = []
    for c in counter_map.values():
        dt = days(c["last_touch"]) if c["last_touch"] else None
        warmth = "light"
        if dt is not None and dt <= 30 and c["total"] >= 3:
            warmth = "hot"
        elif dt is not None and dt <= 90:
            warmth = "warm"
        elif c["total"] >= 5:
            warmth = "dormant"
        last_touch = (datetime.datetime.fromtimestamp(c["last_touch"], datetime.timezone.utc)
                      .date().isoformat()) if c["last_touch"] else None
        counterparties.append({
            "name": c["name"], "total": c["total"], "in": c["in"], "out": c["out"],
            "conversations": len(c["conv"]), "last_touch": last_touch,
            "last_touch_days": dt, "warmth": warmth,
        })
    counterparties.sort(key=lambda x: -x["total"])

    warmth_distribution = {"hot": 0, "warm": 0, "dormant": 0, "light": 0}
    for c in counterparties:
        warmth_distribution[c["warmth"]] += 1
    monthly_activity = [{"month": k, "count": v} for k, v in sorted(month_map.items())]

    return {
        "total": total, "conversations": len(conversation_set),
        "counterparties": counterparties[:50], "counterparties_total": len(counterparties),
        "warmth_distribution": warmth_distribution, "monthly_activity": monthly_activity,
        "themes": [],
    }


def process_invitations(rows, owner_name):
    owner_low = owner_name.lower().strip()
    incoming = outgoing = 0
    month_map = OrderedDict()
    for r in rows:
        direction = g(r, "Direction").upper()
        sent_at = parse_date(g(r, "Sent At"))
        if not direction:
            direction = "OUTGOING" if g(r, "From").lower() == owner_low else "INCOMING"
        if direction == "OUTGOING":
            outgoing += 1
        else:
            incoming += 1
        k = ym_key(sent_at)
        if k:
            cur = month_map.get(k) or {"month": k, "in": 0, "out": 0}
            if direction == "OUTGOING":
                cur["out"] += 1
            else:
                cur["in"] += 1
            month_map[k] = cur
    monthly_breakdown = sorted(month_map.values(), key=lambda x: x["month"])
    return {"incoming": incoming, "outgoing": outgoing, "monthly_breakdown": monthly_breakdown}


def process_member_follows(rows):
    return [{"name": g(r, "FullName"), "date": g(r, "Date")}
            for r in rows if g(r, "Status").lower() == "active" and g(r, "FullName")]


def process_company_follows(rows):
    return [{"organization": g(r, "Organization"), "followed_on": g(r, "Followed On")}
            for r in rows if g(r, "Organization")]


def process_hashtag_follows(rows):
    return [{"hashtag": g(r, "HashTag")}
            for r in rows if g(r, "State").lower() == "follow" and g(r, "HashTag")]


def process_shares(rows):
    out = []
    for r in rows:
        date = g(r, "Date")
        text = clean_line_quotes(g(r, "ShareCommentary"))
        shared_url = g(r, "SharedUrl")
        out.append({
            "date": date, "text": text, "year": y_key(parse_date(date)),
            "word_count": len([w for w in re.split(r"\s+", text) if w]) if text else 0,
            "is_repost": (not text) and bool(shared_url),
        })
    return [p for p in out if p["date"]]


def process_comments(rows):
    out = [{"date": g(r, "Date"), "message": clean_line_quotes(g(r, "Message"))} for r in rows]
    return [c for c in out if c["date"] and c["message"]]


def process_reactions(rows):
    by_type = OrderedDict()
    for r in rows:
        t = g(r, "Type")
        if t:
            by_type[t] = by_type.get(t, 0) + 1
    return {"total": len(rows),
            "by_type": sorted([{"type": t, "count": c} for t, c in by_type.items()], key=lambda x: -x["count"])}


def process_searches(rows):
    by_year = OrderedDict()
    person = company = ecosystem = government = 0
    for r in rows:
        q = g(r, "Search Query")
        y = y_key(parse_date(g(r, "Time")))
        if y:
            by_year[y] = by_year.get(y, 0) + 1
        if not q:
            continue
        ql = q.lower()
        if re.search(r"\b(govt|government|ministry|authority|public sector)\b", ql):
            government += 1
        elif re.search(r"\b(group|companies|company|corp|inc|llc|ltd|holdings|hospital|school|university|college|bank)\b", ql):
            company += 1
        elif re.search(r"\b(community|chamber|association|forum|federation|council)\b", ql):
            ecosystem += 1
        elif len(re.split(r"\s+", q)) <= 3 and re.match(r"^[A-Za-z\s.'-]+$", q):
            person += 1
        else:
            company += 1
    searches_by_year = [{"year": y, "count": c} for y, c in sorted(by_year.items())]
    return {"total": len(rows), "searches_by_year": searches_by_year,
            "behaviour": {"person_searches": person, "company_searches": company,
                          "ecosystem_searches": ecosystem, "government_searches": government}}


def process_learning(rows):
    kept = [r for r in rows if g(r, "Content Title")
            and not g(r, "Content Title").startswith("CONTENT METADATA NO LONGER EXISTS")]
    return [{"title": g(r, "Content Title"), "type": g(r, "Content Type") or None,
             "last_watched": g(r, "Content Last Watched Date (if viewed)") or None} for r in kept]


def process_jobs(rows):
    return [{k: (v or "").strip() for k, v in r.items()} for r in rows]


def process_recommendations(received_rows, given_rows):
    def clean(rows):
        return [{k: (v or "").strip() for k, v in r.items()} for r in rows]
    received = clean(received_rows)
    given = clean(given_rows)

    def visible_count(rows):
        if not rows:
            return 0
        if "Status" not in rows[0]:
            return len(rows)
        return len([r for r in rows if re.search(r"visible|accepted", r.get("Status", ""), re.I)])
    return {"received": visible_count(received), "given": visible_count(given),
            "received_records": received[:20], "given_records": given[:20]}


def posts_by_year(shares):
    m = OrderedDict()
    for p in shares:
        if not p["year"]:
            continue
        m[p["year"]] = m.get(p["year"], 0) + 1
    return [{"year": y, "count": c} for y, c in sorted(m.items())]


# ----------------------------------------------------------------------------
# Orchestrator (port of extract.js extract())
# ----------------------------------------------------------------------------

OPTIONAL_BUT_USED_CSVS = [
    "Profile.csv", "Positions.csv", "Skills.csv", "Endorsement_Received_Info.csv",
    "Connections.csv", "messages.csv", "Invitations.csv",
    "Member_Follows.csv", "Company Follows.csv", "Hashtag_Follows.csv",
    "Shares.csv", "Comments.csv", "Reactions.csv",
    "Education.csv", "Learning.csv", "SearchQueries.csv",
]

SKIPPED_CSVS = [
    "Ad_Targeting.csv", "Ads Clicked.csv", "LAN Ads Engagement.csv",
    "Inferences_about_you.csv", "Email Addresses.csv", "PhoneNumbers.csv",
    "Whatsapp Phone Numbers.csv", "Logins.csv", "Receipts_v2.csv",
    "Private_identity_asset.csv", "ImportedContacts.csv", "Registration.csv",
    "guide_messages.csv", "learning_coach_messages.csv", "learning_role_play_messages.csv",
    "LearningCoachMessages.csv", "Saved_Items.csv", "SavedJobAlerts.csv",
    "Reviews.csv", "Votes.csv", "Rich_Media.csv", "InstantReposts.csv",
]


class MissingCsvError(Exception):
    pass


def _load_json(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=OrderedDict)


def extract(export_dir):
    warnings = []
    taxonomy = _load_json("taxonomy.json")

    if isinstance(export_dir, str) and re.search(r"\.zip$", export_dir, re.I):
        raise ValueError(
            "Got a ZIP file path. The skill expects an unzipped folder.\n"
            f"Unzip \"{os.path.basename(export_dir)}\" first, then point at the resulting folder.\n"
            "If your ZIP unzipped to another ZIP (LinkedIn sometimes wraps twice), unzip again "
            "until you see Profile.csv and Connections.csv."
        )
    if not os.path.exists(export_dir):
        raise ValueError(f"Export directory not found: {export_dir}")

    if not os.path.exists(os.path.join(export_dir, "Profile.csv")):
        subdirs = [e for e in os.listdir(export_dir) if os.path.isdir(os.path.join(export_dir, e))]
        if len(subdirs) == 1 and os.path.exists(os.path.join(export_dir, subdirs[0], "Profile.csv")):
            warnings.append(f"nested folder detected: descended into {subdirs[0]}")
            export_dir = os.path.join(export_dir, subdirs[0])

    def resolve_csv(name):
        exact = os.path.join(export_dir, name)
        if os.path.exists(exact):
            return exact
        base = re.sub(r"\.csv$", "", name, flags=re.I)
        rx = re.compile("^" + re.escape(base) + r"_.+\.csv$", re.I)
        try:
            for f in os.listdir(export_dir):
                if rx.match(f):
                    return os.path.join(export_dir, f)
        except OSError:
            pass
        return exact

    def has_csv(name):
        return os.path.exists(resolve_csv(name))

    def rd(name, required=False):
        p = resolve_csv(name)
        result = read_csv(p)
        if not result["present"]:
            if required:
                raise MissingCsvError(f"Required CSV missing: {name} at {p}")
            warnings.append(f"csv missing (skipped): {name}")
        return result

    profile_res = rd("Profile.csv", True)
    connections_res = rd("Connections.csv", True)
    positions_res = rd("Positions.csv")
    skills_res = rd("Skills.csv")
    endorsements_res = rd("Endorsement_Received_Info.csv")
    messages_res = rd("messages.csv")
    invitations_res = rd("Invitations.csv")
    member_follows_res = rd("Member_Follows.csv")
    company_follows_res = rd("Company Follows.csv")
    hashtag_follows_res = rd("Hashtag_Follows.csv")
    shares_res = rd("Shares.csv")
    comments_res = rd("Comments.csv")
    reactions_res = rd("Reactions.csv")
    education_res = rd("Education.csv")
    learning_res = rd("Learning.csv")
    searches_res = rd("SearchQueries.csv")
    recv_res = rd("Recommendations_Received.csv")
    given_res = rd("Recommendations_Given.csv")

    jobs_res = {"present": False, "rows": []}
    jobs_path = os.path.join(export_dir, "Jobs", "Online Job Postings.csv")
    if os.path.exists(jobs_path):
        jobs_res = read_csv(jobs_path)

    profile = process_profile(profile_res["rows"])
    owner_name = f"{profile['first_name']} {profile['last_name']}".strip() if profile else ""

    positions = process_positions(positions_res["rows"])
    skills = process_skills(skills_res["rows"])
    endorse = process_endorsements(endorsements_res["rows"])
    network = process_connections(connections_res["rows"], taxonomy)
    messages = (process_messages(messages_res["rows"], owner_name) if messages_res["present"]
                else {"total": 0, "conversations": 0, "counterparties": [], "counterparties_total": 0,
                      "warmth_distribution": {"hot": 0, "warm": 0, "dormant": 0, "light": 0},
                      "monthly_activity": [], "themes": []})
    invites = (process_invitations(invitations_res["rows"], owner_name) if invitations_res["present"]
               else {"incoming": 0, "outgoing": 0, "monthly_breakdown": []})
    member_follows = process_member_follows(member_follows_res["rows"])
    company_follows = process_company_follows(company_follows_res["rows"])
    hashtag_follows = process_hashtag_follows(hashtag_follows_res["rows"])
    shares = process_shares(shares_res["rows"])
    comments = process_comments(comments_res["rows"])
    reactions = process_reactions(reactions_res["rows"]) if reactions_res["present"] else {"total": 0, "by_type": []}
    education = process_education(education_res["rows"])
    learning = process_learning(learning_res["rows"])
    searches = (process_searches(searches_res["rows"]) if searches_res["present"]
                else {"total": 0, "searches_by_year": [],
                      "behaviour": {"person_searches": 0, "company_searches": 0,
                                    "ecosystem_searches": 0, "government_searches": 0}})
    jobs_posted = process_jobs(jobs_res["rows"]) if jobs_res["present"] else []
    recommendations = process_recommendations(recv_res["rows"] if recv_res["present"] else [],
                                              given_res["rows"] if given_res["present"] else [])

    reposts = len([s for s in shares if s["is_repost"]])
    real_posts = len([s for s in shares if not s["is_repost"]])

    endorse_by_skill_cluster = [{"skill": s, "count": c} for s, c in
                                sorted(endorse["by_skill"].items(), key=lambda kv: -kv[1])]
    skills_rollup = sorted([{"skill": s, "endorsements": endorse["by_skill"].get(s, 0)} for s in skills],
                           key=lambda x: -x["endorsements"])

    theme_kw = _load_json("theme-keywords.json")
    follow_buckets = theme_kw.get("follow_theme_buckets", {})
    follow_bucket_regex = {k: compile_patterns(v) for k, v in follow_buckets.items()}
    follow_tagged = {k: 0 for k in follow_buckets}
    for ht in hashtag_follows:
        for k, regs in follow_bucket_regex.items():
            if matches_any(ht["hashtag"], regs):
                follow_tagged[k] += 1
    follow_themes = sorted([{"bucket": k, "label": theme_kw["follow_theme_labels"].get(k, k), "count": c}
                            for k, c in follow_tagged.items()], key=lambda x: -x["count"])

    posts_year = posts_by_year([s for s in shares if not s["is_repost"]])

    if owner_name:
        if any((c.get("name") or "").lower().strip() == owner_name.lower() for c in messages["counterparties"]):
            warnings.append(f"privacy leak: owner appeared as counterparty ({owner_name}) - dropped")

    rich_signals = ["messages.csv", "Shares.csv", "Reactions.csv", "Invitations.csv", "Comments.csv"]
    rich_present = [f for f in rich_signals if has_csv(f)]
    if len(rich_present) == len(rich_signals):
        export_type = "complete"
    elif len(rich_present) == 0:
        export_type = "basic"
    else:
        export_type = "partial"
    folder_name = os.path.basename(export_dir).lower()
    if export_type == "partial" and re.match(r"^basic_linkedindata", folder_name):
        export_type = "basic"
    if export_type == "partial" and re.match(r"^complete_linkedindata", folder_name):
        export_type = "complete"

    if export_type == "basic":
        warnings.insert(0,
            "BASIC EXPORT DETECTED. LinkedIn delivers a Basic export within ~10 minutes of the request, "
            "then the Complete export ~24 hours later. The Basic export is missing messages, posts, "
            "reactions, comments, invitations, and follows. This audit will run on connections and "
            "profile only. Re-run the skill on the Complete export when it arrives - the audit becomes much richer.")
    elif export_type == "partial":
        warnings.insert(0,
            f"PARTIAL EXPORT. Found {len(rich_present)} of {len(rich_signals)} core activity CSVs "
            f"({', '.join(rich_present)}). Some sections of the audit will be empty. If this is a Basic "
            "export, re-run on the Complete export when it arrives.")

    network_out = {k: v for k, v in network.items()}

    audit = OrderedDict()
    audit["_notice"] = LOCAL_WARNING
    audit["_meta"] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": NOW.isoformat(),
        "source_export_folder": os.path.basename(export_dir),
        "export_type": export_type,
        "owner": {"first_name": (profile or {}).get("first_name", ""),
                  "last_name": (profile or {}).get("last_name", ""), "name": owner_name},
        "csv_files_present": [f for f in OPTIONAL_BUT_USED_CSVS if has_csv(f)],
        "csv_files_skipped": SKIPPED_CSVS,
        "warnings": warnings,
    }
    audit["profile"] = profile
    audit["metrics"] = {
        "connections": network["total"], "connections_in_export": network["total_in_export"],
        "connections_private": network["private_count"], "posts": real_posts, "reposts": reposts,
        "comments": len(comments), "reactions": reactions["total"],
        "member_follows": len(member_follows), "company_follows": len(company_follows),
        "hashtag_follows": len(hashtag_follows), "job_postings": len(jobs_posted),
        "searches": searches["total"], "recommendations_received": recommendations["received"],
        "recommendations_given": recommendations["given"], "dm_messages": messages["total"],
        "dm_counterparties": messages["counterparties_total"], "conversations": messages["conversations"],
        "invites_in": invites["incoming"], "invites_out": invites["outgoing"],
        "skills_count": len(skills), "endorsements_count": endorse["total"],
    }
    audit["activity_timeline"] = {
        "posts_by_year": posts_year, "searches_by_year": searches["searches_by_year"],
        "dm_messages_by_month": messages["monthly_activity"],
        "connections_by_month": network["connections_by_month"],
    }
    audit["network"] = network_out
    audit["messages"] = messages
    audit["invitations"] = invites
    audit["content"] = {"posting_themes": [], "follow_themes": follow_themes,
                        "hashtag_follows": [h["hashtag"] for h in hashtag_follows][:50]}
    audit["skills"] = skills_rollup
    audit["endorsements_by_skill_cluster"] = endorse_by_skill_cluster
    audit["learning_themes"] = learning[:30]
    audit["events"] = []
    audit["jobs_posted"] = jobs_posted
    audit["search_behaviour"] = searches["behaviour"]
    audit["positions"] = positions
    audit["education"] = education
    audit["recommendations"] = {"received": recommendations["received"], "given": recommendations["given"]}
    audit["_raw"] = {"shares": [{"date": s["date"], "text": s["text"], "year": s["year"],
                                 "word_count": s["word_count"], "is_repost": s["is_repost"]} for s in shares]}

    total_tagged = sum(r["count"] for r in network["role_clusters"])
    if network["total"] > 0 and total_tagged < network["total"] * 0.3:
        warnings.append(f"role-cluster coverage below 30% ({total_tagged}/{network['total']}) - taxonomy may need expansion")

    return audit


# ----------------------------------------------------------------------------
# Layer 2: keyword theme classifier (port of classify.js)
# ----------------------------------------------------------------------------

def classify(audit):
    kw = _load_json("theme-keywords.json")
    post_regex = {k: compile_patterns(v) for k, v in kw["post_themes"].items()}
    shares = (audit.get("_raw") or {}).get("shares", [])
    real_posts = [s for s in shares if not s["is_repost"]]

    counts = {k: 0 for k in kw["post_themes"]}
    tagged_at_least_one = 0
    for p in real_posts:
        any_hit = False
        for k, regs in post_regex.items():
            if matches_any(p["text"], regs):
                counts[k] += 1
                any_hit = True
        if any_hit:
            tagged_at_least_one += 1
    total = len(real_posts)
    audit["content"]["posting_themes"] = sorted([{
        "bucket": k, "label": kw["post_theme_labels"].get(k, k), "count": c,
        "share": round1(c / total * 100) if total else 0,
    } for k, c in counts.items()], key=lambda x: -x["count"])
    audit["content"]["_post_theme_coverage"] = round1(tagged_at_least_one / total * 100) if total else 0

    proxies = kw.get("message_theme_proxies_by_role_cluster", {})
    labels = kw.get("message_theme_labels", {})
    cluster_volume = {rc["cluster"]: rc["count"] for rc in audit["network"].get("role_clusters", [])}
    theme_out = []
    for theme, clusters in proxies.items():
        if not clusters:
            continue
        sum_vol = sum(cluster_volume.get(c, 0) for c in clusters)
        if sum_vol > 0:
            theme_out.append({"theme": theme, "label": labels.get(theme, theme),
                              "proxy_clusters": clusters, "proxy_signal": sum_vol})
    if (audit["messages"].get("total", 0) > 0
            and not any(t["theme"] == "internal_operations" for t in theme_out)):
        theme_out.append({"theme": "internal_operations",
                          "label": labels.get("internal_operations", "Internal / operations"),
                          "proxy_clusters": [], "proxy_signal": 0})
    theme_out.sort(key=lambda x: -x["proxy_signal"])
    audit["messages"]["themes"] = theme_out
    return audit


# ----------------------------------------------------------------------------
# WS3b: network-gap analysis (NEW feature, not part of the Node port).
# Over/under-representation of the roles your goal needs, evidence-cited.
# ----------------------------------------------------------------------------

UNDER_SHARE = 10.0   # below this share of the network = thin
STRONG_SHARE = 25.0  # above this = strong


def network_gap(audit, goal_buckets):
    """Read the single-tag stakeholder distribution and report, for each role the
    user's goal needs, whether the network is thin / present / strong. Every line
    traces to a real count. goal_buckets are stakeholder_priority keys."""
    buckets = {b["bucket"]: b for b in audit["network"].get("stakeholder_buckets", [])}
    total = audit["network"].get("total") or audit["metrics"].get("connections", 0)
    per_bucket = []
    evidence = []
    for key in goal_buckets:
        b = buckets.get(key)
        count = b["count"] if b else 0
        share = b["share"] if b else 0.0
        label = b["label"] if b else key
        if share < UNDER_SHARE:
            status = "under"
        elif share > STRONG_SHARE:
            status = "over"
        else:
            status = "balanced"
        per_bucket.append({"bucket": key, "label": label, "count": count,
                           "share": share, "status": status})
        evidence.append(f"{label}: {count} of {total} connections ({share}%) - {status}")
    under = [b for b in per_bucket if b["status"] == "under"]
    biggest_gap = min(per_bucket, key=lambda b: b["share"]) if per_bucket else None
    return {
        "goal_buckets": list(goal_buckets),
        "total_connections": total,
        "per_bucket": per_bucket,
        "under_represented": under,
        "biggest_gap": biggest_gap,
        "evidence": evidence,
    }


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Deep audit of a LinkedIn export -> audit.json")
    ap.add_argument("export", help="path to the UNZIPPED LinkedIn export folder")
    ap.add_argument("outdir", help="folder to write audit.json into (keep it OUTSIDE any repo)")
    ap.add_argument("--goal-buckets", default="",
                    help="comma-separated stakeholder buckets your goal needs (adds network.gap)")
    args = ap.parse_args()

    audit = extract(args.export)
    classify(audit)
    if args.goal_buckets.strip():
        goal = [b.strip() for b in args.goal_buckets.split(",") if b.strip()]
        audit["network"]["gap"] = network_gap(audit, goal)

    os.makedirs(args.outdir, exist_ok=True)
    out_path = os.path.join(args.outdir, "audit.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

    print(f"audit.json written: {out_path}")
    print(f"  export type : {audit['_meta']['export_type']}")
    print(f"  connections : {audit['metrics']['connections']}")
    print(f"  dm_messages : {audit['metrics']['dm_messages']}")
    print(f"  posts       : {audit['metrics']['posts']} (+ {audit['metrics']['reposts']} reposts)")
    if audit["_meta"]["warnings"]:
        print("warnings:")
        for w in audit["_meta"]["warnings"]:
            print(f"  - {w}")


if __name__ == "__main__":
    main()
