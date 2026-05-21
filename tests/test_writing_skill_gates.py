from pathlib import Path
import re
import unittest

try:
    import yaml  # type: ignore
    _YAML_AVAILABLE = True
except ImportError:  # pragma: no cover
    _YAML_AVAILABLE = False


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
WRITING_SKILLS = {
    "linkedin-post": REPO_ROOT / "skills" / "linkedin-post" / "SKILL.md",
    "client-update": REPO_ROOT / "skills" / "client-update" / "SKILL.md",
    "proposal-writer": REPO_ROOT / "skills" / "proposal-writer" / "SKILL.md",
    "email-drafter": REPO_ROOT / "skills" / "email-drafter" / "SKILL.md",
    "content-repurposer": REPO_ROOT / "skills" / "content-repurposer" / "SKILL.md",
}

GATE_SCRIPT_CALL = "python scripts/check-voice-ready.py"


class WritingSkillVoiceGateTests(unittest.TestCase):
    def test_each_writing_skill_calls_voice_ready_script(self) -> None:
        for name, path in WRITING_SKILLS.items():
            with self.subTest(skill=name):
                body = path.read_text(encoding="utf-8")
                self.assertIn(GATE_SCRIPT_CALL, body)
                self.assertIn("exit code is 1", body)
                self.assertIn("Stop", body)

    def test_each_skill_still_reads_voice_profile_after_gate(self) -> None:
        for name, path in WRITING_SKILLS.items():
            with self.subTest(skill=name):
                body = path.read_text(encoding="utf-8")
                self.assertIn("core/voice-profile.yml", body)


class WritingSkillAntiExampleFilterTests(unittest.TestCase):
    def test_each_writing_skill_documents_anti_example_filter(self) -> None:
        required_phrases = (
            "After producing a draft and before returning it, run the anti-examples filter",
            "anti_examples.pairs",
            "core/voice-profile.yml",
            "scan for matches against any `bad:` pattern",
            "rewrite it using the `good:` pattern",
            "the `rule:` line as the constraint",
            "aesthetic_crimes",
            "red_flags",
            "Return the cleaned draft",
            "Do not surface this filter to the user as a separate step",
        )
        for name, path in WRITING_SKILLS.items():
            with self.subTest(skill=name):
                body = path.read_text(encoding="utf-8")
                for phrase in required_phrases:
                    self.assertIn(phrase, body)

    def test_each_filter_names_structural_markers(self) -> None:
        markers = (
            "literal substrings",
            "negation-contrast",
            "rule-of-three",
        )
        for name, path in WRITING_SKILLS.items():
            with self.subTest(skill=name):
                body = path.read_text(encoding="utf-8")
                for marker in markers:
                    self.assertIn(marker, body)


SNAPSHOT_SKILLS = [
    "email-drafter",
    "sop-writer",
    "content-repurposer",
    "client-update",
    "proposal-writer",
]


class WritingSkillSnapshotReadTests(unittest.TestCase):
    def test_each_skill_references_snapshot(self):
        for skill in SNAPSHOT_SKILLS:
            path = REPO_ROOT / "skills" / skill / "SKILL.md"
            body = path.read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                self.assertIn("brain/.snapshot.md", body)
                self.assertIn("open-flags", body.lower())
                self.assertIn("must-do", body.lower())

    def test_each_skill_treats_snapshot_as_optional(self):
        for skill in SNAPSHOT_SKILLS:
            path = REPO_ROOT / "skills" / skill / "SKILL.md"
            body = path.read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                self.assertTrue(
                    "optional" in body.lower() or "if it exists" in body.lower(),
                    f"{skill}: snapshot must be optional, not required"
                )


