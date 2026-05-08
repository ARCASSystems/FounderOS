#!/usr/bin/env python3
"""Plain-file query helper for Founder OS."""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict, deque
from datetime import date, datetime, timedelta
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
# Wiki-layer scope. Must match scripts/wiki-build.py:INCLUDE_PREFIXES so a node
# the persisted graph references can also surface as a query candidate. Drift
# between these two lists means a query can miss content the graph already
# knows about. Update both files together if you change scope.
INCLUDE_PREFIXES = (
    "core",
    "context",
    "cadence",
    "brain",
    "network",
    "companies",
    "roles",
    "rules",
)
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
    "tests",
}

# Mode caps and per-hit budgets.
INDEX_HIT_CAP = 10
INDEX_CONTEXT_CHARS = 200
TIMELINE_HIT_CAP = 20
TIMELINE_BODY_CHARS = 600
TIMELINE_WINDOW_DAYS = 7


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
    try:
        parts = set(path.relative_to(root).parts)
    except ValueError:
        return False
    if parts & EXCLUDED_PARTS:
        return False
    return path.suffix.lower() in {".md", ".yaml", ".yml"}


def all_markdown_files(root: Path) -> list[Path]:
    """All in-scope markdown/yaml files under root, used by timeline and full modes."""
    return sorted(p for p in root.rglob("*") if p.is_file() and should_scan(p, root))


def candidate_files(root: Path) -> list[Path]:
    """All in-scope wiki-layer files. Walks every prefix in INCLUDE_PREFIXES so
    a node the persisted graph references can also surface as a query
    candidate. DEFAULT_FILES are listed first so the canonical seeded files
    lead the index. Falls back to all in-scope markdown if neither survives.
    """
    specific = [root / p for p in DEFAULT_FILES if (root / p).exists()]
    extra: list[Path] = []
    for prefix in INCLUDE_PREFIXES:
        folder = root / prefix
        if folder.exists():
            extra.extend(p for p in folder.rglob("*.md") if should_scan(p, root))
    combined = sorted(set(specific + extra))
    if combined:
        return combined
    return all_markdown_files(root)


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


def first_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("# ").strip()[:140]
    return ""


ID_PATTERN = re.compile(r"\b(log|pattern|flag|parked|need|know)-\d{4}-\d{2}-\d{2}-\d{3}\b")
ID_LINE_PATTERN = re.compile(r"^\s*id:\s*((?:log|pattern|flag|parked|need|know)-\d{4}-\d{2}-\d{2}-\d{3})\s*$")
ID_DATE_PATTERN = re.compile(r"-(\d{4})-(\d{2})-(\d{2})-\d{3}$")
DECAY_LINE_PATTERN = re.compile(r"^\s*decay_after:\s*(\S+)", re.IGNORECASE)
FRONTMATTER_DATE_PATTERN = re.compile(r"^\s*(updated|date):\s*(\S+)", re.IGNORECASE)


def top_entry_id(text: str) -> str | None:
    """Return the ID of the first (top-most) entry in the file.

    For brain files using the newest-at-top convention this is the most
    recent entry's ID. Scans for an `id: <id>` frontmatter line first, then
    falls back to a trailing parenthetical ID on a heading or list line.
    Returns None if no ID convention match is present.
    """
    for line in text.splitlines():
        match = ID_LINE_PATTERN.match(line)
        if match:
            return match.group(1)
    match = ID_PATTERN.search(text)
    if match:
        return match.group(0)
    return None


def parse_date_str(value: str) -> date | None:
    """Parse a YYYY-MM-DD string into a date. Returns None if invalid."""
    value = value.strip().strip('"\'')
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def date_from_id(entry_id: str) -> date | None:
    """Extract YYYY-MM-DD date from a brain ID like log-2026-05-07-001."""
    match = ID_DATE_PATTERN.search(entry_id)
    if not match:
        return None
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def file_date(path: Path, text: str | None = None) -> date | None:
    """Best-effort date for a file: frontmatter updated/date, then mtime."""
    if text is None:
        text = safe_read(path)
    in_fm = False
    fm_seen = 0
    for line in text.splitlines()[:40]:
        stripped = line.strip()
        if stripped == "---":
            fm_seen += 1
            in_fm = fm_seen == 1
            if fm_seen >= 2:
                break
            continue
        if in_fm:
            match = FRONTMATTER_DATE_PATTERN.match(line)
            if match:
                parsed = parse_date_str(match.group(2))
                if parsed:
                    return parsed
    try:
        return date.fromtimestamp(path.stat().st_mtime)
    except OSError:
        return None


