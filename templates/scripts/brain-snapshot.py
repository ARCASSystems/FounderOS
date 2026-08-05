#!/usr/bin/env python3
"""Brain snapshot generator for Founder OS.

Reads brain + cadence + profile files and emits a small deterministic
markdown payload that any skill can consume at task time.

Pure stdlib. Fail-soft: missing files render `[unavailable]` sections
rather than crashing.
"""

from __future__ import annotations

import argparse
import re
from datetime import date, datetime
from pathlib import Path

VOICE_FIELDS = ["rhythm", "opening_style", "closing_style", "contractions", "reading_level"]
DAILY_HEADER = re.compile(r"^##\s+Today:\s*(\d{4}-\d{2}-\d{2})\s*$")
WEEKLY_HEADER = re.compile(r"^##\s+Week\s+of\s+(\d{4}-\d{2}-\d{2})\s*$")
MUST_DO_HEADER = re.compile(r"^##\s+Must\s+Do\b", re.IGNORECASE)
NEXT_H2 = re.compile(r"^##\s+")
LIST_LINE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(.+?)\s*$")
STATUS_OPEN = re.compile(r"Status:\s*\**OPEN", re.IGNORECASE)
H2_HEADER = re.compile(r"^##\s+(.+?)\s*$")
H3_HEADER = re.compile(r"^###\s+(.+?)\s*$")
FOUNDER_FIELD = re.compile(r"^\*\*(Venture|Customer|Stage \(seed\)|Biggest blocker):\*\*\s*(.*?)\s*$")
ROLE_FIELD = re.compile(r"^\*\*(Scope|Answers to|Yours to own|Not yours to decide|Biggest blocker):\*\*\s*(.*?)\s*$")


def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            return ""
    except OSError:
        return ""


def is_unset(value: str | None) -> bool:
    """A bracketed template default or empty string counts as unset."""
    if value is None:
        return True
    s = value.strip().strip('"').strip("'")
    if not s:
        return True
    if s.startswith("[") and s.endswith("]"):
        return True
    return False


def strip_inline_comment(content: str) -> str:
    """Drop a trailing ' #...' comment from a YAML key-value line."""
    if '"' in content or "'" in content:
        # Strip comment that appears after the closing quote character.
        for q in ('"', "'"):
            pos = content.rfind(q)
            if pos != -1:
                after = content[pos + 1:]
                if " #" in after:
                    return content[: pos + 1].rstrip()
        return content
    if " #" in content:
        return content.split(" #", 1)[0].rstrip()
    return content


def yaml_scalar(text: str, *path: str) -> str | None:
    """Return the scalar value at the dotted path or None.

    Handles only simple key/value YAML. No anchors, no flow style, no
    multi-line scalars. Sufficient for voice-profile.yml and
    brand-profile.yml which are flat configs.
    """
    target = list(path)
    stack: list[tuple[int, str]] = []

    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        content = strip_inline_comment(raw.strip())
        match = re.match(r"([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", content)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        while stack and stack[-1][0] >= indent:
            stack.pop()
        current = [k for _, k in stack] + [key]
        if current == target:
            return value.strip().strip('"').strip("'") if value else None
        if not value:
            stack.append((indent, key))
    return None


def yaml_list(text: str, *path: str) -> list[str]:
    """Return list items under the dotted path."""
    target = list(path)
    stack: list[tuple[int, str]] = []
    capturing = False
    capture_indent = -1
    out: list[str] = []

    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        content = strip_inline_comment(raw.strip())

        if capturing:
            if indent <= capture_indent:
                capturing = False
            else:
                item = re.match(r"-\s+(.+)$", content)
                if item:
                    out.append(item.group(1).strip().strip('"').strip("'"))
                continue

        match = re.match(r"([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", content)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        while stack and stack[-1][0] >= indent:
            stack.pop()
        current = [k for _, k in stack] + [key]
        if current == target and not value:
            capturing = True
            capture_indent = indent
            continue
        if not value:
            stack.append((indent, key))
    return out


