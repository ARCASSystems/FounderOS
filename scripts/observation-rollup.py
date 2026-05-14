#!/usr/bin/env python3
"""
Compress weekly JSONL observation logs into markdown summaries.

Walks brain/observations/*.jsonl, groups by ISO week, and for each week with
>= 7 days of data that ended >= 3 days ago writes a markdown rollup to
brain/observations/_rollups/YYYY-Wnn.md. By default the source JSONL files
are MOVED to brain/observations/_archived/YYYY-Wnn/ after a successful
rollup, not deleted. Pass --delete-sources to remove them instead.

Idempotent: weeks that already have a rollup file are skipped.
Pure stdlib. No dependencies.
"""

import argparse
import json
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    """Walk up from start until we find a directory with brain/observations/."""
    for candidate in [start.resolve()] + list(start.resolve().parents):
        if (candidate / "brain" / "observations").is_dir():
            return candidate
    raise RuntimeError(
        f"Could not find brain/observations/ searching up from {start}"
    )


def iso_week_key(d: date) -> str:
    """Return 'YYYY-Wnn' for the ISO week containing d."""
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def week_end_date(d: date) -> date:
    """Return the Sunday that closes the ISO week containing d."""
    iso = d.isocalendar()
    # isocalendar weekday: Mon=1 ... Sun=7
    return d + timedelta(days=7 - iso[2])


def write_rollup(week_key: str, files: list, rollup_dir: Path) -> Path:
    """Aggregate JSONL files for one week and write a markdown rollup."""
    tool_counts: Counter = Counter()
    skill_counts: Counter = Counter()
    session_ids: set = set()
    total_lines = 0

    for f in sorted(files):
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        for raw in text.splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            total_lines += 1
            tool = entry.get("tool", "")
            if tool:
                tool_counts[tool] += 1
            skill = entry.get("skill", "")
            if skill:
                skill_counts[skill] += 1
            sid = entry.get("session", "") or entry.get("session_id", "")
            if sid:
                session_ids.add(sid)

    top5_tools = tool_counts.most_common(5)
    days_represented = sorted(f.stem for f in files)

    rollup_dir.mkdir(parents=True, exist_ok=True)
    rollup_path = rollup_dir / f"{week_key}.md"

    out = [
        f"# Observation rollup - {week_key}",
        "",
        f"Days: {', '.join(days_represented)}",
        f"Total observations: {total_lines}",
        f"Unique sessions: {len(session_ids)}",
        "",
        "## Tool usage",
        "",
    ]

    if tool_counts:
        out.append(f"Total tool calls: {sum(tool_counts.values())}")
        out.append("")
        out.append("Top 5 tools:")
        for tool, count in top5_tools:
            out.append(f"- {tool}: {count}")
    else:
        out.append("No tool calls recorded.")

    out += ["", "## Skill invocations", ""]

    if skill_counts:
        out.append(f"Total skill invocations: {sum(skill_counts.values())}")
        out.append("")
        for skill, count in sorted(skill_counts.items()):
            out.append(f"- {skill}: {count}")
    else:
        out.append("No skill invocations recorded.")

    if session_ids:
        out += ["", "## Session IDs", ""]
        for sid in sorted(session_ids):
            out.append(f"- {sid}")

    rollup_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return rollup_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compress weekly JSONL observation logs into markdown summaries."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Override the repo root. Defaults to the directory containing brain/observations/ above scripts/.",
    )
    parser.add_argument(
        "--delete-sources",
        action="store_true",
        help="Delete source JSONL files after rollup instead of archiving them. Default is to MOVE them to brain/observations/_archived/YYYY-Wnn/.",
    )
    args = parser.parse_args()

    today = date.today()

    if args.root is not None:
        candidate = args.root.resolve()
        if not (candidate / "brain" / "observations").is_dir():
            print(
                f"--root {candidate} does not contain brain/observations/",
                file=sys.stderr,
            )
            sys.exit(1)
        repo = candidate
    else:
        try:
            repo = find_repo_root(Path(__file__).parent)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)

    obs_dir = repo / "brain" / "observations"
    rollup_dir = obs_dir / "_rollups"
    archive_dir = obs_dir / "_archived"

    # Collect JSONL files by ISO week. Filenames must be YYYY-MM-DD.jsonl.
    by_week: dict = {}
    for f in obs_dir.glob("*.jsonl"):
        try:
            file_date = date.fromisoformat(f.stem)
        except ValueError:
            continue  # skip filenames that are not dates
        key = iso_week_key(file_date)
        by_week.setdefault(key, []).append(f)

    if not by_week:
        print("No observation files found. Nothing to roll up.")
        return

    rolled = 0
    skipped_pending = 0
    skipped_already = 0

    for week_key, files in sorted(by_week.items()):
        # Use the first file's date to locate the week.
        representative = date.fromisoformat(sorted(f.stem for f in files)[0])
        w_end = week_end_date(representative)

        # Must have >= 7 days of data AND be at least 3 days past week-end.
        if len(files) < 7 or today < w_end + timedelta(days=3):
            skipped_pending += 1
            continue

        rollup_path = rollup_dir / f"{week_key}.md"
        if rollup_path.exists():
            skipped_already += 1
            continue

        written = write_rollup(week_key, files, rollup_dir)

        # Only dispose of source files after verifying the rollup was written.
        if not written.exists():
            print(
                f"ERROR: rollup write failed for {week_key}. Source files preserved.",
                file=sys.stderr,
            )
            sys.exit(1)

        if args.delete_sources:
            for f in files:
                try:
                    f.unlink()
                except OSError as exc:
                    print(f"WARNING: could not delete {f}: {exc}", file=sys.stderr)
            disposition = "deleted"
        else:
            week_archive = archive_dir / week_key
            week_archive.mkdir(parents=True, exist_ok=True)
            for f in files:
                try:
                    f.replace(week_archive / f.name)
                except OSError as exc:
                    print(
                        f"WARNING: could not archive {f}: {exc}",
                        file=sys.stderr,
                    )
            disposition = f"archived to {week_archive.relative_to(repo)}"

        rolled += 1
        print(f"Rolled up {week_key} ({len(files)} days -> {written.name}, sources {disposition})")

    print(
        f"Done. Rolled: {rolled}, "
        f"skipped (pending/incomplete): {skipped_pending}, "
        f"skipped (already rolled): {skipped_already}."
    )


if __name__ == "__main__":
    main()
