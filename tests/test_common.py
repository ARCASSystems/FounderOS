"""
Unit tests for scripts/_common.py — the canonical wiki-layer scope helpers
shared by scripts/wiki-build.py and scripts/query.py.

These tests lock the contract that both scripts depend on: the prefix tuple,
the excluded-parts set, the path-classification function, the walker, and
the wikilink-target normaliser. See plans/v1.27-f38-rglob-consolidation-2026-05-22.md.
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
COMMON_SCRIPT = REPO_ROOT / "scripts" / "_common.py"


def load_common_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WikiLayerPrefixesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.common = load_common_module(COMMON_SCRIPT, "common_prefixes")

    def test_prefixes_are_exact_canonical_tuple(self) -> None:
        # Lock the canonical order so callers (wiki-build, query, future
        # scripts) cannot quietly disagree on which prefixes are wiki-layer.
        self.assertEqual(
            self.common.WIKI_LAYER_PREFIXES,
            ("core", "context", "cadence", "brain", "network",
             "companies", "roles", "rules"),
        )


class IsWikiLayerPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.common = load_common_module(COMMON_SCRIPT, "common_path")

    def test_in_scope_prefix_returns_true(self) -> None:
        self.assertTrue(self.common.is_wiki_layer_path("core/identity.md"))

    def test_top_level_file_returns_false(self) -> None:
        # CLAUDE.md sits at repo root and is not under any wiki prefix.
        # Query layer surfaces it via DEFAULT_FILES; the wiki-layer walk
        # must not include it.
        self.assertFalse(self.common.is_wiki_layer_path("CLAUDE.md"))

    def test_archive_part_excludes_path(self) -> None:
        self.assertFalse(self.common.is_wiki_layer_path("brain/archive/2026-05.md"))

    def test_unnormalised_backslash_returns_false(self) -> None:
        # Caller is responsible for forward-slash normalisation. A literal
        # backslash path does not match because its sole part doesn't equal
        # any wiki prefix string.
        self.assertFalse(self.common.is_wiki_layer_path("brain\\log.md"))

    def test_rants_part_excluded_by_default(self) -> None:
        self.assertFalse(self.common.is_wiki_layer_path("brain/rants/2026-05-21.md"))

    def test_rants_part_included_with_flag(self) -> None:
        self.assertTrue(
            self.common.is_wiki_layer_path(
                "brain/rants/2026-05-21.md", include_rants=True
            )
        )


class WikiLayerFilesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.common = load_common_module(COMMON_SCRIPT, "common_walker")

    def _build_fixture(self, tmp: Path) -> None:
        # One in-scope file per prefix.
        for sub in ("core", "context", "cadence", "brain", "network",
                    "companies", "roles", "rules"):
            (tmp / sub).mkdir(parents=True, exist_ok=True)
            (tmp / sub / f"{sub}-node.md").write_text(
                f"# {sub} node\n", encoding="utf-8"
            )
        # Out-of-scope siblings the walker must skip.
        (tmp / "skills").mkdir()
        (tmp / "skills" / "skip.md").write_text("# skip\n", encoding="utf-8")
        (tmp / "raw").mkdir()
        (tmp / "raw" / "skip.md").write_text("# skip\n", encoding="utf-8")
        (tmp / "tests").mkdir()
        (tmp / "tests" / "skip.md").write_text("# skip\n", encoding="utf-8")
        (tmp / ".git").mkdir()
        (tmp / ".git" / "skip.md").write_text("# skip\n", encoding="utf-8")
        (tmp / "brain" / "archive").mkdir()
        (tmp / "brain" / "archive" / "old.md").write_text("# old\n", encoding="utf-8")
        (tmp / "brain" / "rants").mkdir()
        (tmp / "brain" / "rants" / "2026-05-21.md").write_text(
            "# rant\n", encoding="utf-8"
        )

    def test_walk_returns_all_prefix_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._build_fixture(tmp)
            files = self.common.wiki_layer_files(tmp)
            rel_names = {p.relative_to(tmp).as_posix() for p in files}

            for sub in ("core", "context", "cadence", "brain", "network",
                        "companies", "roles", "rules"):
                self.assertIn(f"{sub}/{sub}-node.md", rel_names)

    def test_walk_excludes_out_of_scope_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._build_fixture(tmp)
            files = self.common.wiki_layer_files(tmp)
            rel_names = {p.relative_to(tmp).as_posix() for p in files}

            self.assertNotIn("skills/skip.md", rel_names)
            self.assertNotIn("raw/skip.md", rel_names)
            self.assertNotIn("tests/skip.md", rel_names)
            self.assertNotIn(".git/skip.md", rel_names)
            self.assertNotIn("brain/archive/old.md", rel_names)

    def test_rants_excluded_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._build_fixture(tmp)
            files = self.common.wiki_layer_files(tmp)
            rel_names = {p.relative_to(tmp).as_posix() for p in files}
            self.assertNotIn("brain/rants/2026-05-21.md", rel_names)

    def test_rants_included_with_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._build_fixture(tmp)
            files = self.common.wiki_layer_files(tmp, include_rants=True)
            rel_names = {p.relative_to(tmp).as_posix() for p in files}
            self.assertIn("brain/rants/2026-05-21.md", rel_names)


class NormalizeWikilinkTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.common = load_common_module(COMMON_SCRIPT, "common_normalize")

    def test_strips_trailing_md(self) -> None:
        self.assertEqual(
            self.common.normalize_wikilink_target("brain/log.md"),
            "brain/log",
        )

    def test_preserves_anchor_after_md_strip(self) -> None:
        self.assertEqual(
            self.common.normalize_wikilink_target("brain/log.md#anchor"),
            "brain/log#anchor",
        )

    def test_converts_backslashes_to_forward_slashes(self) -> None:
        self.assertEqual(
            self.common.normalize_wikilink_target("brain\\log"),
            "brain/log",
        )

    def test_bare_slug_passes_through(self) -> None:
        self.assertEqual(
            self.common.normalize_wikilink_target("feedback_some_rule"),
            "feedback_some_rule",
        )


if __name__ == "__main__":
    unittest.main()