class EmailDrafterVoiceGateFallbackTests(unittest.TestCase):
    """email-drafter must route all three branches (operator, brand, fallback) through a voice-ready gate."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.body = (SKILLS_DIR / "email-drafter" / "SKILL.md").read_text(encoding="utf-8")

    def test_operator_voice_branch_calls_check_voice_ready(self) -> None:
        self.assertIn("If using operator voice", self.body)
        # Operator branch must reach check-voice-ready.py
        self.assertIn("python scripts/check-voice-ready.py", self.body)

    def test_brand_voice_branch_calls_check_brand_voice_ready(self) -> None:
        self.assertIn("If using brand voice", self.body)
        self.assertIn("python scripts/check-brand-voice-ready.py", self.body)

    def test_fallback_branch_calls_check_voice_ready(self) -> None:
        """When neither voice is explicitly named, the skill must default to operator voice gate."""
        # Find the fallback line and verify it points to check-voice-ready.py
        self.assertIn("neither operator nor brand voice is explicitly named", self.body)
        # Pull out the fallback sentence and confirm it names the script
        fallback_match = re.search(
            r"If neither operator nor brand voice is explicitly named[^\n]*",
            self.body,
        )
        self.assertIsNotNone(fallback_match, "fallback line not found in email-drafter SKILL.md")
        fallback_line = fallback_match.group(0)
        self.assertIn("python scripts/check-voice-ready.py", fallback_line)
        self.assertIn("Stop on exit code 1", fallback_line)


# ---------------------------------------------------------------------------
# allowed-tools frontmatter must include Bash when SKILL body invokes `python scripts/`
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
ALLOWED_TOOLS_RE = re.compile(r"^allowed-tools\s*:\s*(.+?)$", re.MULTILINE)


def _split_frontmatter(text: str) -> tuple[str, str] | None:
    """Return (frontmatter, body) or None if no frontmatter block."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    return m.group(1), m.group(2)


def _parse_allowed_tools(frontmatter: str) -> list[str] | None:
    """Parse allowed-tools list from a frontmatter block.

    Prefers PyYAML; falls back to a simple regex parser if PyYAML is unavailable
    or if the field value is malformed. Returns None when no allowed-tools
    field is present so callers can distinguish missing from empty.
    """
    if _YAML_AVAILABLE:
        try:
            data = yaml.safe_load(frontmatter)
            if isinstance(data, dict) and "allowed-tools" in data:
                value = data["allowed-tools"]
                if isinstance(value, list):
                    return [str(v) for v in value]
                if isinstance(value, str):
                    # Comma-separated string form
                    return [v.strip() for v in value.split(",") if v.strip()]
        except yaml.YAMLError:
            pass
    # Regex fallback (handles single-line inline list like ["Read", "Bash"])
    m = ALLOWED_TOOLS_RE.search(frontmatter)
    if not m:
        return None
    raw = m.group(1).strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    items = []
    for chunk in raw.split(","):
        cleaned = chunk.strip().strip('"').strip("'")
        if cleaned:
            items.append(cleaned)
    return items


class AllowedToolsBashPresenceTests(unittest.TestCase):
    """Skills that invoke `python scripts/...` in their body must declare Bash in allowed-tools."""

    def test_skills_with_python_script_calls_declare_bash(self) -> None:
        missing: list[str] = []
        for skill_path in SKILLS_DIR.glob("*/SKILL.md"):
            if "_archive" in skill_path.parts:
                continue
            text = skill_path.read_text(encoding="utf-8")
            split = _split_frontmatter(text)
            if split is None:
                # Defensive: skip files with no frontmatter block
                continue
            frontmatter, body = split
            if not body.strip():
                # Defensive: skip files with empty body
                continue
            if "python scripts/" not in body:
                continue
            allowed = _parse_allowed_tools(frontmatter)
            if allowed is None:
                missing.append(
                    f"{skill_path.parent.name}: SKILL.md body calls `python scripts/...` "
                    f"but allowed-tools frontmatter field is missing"
                )
                continue
            if "Bash" not in allowed:
                missing.append(
                    f"{skill_path.parent.name}: SKILL.md body calls `python scripts/...` "
                    f"but allowed-tools does not include 'Bash' (got {allowed})"
                )
        self.assertEqual(
            missing,
            [],
            "Skills invoke `python scripts/` without declaring Bash in allowed-tools:\n"
            + "\n".join(missing),
        )


if __name__ == "__main__":
    unittest.main()