def decay_flag(text: str) -> str | None:
    """Return a short decay marker if the file has a decay_after that is past or imminent."""
    today = date.today()
    for line in text.splitlines()[:40]:
        match = DECAY_LINE_PATTERN.match(line)
        if not match:
            continue
        parsed = parse_date_str(match.group(1))
        if not parsed:
            return None
        if parsed < today:
            return f"DECAY (past {parsed.isoformat()})"
        if parsed - today <= timedelta(days=7):
            return f"DECAY soon ({parsed.isoformat()})"
        return None
    return None


def parse_edges(relations_text: str) -> list[tuple[str, str]]:
    """Parse edges out of brain/relations.yaml.

    Supports three shapes that coexist in the file:
      1. Flat curated entries under `relations:` -- `- source: a` / `target: b`
         or `- from: a` / `to: b`.
      2. The auto-generated `wiki_links:` block written by
         scripts/wiki-build.py, which uses `- source: a` followed by
         `targets:` and a nested list of quoted target strings.
      3. Both, in the same file.

    Stdlib only. No PyYAML dependency.
    """
    edges: list[tuple[str, str]] = []
    pending: dict[str, str] = {}
    current_source: str | None = None
    in_targets_block = False
    # Quoted form is what scripts/wiki-build.py emits and is always a target,
    # even if the inner value happens to start with `source:` or `target:`.
    target_quoted_re = re.compile(r'^\s+-\s+(["\'])(.*)\1\s*$')
    # Unquoted form -- a hand-written list item in YAML.
    target_unquoted_re = re.compile(r'^\s+-\s+([^"\'\s].*?)\s*$')
    flat_key_re = re.compile(r'^(from|to|source|target):\s')

    for raw in relations_text.splitlines():
        # Inside a `targets:` list, each `- "name"` (quoted) or `- name`
        # (unquoted) is one edge target for the most recent source. A
        # `- source:` boundary ends the block. Quoted values are always
        # treated as targets; only unquoted values can signal a record
        # boundary by matching the flat-key pattern.
        if in_targets_block:
            quoted = target_quoted_re.match(raw)
            if quoted:
                # Only the matching quote needs un-escaping. scripts/wiki-build.py
                # emits double-quoted targets and escapes an inner `"` as `\"`,
                # so a `"` quote unescapes `\"`. A hand-written single-quoted
                # target may use `\'` for an inner apostrophe, so a `'` quote
                # unescapes `\'`. Crossing the two would corrupt literal
                # backslashes in the other shape (e.g. `'foo\"bar'` should
                # round-trip as `foo\"bar`, not `foo"bar`).
                quote_char = quoted.group(1)
                inner = quoted.group(2)
                if quote_char == '"':
                    target = inner.replace('\\"', '"')
                else:
                    target = inner.replace("\\'", "'")
                if current_source and target:
                    edges.append((current_source, target))
                continue
            unquoted = target_unquoted_re.match(raw)
            if unquoted:
                candidate = unquoted.group(1).strip()
                if flat_key_re.match(candidate):
                    in_targets_block = False  # fall through to flat handling
                else:
                    if current_source and candidate:
                        edges.append((current_source, candidate))
                    continue
            else:
                in_targets_block = False  # fall through to flat handling

        line = raw.strip()
        if line == 'targets:':
            in_targets_block = True
            continue

        match = re.match(r"(?:-\s+)?(from|to|source|target):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.groups()
        value = value.strip().strip('"\'')

        if key in {"from", "source"}:
            if pending:
                pending = {}
            pending["from"] = value
            current_source = value if key == "source" else None
        elif key in {"to", "target"}:
            pending["to"] = value

        if "from" in pending and "to" in pending:
            edges.append((pending["from"], pending["to"]))
            pending = {}
    return edges


def wikilink_edges(files: Iterable[Path], root: Path) -> list[tuple[str, str]]:
    """Extract [[wikilinks]] and produce (source, target) edges.

    Targets are normalized (trailing .md stripped, backslashes converted) so
    edges agree with the persisted graph in brain/relations.yaml. See
    scripts/wiki-build.py:normalize_target.
    """
    edges: list[tuple[str, str]] = []
    pattern = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
    for path in files:
        text = safe_read(path)
        source = rel(path, root)
        for target in pattern.findall(text):
            normalized = target.replace('\\', '/').strip()
            if normalized.endswith('.md'):
                normalized = normalized[:-3]
            if normalized:
                edges.append((source, normalized))
    return edges


def build_graph(edges: Iterable[tuple[str, str]]) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    for a, b in edges:
        if not a or not b:
            continue
        graph[a].add(b)
        graph[b].add(a)
    return graph


def score_files(files: Iterable[Path], root: Path, question_tokens: set[str]) -> dict[str, tuple[int, str, str | None]]:
    scores: dict[str, tuple[int, str, str | None]] = {}
    for path in files:
        text = safe_read(path)
        node = rel(path, root)
        words = Counter(tokenize(node + "\n" + text[:12000]))
        score = sum(words[t] for t in question_tokens)
        if score:
            score += sum(2 for t in question_tokens if t in node.lower())
        context = heading_or_match(text, question_tokens)
        entry_id = top_entry_id(text)
        scores[node] = (score, context, entry_id)
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


# ---------- Mode: index ----------


def run_index_mode(question: str, root: Path) -> int:
    files = candidate_files(root)
    if not files:
        print(f"QUERY: {question}\n---\nTop results:\n\nNo markdown files found under {root}.")
        return 1

    q_tokens = set(tokenize(question))
    if not q_tokens:
        print(
            f"QUERY: {question}\n---\nNo searchable tokens in the question. "
            "Try a question with at least one word or identifier (e.g. 'what blocks the launch?')."
        )
        return 2
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
    starts = [node for node, (score, _, _) in ranked if score > 0][:5]
    if not starts:
        starts = [node for node, _ in ranked[:5]]

    paths = traverse(starts, graph, 3)
    combined = []
    for node, (score, context, entry_id) in ranked:
        edge_bonus = len(graph.get(node, set()))
        path = paths.get(node)
        if score == 0 and not path and len(combined) >= 3:
            continue
        combined.append((score + edge_bonus, node, context, path or node, entry_id))

    combined.sort(key=lambda item: (item[0], item[1]), reverse=True)
    top = combined[:INDEX_HIT_CAP]

    print(f"QUERY: {question}")
    print("---")
    print("Top results:\n")
    for idx, (_, node, context, path, entry_id) in enumerate(top, 1):
        text = safe_read(root / node) if (root / node).exists() else ""
        decay = decay_flag(text) if text else None
        id_part = f" (id: {entry_id})" if entry_id else ""
        decay_part = f" [{decay}]" if decay else ""
        trimmed_context = context[:INDEX_CONTEXT_CHARS]
        print(f"{idx}. {node}{id_part}{decay_part} - {trimmed_context} - reached via: {path}")
    if top:
        print(f"\nRecommend reading: {top[0][1]}")
    return 0


# ---------- Mode: timeline ----------


def find_anchor_file(anchor: str, root: Path) -> Path | None:
    """Resolve anchor (slug or path) to an actual file under root."""
    candidate = root / anchor
    if candidate.is_file():
        return candidate
    matches = [p for p in all_markdown_files(root) if rel(p, root) == anchor]
    if matches:
        return matches[0]
    base = anchor.lower()
    for p in all_markdown_files(root):
        if p.name.lower() == base or p.stem.lower() == base:
            return p
    return None


def find_id_in_corpus(entry_id: str, root: Path) -> Path | None:
    """Find the file in the corpus that defines entry_id.

    Structured match against frontmatter `id:` line OR heading trailing-paren -
    not a substring search. A plain prose mention or wikilink containing the
    ID does not count as a definition and is ignored, so cross-references in
    other files cannot cause wrong-file attribution.
    """
    fm_pattern = re.compile(rf"^\s*id:\s*{re.escape(entry_id)}\s*$")
    heading_with_id = re.compile(rf"^#+\s+.*\(\s*{re.escape(entry_id)}\s*\)\s*$")
    for p in all_markdown_files(root):
        text = safe_read(p)
        if entry_id not in text:
            continue
        for line in text.splitlines():
            if fm_pattern.match(line) or heading_with_id.match(line):
                return p
    return None


def anchor_date(anchor: str, root: Path) -> tuple[date | None, Path | None]:
    """Resolve anchor to a (date, path) pair. Path may be None for ID anchors with no file match."""
    match = ID_PATTERN.search(anchor)
    if match:
        entry_id = match.group(0)
        d = date_from_id(entry_id)
        path = find_id_in_corpus(entry_id, root)
        return d, path
    path = find_anchor_file(anchor, root)
    if not path:
        return None, None
    d = file_date(path)
    return d, path


def run_timeline_mode(anchor: str, root: Path) -> int:
    if not anchor:
        print("Usage: python scripts/query.py --mode timeline --anchor <slug-or-id>")
        return 2
    a_date, a_path = anchor_date(anchor, root)
    if a_date is None:
        print(f"timeline: anchor not found or undated: {anchor}")
        return 1

    window_start = a_date - timedelta(days=TIMELINE_WINDOW_DAYS)
    window_end = a_date + timedelta(days=TIMELINE_WINDOW_DAYS)

    entries: list[tuple[date, str, str, str | None, str]] = []
    for path in all_markdown_files(root):
        text = safe_read(path)
        d = file_date(path, text)
        if d is None:
            continue
        if d < window_start or d > window_end:
            continue
        node = rel(path, root)
        heading = first_heading(text) or node
        entry_id = top_entry_id(text)
        body = text.strip()
        if len(body) > TIMELINE_BODY_CHARS:
            body = body[:TIMELINE_BODY_CHARS].rstrip() + "..."
        entries.append((d, node, heading, entry_id, body))

    entries.sort(key=lambda item: (item[0], item[1]))
    entries = entries[:TIMELINE_HIT_CAP]

    anchor_label = rel(a_path, root) if a_path else anchor
    print(f"TIMELINE: {anchor_label} ({a_date.isoformat()}) +/- {TIMELINE_WINDOW_DAYS} days")
    print("---")
    if not entries:
        print("No entries found in window.")
        return 0
    for d, node, heading, entry_id, body in entries:
        id_part = f" (id: {entry_id})" if entry_id else ""
        print(f"\n{d.isoformat()} - {node}{id_part}")
        print(f"  {heading}")
        for line in body.splitlines()[:6]:
            print(f"  {line}")
    return 0


# ---------- Mode: full ----------


HEADING_PATTERN = re.compile(r"^(#+)\s+")


def heading_level(line: str) -> int | None:
    match = HEADING_PATTERN.match(line)
    if not match:
        return None
    return len(match.group(1))


def extract_full_block(text: str, entry_id: str) -> str | None:
    """Return the body block matching entry_id within text.

    Match modes (structured only - prose-only references are ignored):
      1. Heading line ending with `(<id>)`: return that heading and all
         lines until the next heading at equal-or-shallower depth.
      2. Frontmatter line `id: <id>` between two `---` fences: return from
         the line after the closing `---` up to the first heading (or end
         of file). If the closing `---` is not found, fall back to the
         line after the matched `id:` line.

    A plain ID mention in prose, wikilinks, or comments does NOT match.
    Returns None if no structured match is found; the caller treats that
    as "id <X>: not found".
    """
    lines = text.splitlines()

    # Mode 1: heading with trailing (<id>)
    heading_with_id = re.compile(rf"^(#+)\s+.*\(\s*{re.escape(entry_id)}\s*\)\s*$")
    for i, line in enumerate(lines):
        match = heading_with_id.match(line)
        if not match:
            continue
        level = len(match.group(1))
        out = [line]
        for j in range(i + 1, len(lines)):
            nxt_level = heading_level(lines[j])
            if nxt_level is not None and nxt_level <= level:
                break
            out.append(lines[j])
        return "\n".join(out).rstrip() + "\n"

    # Mode 2: frontmatter id line. Only match if the id: is genuinely inside a
    # frontmatter block bounded by `---` fences. A bare `id:` line outside a
    # block (malformed file or inline reference) must not match - otherwise the
    # function returns raw YAML / prose instead of the entry body.
    fm_pattern = re.compile(rf"^\s*id:\s*{re.escape(entry_id)}\s*$")
    for i, line in enumerate(lines):
        if not fm_pattern.match(line):
            continue

        # Verify the id: line is preceded by an opening `---` fence with no
        # heading or closing fence between. Frontmatter must start within the
        # first few lines or after a heading; we only accept the canonical
        # case: file starts with `---`, frontmatter, id line, closing `---`.
        opening_fence_found = False
        for k in range(i - 1, -1, -1):
            stripped = lines[k].strip()
            if stripped == "---":
                opening_fence_found = True
                break
            if heading_level(lines[k]) is not None:
                break
            if stripped == "":
                continue
        if not opening_fence_found:
            continue

        # Require a closing `---` after the id line, before any heading.
        closing_fence_idx = None
        for k in range(i + 1, len(lines)):
            stripped = lines[k].strip()
            if stripped == "---":
                closing_fence_idx = k
                break
            if heading_level(lines[k]) is not None:
                break
        if closing_fence_idx is None:
            continue

        body_start = closing_fence_idx + 1
        out = []
        for j in range(body_start, len(lines)):
            if heading_level(lines[j]) is not None:
                break
            out.append(lines[j])
        return "\n".join(out).rstrip() + "\n"

    return None


def run_full_mode(ids_arg: str, root: Path) -> int:
    if not ids_arg:
        print("Usage: python scripts/query.py --mode full --ids <id1,id2,...>")
        return 2
    ids = [i.strip() for i in ids_arg.split(",") if i.strip()]
    if not ids:
        print("Usage: python scripts/query.py --mode full --ids <id1,id2,...>")
        return 2

    files = all_markdown_files(root)

    print(f"FULL: {', '.join(ids)}")
    print("---")
    for entry_id in ids:
        found = False
        for path in files:
            text = safe_read(path)
            if entry_id not in text:
                continue
            block = extract_full_block(text, entry_id)
            if block is None:
                continue
            node = rel(path, root)
            print(f"\n=== {entry_id} ({node}) ===")
            print(block.rstrip())
            found = True
            break
        if not found:
            print(f"\nid {entry_id}: not found")
    return 0


# ---------- main ----------


def main() -> int:
    parser = argparse.ArgumentParser(description="Query Founder OS markdown graph")
    parser.add_argument("question", nargs="*", help="Question to query (index mode)")
    parser.add_argument("--root", default=".", help="Founder OS root")
    parser.add_argument(
        "--mode",
        choices=("index", "timeline", "full"),
        default="index",
        help="Output mode (default: index)",
    )
    parser.add_argument("--anchor", default="", help="Anchor slug or ID for timeline mode")
    parser.add_argument("--ids", default="", help="Comma-separated IDs for full mode")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    if args.mode == "timeline":
        return run_timeline_mode(args.anchor, root)
    if args.mode == "full":
        return run_full_mode(args.ids, root)

    # index mode (default)
    question = " ".join(args.question).strip()
    if not question:
        print("Usage: python scripts/query.py <question>")
        return 2
    return run_index_mode(question, root)


if __name__ == "__main__":
    raise SystemExit(main())
