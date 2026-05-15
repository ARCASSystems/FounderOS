"""Corpus test for scripts/user-prompt-capture.py detection accuracy.

Loads tests/fixtures/founder_utterances.txt (80 annotated lines, one prompt
per line) and asserts that detect_shape() returns the annotated shape for
every line. Failures report the offending line number, prompt, expected shape,
and actual shape so regressions are easy to locate.

Line format:
    <prompt text> # shape: <rant|named-entity|status-update|preference|none>

Lines starting with # are comments. Blank lines are skipped.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "user-prompt-capture.py"
CORPUS = REPO_ROOT / "tests" / "fixtures" / "founder_utterances.txt"

VALID_SHAPES = {"rant", "named-entity", "status-update", "preference", "none"}


def _load_module():
    spec = importlib.util.spec_from_file_location("user_prompt_capture", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


UPC = _load_module()


def _load_corpus() -> list[tuple[int, str, str]]:
    """Return list of (line_number, prompt, expected_shape)."""
    entries: list[tuple[int, str, str]] = []
    for line_num, raw_line in enumerate(
        CORPUS.read_text(encoding="utf-8").splitlines(), 1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "# shape:" not in line:
            raise ValueError(
                f"Line {line_num} missing '# shape:' annotation: {raw_line!r}"
            )
        prompt_part, shape_part = line.rsplit("# shape:", 1)
        prompt = prompt_part.strip()
        shape = shape_part.strip()
        if shape not in VALID_SHAPES:
            raise ValueError(
                f"Line {line_num} has unknown shape {shape!r}: {raw_line!r}"
            )
        entries.append((line_num, prompt, shape))
    return entries


class CaptureCorpusTests(unittest.TestCase):
    def test_all_corpus_lines_match_annotation(self) -> None:
        """Every annotated line in founder_utterances.txt must match detect_shape()."""
        entries = _load_corpus()
        self.assertGreaterEqual(
            len(entries), 80, "corpus must have at least 80 annotated lines"
        )
        for line_num, prompt, expected in entries:
            with self.subTest(line=line_num, prompt=prompt[:60]):
                actual_raw = UPC.detect_shape(prompt)
                actual = actual_raw if actual_raw is not None else "none"
                self.assertEqual(
                    actual,
                    expected,
                    f"line {line_num}: expected {expected!r}, got {actual!r}\n"
                    f"  prompt: {prompt!r}",
                )


if __name__ == "__main__":
    unittest.main()
