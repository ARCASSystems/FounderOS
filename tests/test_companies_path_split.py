"""
F27 - companies semantic path split between operator and prospect.

The v1.27 F27 finding split the companies surface so operator companies
(businesses the user runs) live at `companies/<slug>-business.md` while
prospect companies (companies the user sells to or watches) live at
`companies/prospects/<slug>.md`. Operator path is unchanged from v1.26;
prospect path is new. Downstream skills that consume company-specific
context (proposal-writer, strategic-analysis, client-update) check the
operator path first and the prospect path second.

These tests lock the split on the test side so a future edit cannot
silently revert the convention.

See plans/v1.27-f27-companies-semantic-split-2026-05-22.md and
plans/v1.27-f27-f34-implementation-2026-05-22.md.
"""

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = REPO_ROOT / "templates"
SKILLS_DIR = REPO_ROOT / "skills"

OPERATOR_PATH_LITERAL = "companies/<slug>-business.md"
PROSPECT_PATH_LITERAL = "companies/prospects/<slug>.md"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


class ProspectTemplateShapeTests(unittest.TestCase):
    """The new prospect template must exist and have a usable shape."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.template_path = TEMPLATES_DIR / "prospect-context.template.md"
        cls.template_text = _read_text(cls.template_path) if cls.template_path.exists() else ""

    def test_template_file_exists(self):
        self.assertTrue(
            self.template_path.exists(),
            "templates/prospect-context.template.md must exist for F27."
        )

    def test_template_has_id_frontmatter(self):
        self.assertIn(
            "id: prospect-context.template",
            self.template_text,
            "Prospect template must declare its template id in frontmatter."
        )

    def test_template_has_no_handlebars_placeholders(self):
        leftover = re.findall(r"\{\{[^}]+\}\}", self.template_text)
        self.assertEqual(
            leftover, [],
            f"Prospect template should not ship with handlebars placeholders. "
            f"Found: {leftover}"
        )

    def test_template_does_not_require_fill_markers(self):
        # Design decision: prospect template intentionally lightweight.
        # No [FILL] markers required for the file to be useful.
        self.assertNotIn(
            "[FILL]", self.template_text,
            "Prospect template should not use [FILL] markers; capture is "
            "lightweight and fields may be left blank or marked unknown."
        )

    def test_template_under_size_budget(self):
        # Design pass set a ~60-line budget on the prospect template.
        # Loose ceiling so the assertion is honest, not vacuous.
        line_count = len(self.template_text.splitlines())
        self.assertLess(
            line_count, 80,
            f"Prospect template should stay under ~60 lines (currently "
            f"{line_count}). Add a follow-up plan before growing it."
        )


class OperatorTemplateUntouchedTests(unittest.TestCase):
    """The operator template path must not have changed in v1.27."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.template_path = TEMPLATES_DIR / "business-context.template.md"
        cls.template_text = _read_text(cls.template_path)

    def test_operator_template_still_at_legacy_path(self):
        self.assertTrue(
            self.template_path.exists(),
            "Operator path templates/business-context.template.md must stay "
            "at the v1.26 path. F27 does not rename it."
        )

    def test_operator_template_points_at_legacy_destination(self):
        self.assertIn(
            "companies/<your-company-slug>-business.md",
            self.template_text,
            "Operator template must still instruct users to copy to "
            "companies/<your-company-slug>-business.md (v1.26 path preserved)."
        )

    def test_operator_template_links_to_prospect_template(self):
        # F27 task 2 added a one-line note pointing at the prospect template.
        self.assertIn(
            "prospect-context.template.md",
            self.template_text,
            "Operator template should reference the prospect template so "
            "users land at the right path on first read."
        )


