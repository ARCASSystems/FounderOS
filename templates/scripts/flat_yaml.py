#!/usr/bin/env python3
"""flat_yaml.py - the one reader for the OS's flat registry files.

The problem it exists for: the OS needs to read a couple of small structured
registry files (the digital-employee org chart, for one), and it must do that
without asking you to `pip install` anything. Every shipped script here runs on
the standard library alone, which is the floor that keeps the OS usable on a
machine with no package manager and no paid plan.

The second problem it exists for: when two different bits of code parse the same
file with two hand-rolled parsers, they eventually disagree about what the file
says. One raises on a mis-indented line, the other quietly skips it, and two
surfaces of the OS report different contents for the same file. One
implementation, strict everywhere, is the fix.

THE FORMAT is deliberately a subset of YAML, not the whole language:

    <record_key>:
      - first_key: value          # a new record opens on a 2-space "- key: value"
        other_key: value          # 4-space scalars belong to the current record
        a_list_key:               # a bare 4-space "key:" opens a list
          - item                  # 6-space "- item" for a list of scalars
        a_maplist_key:
          - label: x              # 6-space "- key: value" opens a map in a list of maps
            type: y               # 8-space scalars belong to that map

Values may contain colons (the split is on the first ": " only). Comments and
blank lines are skipped.

Invariants: read-only, standard library only, and it FAILS LOUD. Any line that
does not match one of the shapes above raises ValueError naming the file and the
line number. A registry file that will not parse stops the caller rather than
returning a silently shorter list, because a short list looks like a working
answer and is the harder bug to find.

Usage (as a module, not a command):
  >>> from flat_yaml import parse_flat_yaml
  >>> rows = parse_flat_yaml(text, filename="roles/employees.yaml",
  ...                        record_key="employees")
"""

from __future__ import annotations

import re

_RECORD_RE = re.compile(r"^  - (\w+):\s?(.*)$")
_SCALAR_RE = re.compile(r"^    (\w+):\s?(.*)$")
_LIST_ITEM_RE = re.compile(r"^      - (?=\S)(.*)$")
_MAP_OPEN_RE = re.compile(r"^      - (\w+):\s?(.*)$")
_MAP_SCALAR_RE = re.compile(r"^        (\w+):\s?(.*)$")


def yaml_val(s: str):
    """The scalar rules this subset supports: null, quoted string, or bare string."""
    s = s.strip()
    if s == "" or s.lower() in ("null", "~", "none"):
        return None
    if len(s) >= 2 and s[0] in "\"'" and s[-1] == s[0]:
        return s[1:-1]
    return s


def parse_flat_yaml(text: str, *, filename: str, record_key: str,
                    list_keys: tuple[str, ...] = (),
                    map_list_keys: tuple[str, ...] = ()) -> list[dict]:
    """Parse one `<record_key>:` block into a list of dicts.

    filename       - named in every error message, so the error sends you to the
                     right file instead of to whichever file the parser was
                     written for.
    record_key     - the top-level block to read. Other top-level blocks in the
                     same file are skipped, so one file may hold several blocks.
    list_keys      - keys whose value is a list of scalars.
    map_list_keys  - keys whose value is a list of maps.
    """
    records: list[dict] = []
    cur: dict | None = None
    mode: str | None = None
    node: dict | None = None
    in_block = False

    for ln, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Any column-0 key switches blocks: ours opens it, anything else closes it.
        # `key: value` counts too - a top-level scalar sitting after our block is
        # another block's business, not an unparseable line.
        if not line.startswith(" ") and ":" in stripped:
            in_block = stripped == f"{record_key}:"
            cur = node = None
            mode = None
            continue
        if not in_block:
            continue

        m = _RECORD_RE.match(line)
        if m:
            cur = {m.group(1): yaml_val(m.group(2))}
            records.append(cur)
            mode = None
            node = None
            continue

        if cur is None:
            raise ValueError(f"{filename} line {ln}: content before the first record "
                             f"in the {record_key!r} block: {stripped!r}")

        m = _SCALAR_RE.match(line)
        if m:
            key, val = m.group(1), yaml_val(m.group(2))
            if val is None and (key in list_keys or key in map_list_keys):
                mode, node = key, None
                cur[key] = []
            else:
                mode = node = None
                cur[key] = val
            continue

        if mode in list_keys:
            m = _LIST_ITEM_RE.match(line)
            if m:
                cur[mode].append(m.group(1).strip())
                continue

        if mode in map_list_keys:
            m = _MAP_OPEN_RE.match(line)
            if m:
                node = {m.group(1): yaml_val(m.group(2))}
                cur[mode].append(node)
                continue
            m = _MAP_SCALAR_RE.match(line)
            if m and node is not None:
                node[m.group(1)] = yaml_val(m.group(2))
                continue

        raise ValueError(f"{filename} line {ln}: unparseable line {stripped!r}")

    return records
