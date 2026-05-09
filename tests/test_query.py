import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import date, timedelta
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
QUERY_SCRIPT = REPO_ROOT / "scripts" / "query.py"
TEMPLATE_QUERY_SCRIPT = REPO_ROOT / "templates" / "scripts" / "query.py"
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "query-corpus"


def run_query(*args: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(QUERY_SCRIPT), "--root", str(FIXTURE_ROOT), *args]
    return subprocess.run(cmd, text=True, capture_output=True)


def load_query_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class QueryCliTests(unittest.TestCase):
    def test_bare_index_matches_explicit_index(self) -> None:
        bare = run_query("outreach", "stalled")
        explicit = run_query("--mode", "index", "outreach", "stalled")

        self.assertEqual(bare.returncode, 0)
        self.assertEqual(explicit.returncode, 0)
        self.assertEqual(bare.stdout, explicit.stdout)

    def test_index_caps_results_and_shows_id(self) -> None:
        result = run_query("outreach", "stalled")

        self.assertEqual(result.returncode, 0)
        rows = re.findall(r"^\d+\. ", result.stdout, flags=re.MULTILINE)
        self.assertGreaterEqual(len(rows), 1)
        self.assertLessEqual(len(rows), 10)
        self.assertIn("(id: flag-2026-05-04-001)", result.stdout)

    def test_timeline_is_chronological_and_windowed(self) -> None:
        result = run_query("--mode", "timeline", "--anchor", "CLAUDE.md")

        self.assertEqual(result.returncode, 0)
        dates = re.findall(r"^(2026-\d{2}-\d{2}) - ", result.stdout, flags=re.MULTILINE)
        self.assertGreaterEqual(len(dates), 2)
        self.assertEqual(dates, sorted(dates))
        self.assertIn("2026-05-04 - brain/flags.md", result.stdout)
        self.assertNotIn("2026-04-20 - brain/patterns.md", result.stdout)
        self.assertNotIn("tests/hidden.md", result.stdout)

    def test_full_mode_resolves_frontmatter_and_heading_ids(self) -> None:
        result = run_query(
            "--mode",
            "full",
            "--ids",
            "know-2026-05-08-001,flag-2026-05-04-001",
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("=== know-2026-05-08-001 (brain/knowledge/sales.md) ===", result.stdout)
        self.assertIn("Signals from early outreach live here.", result.stdout)
        self.assertIn("=== flag-2026-05-04-001 (brain/flags.md) ===", result.stdout)
        self.assertIn("Pipeline follow-up stalled after the first outreach pass.", result.stdout)

    def test_punctuation_guard_exits_two(self) -> None:
        result = run_query("?")

        self.assertEqual(result.returncode, 2)
        self.assertIn("No searchable tokens", result.stdout)

    def test_no_argument_usage_exits_two(self) -> None:
        result = run_query()

        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage: python scripts/query.py <question>", result.stdout)


class ParseEdgesTests(unittest.TestCase):
    """Direct unit tests for parse_edges in scripts/query.py and its template
    mirror. Confirms both flat curated entries and the nested wiki_links block
    written by scripts/wiki-build.py round-trip into edges."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.live = load_query_module(QUERY_SCRIPT, "query_live")
        cls.template = load_query_module(TEMPLATE_QUERY_SCRIPT, "query_template")

    def _both(self, text: str) -> list[list[tuple[str, str]]]:
        return [self.live.parse_edges(text), self.template.parse_edges(text)]

    def test_flat_from_to_pairs(self) -> None:
        text = (
            "relations:\n"
            "  - from: a.md\n"
            "    to: b.md\n"
            "  - from: c.md\n"
            "    to: d.md\n"
        )
        for edges in self._both(text):
            self.assertEqual(edges, [("a.md", "b.md"), ("c.md", "d.md")])

    def test_flat_source_target_pairs(self) -> None:
        text = (
            "relations:\n"
            "  - source: a.md\n"
            "    target: b.md\n"
        )
        for edges in self._both(text):
            self.assertEqual(edges, [("a.md", "b.md")])

    def test_nested_wiki_links_block(self) -> None:
        text = (
            "wiki_links:\n"
            "  - source: cadence/daily-anchors.md\n"
            "    targets:\n"
            "      - \"context/priorities\"\n"
            "      - \"brain/log\"\n"
            "  - source: roles/coo.md\n"
            "    targets:\n"
            "      - \"rules/operating-rules\"\n"
        )
        for edges in self._both(text):
            self.assertIn(("cadence/daily-anchors.md", "context/priorities"), edges)
            self.assertIn(("cadence/daily-anchors.md", "brain/log"), edges)
            self.assertIn(("roles/coo.md", "rules/operating-rules"), edges)

    def test_mixed_curated_and_wiki_links(self) -> None:
        text = (
            "relations:\n"
            "  - source: a.md\n"
            "    target: b.md\n"
            "wiki_links:\n"
            "  - source: c.md\n"
            "    targets:\n"
            "      - \"d\"\n"
        )
        for edges in self._both(text):
            self.assertIn(("a.md", "b.md"), edges)
            self.assertIn(("c.md", "d"), edges)

    def test_targets_block_does_not_swallow_next_source(self) -> None:
        # Without the source-line exit guard, the second source label would
        # have been captured as a fake target of the first source.
        text = (
            "wiki_links:\n"
            "  - source: a.md\n"
            "    targets:\n"
            "      - \"b\"\n"
            "  - source: c.md\n"
            "    targets:\n"
            "      - \"d\"\n"
        )
        for edges in self._both(text):
            self.assertEqual(
                sorted(edges),
                [("a.md", "b"), ("c.md", "d")],
            )

    def test_quoted_target_starting_with_key_word_is_kept(self) -> None:
        # A quoted target whose value begins with `source:`/`target:`/`from:`/
        # `to:` is still a target, not a record boundary. The previous parser
        # stripped the quotes first and then treated the inner string as a key
        # match, dropping the edge.
        text = (
            "wiki_links:\n"
            "  - source: a.md\n"
            "    targets:\n"
            "      - \"source: note\"\n"
            "      - \"target: another note\"\n"
            "      - \"plain target\"\n"
        )
        for edges in self._both(text):
            self.assertIn(("a.md", "source: note"), edges)
            self.assertIn(("a.md", "target: another note"), edges)
            self.assertIn(("a.md", "plain target"), edges)

    def test_quoted_target_with_escaped_quote_round_trips(self) -> None:
        # scripts/wiki-build.py escapes a literal `"` inside a target as `\"`
        # before writing it inside double quotes. parse_edges must reverse the
        # escape so the edge name contains the original character.
        text = (
            "wiki_links:\n"
            "  - source: a.md\n"
            "    targets:\n"
            r'      - "foo\"bar"' + "\n"
        )
        for edges in self._both(text):
            self.assertIn(("a.md", 'foo"bar'), edges)

    def test_single_quoted_target_preserves_backslash(self) -> None:
        # A hand-written single-quoted YAML target like 'foo\"bar' is NOT a
        # double-quoted escape -- the backslash is literal. The unescape must
        # only operate on the matching quote character. Cross-quote unescape
        # (treating \" as escape inside a single-quoted string) would corrupt
        # the literal backslash.
        # Python string literal: "'foo\\\"bar'" = single-quote, f, o, o,
        # backslash, double-quote, b, a, r, single-quote.
        text = (
            "wiki_links:\n"
            "  - source: a.md\n"
            "    targets:\n"
            "      - 'foo\\\"bar'\n"
        )
        for edges in self._both(text):
            self.assertIn(("a.md", "foo\\\"bar"), edges)
            self.assertNotIn(("a.md", 'foo"bar'), edges)

    def test_flat_double_quoted_value_unescapes(self) -> None:
        # The same delimiter-aware unescape applies to flat curated entries.
        # A double-quoted value with an inner \" should round-trip to a
        # literal " in the edge.
        text = (
            "relations:\n"
            "  - source: \"foo\\\"bar\"\n"
            "    target: \"baz\\\"qux\"\n"
        )
        for edges in self._both(text):
            self.assertEqual(edges, [('foo"bar', 'baz"qux')])

    def test_flat_single_quoted_value_unescapes(self) -> None:
        # A single-quoted value with an inner \' should round-trip to a
        # literal ' in the edge.
        text = (
            "relations:\n"
            "  - source: 'a.md'\n"
            "    target: 'don\\'t panic'\n"
        )
        for edges in self._both(text):
            self.assertEqual(edges, [("a.md", "don't panic")])

    def test_flat_single_quoted_value_preserves_backslash(self) -> None:
        # Single-quoted value with a literal \" is NOT a double-quoted
        # escape; the backslash must survive.
        text = (
            "relations:\n"
            "  - source: 'a.md'\n"
            "    target: 'foo\\\"bar'\n"
        )
        for edges in self._both(text):
            self.assertEqual(edges, [("a.md", "foo\\\"bar")])
            self.assertNotIn(("a.md", 'foo"bar'), edges)


class CandidateFilesScopeTests(unittest.TestCase):
    """Confirms candidate_files walks every prefix in INCLUDE_PREFIXES so a
    node the persisted graph references can also surface as a query
    candidate. Locks in parity with scripts/wiki-build.py:INCLUDE_PREFIXES."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.live = load_query_module(QUERY_SCRIPT, "query_live_scope")
        cls.template = load_query_module(TEMPLATE_QUERY_SCRIPT, "query_template_scope")

    def _build_fixture(self, tmp: Path) -> None:
        # Create one in-scope markdown under each of the eight INCLUDE_PREFIXES
        # plus a few that should be excluded (skills/, raw/, .git/).
        for sub in ("core", "context", "cadence", "brain", "network",
                    "companies", "roles", "rules"):
            (tmp / sub).mkdir(parents=True, exist_ok=True)
            (tmp / sub / f"{sub}-node.md").write_text(
                f"# {sub} node\n", encoding="utf-8"
            )
        (tmp / "skills").mkdir()
        (tmp / "skills" / "should-be-skipped.md").write_text("# skip\n", encoding="utf-8")
        (tmp / "raw").mkdir()
        (tmp / "raw" / "should-be-skipped.md").write_text("# skip\n", encoding="utf-8")
        (tmp / "context" / "clients.md").write_text("# clients\n", encoding="utf-8")
        (tmp / "cadence" / "daily-anchors.md").write_text(
            "# Today: 2026-05-09\n", encoding="utf-8"
        )

    def _check(self, module) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._build_fixture(tmp)
            files = module.candidate_files(tmp)
            rel_names = {p.relative_to(tmp).as_posix() for p in files}

            # Every prefix must contribute at least one node.
            for sub in ("core", "context", "cadence", "brain", "network",
                        "companies", "roles", "rules"):
                self.assertTrue(
                    any(name.startswith(f"{sub}/") for name in rel_names),
                    f"no {sub}/ node surfaced; got {sorted(rel_names)}",
                )
            # Specific files the prior review called out as previously missing.
            self.assertIn("context/clients.md", rel_names)
            self.assertIn("cadence/daily-anchors.md", rel_names)
            # skills/ and raw/ stay out of scope.
            self.assertFalse(
                any(name.startswith("skills/") for name in rel_names),
                f"skills/ leaked into candidates: {sorted(rel_names)}",
            )
            self.assertFalse(
                any(name.startswith("raw/") for name in rel_names),
                f"raw/ leaked into candidates: {sorted(rel_names)}",
            )

    def test_live_walks_every_include_prefix(self) -> None:
        self._check(self.live)

    def test_template_walks_every_include_prefix(self) -> None:
        self._check(self.template)


class ScoringBehaviorTests(unittest.TestCase):
    """v1.20 query scoring additions: zero-score fallback, stop-word filter,
    light stemming, recency bonus, rant-keyword inclusion. Each test runs
    against scripts/query.py via subprocess to verify the user-visible
    output, plus the in-process module for the unit-level helpers.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.live = load_query_module(QUERY_SCRIPT, "query_live_scoring")
        cls.template = load_query_module(TEMPLATE_QUERY_SCRIPT, "query_template_scoring")

    def _run_in_corpus(self, corpus: Path, *args: str) -> subprocess.CompletedProcess[str]:
        cmd = [sys.executable, str(QUERY_SCRIPT), "--root", str(corpus), *args]
        return subprocess.run(cmd, text=True, capture_output=True)

    def _make_corpus(self, tmp: Path) -> None:
        """Minimal in-scope corpus: one file with the marker token."""
        (tmp / "context").mkdir()
        (tmp / "context" / "priorities.md").write_text(
            "# Priorities\n\nLaunch outreach next week.\n", encoding="utf-8"
        )

    def test_zero_score_fallback_returns_no_match_block_live(self) -> None:
        # The query argument is a deliberately unique token nothing in the
        # fixture corpus will match. Old behaviour: fall back to graph-
        # popular nodes. v1.20: return the honest no-match block instead.
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._make_corpus(tmp)
            result = self._run_in_corpus(
                tmp, "zzzz-no-such-token-anywhere-zzzz"
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("No positive match for", result.stdout)
        self.assertIn("Suggestions:", result.stdout)
        self.assertIn("Rephrase with a more specific term.", result.stdout)
        self.assertIn("rant", result.stdout)
        self.assertIn("/founder-os:brain-pass", result.stdout)
        # Zero-score fallback must NOT print the "Top results:" header,
        # otherwise users see the no-match block AND a list of guesses.
        self.assertNotIn("Top results:", result.stdout)

    def _both_modules(self):
        return [self.live, self.template]

    def test_stop_words_are_filtered(self) -> None:
        # Stop words like "the", "is", "what" must be removed from the
        # tokenized question. If they leaked through, every file with the
        # stop word would score and the index would be noisy.
        for module in self._both_modules():
            tokens = module.tokenize("what is the launch")
            self.assertNotIn("the", tokens)
            self.assertNotIn("is", tokens)
            self.assertNotIn("what", tokens)
            self.assertIn("launch", tokens)

    def test_stemming_matches_plurals(self) -> None:
        # "decisions" should stem to the same root as "decision" so a
        # query for "decisions" matches a file containing "decision".
        # This is the canonical stemming guarantee the plan calls out.
        for module in self._both_modules():
            self.assertEqual(
                module.stem("decisions"), module.stem("decision"),
                f"plural and singular must share a stem in {module.__name__}",
            )
            # Past-tense suffix should also collapse to the verb root.
            self.assertEqual(
                module.stem("launched"), module.stem("launches"),
                f"past tense and plural verb must share a stem in {module.__name__}",
            )

    def test_recency_bonus_surfaces_recent_file(self) -> None:
        # Two files containing the same single-token match. The recent
        # file has its mtime set to today; the older file is set 30 days
        # ago. The recent file must rank above the older one.
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            (tmp / "context").mkdir()
            recent = tmp / "context" / "recent.md"
            older = tmp / "context" / "older.md"
            recent.write_text("# Recent\n\nlaunch plan\n", encoding="utf-8")
            older.write_text("# Older\n\nlaunch plan\n", encoding="utf-8")
            now = time.time()
            old_ts = now - 30 * 86400
            os.utime(older, (old_ts, old_ts))
            os.utime(recent, (now, now))

            for module in self._both_modules():
                today = date.today()
                scores = module.score_files(
                    [recent, older],
                    tmp,
                    {"launch", "plan"},
                    today=today,
                )
                recent_score = scores["context/recent.md"][0]
                older_score = scores["context/older.md"][0]
                self.assertGreater(
                    recent_score, older_score,
                    f"recent file must score higher than older file in {module.__name__}; "
                    f"got recent={recent_score}, older={older_score}",
                )

    def test_rant_keyword_includes_brain_rants(self) -> None:
        # Default scope excludes brain/rants/. A query containing a rant
        # trigger word must include rant entries in the candidate set.
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            (tmp / "brain" / "rants").mkdir(parents=True)
            (tmp / "context").mkdir()
            rant_file = tmp / "brain" / "rants" / "2026-05-07.md"
            rant_file.write_text(
                "# Rant\n\nfrustrated about pipeline\n", encoding="utf-8"
            )
            (tmp / "context" / "priorities.md").write_text(
                "# Priorities\n\npipeline launch\n", encoding="utf-8"
            )

            # Default query: rant file is excluded.
            default = self._run_in_corpus(tmp, "pipeline")
            self.assertEqual(default.returncode, 0)
            self.assertNotIn("brain/rants/2026-05-07.md", default.stdout)

            # Rant query: rant file is included.
            rant = self._run_in_corpus(tmp, "what was I ranting about")
            self.assertEqual(rant.returncode, 0)
            self.assertIn("brain/rants/2026-05-07.md", rant.stdout)

    def test_is_rant_query_detects_triggers(self) -> None:
        for module in self._both_modules():
            self.assertTrue(module.is_rant_query("what was I ranting about"))
            self.assertTrue(module.is_rant_query("show me the latest brain dump"))
            self.assertTrue(module.is_rant_query("avoidance pattern this week"))
            self.assertTrue(module.is_rant_query("a raw vent from yesterday"))
            self.assertFalse(module.is_rant_query("what is the launch plan"))


if __name__ == "__main__":
    unittest.main()
