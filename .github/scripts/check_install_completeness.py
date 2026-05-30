#!/usr/bin/env python3
"""Install-completeness smoke test: every source the setup wizard copies must exist,
and the wizard must name every script and hook a fresh install depends on.

A fresh user clones this repo and runs skills/founder-os-setup. Its copy steps name
the templates, scripts, and hooks to place in the founder's working directory. If the
wizard references a file that is not in the repo - or omits a script or hook the runtime
needs - the install is silently broken on day one. This guard would have caught:
  - _common.py missing from the scripts copy list (wiki-build.py and query.py import it)
  - session_start_brief.py missing from the hook copy list (session-start-brief.sh calls it)

This is a static parity check run in CI on every push and PR. It does NOT execute the
LLM-driven wizard (that cannot run headlessly); it verifies the wizard's copy contract
against the repo so the contract and the filesystem cannot silently drift apart.

Exit 0 when complete, 1 with a report otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIZARD = REPO / "skills" / "founder-os-setup" / "SKILL.md"
SETTINGS = REPO / ".claude" / "settings.json"
TEMPLATE_SCRIPTS = REPO / "templates" / "scripts"
HOOKS_DIR = REPO / ".claude" / "hooks"
LIVE_SCRIPTS = REPO / "scripts"


def main() -> int:
    failures: list[str] = []
    notes: list[str] = []

    if not WIZARD.exists():
        print(f"FAIL: wizard not found at {WIZARD}")
        return 1
    wizard_text = WIZARD.read_text(encoding="utf-8")

    # 1. Every source path the wizard names must exist in the repo, so a fresh clone
    #    contains every file the copy steps reference.
    referenced: set[str] = set()
    for m in re.finditer(r"templates/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+", wizard_text):
        referenced.add(m.group(0))
    for m in re.finditer(r"\.claude/hooks/[A-Za-z0-9_.-]+\.(?:sh|ps1|py)", wizard_text):
        referenced.add(m.group(0))
    if ".claude/settings.json" in wizard_text:
        referenced.add(".claude/settings.json")
    for rel in sorted(referenced):
        if not (REPO / rel).exists():
            failures.append(f"wizard references a source that does not exist: {rel}")

    # 2. Every template script must be named somewhere in the wizard so it gets copied.
    if TEMPLATE_SCRIPTS.is_dir():
        for py in sorted(TEMPLATE_SCRIPTS.glob("*.py")):
            if py.name not in wizard_text:
                failures.append(
                    f"templates/scripts/{py.name} exists but the wizard never names it - it will not be copied"
                )

    # 3. Every hook that settings.json wires must be named in the wizard, plus the
    #    session_start_brief.py helper that session-start-brief.sh calls at runtime.
    if SETTINGS.exists():
        settings_text = SETTINGS.read_text(encoding="utf-8")
        wired = set(re.findall(r"hooks/([A-Za-z0-9_.-]+\.(?:sh|ps1|py))", settings_text))
        for hook in sorted(wired):
            if hook not in wizard_text:
                failures.append(
                    f".claude/settings.json wires {hook} but the wizard never names it - it will not be copied"
                )
    else:
        notes.append(".claude/settings.json not found (skipped hook-wiring check)")

    if (HOOKS_DIR / "session_start_brief.py").exists() and "session_start_brief.py" not in wizard_text:
        failures.append(
            "hook session_start_brief.py exists (session-start-brief.sh calls it) but the wizard never names it"
        )

    # 4. scripts/ and templates/scripts/ must hold the same .py set: the wizard copies
    #    templates/scripts/ into the founder's scripts/. Extras in scripts/ that the
    #    wizard does not ship are a note, not a failure - this is the documented policy,
    #    not an oversight. scrape.py (web-fetch-extract) is a deterministic helper that
    #    ships plugin-repo-only; the skill documents an inline keyless fallback and runs
    #    without the script, so it is deliberately NOT in templates/scripts/. Do not "fix"
    #    this by force-adding it to the copy list - that would push httpx/selectolax deps
    #    onto every free-tier install.
    if TEMPLATE_SCRIPTS.is_dir() and LIVE_SCRIPTS.is_dir():
        live = {p.name for p in LIVE_SCRIPTS.glob("*.py")}
        tmpl = {p.name for p in TEMPLATE_SCRIPTS.glob("*.py")}
        only_tmpl = sorted(tmpl - live)
        only_live = sorted(live - tmpl)
        if only_tmpl:
            failures.append(f"templates/scripts/ has .py missing from scripts/: {only_tmpl}")
        if only_live:
            notes.append(f"scripts/ has .py not in templates/scripts/ (fallback-only by policy): {only_live}")

    for n in notes:
        print(f"note: {n}")
    if failures:
        print("\nINSTALL COMPLETENESS FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("Install completeness OK: wizard names every template script and wired hook; all referenced sources exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
