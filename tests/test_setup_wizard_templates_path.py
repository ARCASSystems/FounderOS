from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SETUP_SKILL = REPO_ROOT / "skills" / "founder-os-setup" / "SKILL.md"


class SetupWizardTemplatesPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.body = SETUP_SKILL.read_text(encoding="utf-8")

    def test_vague_phrase_is_gone(self) -> None:
        self.assertNotIn("find the plugin install path", self.body)

    def test_all_three_install_methods_named(self) -> None:
        self.assertIn("Plugin install", self.body)
        self.assertIn("Git clone", self.body)
        self.assertIn("Curl install", self.body)

    def test_glob_fallback_recipe_present(self) -> None:
        self.assertIn("**/templates/identity.md", self.body)

    def test_expected_template_files_listed(self) -> None:
        self.assertIn("identity.md", self.body)
        self.assertIn("bootloader-claude-md.md", self.body)
        self.assertIn("voice-profile.yml.template", self.body)

    def test_marketplace_json_marker_documented(self) -> None:
        self.assertIn(".claude-plugin/marketplace.json", self.body)


if __name__ == "__main__":
    unittest.main()
