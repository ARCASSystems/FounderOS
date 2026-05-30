#!/usr/bin/env python3
"""Brief-cleanliness guard: template example blocks must not inflate a fresh install's first brief.

The SessionStart brief (.claude/hooks/session-start-brief.sh and .ps1) counts live entries in the
operating files a fresh install scaffolds from templates/. Three of those counters are line-based
and do NOT skip fenced code blocks, so a format-spec or example heading written the wrong way gets
miscounted as a real entry and the brand-new user's very first brief lies:

  - Pending decisions: counts '### ' headings under '## Pending' in context/decisions.md.
  - Open flags:        counts 'Status: OPEN' lines in brain/flags.md.
  - Review Due (decay): scans '### ' / '## ' entries in brain/patterns.md and brain/flags.md for a
                        resolved 'Decay after:' date.

This class has bitten us three times. Commit 8d65990 angle-bracketed the fenced format-spec values
in flags.md and patterns.md so the counters skip them, but the same class survived in decisions.md
('### Format' plus a fenced '### [Decision Name]' under '## Pending' counted as two pending
decisions on a brand-new install). This guard locks all three template families so it cannot return
a fourth time.

What is allowed: the dated demo entries (flags.md '## 2024-01-01 ...', patterns.md
'### Free-value drift ...') are intentional. They surface once on the first brief to show the system
working, then the user deletes them. They live OUTSIDE fenced blocks with real values, so the checks
below never touch them. Only format-spec and placeholder content is policed.

Each check mirrors the actual counter it protects rather than a blanket heuristic - the decisions
counter is fence-agnostic and section-scoped, so the decisions check is too; the flag and decay
counters are dodged with placeholders inside fences, so those checks police fenced content only.

Exit 0 when every template is clean, 1 with a report otherwise. Pure stdlib, no deps.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

# Regexes copied from the shipped hooks so this guard polices exactly what the brief would count.
OPEN_RE = re.compile(r"Status:\s*\**OPEN")              # flags counter (session-start-brief.sh:101)
H3_RE = re.compile(r"^###\s")                            # decisions pending counter (.sh:166-170)
DECAY_RE = re.compile(r"^\s*-?\s*Decay after:\s*(.+?)\s*$")
CONCRETE_DECAY_RE = re.compile(r"^(?:\d{4}-\d{2}-\d{2}|\d+d)$")  # a value the decay scanner resolves
FENCE_RE = re.compile(r"^\s*```")


def _with_fence_state(lines: list[str]):
    """Yield (lineno, line, in_fence) tracking ``` code-fence state. The fence marker line itself
    carries the post-toggle state; marker lines never hold counted content so this is harmless."""
    in_fence = False
    for i, line in enumerate(lines, 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            yield i, line, in_fence
            continue
        yield i, line, in_fence


def check_decisions(path: Path) -> list[str]:
    """Replicate the pending-decisions counter: it counts '### ' headings under a decision section,
    fence-agnostic. decisions.md ships no live demo, so any such heading is a phantom. Assert zero
    across Pending / Parked / Resolved (the runtime only scans Pending, but a future counter change
    could scan the others, so keep all three clean)."""
    failures: list[str] = []
    section = None
    for ln in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+(Pending|Parked|Resolved)\b", ln)
        if m:
            section = m.group(1)
            continue
        if re.match(r"^##\s", ln):  # any other H2 ends the current section
            section = None
            continue
        if section and H3_RE.match(ln):
            failures.append(
                f"{path.name}: '### ' heading under '## {section}' is counted as a live decision "
                f"by the brief - reword to a non-heading format reference: {ln.strip()!r}"
            )
    return failures


def check_flags(path: Path) -> list[str]:
    """The flags counter matches 'Status: OPEN' line-wise, fence-agnostic. A 'Status: OPEN' inside a
    fenced format-spec is a phantom (the pre-8d65990 bug). The dated demo's 'Status: **OPEN.**' lives
    outside any fence and is allowed."""
    failures: list[str] = []
    for i, line, in_fence in _with_fence_state(path.read_text(encoding="utf-8").splitlines()):
        if in_fence and OPEN_RE.search(line):
            failures.append(
                f"{path.name}:{i}: fenced format-spec matches the OPEN-flag counter - use an angle "
                f"placeholder like <OPEN | ESCALATED | RESOLVED>: {line.strip()!r}"
            )
    return failures


def check_decay(path: Path) -> list[str]:
    """The decay scanner resolves 'Decay after:' to a date and surfaces past-decay entries. A fenced
    format-spec whose 'Decay after:' is concrete (YYYY-MM-DD or Nd) would be surfaced as a phantom;
    fenced values must be placeholders. The dated demo lives outside the fence and is allowed."""
    failures: list[str] = []
    for i, line, in_fence in _with_fence_state(path.read_text(encoding="utf-8").splitlines()):
        if not in_fence:
            continue
        m = DECAY_RE.match(line)
        if m and CONCRETE_DECAY_RE.match(m.group(1).strip()):
            failures.append(
                f"{path.name}:{i}: fenced format-spec 'Decay after:' is concrete and would be "
                f"surfaced by the decay scanner - use a placeholder like <Nd, e.g. 90d>: {line.strip()!r}"
            )
    return failures


# Each template is policed by its own counter, plus the cross-axis counter so neither flag/decay
# family can regress on the other axis.
CHECKS = [
    (REPO / "templates" / "context" / "decisions.md", check_decisions),
    (REPO / "templates" / "brain" / "flags.md", check_flags),
    (REPO / "templates" / "brain" / "flags.md", check_decay),
    (REPO / "templates" / "brain" / "patterns.md", check_flags),
    (REPO / "templates" / "brain" / "patterns.md", check_decay),
]


def run() -> list[str]:
    """Run every check and return the flat list of failure strings. Importable by the maintainer
    test in tests/ so the CI guard and the local suite assert the same thing."""
    failures: list[str] = []
    for path, check in CHECKS:
        if not path.exists():
            failures.append(f"missing template: {path.relative_to(REPO)}")
            continue
        failures.extend(check(path))
    return failures


def main() -> int:
    failures = run()
    if failures:
        print("BRIEF CLEANLINESS FAILED:")
        for f in failures:
            print(f"  - {f}")
        print(
            "\nA fresh install scaffolds these templates into its operating files; the SessionStart "
            "brief\ncounters would miscount the lines above as live entries on the user's first brief."
        )
        return 1
    print("Brief cleanliness OK: no template example block inflates a fresh first brief.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
