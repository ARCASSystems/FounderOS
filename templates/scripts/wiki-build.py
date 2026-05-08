#!/usr/bin/env python3
"""
Founder OS - wiki-build

Walks all markdown files in your repo, extracts [[wikilinks]], and writes the
auto-generated wiki_links section into brain/relations.yaml.

The hand-curated `relations:` section in brain/relations.yaml is preserved.
Only the block between the auto-generated sentinel markers is replaced. Run
this whenever you have added cross-references between OS files. Idempotent:
running twice in a row produces no diff.

Wikilink syntax (Obsidian-compatible):
  [[target]]               - bare slug, resolved at query time
  [[target.md]]            - explicit file path (basename or repo-relative)
  [[target.md#anchor]]     - file with anchor
  [[target|display text]]  - alias form, display text discarded for graph

Wiki-layer scope: scans `core/`, `context/`, `cadence/`, `brain/`, `network/`,
`companies/`, `roles/`, `rules/`. Plugin-internal directories (`.claude/`,
`skills/`, `templates/`, `docs/`), the source archive (`raw/`), brain archive,
and binary files are excluded.

Run via /founder-os:wiki-build, or directly:  python scripts/wiki-build.py [--root /path/to/repo]
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

# NOTE: If you change INCLUDE_PREFIXES, also update:
#   - scripts/wiki-build.py (live script, must match line-for-line)
#   - skills/lint/SKILL.md (Scope section)
#   - skills/wiki-build/SKILL.md (Scope section)
# The lint skill scopes are documentation, not code, so they will silently drift
# unless updated by hand here.
INCLUDE_PREFIXES = (
    'core/',
    'context/',
    'cadence/',
    'brain/',
    'network/',
    'companies/',
    'roles/',
    'rules/',
)
EXCLUDE_PREFIXES = (
    '.git/',
    'brain/archive/',
    'brain/transcripts/',
    'brain/rants/',
    'node_modules/',
    'scripts/__pycache__/',
)
WIKI_PATTERN = re.compile(r'\[\[([^\]\|\n]+?)(?:\|([^\]\n]+?))?\]\]')
INLINE_CODE_PATTERN = re.compile(r'`[^`\n]*`')


def is_in_scope(rel_path: str) -> bool:
    rel = rel_path.replace('\\', '/')
    if any(rel.startswith(p) for p in EXCLUDE_PREFIXES):
        return False
    return any(rel.startswith(p) for p in INCLUDE_PREFIXES)


def normalize_target(target: str) -> str:
    """Canonicalize a wikilink target so [[file]] and [[file.md]] dedupe to one node.

    Strips a trailing `.md` from the path part (preserves any `#anchor` suffix)
    and normalizes Windows backslashes to forward slashes. Does not lowercase
    (preserves the user's display intent). Bare slugs and path forms are both
    handled: [[file]], [[file.md]], [[brain/log]], [[brain/log.md]],
    [[brain/log.md#anchor]] all collapse to a stable graph node name.
    """
    target = target.replace('\\', '/').strip()
    if '#' in target:
        path, _, anchor = target.partition('#')
        if path.endswith('.md'):
            path = path[:-3]
        return f'{path}#{anchor}' if anchor else path
    if target.endswith('.md'):
        return target[:-3]
    return target


def extract_links(text: str):
    """Yield (target, line_no) for each wikilink. Skips fenced code blocks
    and inline backtick-delimited code spans (so docs that describe the
    [[wikilink]] syntax don't pollute the graph). Targets are normalized via
    normalize_target() so [[file]] and [[file.md]] produce the same node."""
    in_fence = False
    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        cleaned = INLINE_CODE_PATTERN.sub('', line)
        for m in WIKI_PATTERN.finditer(cleaned):
            target = normalize_target(m.group(1))
            if target:
                yield target, line_no


def main():
    parser = argparse.ArgumentParser(
        description='Walk markdown files in a Founder OS repo and refresh the '
                    'wiki_links section in brain/relations.yaml.'
    )
    parser.add_argument(
        '--root',
        default='.',
        help='Founder OS root directory. Defaults to the current working directory.',
    )
    args = parser.parse_args()
    repo = Path(args.root).resolve()

    by_source = defaultdict(set)
    total = 0

    for md in repo.rglob('*.md'):
        rel = str(md.relative_to(repo)).replace('\\', '/')
        if not is_in_scope(rel):
            continue
        try:
            content = md.read_text(encoding='utf-8')
        except (UnicodeDecodeError, PermissionError):
            continue
        for target, _ in extract_links(content):
            by_source[rel].add(target)
            total += 1

    out = [
        '#@@WIKI_LINKS_AUTOGEN_BEGIN@@ - do not edit; overwritten by scripts/wiki-build.py',
        f'# Last build: {date.today().isoformat()}',
        f'# Total: {total} links across {len(by_source)} source files',
        'wiki_links:',
    ]
    if not by_source:
        out.append('  []')
    for src in sorted(by_source):
        out.append(f'  - source: {src}')
        out.append('    targets:')
        for tgt in sorted(by_source[src]):
            escaped = tgt.replace('"', '\\"')
            out.append(f'      - "{escaped}"')
    out.append('#@@WIKI_LINKS_AUTOGEN_END@@')
    new_block = '\n'.join(out)

    yaml_path = repo / 'brain' / 'relations.yaml'
    if not yaml_path.exists():
        print(
            "ERROR: brain/relations.yaml not found. Run /founder-os:setup "
            "to initialise the brain layer, or create brain/relations.yaml "
            "with a 'relations:' stub before running wiki-build.",
            file=sys.stderr,
        )
        return 1
    existing = yaml_path.read_text(encoding='utf-8')
    begin_re = re.compile(r'^#@@WIKI_LINKS_AUTOGEN_BEGIN@@.*$', re.MULTILINE)
    end_re = re.compile(r'^#@@WIKI_LINKS_AUTOGEN_END@@.*$', re.MULTILINE)
    begin_match = begin_re.search(existing)
    end_match = end_re.search(existing)

    if begin_match and (not end_match or end_match.start() < begin_match.start()):
        print(
            "ERROR: WIKI_LINKS_AUTOGEN_BEGIN marker found but matching END "
            "marker is missing or out of order in brain/relations.yaml. "
            "Manual fix required: re-add the '#@@WIKI_LINKS_AUTOGEN_END@@' "
            "line at the correct position, then re-run.",
            file=sys.stderr,
        )
        return 1

    if begin_match and end_match:
        pre = existing[:begin_match.start()].rstrip()
        post = existing[end_match.end():].lstrip()
        new = pre + '\n\n' + new_block + ('\n\n' + post if post else '\n')
    else:
        new = existing.rstrip() + '\n\n' + new_block + '\n'

    yaml_path.write_text(new, encoding='utf-8')
    print(f'Wrote {total} wiki links from {len(by_source)} source files into brain/relations.yaml')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
