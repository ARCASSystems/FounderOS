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

The backup line tells two separate truths, never one blurred one (a v1.53.0
review finding: "backed up" used to mean "git has heard of this file", which is
true of a staged-never-committed file whose only copy is this laptop):

  - SAVED IN HISTORY: the folder's content is committed and clean against HEAD.
    A dirty folder gets the honest line "an older version is saved - today's
    changes exist only here."
  - A SECOND COPY EXISTS: the current commit is contained in a remote-tracking
    ref, meaning a remote this machine has synced with actually holds it. No
    remote knowledge, no second-copy claim.

Git detection uses `git rev-parse`, not a `.git` folder test: a linked worktree
and a submodule have a `.git` FILE, and an OS folder nested inside a bigger
repo has neither, yet all three have real history.

Standard library only. Read-only: it opens nothing, moves nothing, writes
nothing. Safe to run on any install, git or ZIP. The scan is budgeted (time and
entry caps) so a folder holding a mounted archive answers partially instead of
hanging.

Usage:
  python scripts/where.py                    last 14 days, grouped by project
  python scripts/where.py vendor list        highlight folders matching a search
  python scripts/where.py --days 3           narrow the window
  python scripts/where.py --all              every project folder, however old
  python scripts/where.py --json             machine-readable, for the skill
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Machinery that is machinery on EVERY install shape: setup itself creates
# scripts/ and state/ in the founder's folder, and the dot-dirs are tooling.
MACHINERY_DIRS = {
    ".git", ".github", ".claude", ".claude-plugin", "scripts", "state",
    "node_modules", "__pycache__", ".venv", "venv", ".pytest_cache", ".obsidian",
}
# Engine-only surfaces. Skipped ONLY when this folder actually carries the
# engine (clone, curl, ZIP) - on a data-folder install these names belong to
# the founder, and skipping them unconditionally is how a project named "docs"
# vanished from the answer (a v1.53.0 review finding). On a full install a
# founder project with one of these names genuinely cannot be told apart from
# the engine's own folder; that boundary is documented, not hidden.
ENGINE_DIRS = {"skills", "templates", "tests", "docs", "updates", "notion-package"}
# The brain and the operating files are the OS working normally, not a project.
# They are summarised in one line at the end rather than listed file by file.
OS_CONTENT_DIRS = {"brain", "core", "context", "cadence", "rules", "roles",
                   "system", "memory", "capture", "raw", "clients", "companies",
                   "network", "brands"}
SKIP_FILES = {".DS_Store", "Thumbs.db", ".gitignore", ".gitattributes"}

# Scan budget: a founder's folder can contain anything (a mounted drive, an
# extracted archive). Answering partially and saying so beats hanging.
MAX_SECONDS = 5.0
MAX_ENTRIES = 50_000

ROOT_FILES = "(files at the folder root)"


