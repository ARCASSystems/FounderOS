#!/usr/bin/env python3
"""Role-parity guard: the role surface must agree across disk, the role index, and the wizard copy list.

Ground truth is the filesystem:
  roles = the set of templates/roles/*.md filenames, minus index.md

v1.37.0 took the role set from four to six (added cso, cto) and expanded the setup
wizard's copy list, with no guard. check_doc_parity.py counts skills and commands, not
roles, so a future doc refactor could drop a role file from templates/roles/index.md or
from the wizard copy list and CI would stay green - the same class of silent break that
turned the install-completeness gate red on 2026-06-05. This guard closes it with
positive assertions: every role file on disk must be named by the index and by the
wizard copy list.

What this guard does NOT check, on purpose:
  - It does NOT ban a "four active" or "four roles" statement. Four active by default
    (with two reference-until-invoked) is correct, durable prose; a regex banning the
    word "four" would be brittle and would fail legitimate CHANGELOG and plan text.
    Positive assertions (every role is referenced everywhere it must be) are the durable
    part.

Exit 0 when every role on disk is referenced everywhere it must be, 1 with a report.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

ROLES_DIR = REPO / "templates" / "roles"
INDEX = ROLES_DIR / "index.md"
WIZARD_COPY_LIST = REPO / "skills" / "founder-os-setup" / "references" / "root-structure.md"

# The role set v1.37.0 ships. Disk is the source of truth; this expected set is here so a
# silently-added or silently-removed role file is also caught, not just a doc that forgot one.
EXPECTED_ROLES = {"coo", "cmo", "chief-of-staff", "bd", "cso", "cto"}


def disk_roles() -> set[str]:
    return {p.stem for p in ROLES_DIR.glob("*.md") if p.stem != "index"}


def main() -> int:
    roles = disk_roles()
    failures: list[str] = []

    print(
        f"Disk truth: {len(roles)} role files in templates/roles/ -> "
        f"{', '.join(sorted(roles)) if roles else '(none)'}"
    )

    # 1. Disk matches the expected set (catches a silently added or removed role file).
    if roles != EXPECTED_ROLES:
        missing = EXPECTED_ROLES - roles
        extra = roles - EXPECTED_ROLES
        if missing:
            failures.append(
                f"expected role files missing from templates/roles/: {', '.join(sorted(missing))}"
            )
        if extra:
            failures.append(
                "unexpected role files in templates/roles/ "
                f"(add to EXPECTED_ROLES if intended): {', '.join(sorted(extra))}"
            )

    # 2. The role index references every role file (by `<role>.md`).
    if not INDEX.exists():
        failures.append(f"role index missing: {INDEX.relative_to(REPO).as_posix()}")
    else:
        index_text = INDEX.read_text(encoding="utf-8")
        for role in sorted(roles):
            if f"{role}.md" not in index_text:
                failures.append(f"templates/roles/index.md does not reference {role}.md")

    # 3. The setup wizard's copy list (root-structure.md) names every role file.
    if not WIZARD_COPY_LIST.exists():
        failures.append(f"wizard copy list missing: {WIZARD_COPY_LIST.relative_to(REPO).as_posix()}")
    else:
        wizard_text = WIZARD_COPY_LIST.read_text(encoding="utf-8")
        for role in sorted(roles):
            if f"{role}.md" not in wizard_text:
                failures.append(
                    f"setup wizard copy list (references/root-structure.md) does not name {role}.md"
                )

    if failures:
        print("\nROLE PARITY FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("Role parity OK: every role on disk is referenced by index.md and the wizard copy list.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
