"""
W2 - Skill catalogue integrity tests.
Verifies that skills/index.md matches the filesystem, no dead script references
exist, no live skills are marked as skeletons, archived skills have required
frontmatter, and the skill count is consistent across the key manifest files.
"""
import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
ARCHIVE_DIR = SKILLS_DIR / "_archive"
INDEX_FILE = SKILLS_DIR / "index.md"
PLUGIN_JSON = REPO_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"
README = REPO_ROOT / "README.md"


def _parse_index_skill_names() -> list[str]:
    """Extract skill names from the skills table in skills/index.md."""
    body = INDEX_FILE.read_text(encoding="utf-8")
    names = []
    # Rows look like: | [skill-name](skill-name/SKILL.md) | ...
    for m in re.finditer(r"^\|\s*\[([a-z0-9_-]+)\]\([^)]+/SKILL\.md\)", body, re.MULTILINE):
        names.append(m.group(1))
    return names


def _parse_index_skill_count_text() -> int | None:
    """Extract the numeric skill count stated at the top of index.md."""
    body = INDEX_FILE.read_text(encoding="utf-8")
    m = re.search(r"(\d+)\s+skills?\s+included", body)
    return int(m.group(1)) if m else None


class SkillCatalogueIntegrityTests(unittest.TestCase):

    def test_every_skill_in_index_has_a_file(self):
        """Every skill listed in skills/index.md must have a SKILL.md on disk."""
        names = _parse_index_skill_names()
        self.assertGreater(len(names), 0, "No skill rows parsed from index.md")
        missing = [n for n in names if not (SKILLS_DIR / n / "SKILL.md").exists()]
        self.assertEqual(
            missing,
            [],
            f"Skills listed in index.md but missing from filesystem: {missing}",
        )

    def test_no_skill_body_references_nonexistent_scripts(self):
        """No live SKILL.md body may reference a scripts/ path that does not exist."""
        scripts_dir = REPO_ROOT / "scripts"
        live_skills = [
            p for p in SKILLS_DIR.glob("*/SKILL.md")
            if "_archive" not in p.parts
        ]
        broken = []
        for skill_path in live_skills:
            body = skill_path.read_text(encoding="utf-8")
            for m in re.finditer(r"scripts/([a-zA-Z0-9_.-]+\.py)", body):
                script_name = m.group(1)
                if not (scripts_dir / script_name).exists():
                    broken.append(f"{skill_path.parent.name}: scripts/{script_name}")
        self.assertEqual(
            broken,
            [],
            f"Skills reference nonexistent scripts: {broken}",
        )

    def test_no_skill_marked_skeleton_or_draft_in_live_directory(self):
        """No live SKILL.md may have skeleton/stub quality markers in its frontmatter."""
        live_skills = [
            p for p in SKILLS_DIR.glob("*/SKILL.md")
            if "_archive" not in p.parts
        ]
        flagged = []
        # Check frontmatter block only (between the first two --- lines)
        for skill_path in live_skills:
            body = skill_path.read_text(encoding="utf-8")
            # Extract frontmatter: content between first and second ---
            parts = body.split("---", 2)
            if len(parts) < 3:
                continue
            frontmatter = parts[1].lower()
            for marker in ("status: draft", "status: skeleton", "status: stub", "status: wip"):
                if marker in frontmatter:
                    flagged.append(f"{skill_path.parent.name}: {marker}")
        self.assertEqual(
            flagged,
            [],
            f"Live skills with quality markers in frontmatter: {flagged}",
        )

    def test_archived_skills_have_required_frontmatter(self):
        """Every skill in skills/_archive/ must have archived:, archived_reason:, and revival_trigger: fields."""
        if not ARCHIVE_DIR.exists():
            self.skipTest("skills/_archive/ does not exist yet")
        archived_skills = list(ARCHIVE_DIR.glob("*/SKILL.md"))
        if not archived_skills:
            # No archived skills is a valid state; nothing to check.
            return
        missing_fields = []
        for skill_path in archived_skills:
            body = skill_path.read_text(encoding="utf-8")
            parts = body.split("---", 2)
            if len(parts) < 3:
                missing_fields.append(f"{skill_path.parent.name}: no frontmatter block")
                continue
            fm = parts[1]
            for field in ("archived:", "archived_reason:", "revival_trigger:"):
                if field not in fm:
                    missing_fields.append(f"{skill_path.parent.name}: missing {field}")
        self.assertEqual(
            missing_fields,
            [],
            f"Archived skills with missing required frontmatter: {missing_fields}",
        )

    def test_skill_count_consistent_across_files(self):
        """Skill count stated in README, plugin.json, marketplace.json, and index.md must all agree."""
        # Count from filesystem (live skills, excluding _archive)
        live_count = sum(
            1 for p in SKILLS_DIR.glob("*/SKILL.md")
            if "_archive" not in p.parts
        )

        # Count from index.md header
        index_count = _parse_index_skill_count_text()

        # Count from plugin.json description
        plugin_text = PLUGIN_JSON.read_text(encoding="utf-8")
        plugin_m = re.search(r"(\d+)\s+skills?", plugin_text)
        plugin_count = int(plugin_m.group(1)) if plugin_m else None

        # Count from marketplace.json description
        market_text = MARKETPLACE_JSON.read_text(encoding="utf-8")
        market_m = re.search(r"(\d+)\s+skills?", market_text)
        market_count = int(market_m.group(1)) if market_m else None

        # Count from README (multiple mentions - take first)
        readme_text = README.read_text(encoding="utf-8")
        readme_m = re.search(r"(\d+)\s+skills?", readme_text)
        readme_count = int(readme_m.group(1)) if readme_m else None

        counts = {
            "filesystem": live_count,
            "index.md": index_count,
            "plugin.json": plugin_count,
            "marketplace.json": market_count,
            "README.md": readme_count,
        }

        # Remove None entries (file missing or regex missed - not an agreement failure)
        present = {k: v for k, v in counts.items() if v is not None}

        if len(present) < 2:
            self.skipTest("Not enough manifest files present to compare counts")

        unique_counts = set(present.values())
        self.assertEqual(
            len(unique_counts),
            1,
            f"Skill counts disagree across files: {present}",
        )


if __name__ == "__main__":
    unittest.main()