def voice_section(root: Path) -> list[str]:
    path = root / "core" / "voice-profile.yml"
    text = safe_read(path) if path.exists() else ""

    lines = ["## Voice (key rules)"]
    for field in VOICE_FIELDS:
        value = yaml_scalar(text, "voice", field) if text else None
        lines.append(f"- {field}: {'[NOT SET]' if is_unset(value) else value}")

    preferred_raw = yaml_list(text, "voice", "preferred_words") if text else []
    banned_raw = yaml_list(text, "voice", "banned_words") if text else []
    preferred = [p for p in preferred_raw if not is_unset(p)]
    banned = [b for b in banned_raw if not is_unset(b)]

    lines.append(f"- preferred: {', '.join(preferred[:5]) if preferred else '[NOT SET]'}")
    lines.append(f"- banned: {', '.join(banned[:5]) if banned else '[NOT SET]'}")
    return lines


def brand_section(root: Path) -> list[str]:
    path = root / "core" / "brand-profile.yml"
    text = safe_read(path) if path.exists() else ""
    display_name = yaml_scalar(text, "identity", "display_name") if text else None
    primary_color = yaml_scalar(text, "colors", "primary", "hex") if text else None
    primary_font = yaml_scalar(text, "fonts", "primary", "family") if text else None
    return [
        "## Brand (key fields)",
        f"- display_name: {'[NOT SET]' if is_unset(display_name) else display_name}",
        f"- primary_color: {'[NOT SET]' if is_unset(primary_color) else primary_color}",
        f"- primary_font: {'[NOT SET]' if is_unset(primary_font) else primary_font}",
    ]


def _identity_section(root: Path, section_name: str, field_re: re.Pattern, labels: tuple) -> list[str]:
    """Read one snapshot block from core/identity.md. Returns the field lines,
    or [] when identity.md or the section is absent, so the snapshot stays
    silent rather than emitting an empty header. Each install carries exactly
    one of the two snapshot blocks (Founder for founder / team_of_one, Role
    for operator), so at most one of these readers returns fields.
    """
    path = root / "core" / "identity.md"
    if not path.exists():
        return []
    text = safe_read(path)
    if not text:
        return []

    in_section = False
    fields: dict[str, str] = {}
    for line in text.splitlines():
        header = H2_HEADER.match(line)
        if header:
            in_section = header.group(1).strip().lower() == section_name
            continue
        if not in_section:
            continue
        match = field_re.match(line)
        if match:
            fields[match.group(1)] = match.group(2).strip()

    if not fields:
        return []

    out: list[str] = []
    for label in labels:
        value = fields.get(label, "")
        if value.startswith("{{"):
            value = ""
        out.append(f"- {label}: {'[NOT SET]' if is_unset(value) else value}")
    return out


def founder_snapshot(root: Path) -> list[str]:
    """The four fields the founder-path propose engine reads."""
    return _identity_section(
        root, "founder snapshot", FOUNDER_FIELD,
        ("Venture", "Customer", "Stage (seed)", "Biggest blocker"),
    )


def role_snapshot(root: Path) -> list[str]:
    """The operator-role twin: the fields the operator-path propose engine reads."""
    return _identity_section(
        root, "role snapshot", ROLE_FIELD,
        ("Scope", "Answers to", "Yours to own", "Not yours to decide", "Biggest blocker"),
    )


TABLE_SEP = re.compile(r"^\|[\s:|-]+\|$")


def _preference_rows(text: str, section: str) -> list[tuple[str, str]]:
    """Table rows under one H2 of core/working-preferences.md, as
    (preference, applies-to) pairs. Header and separator rows are dropped, and
    so is any row whose first cell is empty - an empty table ships on purpose,
    so the parser has to read one as zero preferences rather than as one blank."""
    rows: list[tuple[str, str]] = []
    in_section = False
    for line in text.splitlines():
        header = H2_HEADER.match(line)
        if header:
            in_section = header.group(1).strip().lower() == section
            continue
        if not in_section:
            continue
        stripped = line.strip()
        if not stripped.startswith("|") or TABLE_SEP.match(stripped):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells or not cells[0]:
            continue
        if cells[0].lower() == "preference":
            continue  # the header row
        rows.append((cells[0], cells[1] if len(cells) > 1 else ""))
    return rows


