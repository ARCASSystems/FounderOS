from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
BRAND_SKILL = REPO_ROOT / "skills" / "brand-interview" / "SKILL.md"
BRAND_TEMPLATE = REPO_ROOT / "templates" / "brand-profile.yml.template"
DELIVERABLE_SKILL = REPO_ROOT / "skills" / "your-deliverable-template" / "SKILL.md"


class BrandInterviewExistingAssetsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = BRAND_SKILL.read_text(encoding="utf-8")
        cls.template = BRAND_TEMPLATE.read_text(encoding="utf-8")
        cls.deliverable = DELIVERABLE_SKILL.read_text(encoding="utf-8")

    def test_visual_proof_question_present(self) -> None:
        self.assertIn("Do you have any existing visual proof", self.skill)
        for asset_type in ("deck", "website", "logo folder", "proposal", "style guide"):
            with self.subTest(asset_type=asset_type):
                self.assertIn(asset_type, self.skill)

    def test_existing_assets_field_present_in_output_shape(self) -> None:
        for field in ("existing_assets:", "has_assets:", "references:", "location:"):
            with self.subTest(field=field):
                self.assertIn(field, self.template)
        self.assertIn("existing_assets:", self.skill)

    def test_confirm_step_names_visual_proof(self) -> None:
        self.assertIn("Existing visual proof", self.skill)

    def test_deliverable_template_reads_existing_assets(self) -> None:
        self.assertIn("existing_assets", self.deliverable)
        self.assertIn("review those references", self.deliverable)


if __name__ == "__main__":
    unittest.main()
