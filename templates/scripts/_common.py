"""
Canonical wiki-layer scope helpers shared by scripts/wiki-build.py and
scripts/query.py.

Both scripts must agree on which markdown files compose the wiki-layer
graph; before this module existed, they computed that set via two different
mechanisms (prefix-string startswith vs part-set intersection), coupled only
by manual "also update" comments that no test enforced. Drift between the
two produces silent disagreement between the on-disk graph (relations.yaml)
and the in-memory graph (query). Defining the scope here once eliminates
the drift class.

Pure stdlib. No new install dependency - the free-tier accessibility floor
stays intact. See plans/v1.27-f38-rglob-consolidation-2026-05-22.md.
"""

from __future__ import annotations

from pathlib import Path


WIKI_LAYER_PREFIXES: tuple[str, ...] = (
    "core",
    "context",
    "cadence",
    "brain",
    "network",
    "companies",
    "roles",
    "rules",
)

WIKI_LAYER_EXCLUDED_PARTS: frozenset[str] = frozenset({
    ".git",
    ".claude",
    "skills",
    "docs",
    "raw",
    "templates",
    "node_modules",
    "archive",
    "transcripts",
    "rants",
    "tests",
    "__pycache__",
})


def is_wiki_layer_path(rel_path: str, include_rants: bool = False) -> bool:
    """True iff a forward-slash relative path is in the wiki-layer graph scope.

    The first segment must be one of WIKI_LAYER_PREFIXES, and no segment may
    appear in WIKI_LAYER_EXCLUDED_PARTS. When include_rants is True, "rants"
    is dropped from the excluded set so brain/rants/ files can pass.

    Caller is responsible for forward-slash normalisation; a literal-backslash
    string like "brain\\log.md" is not normalised and returns False.
    """
    parts = rel_path.split("/")
    if not parts or parts[0] not in WIKI_LAYER_PREFIXES:
        return False
    excluded = WIKI_LAYER_EXCLUDED_PARTS - {"rants"} if include_rants else WIKI_LAYER_EXCLUDED_PARTS
    if any(p in excluded for p in parts):
        return False
    return True


def wiki_layer_files(root: Path, include_rants: bool = False) -> list[Path]:
    """All wiki-layer .md files under root, deterministically sorted.

    Walks each prefix folder via rglob and filters with is_wiki_layer_path.
    Does NOT include CLAUDE.md or other DEFAULT_FILES - those are query-local
    score seeds, not graph edges. Does NOT include .yaml/.yml - only .md.
    """
    found: set[Path] = set()
    for prefix in WIKI_LAYER_PREFIXES:
        folder = root / prefix
        if not folder.exists():
            continue
        for path in folder.rglob("*.md"):
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError:
                continue
            if is_wiki_layer_path(rel, include_rants=include_rants):
                found.add(path)
    return sorted(found)


def normalize_wikilink_target(target: str) -> str:
    """Canonicalise a wikilink target so [[file]] and [[file.md]] dedupe.

    Converts backslashes to forward slashes, strips a trailing .md from the
    path part (preserving any #anchor suffix). Does not lowercase: preserves
    the user's display intent. Bare slugs pass through unchanged.
    """
    target = target.replace("\\", "/").strip()
    if "#" in target:
        path, _, anchor = target.partition("#")
        if path.endswith(".md"):
            path = path[:-3]
        return f"{path}#{anchor}" if anchor else path
    if target.endswith(".md"):
        return target[:-3]
    return target