def working_preferences(root: Path) -> list[str]:
    """How the operator has said they want to be worked with.

    This is the behaviour twin of the voice profile: voice gates HOW output is
    written, this gates HOW the OS works with them - decide or offer options,
    show the working or just answer, what never to ask twice. It is in the
    snapshot because a preference nothing reads before it acts is a diary, and
    the operator finds that out by having to give the same correction twice.

    Only Active rows are returned. Proposed rows are counted, never applied:
    they are waiting on a yes, and applying one early is the exact thing that
    makes a behaviour layer feel like it was written behind somebody's back.
    """
    path = root / "core" / "working-preferences.md"
    if not path.exists():
        return []
    text = safe_read(path)
    if not text:
        return []
    active = _preference_rows(text, "active")
    proposed = _preference_rows(text, "proposed")
    out = [f"- {pref}" + (f" (applies to: {scope})" if scope else "")
           for pref, scope in active]
    if proposed:
        out.append(f"- [{len(proposed)} proposed, waiting on your yes - not applied]")
    return out


H3_PATTERN_HEADER = re.compile(r"^###\s+(.+?)\s*$")
PATTERN_FIELD = re.compile(r"^(First observed|Last seen|Impact):\s*(.+?)\s*$")


def active_patterns(root: Path, limit: int = 3) -> list[str]:
    """Top patterns from brain/patterns.md, one line each.

    patterns.md is the only file that encodes what the OS has LEARNED about
    the operator (3+ repetitions, evidence, impact) - and before v1.47 no
    output-producing skill ever saw it: the learning layer was write-only.
    Putting the active patterns in the snapshot is what lets a draft or a
    proposal say "this repeats" instead of treating every week as the first.
    Placeholder rows ([Pattern Name]) and the template's worked example are
    real entries to a parser, so bracket-only names are skipped.
    """
    path = root / "brain" / "patterns.md"
    if not path.exists():
        return []
    text = safe_read(path)
    if not text:
        return []
    out: list[str] = []
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        m = H3_PATTERN_HEADER.match(line)
        if not m:
            continue
        name = m.group(1).strip()
        if name.startswith("[") and name.endswith("]"):
            continue  # template placeholder, not a learned pattern
        fields = {}
        for follow in lines[idx + 1: idx + 15]:
            if H3_PATTERN_HEADER.match(follow):
                break
            fm = PATTERN_FIELD.match(follow.strip())
            if fm:
                fields[fm.group(1)] = fm.group(2)
        detail = []
        if fields.get("Last seen"):
            detail.append(f"last seen {fields['Last seen']}")
        if fields.get("Impact"):
            detail.append(fields["Impact"][:80])
        suffix = f" ({'; '.join(detail)})" if detail else ""
        out.append(f"- {name}{suffix}")
        if len(out) >= limit:
            break
    return out


def open_flags(root: Path, limit: int = 3) -> list[str]:
    path = root / "brain" / "flags.md"
    if not path.exists():
        return ["[unavailable]"]
    text = safe_read(path)
    if not text:
        return ["[unavailable]"]

    lines = text.splitlines()
    out: list[str] = []
    for idx, line in enumerate(lines):
        match = H2_HEADER.match(line)
        if not match:
            continue
        header = match.group(1).strip()
        # Look ahead for OPEN status before the next H2.
        is_open = False
        for follow in lines[idx + 1 : idx + 25]:
            if H2_HEADER.match(follow):
                break
            if STATUS_OPEN.search(follow):
                is_open = True
                break
        if is_open:
            out.append(f"- {header}")
            if len(out) >= limit:
                break
    return out if out else ["[no open flags]"]


def must_do(root: Path, limit: int = 3) -> list[str]:
    path = root / "cadence" / "weekly-commitments.md"
    if not path.exists():
        return []
    text = safe_read(path)
    if not text:
        return []
    lines = text.splitlines()
    items: list[str] = []
    in_block = False
    for line in lines:
        if MUST_DO_HEADER.match(line):
            in_block = True
            continue
        if in_block and (NEXT_H2.match(line) or line.strip() == "---"):
            break
        if in_block:
            match = LIST_LINE.match(line)
            if match:
                token = match.group(1).strip()
                if token.startswith("{{") and token.endswith("}}"):
                    continue
                if token:
                    items.append(token)
                    if len(items) >= limit:
                        break
    return items


