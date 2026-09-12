#!/usr/bin/env python3
"""writing_scorecard.py - the register census over everything you wrote lately.

The problem it exists for: a gate on one document tells you whether that
document is clean. It cannot tell you whether your writing is getting better,
and that is the question worth answering, because the tells come back. This
runs scripts/register_census.py across your recent files, groups the scores by
folder, and writes a scorecard with the change since the last run. One number
you can watch, and the three classes to fix first.

It scores your writing, not the OS's. Engine folders (skills, scripts, rules,
docs, templates, updates) are skipped by default: they are the product, and
scoring them would bury your own files in noise. `--all` includes them.

Invariants: read-only on everything it measures, standard library only, no
network, no API key, no model call. Writes exactly two paths, both under
state/, and `--no-write` suppresses even those.

Usage:
  python scripts/writing_scorecard.py                  # last 30 days
  python scripts/writing_scorecard.py --days 90
  python scripts/writing_scorecard.py --path brain --no-write
  python scripts/writing_scorecard.py --json
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import register_census as rc  # noqa: E402

VIEW = REPO / "state" / "writing-scorecard.md"
HISTORY = REPO / "state" / "writing-scores.jsonl"

# The OS's own files. Yours are everything else.
ENGINE_DIRS = {"skills", "scripts", "rules", "docs", "templates", "updates",
               "archive", "notes", "plans", "tests", "traces", "notion-package",
               ".claude", ".claude-plugin", ".github", ".githooks", ".git",
               ".agents", ".codex", "dist"}
SKIP_PARTS = ("__pycache__", ".snapshots", "node_modules", ".pytest_cache")
SKIP_NAMES = {"CHANGELOG.md", "README.md", "LICENSE", "AGENTS.md", "GEMINI.md",
              "CLAUDE.md", "CONTRIBUTING.md", "SECURITY.md", "llms.txt"}
READABLE = {".md", ".markdown", ".txt", ".html", ".htm", ".docx"}
MAX_BYTES = 400_000

# A file whose whole job is to name bad writing will be full of bad writing.
# Scoring the examples teaches nothing.
QUOTES_ITS_OWN_BANS = {"writing-style.md", "banned-words-exceptions.txt"}

# Folders whose content is a note to yourself, not something a reader receives.
INTERNAL_DIRS = {"brain", "cadence", "context", "system", "state", "memory", "raw"}


def profile_for(rel: Path) -> str:
    top = rel.parts[0] if rel.parts else ""
    return "internal" if top in INTERNAL_DIRS else "deliverable"


def candidates(root: Path, days: int, scope: Path | None, include_engine: bool) -> list[Path]:
    cutoff = time.time() - days * 86400
    base = scope or root
    out: list[Path] = []
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in READABLE:
            continue
        rel = p.relative_to(root)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        if not include_engine and rel.parts and rel.parts[0] in ENGINE_DIRS:
            continue
        if p.name in SKIP_NAMES or p.name in QUOTES_ITS_OWN_BANS:
            continue
        try:
            stat = p.stat()
        except OSError:
            continue
        if stat.st_mtime < cutoff or stat.st_size > MAX_BYTES:
            continue
        out.append(p)
    return sorted(out)


def score_files(root: Path, files: list[Path]) -> list[dict]:
    rows: list[dict] = []
    for p in files:
        rel = p.relative_to(root)
        profile = profile_for(rel)
        try:
            c = rc.census_file(p, profile)
        except Exception as exc:                      # a malformed docx is a skip, not a crash
            rows.append({"path": rel.as_posix(), "skipped": str(exc)[:60]})
            continue
        if c is None or c.words < 60:                 # too short to measure honestly
            continue
        status, reasons = rc.gate(c, profile)
        top = rc.top_classes(c, profile)
        rows.append({
            "path": rel.as_posix(), "group": rel.parts[0] if len(rel.parts) > 1 else ".",
            "profile": profile, "score": c.score, "grade": rc.grade(c.score),
            "words": c.words, "fk_grade": c.fk_grade, "gate": status,
            "reasons": reasons,
            "top": [{"cls": cls, "hits": n} for cls, n in top],
        })
    return rows


def summarise(rows: list[dict]) -> dict:
    scored = [r for r in rows if "score" in r]
    if not scored:
        return {"files": 0, "words": 0, "mean": 0, "worst": [], "classes": {}}
    words = sum(r["words"] for r in scored)
    # Weighted by length: a 4,000-word document that reads badly matters more
    # than a 70-word note that does.
    mean = round(sum(r["score"] * r["words"] for r in scored) / words) if words else 0
    classes: dict[str, int] = {}
    for r in scored:
        for t in r["top"]:
            classes[t["cls"]] = classes.get(t["cls"], 0) + t["hits"]
    groups: dict[str, list[int]] = {}
    for r in scored:
        groups.setdefault(r["group"], []).append(r["score"])
    return {
        "files": len(scored), "words": words, "mean": mean,
        "failing": sum(1 for r in scored if r["gate"] == "fail"),
        "worst": sorted(scored, key=lambda r: r["score"])[:8],
        "classes": dict(sorted(classes.items(), key=lambda kv: -kv[1])[:8]),
        "groups": {g: round(sum(v) / len(v)) for g, v in sorted(groups.items())},
    }


def previous(history: Path) -> dict | None:
    if not history.is_file():
        return None
    lines = [x for x in history.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not lines:
        return None
    try:
        return json.loads(lines[-1])
    except json.JSONDecodeError:
        return None


def render(summary: dict, rows: list[dict], prev: dict | None, days: int) -> str:
    today = _dt.date.today().isoformat()
    delta = ""
    if prev and prev.get("mean"):
        d = summary["mean"] - prev["mean"]
        delta = (f"  ({d:+d} since {prev.get('date', 'the last run')})" if d
                 else f"  (unchanged since {prev.get('date', 'the last run')})")
    out = [
        "# Writing scorecard",
        "",
        f"Run {today}. Last {days} days: {summary['files']} files, "
        f"{summary['words']:,} words.",
        "",
        f"**Mean score {summary['mean']}{delta}.** "
        f"{summary['failing']} would fail their gate.",
        "",
        "Scores come from `scripts/register_census.py`, which counts the classes "
        "named in `rules/writing-style.md`. Nothing here judges whether the "
        "writing is true or worth sending.",
        "",
    ]
    if summary["classes"]:
        out += ["## Fix these first", "",
                "| Class | Hits | The rule |", "|---|---|---|"]
        for cls, n in summary["classes"].items():
            rule = rc.CLASS_RULE.get(cls, cls.replace("_", " "))
            out.append(f"| `{cls}` | {n} | {rule} |")
        out.append("")
    if summary.get("groups"):
        out += ["## By folder", "", "| Folder | Mean score |", "|---|---|"]
        for g, v in summary["groups"].items():
            out.append(f"| {g} | {v} |")
        out.append("")
    if summary["worst"]:
        out += ["## Lowest scoring", "",
                "| File | Score | Words | Gate | Why |", "|---|---|---|---|---|"]
        for r in summary["worst"]:
            why = "; ".join(r["reasons"])[:80] or "-"
            out.append(f"| {r['path']} | {r['score']} ({r['grade']}) | "
                       f"{r['words']} | {r['gate']} | {why} |")
        out.append("")
    skipped = [r for r in rows if "skipped" in r]
    if skipped:
        out += [f"{len(skipped)} file(s) could not be read and were skipped.", ""]
    out.append("Run one file in detail: "
               "`python scripts/register_census.py <path> --lines`")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    rc._force_utf8()
    ap = argparse.ArgumentParser(description="Score your recent writing against rules/writing-style.md.")
    ap.add_argument("--days", type=int, default=30, help="how far back to look (default 30)")
    ap.add_argument("--path", default=None, help="score this folder only")
    ap.add_argument("--all", action="store_true", help="include the OS's own engine files")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true", help="report without writing state/")
    ap.add_argument("--root", default=str(REPO))
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    scope = (root / args.path).resolve() if args.path else None
    if scope is not None and not scope.exists():
        print(f"writing-scorecard: no folder at {scope}", file=sys.stderr)
        return 1

    files = candidates(root, args.days, scope, args.all)
    rows = score_files(root, files)
    summary = summarise(rows)
    prev = previous(root / "state" / "writing-scores.jsonl")

    if args.json:
        print(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=True, default=str))
    else:
        print(render(summary, rows, prev, args.days))

    if not args.no_write and summary["files"]:
        view = root / "state" / "writing-scorecard.md"
        history = root / "state" / "writing-scores.jsonl"
        view.parent.mkdir(parents=True, exist_ok=True)
        view.write_text(render(summary, rows, prev, args.days), encoding="utf-8", newline="")
        record = {"date": _dt.date.today().isoformat(), "days": args.days,
                  "files": summary["files"], "words": summary["words"],
                  "mean": summary["mean"], "failing": summary["failing"]}
        with history.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
