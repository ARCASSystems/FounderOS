"""
Tests for the v1.21 queue workstream.
Asserts behavioral content in skill body, template, slash command, and hooks.
No mocking - reads actual files to verify documented behavior is present.
"""
import os
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_file(rel_path):
    path = os.path.join(REPO, rel_path)
    with open(path, encoding='utf-8') as f:
        return f.read()


class QueueTemplateTests(unittest.TestCase):

    def setUp(self):
        self.body = read_file('templates/cadence/queue.md')

    def test_template_has_three_sections(self):
        self.assertIn('## ACTIVE', self.body)
        self.assertIn('## BACKLOG', self.body)
        self.assertIn('## DONE', self.body)

    def test_template_has_conventions_block(self):
        self.assertIn('## Conventions', self.body)
        self.assertIn('YYYY-MM-DD', self.body)
        self.assertIn('next action', self.body)
        self.assertIn('source', self.body)

    def test_template_documents_3_item_cap(self):
        self.assertIn('max 3', self.body.lower())
        self.assertIn('non-negotiable', self.body.lower())


class QueueSkillTests(unittest.TestCase):

    def setUp(self):
        self.body = read_file('skills/queue/SKILL.md')

    def test_skill_body_documents_five_operations(self):
        for op in ['read', 'add', 'start', 'done', 'park']:
            self.assertIn(f'### {op}', self.body.lower(),
                          f'Operation "{op}" not documented in queue skill')

    def test_skill_documents_3_item_gate(self):
        body_lower = self.body.lower()
        self.assertIn('hard precondition', body_lower)
        self.assertIn('does not add', body_lower)
        self.assertIn('3 entries', body_lower)

    def test_skill_documents_natural_language_invocations(self):
        self.assertIn("what's on my plate", self.body)
        self.assertIn("what's moving", self.body)
        self.assertIn("show me the queue", self.body)
        self.assertIn("add to queue", self.body)
        self.assertIn("done with", self.body)
        self.assertIn("park", self.body)

    def test_skill_documents_surface_points(self):
        body_lower = self.body.lower()
        self.assertIn('sessionstart', body_lower)
        self.assertIn('status', body_lower)
        self.assertIn('weekly-review', body_lower)

    def test_skill_reads_cadence_queue(self):
        self.assertIn('cadence/queue.md', self.body)

    def test_skill_documents_3_item_rule_explanation(self):
        # The plan requires two sentences explaining WHY the gate is a feature
        body_lower = self.body.lower()
        self.assertIn('feature', body_lower)
        self.assertIn('capacity', body_lower)


class QueueSlashCommandTests(unittest.TestCase):

    def test_command_file_exists(self):
        # Commands follow the repo convention: filename is the part after "founder-os:"
        # so /founder-os:queue lives at .claude/commands/queue.md
        path = os.path.join(REPO, '.claude', 'commands', 'queue.md')
        self.assertTrue(os.path.exists(path),
                        'queue.md command file missing')

    def test_command_invokes_queue_skill(self):
        body = read_file('.claude/commands/queue.md')
        self.assertIn('skills/queue/SKILL.md', body)

    def test_no_subcommand_files_created(self):
        cmd_dir = os.path.join(REPO, '.claude', 'commands')
        # No separate subcommand files - all operations handled by the single queue.md
        for name in ['queue-add.md', 'queue-start.md', 'queue-done.md', 'queue-park.md']:
            path = os.path.join(cmd_dir, name)
            self.assertFalse(os.path.exists(path),
                             f'Subcommand file {name} should not exist')


class QueueSessionStartTests(unittest.TestCase):

    def test_bash_hook_renders_active_section(self):
        body = read_file('.claude/hooks/session-start-brief.sh')
        self.assertIn('cadence/queue.md', body)
        self.assertIn('Active:', body)
        self.assertIn('ACTIVE', body)

    def test_powershell_hook_renders_active_section(self):
        body = read_file('.claude/hooks/session-start-brief.ps1')
        self.assertIn('cadence\\queue.md', body)
        self.assertIn('Active:', body)
        self.assertIn('ACTIVE', body)

    def test_bash_hook_handles_missing_queue_file(self):
        body = read_file('.claude/hooks/session-start-brief.sh')
        # Must have a branch for when queue.md does not exist
        self.assertIn('queue empty', body)
        self.assertIn('add to queue', body)

    def test_powershell_hook_handles_missing_queue_file(self):
        body = read_file('.claude/hooks/session-start-brief.ps1')
        self.assertIn('queue empty', body)
        self.assertIn('add to queue', body)

    def test_bash_hook_active_section_comes_before_flags(self):
        body = read_file('.claude/hooks/session-start-brief.sh')
        active_pos = body.find('Active:')
        flags_pos = body.find('--- Open flags ---')
        self.assertGreater(flags_pos, active_pos,
                           'Active queue section must appear before flags section')

    def test_powershell_hook_active_section_comes_before_flags(self):
        body = read_file('.claude/hooks/session-start-brief.ps1')
        active_pos = body.find('Active:')
        flags_pos = body.find('--- Open flags ---')
        self.assertGreater(flags_pos, active_pos,
                           'Active queue section must appear before flags section')


class QueueSetupWizardTests(unittest.TestCase):

    def test_setup_wizard_copies_queue_template(self):
        body = read_file('skills/founder-os-setup/SKILL.md')
        self.assertIn('templates/cadence/queue.md', body)
        self.assertIn('cadence/queue.md', body)

    def test_setup_wizard_does_not_overwrite_existing_queue(self):
        body = read_file('skills/founder-os-setup/SKILL.md')
        self.assertIn('already present', body.lower())
        self.assertIn('leaving untouched', body.lower())


class QueueStatusIntegrationTests(unittest.TestCase):

    def test_readiness_check_has_queue_bucket(self):
        body = read_file('skills/readiness-check/SKILL.md')
        self.assertIn('Queue', body)
        self.assertIn('5%', body)

    def test_readiness_check_queue_logic_described(self):
        body = read_file('skills/readiness-check/SKILL.md')
        body_lower = body.lower()
        self.assertIn('active > 0', body_lower)
        self.assertIn('done', body_lower)
        self.assertIn('last 7 days', body_lower)


class QueueWeeklyReviewIntegrationTests(unittest.TestCase):

    def test_weekly_review_has_rolloff_step(self):
        body = read_file('skills/weekly-review/SKILL.md')
        self.assertIn('cadence/queue.md', body)
        self.assertIn('DONE', body)
        self.assertIn('brain/log.md', body)

    def test_weekly_review_surfaces_stuck_items(self):
        body = read_file('skills/weekly-review/SKILL.md')
        self.assertIn('14 days', body)
        self.assertIn('ACTIVE', body)
        self.assertIn('BACKLOG', body)


if __name__ == '__main__':
    unittest.main()