def recent_decisions(root: Path, limit: int = 3) -> list[str]:
    path = root / "context" / "decisions.md"
    if not path.exists():
        return []
    text = safe_read(path)
    if not text:
        return []

    lines = text.splitlines()
    in_pending = False
    in_fence = False
    out: list[str] = []
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        h2 = H2_HEADER.match(line)
        if h2:
            in_pending = h2.group(1).strip().lower() == "pending"
            continue
        if not in_pending:
            continue
        h3 = H3_HEADER.match(line)
        if not h3:
            continue
        header = h3.group(1).strip()
        if header.lower() == "format":
            continue
        if header.startswith("[") and header.endswith("]"):
            continue
        out.append(f"- {header}")
        if len(out) >= limit:
            break
    return out


def first_match_date(text: str, pattern: re.Pattern[str]) -> date | None:
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            try:
                return datetime.strptime(match.group(1), "%Y-%m-%d").date()
            except ValueError:
                return None
    return None


def staleness_section(root: Path, today: date) -> list[str]:
    daily_path = root / "cadence" / "daily-anchors.md"
    weekly_path = root / "cadence" / "weekly-commitments.md"

    daily_state = "[unavailable]"
    weekly_state = "[unavailable]"
    weekly_must_do_state = "[unavailable - weekly file missing]"

    if daily_path.exists():
        anchor_date = first_match_date(safe_read(daily_path), DAILY_HEADER)
        if anchor_date is None:
            daily_state = "[unparsed - no '## Today: YYYY-MM-DD' header]"
        else:
            delta = (today - anchor_date).days
            daily_state = "fresh" if delta <= 0 else f"stale ({delta} days past)"

    if weekly_path.exists():
        week_date = first_match_date(safe_read(weekly_path), WEEKLY_HEADER)
        if week_date is None:
            weekly_state = "[unparsed - no '## Week of YYYY-MM-DD' header]"
            weekly_must_do_state = "[unavailable - weekly file unparsed]"
        else:
            delta = (today - week_date).days
            if delta > 6:
                weekly_state = f"stale ({delta} days past)"
                weekly_must_do_state = "[unavailable - weekly file stale]"
            else:
                weekly_state = "fresh"
                weekly_must_do_state = "fresh"

    return [
        "staleness:",
        f"  daily_anchor: {daily_state}",
        f"  weekly: {weekly_state}",
        f"  weekly-must-do: {weekly_must_do_state}",
    ]


def build_snapshot(root: Path, today: date) -> str:
    out: list[str] = []
    out.append("# Brain snapshot")
    out.append("")
    out.append(f"date: {today.isoformat()}")
    out.extend(staleness_section(root, today))
    out.append("")

    prefs = working_preferences(root)
    if prefs:
        out.append("## Working preferences (read these BEFORE you answer)")
        out.extend(prefs)
        out.append("")

    out.extend(voice_section(root))
    out.append("")

    out.extend(brand_section(root))
    out.append("")

    fs = founder_snapshot(root)
    if fs:
        out.append("## Founder Snapshot")
        out.extend(fs)
        out.append("")

    rs = role_snapshot(root)
    if rs:
        out.append("## Role Snapshot")
        out.extend(rs)
        out.append("")

    flags = open_flags(root)
    out.append("## Open flags (top 3)")
    out.extend(flags)
    out.append("")

    patterns = active_patterns(root)
    if patterns:
        out.append("## Patterns (what keeps happening)")
        out.extend(patterns)
        out.append("")

    must = must_do(root)
    out.append("## This week (must do)")
    if not must:
        out.append("[unavailable]")
    else:
        out.extend(f"- {item}" for item in must)
    out.append("")

    decisions = recent_decisions(root)
    out.append("## Recent decisions (last 3)")
    if not decisions:
        out.append("[unavailable]")
    else:
        out.extend(decisions)
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the Founder OS brain snapshot.")
    parser.add_argument("--root", default=".", help="Founder OS root (default: current directory)")
    parser.add_argument("--write", action="store_true", help="Write to brain/.snapshot.md instead of stdout")
    parser.add_argument("--today", default=None, help="Override today's date (YYYY-MM-DD). Test-only.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    today = date.today()
    if args.today:
        try:
            today = datetime.strptime(args.today, "%Y-%m-%d").date()
        except ValueError:
            print(f"--today must be YYYY-MM-DD, got: {args.today}")
            return 2

    snapshot = build_snapshot(root, today)
    if args.write:
        target = root / "brain" / ".snapshot.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(snapshot, encoding="utf-8")
        return 0
    print(snapshot, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
