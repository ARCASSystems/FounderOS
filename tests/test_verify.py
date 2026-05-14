"""
Tests for the v1.21 verify workstream.
Asserts behavioral content in the verify skill body and command file.
No mocking - reads actual files to verify documented behavior is present.
"""
import os
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_file(rel_path):
    path = os.path.join(REPO, rel_path)
    with open(path, encoding='utf-8') as f:
        return f.read()


class VerifySkillTests(unittest.TestCase):

    def setUp(self):
        self.body = read_file('skills/verify/SKILL.md')

    def test_skill_documents_eight_checks(self):
        # Each check must be named in a section heading
        for n in range(1, 9):
            self.assertIn(f'Check {n}', self.body,
                          f'Check {n} not documented in verify skill')

    def test_skill_documents_output_format(self):
        body = self.body
        self.assertIn('[PASS]', body)
        self.assertIn('[WARN]', body)
        self.assertIn('[FAIL]', body)
        # Max 30 lines specified
        self.assertIn('30 lines', body)
        # No emoji rule
        self.assertIn('No emoji', body)

    def test_skill_documents_no_auto_fix(self):
        body_lower = self.body.lower()
        self.assertIn('never auto-fixes', body_lower)
        self.assertIn('only reports', body_lower)

    def test_skill_distinguishes_warn_vs_fail(self):
        body = self.body
        self.assertIn('[WARN]', body)
        self.assertIn('[FAIL]', body)
        # Must explain the distinction
        self.assertIn('degraded', body.lower())
        self.assertIn('broken', body.lower())

    def test_check_1_plugin_surface_documented(self):
        self.assertIn('Plugin surface integrity', self.body)
        self.assertIn('skills/index.md', self.body)
        self.assertIn('plugin.json', self.body)

    def test_check_2_hooks_documented(self):
        self.assertIn('Hooks installed', self.body)
        self.assertIn('SessionStart', self.body)
        self.assertIn('settings.json', self.body)

    def test_check_3_scripts_documented(self):
        self.assertIn('Scripts present', self.body)
        self.assertIn('brain-snapshot.py', self.body)
        self.assertIn('wiki-build.py', self.body)
        self.assertIn('query.py', self.body)
        self.assertIn('memory-diff.py', self.body)
        self.assertIn('menu.py', self.body)
        self.assertIn('observation-rollup.py', self.body)
        self.assertIn('py_compile', self.body)
        self.assertIn('7/7', self.body)

    def test_check_4_mcp_documented(self):
        self.assertIn('MCP availability', self.body)
        self.assertIn('CLAUDE.md', self.body)

    def test_check_5_free_tier_documented(self):
        self.assertIn('Free-tier floor', self.body)
        self.assertIn('ANTHROPIC_API_KEY', self.body)
        self.assertIn('OPENAI_API_KEY', self.body)

    def test_check_6_wiki_documented(self):
        self.assertIn('Wiki integrity', self.body)
        self.assertIn('[[', self.body)

    def test_check_7_cadence_documented(self):
        self.assertIn('Cadence staleness', self.body)
        self.assertIn('daily-anchors.md', self.body)
        self.assertIn('weekly-commitments.md', self.body)

    def test_check_8_auto_memory_documented(self):
        self.assertIn('Auto-memory presence', self.body)
        self.assertIn('MEMORY.md', self.body)

    def test_skill_summary_footer_documented(self):
        # Summary footer must mention next action
        body_lower = self.body.lower()
        self.assertIn('next:', body_lower)
        self.assertIn('all green', body_lower)


class VerifyCommandTests(unittest.TestCase):

    def test_command_file_exists(self):
        # Commands follow the repo convention: filename is the part after "founder-os:"
        # so /founder-os:verify lives at .claude/commands/verify.md
        path = os.path.join(REPO, '.claude', 'commands', 'verify.md')
        self.assertTrue(os.path.exists(path),
                        'verify.md command file missing')

    def test_command_invokes_verify_skill(self):
        body = read_file('.claude/commands/verify.md')
        self.assertIn('skills/verify/SKILL.md', body)

    def test_command_is_read_only(self):
        body = read_file('.claude/commands/verify.md')
        self.assertIn('Read-only', body)

    def test_command_states_no_auto_fix(self):
        body = read_file('.claude/commands/verify.md')
        body_lower = body.lower()
        self.assertIn('never auto-fixes', body_lower)


class VerifyReadmeTests(unittest.TestCase):

    def test_readme_mentions_verify_natural_language(self):
        body = read_file('README.md')
        self.assertIn('verify the OS', body)

    def test_readme_mentions_verify_slash_command(self):
        body = read_file('README.md')
        self.assertIn('/founder-os:verify', body)


if __name__ == '__main__':
    unittest.main()
