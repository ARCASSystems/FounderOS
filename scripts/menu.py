#!/usr/bin/env python3
"""Menu engine for Founder OS.

Reads state files, scores capabilities against rules, prints the top 5 to 7
suggestions tailored to the founder's current state. No LLM call. No network.
Pure stdlib so the menu works on a free-tier install with no paid AI sub.

CLI: python scripts/menu.py [--root <path>]

Behaviour:
- Zero-state install (no snapshot, no log, no priorities) returns the Day-1
  starter set in a fixed order.
- Populated install returns the top 5 to 7 capabilities by score, with
  context-aware why-now lines.
- Capabilities without a `.claude/commands/<name>.md` file render in
  natural-language only. The `/founder-os:` slash form is never invented.

Path detection:
- Path A (plugin install): commands rendered as `/founder-os:<name>`.
- Path B (manual git clone): commands rendered as `/<name>` because the
  plugin namespace is not active.
- A small set of commands stay bare on both paths: today, next,
  pre-meeting, capture-meeting.
- Detection heuristic: presence of `.claude/commands/<name>.md` files in the
  install root signals Path B. Absence of that directory signals Path A.
"""

from __future__ import annotations

import argparse
import re
from datetime import date, datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Capability to command map. Single source of truth for what surfaces and how.
# A capability with command=None renders natural-language only.
# `always_bare=True` forces `/<name>` on both Path A and Path B.
# ---------------------------------------------------------------------------

CAPABILITIES = {
    "voice-interview": {
        "command": "voice-interview",
        "always_bare": False,
        "phrase": "set up my voice profile",
    },
    "brand-interview": {
        "command": "brand-interview",
        "always_bare": False,
        "phrase": "set up my brand profile",
    },
    "linkedin-post": {
        "command": None,
        "always_bare": False,
        "phrase": "write a LinkedIn post",
    },
    "content-repurposer": {
        "command": None,
        "always_bare": False,
        "phrase": "repurpose this for my main channel",
    },
    "priority-triage": {
        # Skill exists but no command file. Natural-language only.
        "command": None,
        "always_bare": False,
        "phrase": "what should I focus on next",
    },
    "weekly-review": {
        # Skill exists but no command file. Natural-language only.
        "command": None,
        "always_bare": False,
        "phrase": "run my weekly review",
    },
    "forcing-questions": {
        "command": "forcing-questions",
        "always_bare": False,
        "phrase": "run the forcing questions",
    },
    "pre-send-check": {
        # Skill exists but no command file. Natural-language only.
        "command": None,
        "always_bare": False,
        "phrase": "run a pre-send check",
    },
    "capture-meeting": {
        "command": "capture-meeting",
        "always_bare": True,
        "phrase": "capture this meeting",
    },
    "audit": {
        "command": "audit",
        "always_bare": False,
        "phrase": "audit the OS",
    },
    "today": {
        "command": "today",
        "always_bare": True,
        "phrase": "what's on for today?",
    },
    "ingest": {
        "command": "ingest",
        "always_bare": False,
        "phrase": "ingest this",
    },
    "dream": {
        "command": "dream",
        "always_bare": False,
        "phrase": "process my rants",
    },
}

ALWAYS_BARE_NAMES = {
    name for name, cfg in CAPABILITIES.items() if cfg["always_bare"]
}

DAY_ONE_ORDER = [
    "voice-interview",
    "brand-interview",
    "priority-triage",
    "today",
    "ingest",
]

CLOSING_LINE = (
    "These are tailored to your current state. Say any of the natural-language "
    "phrases above. Or ask Claude anything in plain English - most of FounderOS "
    "routes by what you say, not what you type."
)

