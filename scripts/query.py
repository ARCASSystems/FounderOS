#!/usr/bin/env python3
"""Plain-file query helper for Founder OS."""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Iterable

EDGE_TYPES = {"from", "to", "source", "target"}
DEFAULT_FILES = [
    "CLAUDE.md",
    "core/identity.md",
    "context/priorities.md",
    "context/decisions.md",
    "rules/operating-rules.md",
    "brain/patterns.md",
    "brain/flags.md",
    "brain/relations.yaml",
]
EXCLUDED_PARTS = {
    ".git",
    ".claude",
    "skills",
    "docs",
    "raw",
    "node_modules",
    "archive",
    "transcripts",
    "rants",
}


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_-]+", text)]


def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def should_scan(path: Path, root: Path) -> bool:
    parts = set(path.relative_to(root).parts)
    if parts & EXCLUDED_PARTS:
        return False
    return path.suffix.lower() in {".md", ".yaml", ".yml"}


def candidate_files(root: Path) -> list[Path]:
    specific = [root / p for p in DEFAULT_FILES if (root / p).exists()]
    if specific:
        extra = []
        for dirname in ["brain/knowledge", "companies", "network"]:
            folder = root / dirname
            if folder.exists():
                extra.extend(p for p in folder.rglob("*.md") if should_scan(p, root))
        return sorted(set(specific + extra))
    return sorted(p for p in root.rglob("*") if p.is_file() and should_scan(p, root))


def heading_or_match(text: str, tokens: set[str]) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("# ")[:140]
    for line in text.splitlines():
        low = line.lower()
        if any(t in low for t in tokens):
            return line.strip()[:140]
    return "Relevant OS node"


def parse_edges(relations_text: str) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    current: dict[str, str] = {}
    for raw in relations_text.splitlines():
        line = raw.strip()
        match = re.match(r"(?:-\s+)?(from|to|source|target):\s*(.+)$", line)
        if not match:
            continue
        key, value = match.groups()
        value = value.strip().strip('"\'')
        if key in {"from", "source"}:
            if current:
                current = {}
            current["from"] = value
        elif key in {"to", "target"}:
            current["to"] = value
        if "from" in current and "to" in current:
            edges.append((current["from"], current["to"]))
            current = {}
    return edges


def wikilink_edges(files: Iterable[Path], root: Path) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    pattern = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
    for path in files:
        text = safe_read(path)
        source = rel(path, root)
        for target in pattern.findall(text):
            edges.append((source, target.strip()))
    return edges


def build_graph(edges: Iterable[tuple[str, str]]) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    for a, b in edges:
        if not a or not b:
            continue
        graph[a].add(b)
        graph[b].add(a)
    return graph


def score_files(files: Iterable[Path], root: Path, question_tokens: set[str]) -> dict[str, tuple[int, str]]:
    scores: dict[str, tuple[int, str]] = {}
    for path in files:
        text = safe_read(path)
        node = rel(path, root)
        words = Counter(tokenize(node + "\n" + text[:12000]))
        score = sum(words[t] for t in question_tokens)
        if score:
            score += sum(2 for t in question_tokens if t in node.lower())
        context = heading_or_match(text, question_tokens)
        scores[node] = (score, context)
    return scores


def traverse(starts: list[str], graph: dict[str, set[str]], limit: int = 3) -> dict[str, str]:
    paths: dict[str, str] = {}
    queue = deque((s, [s], 0) for s in starts)
    seen = set(starts)
    while queue:
        node, path, depth = queue.popleft()
        paths.setdefault(node, " -> ".join(path))
        if depth >= limit:
            continue
        for nxt in sorted(graph.get(node, [])):
            if nxt in seen:
                continue
            seen.add(nxt)
            queue.append((nxt, path + [nxt], depth + 1))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Query Founder OS markdown graph")
    parser.add_argument("question", nargs="*", help="Question to query")
    parser.add_argument("--root", default=".", help="Founder OS root")
    args = parser.parse_args()

    question = " ".join(args.question).strip()
    if not question:
        print("Usage: python scripts/query.py <question>")
        return 2

    root = Path(args.root).resolve()
    files = candidate_files(root)
    if not files:
        print(f"QUERY: {question}\n---\nTop results:\n\nNo markdown files found under {root}.")
        return 1

    q_tokens = set(tokenize(question))
    file_scores = score_files(files, root, q_tokens)

    relations_path = root / "brain" / "relations.yaml"
    relation_edges = parse_edges(safe_read(relations_path)) if relations_path.exists() else []
    all_edges = relation_edges + wikilink_edges(files, root)
    graph = build_graph(all_edges)

    ranked = sorted(
        file_scores.items(),
        key=lambda item: (item[1][0], len(graph.get(item[0], set())), item[0]),
        reverse=True,
    )
    starts = [node for node, (score, _) in ranked if score > 0][:5]
    if not starts:
        starts = [node for node, _ in ranked[:5]]

    paths = traverse(starts, graph, 3)
    combined = []
    for node, (score, context) in ranked:
        edge_bonus = len(graph.get(node, set()))
        path = paths.get(node)
        if score == 0 and not path and len(combined) >= 3:
            continue
        combined.append((score + edge_bonus, node, context, path or node))

    combined.sort(key=lambda item: (item[0], item[1]), reverse=True)
    top = combined[:5]

    print(f"QUERY: {question}")
    print("---")
    print("Top results:\n")
    for idx, (_, node, context, path) in enumerate(top, 1):
        print(f"{idx}. {node} - {context} - reached via: {path}")
    if top:
        print(f"\nRecommend reading: {top[0][1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
