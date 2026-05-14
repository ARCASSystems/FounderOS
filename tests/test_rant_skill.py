from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
RANT_COMMAND = REPO_ROOT / ".claude" / "commands" / "rant.md"


class RantRoutingTests(unittest.TestCase):
    """Asserts the v1.23 capture-first contract.

    Pre-v1.23 the command asked one qualifying question BEFORE capturing.
    If the user walked away or sent an unrelated message, the rant was lost.
    v1.23 inverted the order: write to brain/rants/ unconditionally first,
    then offer routing on a second line. The user can ignore the routing
    offer entirely and the rant is still safe on disk for /dream to pick up.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.body = RANT_COMMAND.read_text(encoding="utf-8")

    def test_capture_first_contract_documented(self) -> None:
        """The body must explicitly state that capture happens before any
        routing question. The phrase 'Capture first' is the contract marker."""
        self.assertIn("Capture first, qualify second.", self.body)

    def test_capture_write_happens_before_routing_question(self) -> None:
        """The Step 1 (capture) heading must appear before the Step 2 (routing
        offer) heading. If the order flips, the contract is violated."""
        step1_idx = self.body.find("Step 1: Capture immediately")
        step2_idx = self.body.find("Step 2: Offer routing")
        self.assertGreater(step1_idx, 0, "Step 1 capture heading missing")
        self.assertGreater(step2_idx, step1_idx, "Step 2 must come after Step 1")

    def test_routing_offer_is_optional(self) -> None:
        """The Step 2 routing offer must explicitly state that the user can
        ignore it. Otherwise a fresh user might think they MUST answer."""
        self.assertIn("ignore this and /dream will pick it up later", self.body)

    def test_rules_state_capture_is_unconditional(self) -> None:
        """One of the Rules must explicitly say capture happens unconditionally
        (subject to the private-tag filter). This prevents accidental
        regression to a qualify-then-write flow."""
        self.assertIn(
            "The capture write happens FIRST and unconditionally",
            self.body,
        )

    def test_routes_to_specific_skills(self) -> None:
        """The four route words must still hand off to the expected skills.
        These mappings are stable from pre-v1.23 - only the order of capture
        vs question changed."""
        for skill in (
            "decision-framework",
            "linkedin-post",
            "email-drafter",
            "proposal-writer",
            "client-update",
            "priority-triage",
            "forcing-questions",
            "brain-log",
        ):
            with self.subTest(skill=skill):
                self.assertIn(skill, self.body)

    def test_capture_path_targets_brain_rants_with_dated_filename(self) -> None:
        """The capture must land in brain/rants/<YYYY-MM-DD>.md so the
        SessionStart brief and /dream can find it by frontmatter scan."""
        self.assertIn("brain/rants/<YYYY-MM-DD>.md", self.body)

    def test_frontmatter_includes_processed_false_and_mode_unknown(self) -> None:
        """The entry frontmatter must include processed: false (so /dream
        and the SessionStart brief can count it) and mode: unknown (so a
        subsequent route choice can overwrite the field without ambiguity)."""
        self.assertIn("processed: false", self.body)
        self.assertIn("mode: unknown", self.body)

    def test_private_tag_filter_is_documented(self) -> None:
        """Per rules/operating-rules.md, every persistent write must honor the
        <private>...</private> filter. The rant capture is a persistent write."""
        self.assertIn("<private>...</private>", self.body)

    def test_two_line_output_cap(self) -> None:
        """The user-visible output before the user replies is capped at two
        lines (confirmation + routing offer). Anything more pulls attention
        away from the user's next thought."""
        self.assertIn("Do not exceed two lines of output", self.body)


if __name__ == "__main__":
    unittest.main()