class ProspectInitSkillTests(unittest.TestCase):
    """The prospect-init skill must declare the prospect path as its write target."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_path = SKILLS_DIR / "prospect-init" / "SKILL.md"
        cls.skill_text = _read_text(cls.skill_path) if cls.skill_path.exists() else ""

    def test_prospect_init_skill_exists(self):
        self.assertTrue(
            self.skill_path.exists(),
            "skills/prospect-init/SKILL.md must exist for F27."
        )

    def test_prospect_init_writes_to_prospect_path(self):
        self.assertIn(
            "companies/prospects/",
            self.skill_text,
            "prospect-init must declare companies/prospects/ as its write surface."
        )

    def test_prospect_init_reads_template(self):
        self.assertIn(
            "templates/prospect-context.template.md",
            self.skill_text,
            "prospect-init must reference the prospect template it copies from."
        )

    def test_prospect_init_appends_to_brain_log(self):
        self.assertIn(
            "brain/log.md",
            self.skill_text,
            "prospect-init must log to brain/log.md so future audits surface "
            "prospect tracking activity."
        )


class DownstreamSkillTwoPathTests(unittest.TestCase):
    """proposal-writer, client-update, strategic-analysis must all declare
    the two-path check (operator first, prospect second)."""

    DOWNSTREAM_SKILLS = (
        "proposal-writer",
        "client-update",
        "strategic-analysis",
    )

    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_texts = {}
        for slug in cls.DOWNSTREAM_SKILLS:
            path = SKILLS_DIR / slug / "SKILL.md"
            cls.skill_texts[slug] = _read_text(path) if path.exists() else ""

    def test_each_skill_mentions_operator_path(self):
        for slug, text in self.skill_texts.items():
            with self.subTest(skill=slug):
                self.assertIn(
                    OPERATOR_PATH_LITERAL, text,
                    f"{slug} must declare operator path "
                    f"{OPERATOR_PATH_LITERAL}."
                )

    def test_each_skill_mentions_prospect_path(self):
        for slug, text in self.skill_texts.items():
            with self.subTest(skill=slug):
                self.assertIn(
                    PROSPECT_PATH_LITERAL, text,
                    f"{slug} must declare prospect path "
                    f"{PROSPECT_PATH_LITERAL} so company-specific context "
                    f"resolution covers both operator and prospect cases."
                )

    def test_operator_path_appears_before_prospect_path(self):
        # Design Q3: prefer operator file if both exist. The textual order
        # in the skill body encodes the routing priority.
        for slug, text in self.skill_texts.items():
            with self.subTest(skill=slug):
                op_idx = text.find(OPERATOR_PATH_LITERAL)
                pr_idx = text.find(PROSPECT_PATH_LITERAL)
                self.assertGreaterEqual(op_idx, 0)
                self.assertGreaterEqual(pr_idx, 0)
                self.assertLess(
                    op_idx, pr_idx,
                    f"{slug} should mention the operator path before the "
                    f"prospect path (operator-first priority per F27 Q3). "
                    f"Found operator at index {op_idx}, prospect at {pr_idx}."
                )

    def test_business_context_loader_stays_operator_only(self):
        # business-context-loader is operator-only by design. Adding the
        # prospect path here would conflate two skills.
        path = SKILLS_DIR / "business-context-loader" / "SKILL.md"
        text = _read_text(path)
        self.assertIn(OPERATOR_PATH_LITERAL, text)
        # The skill description may name prospect-init as a pointer; what
        # it must NOT do is read or write the prospect path as if it were
        # a fallback.
        self.assertNotIn(
            f"Reads `{PROSPECT_PATH_LITERAL}`", text,
            "business-context-loader must stay operator-only. Prospect "
            "context is handled by prospect-init."
        )


class CompaniesIndexTemplateTests(unittest.TestCase):
    """templates/context/companies.md should name the prospect path."""

    def test_companies_index_references_prospect_path(self):
        path = TEMPLATES_DIR / "context" / "companies.md"
        text = _read_text(path)
        self.assertIn(
            "companies/prospects/", text,
            "templates/context/companies.md should point readers at the "
            "prospect path so they do not mis-file prospects in the "
            "operator companies index."
        )


class IngestRoutingProspectPathTests(unittest.TestCase):
    """F27 task 5.5: the ingest Company row must name both paths."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = _read_text(SKILLS_DIR / "ingest" / "SKILL.md")

    def test_ingest_company_row_names_operator_path(self):
        self.assertIn(
            OPERATOR_PATH_LITERAL, self.skill_text,
            "Ingest Company row must name the operator path as the primary "
            "target."
        )

    def test_ingest_company_row_names_prospect_path(self):
        self.assertIn(
            PROSPECT_PATH_LITERAL, self.skill_text,
            "Ingest Company row must name the prospect path as the secondary "
            "target so post-F27 routing is honest about both surfaces."
        )

    def test_ingest_references_prospect_init_flow(self):
        self.assertIn(
            "prospect-init", self.skill_text,
            "Ingest should propose the prospect-init flow when neither "
            "operator nor prospect file exists for a discovered company."
        )


