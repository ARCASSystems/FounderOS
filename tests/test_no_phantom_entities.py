"""
F34 - phantom-entities absence + ingest routing positives.

The ingest skill historically routed an "Entity" category to
`context/entities/<slug>.md`, but no such directory existed in templates,
no other skill read or wrote there, and no install command created it.
v1.27 F34 removed the reference. This test makes sure it does not come
back without a deliberate re-introduction and that the replacement
routing categories are present.

Allow-list for the forbidden string:
- CHANGELOG.md: historical record; never edited retroactively.
- plans/: design plans referencing the path are historical artifacts.
- tests/test_no_phantom_entities.py: this file itself names the forbidden
  string in order to scan for it.

See plans/v1.27-f34-entities-schema-2026-05-22.md.
"""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = "context/entities"

# Directories that must NOT contain the forbidden string.
SCAN_DIRS = ("skills", "docs", "templates", "tests", "core", "cadence",
             "network", "roles", "rules")

# Files/dirs allowed to keep historical mentions.
ALLOW_LIST_FILES = {"CHANGELOG.md"}
ALLOW_LIST_DIRS = {"plans"}
SELF_REL = "tests/test_no_phantom_entities.py"


def _is_allowed(rel_posix: str) -> bool:
    if rel_posix == SELF_REL:
        return True
    if rel_posix in ALLOW_LIST_FILES:
        return True
    first = rel_posix.split("/", 1)[0]
    if first in ALLOW_LIST_DIRS:
        return True
    return False


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


class PhantomEntitiesAbsentTests(unittest.TestCase):
    """The dangling `context/entities` reference must not reappear."""

    def test_no_forbidden_mention_in_scanned_dirs(self):
        hits = []
        for scan_dir in SCAN_DIRS:
            base = REPO_ROOT / scan_dir
            if not base.exists():
                continue
            for pattern in ("*.md", "*.py"):
                for path in base.rglob(pattern):
                    rel = path.relative_to(REPO_ROOT).as_posix()
                    if _is_allowed(rel):
                        continue
                    if FORBIDDEN in _read_text(path):
                        hits.append(rel)
        self.assertEqual(
            sorted(hits), [],
            f"Forbidden string '{FORBIDDEN}' reappeared in: {sorted(hits)}. "
            "If this is intentional, update the F34 design decision in "
            "plans/v1.27-f34-entities-schema-2026-05-22.md and either "
            "extend this test's allow-list with explicit justification or "
            "delete the test."
        )


class IngestRoutingPositiveTests(unittest.TestCase):
    """skills/ingest/SKILL.md must declare the post-F34 routing categories.

    Negative-only tests (the absent-string check above) pass vacuously if
    the skill body is empty or unrelated. These positive assertions confirm
    the REMOVE branch actually wired in the replacement routing.
    """

    @classmethod
    def setUpClass(cls) -> None:
        skill_path = REPO_ROOT / "skills" / "ingest" / "SKILL.md"
        cls.skill_text = _read_text(skill_path)

    def test_person_routing_declared(self):
        self.assertIn("| Person |", self.skill_text,
                      "ingest skill must declare a Person routing row in Step 3.")
        self.assertIn("context/clients.md", self.skill_text,
                      "ingest skill must reference context/clients.md as Person target.")

    def test_company_routing_declared(self):
        self.assertIn("| Company |", self.skill_text,
                      "ingest skill must declare a Company routing row in Step 3.")
        self.assertIn("companies/<slug>-business.md", self.skill_text,
                      "ingest skill must reference companies/<slug>-business.md as Company target.")

    def test_company_routing_includes_prospect_path(self):
        # F27 task 5.5 reconciles ingest with the new prospect path under
        # Option X: the Company row names both operator and prospect paths
        # in priority order. Without this positive assertion the row could
        # silently drop the prospect path while existing tests still pass.
        self.assertIn("companies/prospects/<slug>.md", self.skill_text,
                      "ingest Company row must also reference "
                      "companies/prospects/<slug>.md as the prospect-path "
                      "target post-F27 (Option X: single Company row, dual "
                      "path in description).")

    def test_entity_row_removed(self):
        self.assertNotIn("| Entity |", self.skill_text,
                         "ingest skill must NOT contain the removed Entity routing row.")
        self.assertNotIn("Entity (new file):", self.skill_text,
                         "ingest skill must NOT contain the removed Entity apply-bullet.")


if __name__ == "__main__":
    unittest.main()
