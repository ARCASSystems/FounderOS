from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
READINESS_SKILL = REPO_ROOT / "skills" / "readiness-check" / "SKILL.md"


class ReadinessCheckHeaderXrefTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.body = READINESS_SKILL.read_text(encoding="utf-8")
        cls.head = "\n".join(cls.body.splitlines()[:15])

    def test_command_label_in_header(self) -> None:
        self.assertIn("**Command:**", self.head)

    def test_xref_lists_both_command_forms(self) -> None:
        self.assertIn("/founder-os:status", self.head)
        self.assertIn("/status", self.head)

    def test_xref_explains_folder_vs_command_naming(self) -> None:
        xref_lines = [line for line in self.head.splitlines() if "**Command:**" in line]
        self.assertEqual(len(xref_lines), 1, "expected exactly one cross-reference line in header")
        xref = xref_lines[0]
        self.assertIn("folder", xref)
        self.assertIn("command", xref)


if __name__ == "__main__":
    unittest.main()