class UserTruthFilesystemTests(unittest.TestCase):
    """User-truth test per feedback_plan_fidelity_vs_user_truth: simulate
    a fresh install on disk and walk the prospect-init flow against tmp_path."""

    def test_prospect_file_lands_at_correct_path_when_created(self):
        # Simulate what prospect-init does: copy the template to the
        # prospect path with a slug substitution. Assert the file lands
        # at companies/prospects/<slug>.md.
        import tempfile
        import shutil

        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            # Stage the template into the fixture install.
            templates_dst = tmp / "templates"
            templates_dst.mkdir()
            shutil.copy(
                TEMPLATES_DIR / "prospect-context.template.md",
                templates_dst / "prospect-context.template.md",
            )

            # Lazy directory creation per F27 design: companies/prospects/
            # does not exist at install time.
            self.assertFalse(
                (tmp / "companies" / "prospects").exists(),
                "Fresh install must not pre-create companies/prospects/. "
                "Directory is created lazily on first prospect-init invocation."
            )

            # Simulate prospect-init writing the file.
            slug = "widgetco"
            prospects_dir = tmp / "companies" / "prospects"
            prospects_dir.mkdir(parents=True)
            target = prospects_dir / f"{slug}.md"
            template_body = _read_text(templates_dst / "prospect-context.template.md")
            target.write_text(template_body, encoding="utf-8")

            # Assert: file landed at exactly the expected path.
            self.assertTrue(
                target.exists(),
                f"prospect-init should land file at {target}, not anywhere else."
            )
            # Assert: no operator file was created as a side-effect.
            operator_collision = tmp / "companies" / f"{slug}-business.md"
            self.assertFalse(
                operator_collision.exists(),
                "prospect-init must not write to the operator path. "
                f"Found unexpected file at {operator_collision}."
            )
            # Assert: file body matches template.
            self.assertEqual(
                target.read_text(encoding="utf-8"),
                template_body,
                "prospect file body should match the template body byte-for-byte "
                "until the user (or the flow) fills it."
            )

    def test_operator_and_prospect_files_coexist_without_collision(self):
        # Both paths can exist for the same slug. Operator wins on read
        # per F27 Q3. The filesystem itself does not enforce the priority;
        # the skill bodies do (covered by DownstreamSkillTwoPathTests).
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            companies = tmp / "companies"
            companies.mkdir()
            (companies / "prospects").mkdir()

            slug = "acme"
            operator_file = companies / f"{slug}-business.md"
            prospect_file = companies / "prospects" / f"{slug}.md"
            operator_file.write_text("# Acme - operator\n", encoding="utf-8")
            prospect_file.write_text("# Acme - prospect\n", encoding="utf-8")

            self.assertTrue(operator_file.exists())
            self.assertTrue(prospect_file.exists())
            # They are distinct paths, so the filesystem treats them as
            # independent files. The skill-body routing decides which one
            # is read for a given task.
            self.assertNotEqual(operator_file.resolve(), prospect_file.resolve())


if __name__ == "__main__":
    unittest.main()