def _git(root: Path, *args: str) -> subprocess.CompletedProcess | None:
    """One guarded git call. None on any failure - no git, not a repo, timeout."""
    try:
        out = subprocess.run(["git", "-C", str(root), *args],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out if out.returncode == 0 else None


def _git_state(root: Path) -> dict | None:
    """What version history actually holds, or None when there is none.

    Returns top-level names committed in HEAD, top-level names with pending
    changes, and whether the current commit provably exists on a remote copy.
    The OS folder is not always the repository top level (it can live inside a
    bigger repo), and git's two listing commands disagree about what a path is
    relative to: ls-tree run in a subdirectory scopes itself there and answers
    cwd-relative, while status --porcelain always answers toplevel-relative.
    Only the second needs re-basing onto this folder."""
    top = _git(root, "rev-parse", "--show-toplevel")
    if top is None:
        return None
    prefix_out = _git(root, "rev-parse", "--show-prefix")
    prefix = prefix_out.stdout.strip() if prefix_out else ""

    def local(path: str) -> str | None:
        if not prefix:
            return path
        return path[len(prefix):] if path.startswith(prefix) else None

    in_history: set[str] = set()
    head = _git(root, "ls-tree", "-r", "--name-only", "HEAD")
    if head:  # a repo with no commits yet has no HEAD - nothing is in history
        for line in head.stdout.splitlines():
            line = line.strip()
            if line:
                in_history.add(line.split("/", 1)[0])

    dirty: set[str] = set()
    porcelain = _git(root, "status", "--porcelain")
    if porcelain:
        for line in porcelain.stdout.splitlines():
            if len(line) < 4:
                continue
            path = line[3:].strip().strip('"')
            if " -> " in path:
                path = path.split(" -> ", 1)[1].strip().strip('"')
            rel = local(path)
            if rel:
                dirty.add(rel.rstrip("/").split("/", 1)[0])

    remote_has_head = False
    refs = _git(root, "for-each-ref", "--format=%(refname)", "refs/remotes")
    if refs:
        for ref in refs.stdout.splitlines():
            ref = ref.strip()
            if not ref or ref.endswith("/HEAD"):
                continue
            if _git(root, "merge-base", "--is-ancestor", "HEAD", ref) is not None:
                remote_has_head = True
                break

    return {"in_history": in_history, "dirty": dirty,
            "remote_has_head": remote_has_head}


def _backup_state(name: str, git: dict | None) -> str:
    """One of five honest answers about a folder's second copy."""
    if git is None:
        return "no-history"    # this install has no version history at all
    if name not in git["in_history"]:
        return "not-saved"     # never committed - the working folder is the only copy
    if name in git["dirty"]:
        return "stale-save"    # an older version is saved; today's changes exist only here
    if git["remote_has_head"]:
        return "second-copy"   # committed, clean, and a synced remote holds the commit
    return "local-only"        # committed and clean, but no copy exists off this machine


def _walk(root: Path, engine_here: bool, query_terms: list[str]) -> tuple[dict, bool]:
    """One budgeted pass over the install.
    Returns ({top-level name: {files, newest, ...}}, partial)."""
    groups: dict[str, dict] = {}
    skip_dirs = MACHINERY_DIRS | (ENGINE_DIRS if engine_here else set())
    deadline = time.monotonic() + MAX_SECONDS
    seen = 0
    partial = False
    for dirpath, dirnames, filenames in os.walk(root):
        if partial or time.monotonic() > deadline or seen > MAX_ENTRIES:
            partial = True
            break
        dirnames[:] = [d for d in dirnames
                       if d not in skip_dirs and not d.startswith(".")]
        rel = Path(dirpath).relative_to(root)
        top = rel.parts[0] if rel.parts else ROOT_FILES
        if top in skip_dirs:
            continue
        for name in filenames:
            seen += 1
            # the cap has to fire inside one directory too - a single folder
            # holding fifty thousand files is exactly the hang this prevents
            if seen > MAX_ENTRIES or time.monotonic() > deadline:
                partial = True
                break
            if name in SKIP_FILES or name.startswith("."):
                continue
            try:
                mtime = (Path(dirpath) / name).stat().st_mtime
            except OSError:
                continue
            g = groups.setdefault(top, {"files": 0, "newest": 0.0, "newest_file": "",
                                        "deepest": "", "match": ""})
            g["files"] += 1
            rel_file = (Path(dirpath) / name).relative_to(root).as_posix()
            if mtime > g["newest"]:
                g["newest"] = mtime
                # forward slashes always: a founder copying a path into Explorer,
                # Finder or a chat should get the same string on every machine
                g["newest_file"] = rel_file
            if query_terms and not g["match"]:
                hay = rel_file.lower()
                if all(t in hay for t in query_terms):
                    g["match"] = rel_file
            # the folder a founder would actually name, one level in
            if len(rel.parts) > 1 and not g["deepest"]:
                g["deepest"] = Path(*rel.parts[:2]).as_posix() + "/"
    return groups, partial


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


def collect(root: Path, days: int | None, query: str = "") -> dict:
    git = _git_state(root)
    engine_here = (root / ".claude-plugin").is_dir() or (root / "skills" / "index.md").is_file()
    query_terms = [t.lower() for t in query.split() if t.strip()]
    groups, partial = _walk(root, engine_here, query_terms)
    now = time.time()
    cutoff = 0.0 if days is None else now - days * 86400

    projects, os_own = [], []
    for name, g in groups.items():
        if g["newest"] < cutoff:
            continue
        row = {
            "name": name,
            "folder": "./" if name == ROOT_FILES else name + "/",
            "files": g["files"],
            "age": _age(now - g["newest"]),
            "newest_file": g["newest_file"],
            "sub": g["deepest"],
            "backup": _backup_state(name, git),
            "match": g["match"],
        }
        is_os = name in OS_CONTENT_DIRS or name == ROOT_FILES
        (os_own if is_os else projects).append(row)

    projects.sort(key=lambda r: (not r["match"], -groups[r["name"]]["newest"]))
    os_own.sort(key=lambda r: -groups[r["name"]]["newest"])
    return {"root": str(root), "has_git": git is not None, "days": days,
            "query": query, "partial": partial,
            "projects": projects, "os_own": os_own}


BACKUP_LINES = {
    "not-saved": ["    NOT BACKED UP. This exists only on this computer. If the",
                  "    laptop dies or the folder is deleted, it is gone."],
    "no-history": ["    Backup unknown - this install has no version history yet."],
    "stale-save": ["    An older version is saved. Today's changes exist only here",
                   "    until the next save runs."],
    "local-only": ["    Saved in version history on this computer. No copy exists",
                   "    anywhere else yet."],
    "second-copy": ["    Backed up. A second copy exists away from this computer."],
}


def render(data: dict) -> str:
    out: list[str] = []
    window = ("everything, however old" if data["days"] is None
              else f"the last {data['days']} days")
    out.append(f"YOUR WORK - {window}, most recent first")
    if data.get("partial"):
        out.append("  (This folder is very large, so the scan stopped early -")
        out.append("  what follows is what it saw, not everything.)")
    out.append("")

    if data.get("query"):
        matches = [p for p in data["projects"] if p["match"]]
        if matches:
            out.append(f"MATCHES '{data['query']}'")
            for p in matches:
                out.append(f"  {p['name']} - {p['match']}")
            out.append("")
        else:
            out.append(f"  Nothing here matches '{data['query']}' by file name.")
            out.append("  Names do not always match content - everything recent is below.")
            out.append("")

    if not data["projects"]:
        out.append("  No project folders changed in this window.")
        out.append("  Try: python scripts/where.py --all")
    for p in data["projects"]:
        label = p["sub"] or p["folder"]
        out.append(f"  {p['name']}   (worked on {p['age']})")
        out.append(f"    Folder:  {label}")
        out.append(f"    {p['files']} file(s). Most recent: {p['newest_file']}")
        out.extend(BACKUP_LINES[p["backup"]])
        out.append("")

    if data["os_own"]:
        names = ", ".join(r["name"] for r in data["os_own"][:6])
        newest = data["os_own"][0]["age"]
        out.append(f"  Your OS files (notes, clients, the week) changed {newest}: {names}")
        out.append("")

    unsafe = [p["name"] for p in data["projects"] if p["backup"] == "not-saved"]
    stale = [p["name"] for p in data["projects"] if p["backup"] == "stale-save"]
    local = [p["name"] for p in data["projects"] if p["backup"] == "local-only"]
    if unsafe:
        out.append("WORTH KNOWING")
        out.append(f"  {len(unsafe)} folder(s) have no backup: " + ", ".join(unsafe))
        out.append("  Say \"back up my work\" and the OS will walk you through it.")
    elif data["has_git"] is False:
        out.append("WORTH KNOWING")
        out.append("  This install has no version history, so nothing here has a")
        out.append("  second copy. Say \"back up my work\" to fix that once.")
    elif stale or local:
        out.append("WORTH KNOWING")
        if stale:
            out.append(f"  {len(stale)} folder(s) have unsaved changes from today: "
                       + ", ".join(stale))
            out.append("  Say \"save my work\" to record them.")
        if local:
            out.append(f"  {len(local)} folder(s) are saved on this computer only: "
                       + ", ".join(local))
            out.append("  Say \"back up my work\" to put a copy somewhere else.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Where your recent work actually lives, in plain language.")
    p.add_argument("query", nargs="*", default=[],
                   help="words to look for in folder and file names")
    p.add_argument("--days", type=int, default=14)
    p.add_argument("--all", action="store_true", help="every folder, no time window")
    p.add_argument("--root", default=str(REPO_ROOT))
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    data = collect(Path(a.root), None if a.all else a.days, " ".join(a.query))
    print(json.dumps(data, ensure_ascii=True, indent=2) if a.json else render(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
