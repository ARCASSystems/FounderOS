"""
Cross-script walk parity for the wiki-layer file set.

scripts/wiki-build.py and scripts/query.py both need to agree on which files
compose the wiki-layer graph: wiki-build writes the persisted edges, query
re-derives them in memory and merges with the persisted set. Before v1.27
F38, the two computed that set via two different mechanisms and were coupled
only by manual "also update" comments. These tests build a fixture corpus
and assert the two scripts produce the same wiki-layer file set, locking the
consolidation on the test side.

See plans/v1.27-f38-rglob-consolidation-2026-05-22.md.
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WIKI_BUILD_SCRIPT = REPO_ROOT / "scripts" / "wiki-build.py"
QUERY_SCRIPT = REPO_ROOT / "scripts" / "query.py"
COMMON_SCRIPT = REPO_ROOT / "scripts" / "_common.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_corpus(tmp: Path) -> None:
    """One in-scope .md file per wiki-layer prefix plus out-of-scope siblings."""
    for sub in ("core", "context", "cadence", "brain", "network",
                "companies", "roles", "rules"):
        (tmp / sub).mkdir(parents=True, exist_ok=True)
        (tmp / sub / f"{sub}-node.md").write_text(
            f"# {sub} node\n", encoding="utf-8"
        )
    # Out-of-scope: must be excluded from BOTH walks.
    (tmp / "skills").mkdir()
    (tmp / "skills" / "skip.md").write_text("# skip\n", encoding="utf-8")
    (tmp / "raw").mkdir()
    (tmp / "raw" / "skip.md").write_text("# skip\n", encoding="utf-8")
    (tmp / "brain" / "archive").mkdir()
    (tmp / "brain" / "archive" / "old.md").write_text("# old\n", encoding="utf-8")
    (tmp / "brain" / "rants").mkdir()
    (tmp / "brain" / "rants" / "2026-05-21.md").write_text(
        "# rant\n", encoding="utf-8"
    )


class WalkParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.common = _load_module(COMMON_SCRIPT, "walk_parity_common")
        cls.wiki_build = _load_module(WIKI_BUILD_SCRIPT, "walk_parity_wiki_build")
        cls.query = _load_module(QUERY_SCRIPT, "walk_parity_query")

    def test_wiki_build_and_query_agree_on_wiki_layer_file_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            _build_corpus(tmp)

            # wiki-build's view: the canonical helper from _common.
            wiki_build_set = {
                p.relative_to(tmp).as_posix()
                for p in self.common.wiki_layer_files(tmp)
            }

            # query's view: candidate_files minus the DEFAULT_FILES seed
            # that don't actually exist in the fixture (they include
            # CLAUDE.md, brain/relations.yaml, etc., which aren't created
            # by _build_corpus).
            query_set = {
                p.relative_to(tmp).as_posix()
                for p in self.query.candidate_files(tmp)
            }
            # Drop default-file seeds that may surface from the fixture; the
            # wiki-layer subset is what must agree.
            default_seeds = {
                p for p in self.query.DEFAULT_FILES
            }
            query_wiki_subset = {p for p in query_set if p not in default_seeds}

            self.assertEqual(query_wiki_subset, wiki_build_set)

    def test_archive_files_excluded_from_both(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            _build_corpus(tmp)

            wiki_build_set = {
                p.relative_to(tmp).as_posix()
                for p in self.common.wiki_layer_files(tmp)
            }
            query_set = {
                p.relative_to(tmp).as_posix()
                for p in self.query.candidate_files(tmp)
            }

            self.assertNotIn("brain/archive/old.md", wiki_build_set)
            self.assertNotIn("brain/archive/old.md", query_set)

    def test_rants_excluded_by_default_included_with_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            _build_corpus(tmp)

            without = {
                p.relative_to(tmp).as_posix()
                for p in self.common.wiki_layer_files(tmp, include_rants=False)
            }
            with_flag = {
                p.relative_to(tmp).as_posix()
                for p in self.common.wiki_layer_files(tmp, include_rants=True)
            }

            self.assertNotIn("brain/rants/2026-05-21.md", without)
            self.assertIn("brain/rants/2026-05-21.md", with_flag)


if __name__ == "__main__":
    unittest.main()
