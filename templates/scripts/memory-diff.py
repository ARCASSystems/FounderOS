#!/usr/bin/env python3
"""Memory/Retrieval Fabric helper.

Closes the cross-session gap where a cloud or parallel local Claude session
creates a client folder under `clients/<slug>/` (with intel, prep, deliverables)
but the next local session boots blind to it because MEMORY.md does not
auto-populate from filesystem changes.

Strategy: walk `clients/*/`, check each slug against the auto-memory index and
the per-file project memories. If a client folder exists with no memory mention,
surface it in the session brief so the operator knows to write one.

Read-only. Stdlib only. Fails silent. Designed to be invoked from
.claude/hooks/session-start-brief.{sh,ps1}.

Usage:
    python scripts/memory-diff.py [REPO_ROOT]

Exits 0 in all cases. Prints nothing if everything is covered.
"""

import os
import re
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    """Walk up to find a repo root with CLAUDE.md AND clients/ folder."""
    cur = start.resolve()
    for _ in range(8):
        if (cur / "CLAUDE.md").exists() and (cur / "clients").is_dir():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start.resolve()


def _slug_matches_founder_os(slug: str) -> bool:
    """True if a project slug under ~/.claude/projects/ looks like a Founder OS install.

    Claude Code encodes the working directory as the slug, replacing path
    separators with hyphens. Common shapes:
      - Mac/Linux: `Users-jane-founder-os` (working dir `/Users/jane/founder-os`)
      - Windows:   `c--Users-Jane-founder-os` (working dir `C:\\Users\\Jane\\founder-os`)
      - Folder-renamed installs without a hyphen: `Users-jane-founderos`

    Match logic: lowercase the slug, strip hyphens and underscores, then
    look for the literal substring `founderos`. That covers both the
    hyphenated and non-hyphenated folder names without false-positives on
    unrelated projects.
    """
    normalized = slug.lower().replace("-", "").replace("_", "")
    return "founderos" in normalized


def find_memory_dir() -> Path | None:
    """Find the auto-memory dir for the current repo's project slug.

    Claude Code stores per-project memory at ~/.claude/projects/<slug>/memory/.
    The slug encodes the absolute path, so we cannot derive it from the repo
    path alone reliably. Heuristic: pick the project dir whose normalized slug
    contains `founderos` (case-insensitive, hyphens and underscores ignored).
    Caller can override the auto-detection by passing the path as the first
    argument to the script if the heuristic fails.
    """
    home = Path(os.path.expanduser("~"))
    projects_dir = home / ".claude" / "projects"
    if not projects_dir.is_dir():
        return None

    for child in sorted(projects_dir.iterdir()):
        if not child.is_dir():
            continue
        if not _slug_matches_founder_os(child.name):
            continue
        memory_dir = child / "memory"
        if (memory_dir / "MEMORY.md").is_file():
            return memory_dir
    return None


def list_active_clients(repo: Path) -> list[str]:
    """Return sorted list of clients/<slug>/ directories with content."""
    clients_dir = repo / "clients"
    if not clients_dir.is_dir():
        return []
    out = []
    for child in sorted(clients_dir.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            continue
        # Skip empty directories (no useful content to flag)
        if not any(child.iterdir()):
            continue
        out.append(child.name)
    return out


def slug_tokens(slug: str) -> list[str]:
    """Split slug into searchable tokens. 'jane-doe' -> ['jane-doe', 'jane']."""
    norm = slug.lower().replace("_", "-")
    parts = [p for p in norm.split("-") if p]
    tokens = [norm]
    if parts and parts[0] not in tokens:
        tokens.append(parts[0])
    return tokens


def is_slug_covered(slug: str, memory_text: str, memory_dir: Path) -> bool:
    """Permissive multi-strategy match. False-negative beats false-positive in a session brief."""
    tokens = slug_tokens(slug)
    memory_lower = memory_text.lower()

    # Strategy 1: any token appears in MEMORY.md index text.
    for token in tokens:
        if token in memory_lower:
            return True

    # Strategy 2: any token appears in a project_*.md filename or content.
    project_files = list(memory_dir.glob("project_*.md"))
    for f in project_files:
        name_lower = f.name.lower()
        for token in tokens:
            if token in name_lower:
                return True
        try:
            content = f.read_text(encoding="utf-8", errors="replace").lower()
        except OSError:
            continue
        for token in tokens:
            if re.search(rf"\b{re.escape(token)}\b", content):
                return True

    return False


def main() -> int:
    if len(sys.argv) > 1:
        repo = Path(sys.argv[1]).resolve()
    else:
        repo = find_repo_root(Path.cwd())

    if not (repo / "clients").is_dir():
        return 0

    memory_dir = find_memory_dir()
    if memory_dir is None:
        return 0

    memory_md = memory_dir / "MEMORY.md"
    try:
        memory_text = memory_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0

    clients = list_active_clients(repo)
    if not clients:
        return 0

    uncovered = [s for s in clients if not is_slug_covered(s, memory_text, memory_dir)]
    if not uncovered:
        return 0

    print()
    print(f"Active client folders without memory entry ({len(uncovered)}):")
    for slug in uncovered[:5]:
        print(f"  - clients/{slug}/")
    if len(uncovered) > 5:
        print(f"  ...and {len(uncovered) - 5} more")
    print(
        "  (write project_<slug>.md in your auto-memory dir so the next session boots aware)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