# Patterns reused across rules.
WEEKLY_HEADER = re.compile(r"^##\s+Week\s+of\s+(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
DAILY_HEADER = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
STATUS_OPEN = re.compile(r"Status:\s*\**\s*OPEN", re.IGNORECASE)
ROLLED_FORWARD = re.compile(r"Week\s+[2-9]\+|Week\s+\d{2,}\+", re.IGNORECASE)
TEMPLATE_DEFAULT = re.compile(r"\{\{[^}]+\}\}|\[[A-Z][A-Z _-]+\]")
NEW_INITIATIVE = re.compile(
    r"\b(new initiative|scope expansion|should I start|new idea|starting a new)\b",
    re.IGNORECASE,
)
OVERWHELM = re.compile(r"\b(overwhelm|stuck|too many|drowning|swamped)\b", re.IGNORECASE)
AUDIT_MENTION = re.compile(r"\b/?audit\b", re.IGNORECASE)


# ---------------------------------------------------------------------------
# State collection. Each function reads a file or directory and returns plain
# data. Missing files yield neutral defaults; never raise.
# ---------------------------------------------------------------------------

def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        try:
            return path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            return ""


def detect_prefix(root: Path) -> str:
    """Path B if commands directory has files; Path A otherwise."""
    cmd_dir = root / ".claude" / "commands"
    if cmd_dir.is_dir() and any(cmd_dir.glob("*.md")):
        return "/"
    return "/founder-os:"


def render_command(name: str, prefix: str) -> str | None:
    cfg = CAPABILITIES.get(name)
    if not cfg or cfg["command"] is None:
        return None
    cmd = cfg["command"]
    if cfg["always_bare"]:
        return f"/{cmd}"
    return f"{prefix}{cmd}"


def read_snapshot(root: Path) -> str:
    return safe_read(root / "brain" / ".snapshot.md")


def open_flag_count(root: Path) -> int:
    body = safe_read(root / "brain" / "flags.md")
    if not body:
        return 0
    return len(STATUS_OPEN.findall(body))


def weekly_state(root: Path, today: date) -> dict:
    body = safe_read(root / "cadence" / "weekly-commitments.md")
    result = {"present": bool(body), "week_of": None, "days_old": None, "must_do": []}
    if not body:
        return result
    m = WEEKLY_HEADER.search(body)
    if m:
        try:
            week_of = datetime.strptime(m.group(1), "%Y-%m-%d").date()
            result["week_of"] = week_of
            result["days_old"] = (today - week_of).days
        except ValueError:
            pass
    # Pull Must Do items.
    must_section = re.search(
        r"^##\s+Must\s+Do.*?$(.*?)(?=^##\s+|\Z)",
        body,
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    if must_section:
        for line in must_section.group(1).splitlines():
            stripped = line.strip()
            item = re.match(r"^(?:[-*]|\d+\.)\s+(.+)$", stripped)
            if item:
                result["must_do"].append(item.group(1).strip())
    return result


def log_recent(root: Path, today: date, days: int = 7) -> str:
    body = safe_read(root / "brain" / "log.md")
    if not body:
        return ""
    cutoff = today - timedelta(days=days)
    chunks = []
    current_date: date | None = None
    buffer: list[str] = []
    for line in body.splitlines():
        m = DAILY_HEADER.match(line)
        if m:
            if current_date is not None and current_date >= cutoff:
                chunks.append("\n".join(buffer))
            try:
                current_date = datetime.strptime(m.group(1), "%Y-%m-%d").date()
            except ValueError:
                current_date = None
            buffer = [line]
        else:
            buffer.append(line)
    if current_date is not None and current_date >= cutoff:
        chunks.append("\n".join(buffer))
    return "\n".join(chunks)


def last_audit_days(root: Path, today: date) -> int | None:
    """Return days since last audit mention in log, or None if never."""
    body = safe_read(root / "brain" / "log.md")
    if not body:
        return None
    last_seen: date | None = None
    current_date: date | None = None
    for line in body.splitlines():
        m = DAILY_HEADER.match(line)
        if m:
            try:
                current_date = datetime.strptime(m.group(1), "%Y-%m-%d").date()
            except ValueError:
                current_date = None
            continue
        if current_date is not None and AUDIT_MENTION.search(line):
            if last_seen is None or current_date > last_seen:
                last_seen = current_date
    if last_seen is None:
        return None
    return (today - last_seen).days


def profile_status(root: Path, name: str) -> str:
    """Return one of: missing, template, set."""
    path = root / "core" / f"{name}.yml"
    body = safe_read(path)
    if not body:
        return "missing"
    if TEMPLATE_DEFAULT.search(body):
        return "template"
    return "set"


def priorities_rolled(root: Path) -> int:
    body = safe_read(root / "context" / "priorities.md")
    if not body:
        return 0
    return len(ROLLED_FORWARD.findall(body))


def read_primary_channel(root: Path) -> str | None:
    """Return primary_channel value from stack.json, or None if not set."""
    import json
    path = root / "stack.json"
    body = safe_read(path)
    if not body:
        return None
    try:
        data = json.loads(body)
        val = data.get("primary_channel")
        return val if isinstance(val, str) and val else None
    except (json.JSONDecodeError, AttributeError):
        return None


def drafts_recent(root: Path, today: date) -> int:
    drafts_dir = root / "drafts"
    if not drafts_dir.is_dir():
        return 0
    cutoff = datetime.combine(today, datetime.min.time()) - timedelta(hours=24)
    count = 0
    for entry in drafts_dir.rglob("*"):
        if entry.is_file():
            try:
                mtime = datetime.fromtimestamp(entry.stat().st_mtime)
            except OSError:
                continue
            if mtime >= cutoff:
                count += 1
    return count


def unprocessed_rant_count(root: Path) -> int:
    """Count rant entries (not files) where frontmatter `processed: false`."""
    rants_dir = root / "brain" / "rants"
    if not rants_dir.is_dir():
        return 0
    count = 0
    pat = re.compile(r"^processed:\s*false\s*$")
    for f in rants_dir.glob("*.md"):
        body = safe_read(f)
        if not body:
            continue
        for line in body.splitlines():
            if pat.match(line):
                count += 1
    return count


# ---------------------------------------------------------------------------
# Rules. Each returns (fired: bool, why_now: str).
# ---------------------------------------------------------------------------

def rule_voice_interview(state: dict) -> tuple[bool, str]:
    status = state["voice"]
    if status == "missing":
        return True, "your voice profile is empty so writing skills fall back to anti-AI defaults."
    if status == "template":
        return True, "your voice profile still has template placeholders, writing skills can't apply your voice yet."
    return False, "day one move - without it, writing skills fall back to anti-AI defaults."


def rule_brand_interview(state: dict) -> tuple[bool, str]:
    status = state["brand"]
    if status == "missing":
        return True, "your brand profile is empty so branded deliverables render plain."
    if status == "template":
        return True, "your brand profile still has template placeholders, branded deliverables won't render in your identity yet."
    return False, "day one move - without it, branded deliverables render plain."


def rule_priority_triage(state: dict) -> tuple[bool, str]:
    rolled = state["priorities_rolled"]
    log = state["log_7d"]
    if rolled >= 3:
        return True, f"{rolled} priorities rolled forward, list needs cutting."
    if OVERWHELM.search(log):
        return True, "recent log entries mention overwhelm, time to cut to one thing."
    return False, "cuts a long open list down to one thing."


def rule_weekly_review(state: dict) -> tuple[bool, str]:
    weekly = state["weekly"]
    if not weekly["present"]:
        return True, "no weekly commitments file yet, time to set this week's must-do."
    days_old = weekly["days_old"]
    if days_old is None:
        return False, "rolls the sprint and resets must-do."
    if days_old > 6:
        return True, f"your weekly commitments file is {days_old} days old, the sprint needs rolling."
    return False, "rolls the sprint and resets must-do."


def rule_forcing_questions(state: dict) -> tuple[bool, str]:
    if NEW_INITIATIVE.search(state["log_7d"]):
        return True, "log shows a new initiative starting this week, run the gate before scope expands."
    return False, "anti-shiny-object gate before starting anything new."


def rule_pre_send_check(state: dict) -> tuple[bool, str]:
    drafts = state["drafts_24h"]
    if drafts > 0:
        return True, f"{drafts} draft(s) modified in the last 24 hours, run the pre-send gate before they leave."
    return False, "the pre-ship gate for any client-facing deliverable."


def rule_capture_meeting(state: dict) -> tuple[bool, str]:
    # Calendar MCP is not always present; surface as a soft, low-priority option.
    return False, "files a meeting transcript or brain dump into the log and client notes."


def rule_audit(state: dict) -> tuple[bool, str]:
    days = state["audit_days"]
    if days is None:
        return True, "no audit on record yet, worth a fresh pass."
    if days > 14:
        return True, f"last audit was {days} days ago, worth a fresh pass."
    return False, "one-screen state view across readiness, lint, wiki, brain, voice."


def rule_today(state: dict) -> tuple[bool, str]:
    return False, "one-screen view of today's anchor, open flags, and next event."


def rule_ingest(state: dict) -> tuple[bool, str]:
    return False, "files a source into raw/ with provenance preserved."


def rule_dream(state: dict) -> tuple[bool, str]:
    n = state.get("unprocessed_rants", 0)
    if n >= 3:
        return True, f"{n} rants captured but not processed - distil them before they go stale at 30 days."
    if n >= 1:
        return True, f"{n} rant(s) waiting - dream distils them into patterns, flags, and one recommended action."
    return False, "distils unprocessed rants into patterns, flags, parked decisions, and one action."


def rule_linkedin_post(state: dict) -> tuple[bool, str]:
    if state["voice"] == "set" and state.get("primary_channel") == "linkedin":
        return True, "your primary channel is LinkedIn and your voice profile is set - you can create posts in your own voice."
    return False, "writes LinkedIn posts in your voice once the voice profile is set."


def rule_content_repurposer(state: dict) -> tuple[bool, str]:
    channel = state.get("primary_channel")
    if state["voice"] == "set" and channel and channel != "linkedin":
        channel_label = channel.replace("_", " ")
        return True, f"your primary channel is {channel_label} and your voice profile is set - you can create content in your own voice."
    return False, "adapts one piece of content across LinkedIn, Instagram, YouTube, email, and more."


RULES = [
    ("voice-interview", rule_voice_interview),
    ("brand-interview", rule_brand_interview),
    ("priority-triage", rule_priority_triage),
    ("weekly-review", rule_weekly_review),
    ("forcing-questions", rule_forcing_questions),
    ("pre-send-check", rule_pre_send_check),
    ("capture-meeting", rule_capture_meeting),
    ("audit", rule_audit),
    ("today", rule_today),
    ("ingest", rule_ingest),
    ("linkedin-post", rule_linkedin_post),
    ("content-repurposer", rule_content_repurposer),
    ("dream", rule_dream),
]


# ---------------------------------------------------------------------------
# Rendering.
# ---------------------------------------------------------------------------

def render_row(name: str, why_now: str, prefix: str) -> str:
    cfg = CAPABILITIES[name]
    phrase = cfg["phrase"]
    cmd = render_command(name, prefix)
    if cmd is None:
        return f'- Say "{phrase}" - {why_now}'
    return f'- Say "{phrase}" (or run {cmd}) - {why_now}'


def is_zero_state(state: dict) -> bool:
    return (
        not state["snapshot"]
        and not state["log_7d"].strip()
        and state["priorities_rolled"] == 0
        and not state["weekly"]["present"]
        and state["voice"] == "missing"
        and state["brand"] == "missing"
    )


def collect_state(root: Path, today: date) -> dict:
    return {
        "snapshot": read_snapshot(root),
        "open_flags": open_flag_count(root),
        "weekly": weekly_state(root, today),
        "log_7d": log_recent(root, today, days=7),
        "audit_days": last_audit_days(root, today),
        "voice": profile_status(root, "voice-profile"),
        "brand": profile_status(root, "brand-profile"),
        "priorities_rolled": priorities_rolled(root),
        "drafts_24h": drafts_recent(root, today),
        "primary_channel": read_primary_channel(root),
        "unprocessed_rants": unprocessed_rant_count(root),
    }


def build_menu(state: dict, prefix: str) -> list[str]:
    if is_zero_state(state):
        rows = []
        for name in DAY_ONE_ORDER:
            why = {
                "voice-interview": "day one move - without it, writing skills fall back to anti-AI defaults.",
                "brand-interview": "day one move - without it, branded deliverables render plain.",
                "priority-triage": "cuts a long open list down to one thing.",
                "today": "one-screen view of today's anchor, open flags, and next event.",
                "ingest": "files a source into raw/ with provenance preserved.",
            }[name]
            rows.append(render_row(name, why, prefix))
        return rows

    scored: list[tuple[int, int, str, str]] = []
    for order_index, (name, rule) in enumerate(RULES):
        fired, why_now = rule(state)
        scored.append((1 if fired else 0, -order_index, name, why_now))

    # Sort: fired first, then original order.
    scored.sort(key=lambda x: (-x[0], -x[1]))

    fired_rows = [r for r in scored if r[0] == 1]
    fallback_rows = [r for r in scored if r[0] == 0]

    chosen: list[tuple[int, int, str, str]] = []
    chosen.extend(fired_rows[:7])
    if len(chosen) < 5:
        chosen.extend(fallback_rows[: 5 - len(chosen)])
    chosen = chosen[:7]

    return [render_row(name, why_now, prefix) for _, _, name, why_now in chosen]


def render_output(rows: list[str]) -> str:
    count = len(rows)
    header = f"Here are {count} things FounderOS can do right now, picked for your current state:"
    return "\n".join([header, "", *rows, "", CLOSING_LINE])


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Founder OS menu engine.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Path to the FounderOS install root (default: cwd).",
    )
    parser.add_argument(
        "--today",
        type=str,
        default=None,
        help="Override today's date as YYYY-MM-DD (for tests).",
    )
    args = parser.parse_args(argv)

    root: Path = args.root.resolve()
    if args.today:
        today = datetime.strptime(args.today, "%Y-%m-%d").date()
    else:
        today = date.today()

    prefix = detect_prefix(root)
    state = collect_state(root, today)
    rows = build_menu(state, prefix)
    print(render_output(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
