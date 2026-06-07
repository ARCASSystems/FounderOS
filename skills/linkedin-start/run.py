# -*- coding: utf-8 -*-
"""Run the complete Founder OS LinkedIn pack from one export path.

The runner accepts a LinkedIn ZIP or folder, unwraps it in a private temporary
workspace, drafts an ICP from the local Founder OS positioning when available,
runs both deterministic engines, and writes action-ready outputs. Nothing is sent
or posted. Message content is never loaded by either engine.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import webbrowser
import zipfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
SCAN = REPO / "skills" / "linkedin-network-scan" / "scan.py"
AUDIT = REPO / "skills" / "linkedin-power-audit" / "power_audit.py"
TAXONOMY = REPO / "skills" / "linkedin-power-audit" / "taxonomy.json"
STATE_DEFAULT = Path.home() / ".founder-os" / "linkedin-pack-state.json"
OUTPUT_DEFAULT = Path.home() / "FounderOS" / "outputs" / "linkedin"

OUTCOME_CHOICES = ("leads", "job", "brand", "network", "revival")


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def read_if_real(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if "{{" in text or "[FILL" in text:
        return ""
    return text


def operating_context() -> str:
    candidates = [
        REPO / "core" / "identity.md",
        REPO / "core" / "profile.md",
        REPO / "core" / "voice-profile.yml",
    ]
    return "\n".join(filter(None, (read_if_real(path) for path in candidates)))


def positioning_value(context: str, label: str) -> str:
    match = re.search(rf"(?mi)^\*\*{re.escape(label)}:\*\*\s*(.+?)\s*$", context)
    return match.group(1).strip() if match else ""


def unique(values):
    out = []
    seen = set()
    for value in values:
        clean = str(value).strip().lower()
        if clean and clean not in seen:
            seen.add(clean)
            out.append(clean)
    return out


def infer_industries(context: str):
    vocabulary = [
        "software",
        "technology",
        "consulting",
        "advisory",
        "agency",
        "professional services",
        "financial services",
        "education",
        "healthcare",
        "hospitality",
        "logistics",
        "manufacturing",
        "real estate",
        "recruitment",
        "marketing",
    ]
    low = context.casefold()
    return [term for term in vocabulary if term in low]


def draft_icp(outcome: str, context: str) -> dict:
    sells_to = positioning_value(context, "Sells to")
    sells = positioning_value(context, "Sells")
    pain = positioning_value(context, "Buyer pain")
    industries = infer_industries(" ".join([context, sells_to, sells, pain]))

    if outcome == "job":
        roles = [
            "recruiter",
            "talent acquisition",
            "talent partner",
            "head of talent",
            "head of people",
            "hiring manager",
            "head of",
            "director",
            "founder",
            "ceo",
            "managing director",
        ]
        return {
            "label": "Auto-drafted career network lens",
            "roles": roles,
            "industries": industries or ["technology", "software", "consulting", "recruitment"],
            "company_keywords": [],
            "region_tokens": [],
            "exclude": ["student"],
            "demote_keywords": [],
            "min_seniority": "ic",
            "require_leadership_title": False,
            "threshold": 18,
            "show_n": 40,
            "_draft_basis": {
                "sells_to": sells_to or None,
                "offer": sells or None,
                "buyer_pain": pain or None,
            },
        }

    role_map = [
        ("operations", ["head of operations", "operations director", "coo"]),
        ("marketing", ["head of marketing", "marketing director", "cmo"]),
        ("sales", ["head of sales", "sales director", "business development"]),
        ("talent", ["head of talent", "head of people", "hr director"]),
        ("finance", ["cfo", "finance director"]),
        ("product", ["head of product", "product director", "cto"]),
        ("founder", ["founder", "owner", "ceo", "managing director"]),
    ]
    low = " ".join([context, sells_to, pain]).casefold()
    roles = []
    for token, mapped in role_map:
        if token in low:
            roles.extend(mapped)
    if not roles:
        roles = ["founder", "owner", "ceo", "managing director", "head of operations"]

    return {
        "label": "Auto-drafted leads lens from Founder OS positioning",
        "roles": unique(roles),
        "industries": industries,
        "company_keywords": [],
        "region_tokens": [],
        "exclude": ["student", "recruiter"],
        "demote_keywords": [],
        "min_seniority": "manager",
        "require_leadership_title": True,
        "threshold": 30,
        "show_n": 40,
        "_draft_basis": {
            "sells_to": sells_to or None,
            "offer": sells or None,
            "buyer_pain": pain or None,
        },
    }


def goal_buckets(outcome: str, context: str) -> list[str]:
    if outcome == "job":
        return ["hr_talent_recruitment", "operations_general_management", "founder_owner_entrepreneur"]
    keyword_map = [
        ("operations", "operations_general_management"),
        ("sales", "sales_partnerships_bd"),
        ("partnership", "sales_partnerships_bd"),
        ("marketing", "marketing_brand_media_pr"),
        ("brand", "marketing_brand_media_pr"),
        ("talent", "hr_talent_recruitment"),
        ("recruit", "hr_talent_recruitment"),
        ("finance", "finance_consulting_advisory"),
        ("consult", "finance_consulting_advisory"),
        ("product", "tech_product_innovation"),
        ("software", "tech_product_innovation"),
        ("technology", "tech_product_innovation"),
        ("education", "education_academia_students"),
        ("government", "government_public_sector"),
        ("hospitality", "events_hospitality_experience"),
    ]
    found = ["founder_owner_entrepreneur"]
    low = context.casefold()
    for token, bucket in keyword_map:
        if token in low:
            found.append(bucket)
    if len(found) == 1:
        found.extend(["operations_general_management", "sales_partnerships_bd"])
    return unique(found)[:4]


def safe_extract(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with zipfile.ZipFile(archive) as handle:
        for member in handle.infolist():
            target = (destination / member.filename).resolve()
            if target != root and root not in target.parents:
                raise ValueError(f"unsafe ZIP member path: {member.filename}")
        handle.extractall(destination)


def find_export_folder(root: Path) -> Path | None:
    matches = []
    for connection in root.rglob("Connections.csv"):
        folder = connection.parent
        if (folder / "Profile.csv").exists():
            matches.append(folder)
    return sorted(matches, key=lambda path: (len(path.parts), str(path).casefold()))[0] if matches else None


def prepare_export(source: Path, workspace: Path) -> Path:
    current = workspace / "input"
    if source.is_dir():
        shutil.copytree(source, current)
    elif source.is_file() and source.suffix.casefold() == ".zip":
        safe_extract(source, current)
    else:
        raise ValueError("export must be a LinkedIn .zip file or folder")

    for depth in range(4):
        found = find_export_folder(current)
        if found:
            return found
        nested = sorted(current.rglob("*.zip"), key=lambda path: str(path).casefold())
        if not nested:
            break
        next_root = workspace / f"unwrap-{depth + 1}"
        safe_extract(nested[0], next_root)
        current = next_root
    raise ValueError("no folder containing both Profile.csv and Connections.csv was found")


def run_checked(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(detail or f"command failed with exit code {result.returncode}")


def public_icp(draft: dict) -> dict:
    return {key: value for key, value in draft.items() if not key.startswith("_")}


def build_brand_direction(audit: dict, outcome: str, context: str) -> dict:
    total = audit["metrics"]["connections"]
    stakeholder = next(
        (item for item in audit["network"]["stakeholder_buckets"] if item["count"] > 0),
        {"label": "the strongest role cluster in your network", "count": 0, "share": 0},
    )
    posting = next(
        (item for item in audit["content"]["posting_themes"] if item["count"] > 0),
        None,
    )
    lane_label = posting["label"] if posting else stakeholder["label"]
    evidence_count = posting["count"] if posting else stakeholder["count"]
    evidence_unit = "published posts" if posting else "connections"

    goal = "job" if outcome == "job" else "brand" if outcome == "brand" else "clients"
    sells_to = positioning_value(context, "Sells to")
    sells = positioning_value(context, "Sells")
    audience = sells_to or ("hiring decision-makers" if goal == "job" else "the people this network already reaches")
    offer = sells or "practical operating experience"
    topic_lane = (
        f"{lane_label} - supported by {evidence_count} of {total if not posting else audit['metrics']['posts']} "
        f"{evidence_unit}"
    )
    angle = f"Show how {offer} helps {audience} make a clearer decision, using specific operating evidence."

    first_three = [
        {
            "hook": f"The useful lesson in {lane_label.lower()} is usually hiding in the operating detail.",
            "angle": "Break down one repeatable method, including where it fails.",
            "format": "document carousel",
        },
        {
            "hook": f"Most advice for {audience} skips the decision that changes the result.",
            "angle": "Name the decision, show the tradeoff, and give a concrete example.",
            "format": "text",
        },
        {
            "hook": f"A small proof point says more about {lane_label.lower()} than another broad prediction.",
            "angle": "Share one observed before-and-after pattern without inventing client facts.",
            "format": "image plus text",
        },
    ]
    return {
        "goal": goal,
        "topic_lane": topic_lane,
        "positioning_angle": angle,
        "format_mix": [
            {
                "format": "document carousel",
                "why": "Current 2026 data places documents and carousels at the top of median reach.",
            },
            {
                "format": "image plus text",
                "why": "Images are the most reliable high-engagement format in the current large-sample data.",
            },
            {
                "format": "text",
                "why": "Strong text remains effective when the idea and opening carry the read.",
            },
        ],
        "cadence": "3 posts per week, inside the conservative 2 to 4 weekly range",
        "first_three_posts": first_three,
        "evidence": [
            f"topic_lane: {evidence_count} {evidence_unit} support {lane_label} (audit.json)",
            "format_mix: documents lead median reach, images are reliable, and video trails text in current AuthoredUp 2026 data",
            "cadence: AuthoredUp recommends 2 to 4 posts per week for most profiles",
        ],
    }


def lead_reason(lead: dict) -> str:
    parts = [lead.get("tier_label") or "Qualified fit"]
    if lead.get("position"):
        parts.append(f"role: {lead['position']}")
    warmth = lead.get("warm_class")
    if warmth in {"hot", "warm", "dormant"}:
        parts.append("they replied on LinkedIn before")
    elif warmth == "outbound_only":
        parts.append("prior outreach was one-way, so treat this as cold")
    return "; ".join(parts)


def lead_opener(lead: dict) -> str:
    first = (lead.get("first") or lead.get("name", "").split(" ")[0] or "there").strip()
    role = lead.get("position") or "your work"
    company = lead.get("company") or "your company"
    if lead.get("warm_class") in {"hot", "warm", "dormant"}:
        return (
            f"Hi {first} - we have spoken on LinkedIn before, and your work as {role} at {company} "
            "gave me a useful reason to reconnect. How is that area changing for you this year?"
        )
    return (
        f"Hi {first} - your work as {role} at {company} stood out while I was reviewing my network. "
        "I have one relevant observation to compare notes on. Open to a short exchange?"
    )


def write_lead_worklist(path: Path, scan: dict) -> None:
    lines = [
        "# Lead worklist",
        "",
        "Manual review only. Verify each current profile before acting. Nothing has been sent.",
        "",
    ]
    for rank, lead in enumerate(scan.get("leads", [])[:20], 1):
        lines.extend(
            [
                f"## {rank}. {lead['name']}",
                f"- Role: {lead.get('position') or 'Not present in export'}",
                f"- Company: {lead.get('company') or 'Not present in export'}",
                f"- Why ranked: {lead_reason(lead)}",
                "- Suggested next action: verify the current profile, then send one manual note if the fit still holds.",
                f"- Draft opener: {lead_opener(lead)}",
                "",
            ]
        )
    if not scan.get("leads"):
        lines.append("No contacts cleared the auto-drafted ICP threshold. Edit `draft-icp.json` and rerun.")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_revival_worklist(path: Path, audit: dict) -> None:
    candidates = [
        item
        for item in audit["messages"]["counterparties"]
        if item["in"] >= 1 and item["warmth"] == "dormant"
    ]
    candidates.sort(
        key=lambda item: (
            -(item["in"]),
            item["last_touch_days"] if item["last_touch_days"] is not None else 10**9,
            item["name"].casefold(),
        )
    )
    lines = [
        "# Revival worklist",
        "",
        "Only prior two-way LinkedIn relationships appear here. Nothing has been sent.",
        "",
    ]
    for rank, item in enumerate(candidates[:20], 1):
        title = item.get("title") or "Title not matched in Connections.csv"
        company = item.get("company") or "Company not matched in Connections.csv"
        first = item["name"].split(" ")[0]
        lines.extend(
            [
                f"## {rank}. {item['name']}",
                f"- Matched role: {title} at {company}",
                f"- Relationship evidence: {item['in']} inbound replies across {item['conversations']} conversation(s); last LinkedIn touch {item['last_touch']}",
                "- Suggested next action: verify the current role, then reconnect manually without pitching.",
                f"- Reopener: Hi {first} - it has been a while since we spoke here. I saw your last listed role was {title} at {company}. How has that work evolved since then?",
                "",
            ]
        )
    if not candidates:
        lines.append("No dormant two-way LinkedIn relationships were found in this export.")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_network_worklist(path: Path, audit: dict) -> None:
    gap = audit["network"].get("gap") or {}
    lines = [
        "# Network-building worklist",
        "",
        "These actions translate measured role gaps into plain language. They do not invent people.",
        "",
    ]
    for item in gap.get("under_represented", []):
        lines.extend(
            [
                f"## Build more relationships with {item['label'].lower()}",
                f"- Current evidence: {item['count']} of {gap['total_connections']} connections ({item['share']}%).",
                "- 30-day action: identify 10 relevant people through existing second-degree introductions, events, or communities.",
                "- Weekly action: make two thoughtful connection requests and leave three useful comments in this role area.",
                "- Review rule: confirm role and relevance manually before connecting.",
                "",
            ]
        )
    if not gap.get("under_represented"):
        lines.append("No selected goal role is below the audit's 10% thin-network threshold.")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def voice_mode(context: str) -> str:
    low = context.casefold()
    if "measured" in low or "restrained" in low:
        return "measured"
    if "casual" in low or "conversational" in low:
        return "conversational"
    return "plain-direct"


def complete_post(seed: dict, direction: dict, index: int, mode: str) -> str:
    hook = seed["hook"]
    lane = direction["topic_lane"]
    angle = seed["angle"]
    closing = {
        "measured": "The useful question is whether the evidence supports the next move.",
        "conversational": "What are you seeing in your own work?",
        "plain-direct": "Check the evidence before you copy the tactic.",
    }[mode]
    bodies = [
        (
            f"{hook}\n\n"
            f"I keep coming back to this lane: {lane}.\n\n"
            "The broad advice is easy to repeat. The operating detail is where the result changes.\n\n"
            f"For this post, the useful move is simple: {angle.lower()}\n\n"
            "Show the starting condition.\n"
            "Name the decision.\n"
            "Show what changed.\n"
            "Keep the limitation in the frame.\n\n"
            f"{closing}"
        ),
        (
            f"{hook}\n\n"
            f"The direction here is {direction['positioning_angle']}\n\n"
            "A strong point of view still needs a traceable reason.\n\n"
            "Start with the decision your reader is facing.\n"
            "Explain the tradeoff in plain language.\n"
            "Use one real example you can defend.\n"
            "Cut any claim the evidence cannot carry.\n\n"
            f"{closing}"
        ),
        (
            f"{hook}\n\n"
            "A useful proof point does three jobs:\n\n"
            "It shows the starting state.\n"
            "It makes the intervention visible.\n"
            "It leaves the reader with a decision they can apply.\n\n"
            f"That is the content opportunity inside {lane}.\n\n"
            "Use a real observation from your own work before publishing. Do not invent a client result to fill the gap.\n\n"
            f"{closing}"
        ),
    ]
    return bodies[index]


def write_posts(path: Path, direction: dict, context: str) -> None:
    mode = voice_mode(context)
    voice_note = (
        f"Voice mode applied from the available profile: {mode}."
        if read_if_real(REPO / "core" / "voice-profile.yml")
        else "No completed voice profile was found, so these complete drafts use the plain-direct baseline."
    )
    lines = ["# First three posts", "", voice_note, ""]
    for index, seed in enumerate(direction["first_three_posts"]):
        lines.extend(
            [
                f"## Post {index + 1} - {seed['format']}",
                "",
                "**Complete draft**",
                "",
                complete_post(seed, direction, index, mode),
                "",
                f"Evidence used: {direction['evidence'][min(index, len(direction['evidence']) - 1)]}",
                "",
            ]
        )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def update_state(path: Path, output: Path, as_of: datetime.date, outcome: str) -> None:
    write_json(
        path,
        {
            "analysis_date": as_of.isoformat(),
            "outcome": outcome,
            "latest_output": str(output.resolve()),
            "brand_direction": str((output / "brand-direction.json").resolve()),
            "anonymized_report": str((output / "network-scan.html").resolve()),
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the complete LinkedIn pack from one export.")
    parser.add_argument("export", help="path to the LinkedIn export ZIP or folder")
    parser.add_argument("--outcome", choices=OUTCOME_CHOICES, default="leads")
    parser.add_argument("--as-of", default=datetime.date.today().isoformat())
    parser.add_argument("--output-root", default=str(OUTPUT_DEFAULT))
    parser.add_argument("--state-file", default=str(STATE_DEFAULT))
    parser.add_argument("--no-open", action="store_true", help="do not open the anonymized HTML report")
    args = parser.parse_args()

    try:
        as_of = datetime.date.fromisoformat(args.as_of)
    except ValueError as exc:
        raise SystemExit("--as-of must use YYYY-MM-DD") from exc

    source = Path(args.export).expanduser().resolve()
    output = Path(args.output_root).expanduser().resolve() / as_of.isoformat()
    output.mkdir(parents=True, exist_ok=True)
    context = operating_context()

    draft = draft_icp(args.outcome, context)
    write_json(output / "draft-icp.json", draft)
    buckets = goal_buckets(args.outcome, context)

    try:
        with tempfile.TemporaryDirectory(prefix="founder-os-linkedin-") as td:
            workspace = Path(td)
            try:
                os.chmod(workspace, 0o700)
            except OSError:
                pass
            export_folder = prepare_export(source, workspace)
            run_checked(
                [
                    sys.executable,
                    str(SCAN),
                    str(export_folder),
                    str(output),
                    "--icp",
                    str(output / "draft-icp.json"),
                    "--as-of",
                    as_of.isoformat(),
                ]
            )
            run_checked(
                [
                    sys.executable,
                    str(AUDIT),
                    str(export_folder),
                    str(output),
                    "--goal-buckets",
                    ",".join(buckets),
                    "--as-of",
                    as_of.isoformat(),
                ]
            )
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        print(f"LinkedIn pack failed: {exc}", file=sys.stderr)
        return 1

    scan = json.loads((output / "network-scan.json").read_text(encoding="utf-8"))
    audit = json.loads((output / "audit.json").read_text(encoding="utf-8"))
    direction = build_brand_direction(audit, args.outcome, context)
    write_json(output / "brand-direction.json", direction)
    write_lead_worklist(output / "lead-worklist.md", scan)
    write_revival_worklist(output / "revival-worklist.md", audit)
    write_network_worklist(output / "network-building-worklist.md", audit)
    write_posts(output / "first-three-posts.md", direction, context)
    update_state(Path(args.state_file).expanduser(), output, as_of, args.outcome)

    if not args.no_open:
        try:
            webbrowser.open((output / "network-scan.html").resolve().as_uri(), new=2)
        except (OSError, webbrowser.Error):
            pass

    print("LinkedIn action bundle written")
    print("Review the worklists and complete post drafts before acting. Nothing was sent or posted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
