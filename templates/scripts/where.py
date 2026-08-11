#!/usr/bin/env python3
"""where.py - answer "where is my work" without making anyone read a path.

The problem it exists for, in a real founder's words: "I have been on 3 or 4
different chats for this project but somehow it is nowhere to be found. It does
things and saves somewhere else." She was not wrong and nothing was lost. The
work was in a folder inside her OS that git had been told to ignore, so it never
appeared in any status, any backup, or any answer she could act on. When she
asked where it went, she got a wall of paths and layer names back and said "I
cannot understand anything it said."

Two failures, and this script is aimed at both:

  1. NOTHING SHOWED HER RECENT WORK GROUPED BY PROJECT. The OS could report its
     own files and its own sessions, but not the plain question "what have I
     been working on and where did it land".
  2. THE FOLDERS MOST LIKELY TO BE LOST WERE THE ONES LEAST LIKELY TO BE SEEN.
     A project folder that git ignores is invisible to every safety net the OS
     has, so the work at the highest risk of vanishing is the work nothing
     mentions. That is backwards, and it is the part this fixes.

So the output leads with what she was doing, names the folder in the same words
she would use, and says in plain English whether a copy of it exists anywhere
other than this laptop. Paths are printed, but they are never the answer on
their own.

Standard library only. Read-only: it opens nothing, moves nothing, writes
nothing. Safe to run on any install, git or ZIP.

Usage:
  python scripts/where.py                 last 14 days, grouped by project
  python scripts/where.py --days 3        narrow the window
  python scripts/where.py --all           every project folder, however old
  python scripts/where.py --json          machine-readable, for the skill
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# The OS's own machinery. A founder asking where their work is does not mean
# the skill files that did the work, and burying the answer under them is how
# the last answer became unreadable.
OS_DIRS = {
    ".git", ".github", ".claude", ".claude-plugin", "scripts", "skills",
    "templates", "state", "tests", "docs", "updates", "notion-package",
    "node_modules", "__pycache__", ".venv", "venv", ".pytest_cache", ".obsidian",
}
# The brain and the operating files are the OS working normally, not a project.
# They are summarised in one line at the end rather than listed file by file.
OS_CONTENT_DIRS = {"brain", "core", "context", "cadence", "rules", "roles",
                   "system", "memory", "capture", "raw"}
SKIP_FILES = {".DS_Store", "Thumbs.db", ".gitignore", ".gitattributes"}


def _git_tracked_dirs(root: Path) -> set[str] | None:
    """Top-level names git actually has a copy of. None when this install has no
    git at all, which is a normal ZIP install and not an error - it just means
    the backup question has one answer for everything."""
    if not (root / ".git").is_dir():
        return None
    try:
        out = subprocess.run(["git", "ls-files"], cwd=str(root), capture_output=True,
                             text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return {line.split("/", 1)[0] for line in out.stdout.splitlines() if line.strip()}


def _walk(root: Path) -> dict[str, dict]:
    """One pass over the install. Returns {top-level name: {files, newest, ...}}."""
    groups: dict[str, dict] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in OS_DIRS and not d.startswith(".")]
        rel = Path(dirpath).relative_to(root)
        top = rel.parts[0] if rel.parts else ""
        if not top or top in OS_DIRS:
            continue
        for name in filenames:
            if name in SKIP_FILES or name.startswith("."):
                continue
            try:
                mtime = (Path(dirpath) / name).stat().st_mtime
            except OSError:
                continue
            g = groups.setdefault(top, {"files": 0, "newest": 0.0, "newest_file": "",
                                        "deepest": ""})
            g["files"] += 1
            if mtime > g["newest"]:
                g["newest"] = mtime
                # forward slashes always: a founder copying a path into Explorer,
                # Finder or a chat should get the same string on every machine
                g["newest_file"] = (Path(dirpath) / name).relative_to(root).as_posix()
            # the folder a founder would actually name, one level in
            if len(rel.parts) > 1 and not g["deepest"]:
                g["deepest"] = Path(*rel.parts[:2]).as_posix() + "/"
    return groups


def _age(seconds_ago: float) -> str:
    """How long ago, in the words a person uses out loud."""
    days = seconds_ago / 86400
    if days < 1:
        return "today"
    if days < 2:
        return "yesterday"
    if days < 14:
        return f"{int(days)} days ago"
    if days < 60:
        return f"{int(days / 7)} weeks ago"
    return f"{int(days / 30)} months ago"


def collect(root: Path, days: int | None) -> dict:
    tracked = _git_tracked_dirs(root)
    groups = _walk(root)
    now = time.time()
    cutoff = 0.0 if days is None else now - days * 86400

    projects, os_own = [], []
    for name, g in groups.items():
        if g["newest"] < cutoff:
            continue
        row = {
            "name": name,
            "folder": name + "/",
            "files": g["files"],
            "age": _age(now - g["newest"]),
            "newest_file": g["newest_file"],
            "sub": g["deepest"],
            # None means "this install has no git, so nothing here is backed up
            # by the OS" - a different answer from "git exists and skips this".
            "backed_up": None if tracked is None else (name in tracked),
        }
        (os_own if name in OS_CONTENT_DIRS else projects).append(row)

    projects.sort(key=lambda r: -groups[r["name"]]["newest"])
    os_own.sort(key=lambda r: -groups[r["name"]]["newest"])
    return {"root": str(root), "has_git": tracked is not None,
            "days": days, "projects": projects, "os_own": os_own}


def render(data: dict) -> str:
    out: list[str] = []
    window = ("everything, however old" if data["days"] is None
              else f"the last {data['days']} days")
    out.append(f"YOUR WORK - {window}, most recent first")
    out.append("")

    if not data["projects"]:
        out.append("  No project folders changed in this window.")
        out.append("  Try: python scripts/where.py --all")
    for p in data["projects"]:
        label = p["sub"] or p["folder"]
        out.append(f"  {p['name']}   (worked on {p['age']})")
        out.append(f"    Folder:  {label}")
        out.append(f"    {p['files']} file(s). Most recent: {p['newest_file']}")
        if p["backed_up"] is False:
            out.append("    NOT BACKED UP. This exists only on this computer. If the")
            out.append("    laptop dies or the folder is deleted, it is gone.")
        elif p["backed_up"] is None:
            out.append("    Backup unknown - this install has no version history yet.")
        else:
            out.append("    Backed up.")
        out.append("")

    if data["os_own"]:
        names = ", ".join(r["name"] for r in data["os_own"][:6])
        newest = data["os_own"][0]["age"]
        out.append(f"  Your OS files (notes, clients, the week) changed {newest}: {names}")
        out.append("")

    unsafe = [p["name"] for p in data["projects"] if p["backed_up"] is False]
    if unsafe:
        out.append("WORTH KNOWING")
        out.append(f"  {len(unsafe)} folder(s) have no backup: " + ", ".join(unsafe))
        out.append("  Say \"back up my work\" and the OS will walk you through it.")
    elif data["has_git"] is False:
        out.append("WORTH KNOWING")
        out.append("  This install has no version history, so nothing here has a")
        out.append("  second copy. Say \"back up my work\" to fix that once.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Where your recent work actually lives, in plain language.")
    p.add_argument("--days", type=int, default=14)
    p.add_argument("--all", action="store_true", help="every folder, no time window")
    p.add_argument("--root", default=str(REPO_ROOT))
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    data = collect(Path(a.root), None if a.all else a.days)
    print(json.dumps(data, ensure_ascii=True, indent=2) if a.json else render(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
