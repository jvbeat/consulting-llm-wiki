"""The lint must stay silent on a clean vault and catch every lock the example breaks on purpose."""
import os
import shutil
import sys
import tempfile
import textwrap
import unittest
import datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import lint  # noqa: E402

TODAY = dt.date(2026, 10, 26)


def errors(findings):
    return sorted((f['check'], f['file']) for f in findings if f['severity'] == 'ERROR')


class TemplateIsClean(unittest.TestCase):
    def test_template_has_no_errors_or_warnings(self):
        findings = lint.check(os.path.join(ROOT, 'template'), TODAY)
        self.assertEqual([f for f in findings if f['severity'] != 'INFO'], [])


class ExampleBreaksEveryLock(unittest.TestCase):
    def setUp(self):
        self.findings = lint.check(os.path.join(ROOT, 'examples', 'northwind-vault'), TODAY)

    def test_catches_the_three_planted_errors(self):
        p = '1-Projects/Northwind-Grocers/'
        self.assertEqual(errors(self.findings), sorted([
            ('superseded-incomplete', p + 'workbook.md'),
            ('supersession-unmarked', p + '_curated/decisions.md'),
            ('state-behind-log', p + '_curated/current-state.md'),
        ]))

    def test_warns_about_the_stale_canonical_document(self):
        stale = [f['file'] for f in self.findings if f['check'] == 'canonical-stale']
        self.assertEqual(stale, ['1-Projects/Northwind-Grocers/_curated/integration-architecture.md'])

    def test_accepts_the_correctly_marked_supersession(self):
        unmarked = [f['message'] for f in self.findings if f['check'] == 'supersession-unmarked']
        self.assertFalse(any('D3' in m for m in unmarked))


class SmallVaults(unittest.TestCase):
    def make(self, files):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root)
        for rel, body in files.items():
            path = os.path.join(root, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(textwrap.dedent(body))
        return root

    def test_successor_must_exist(self):
        root = self.make({'note.md': '> [!superseded] 2026-01-01 · replaced by [[nowhere]]\n'})
        self.assertIn(('superseded-dangling', 'note.md'), errors(lint.check(root, TODAY)))

    def test_complete_callout_passes(self):
        root = self.make({'note.md': '> [!superseded] 2026-01-01 · replaced by [[other]]\n', 'other.md': '# Other\n'})
        self.assertEqual(errors(lint.check(root, TODAY)), [])

    def test_code_blocks_and_inline_code_are_ignored(self):
        root = self.make({'note.md': '```\n> [!superseded] no date\n[[missing]]\n```\nUse `[[missing]]` like this.\n'})
        self.assertEqual(errors(lint.check(root, TODAY)), [])

    def test_raw_is_never_linted(self):
        root = self.make({'p/_raw/t.md': '[[missing]]\n> [!superseded] nothing\n'})
        self.assertEqual(errors(lint.check(root, TODAY)), [])

    def test_heavy_project_needs_a_canonical_map(self):
        files = {f'1-Projects/Acme/_curated/n{i}.md': '# note\n' for i in range(15)}
        files['1-Projects/Acme/CLAUDE.md'] = '# Project: Acme\n'
        root = self.make(files)
        self.assertIn(('no-canonical-map', '1-Projects/Acme/CLAUDE.md'), errors(lint.check(root, TODAY)))

    def test_canonical_without_date_warns(self):
        root = self.make({'arch.md': '---\ncanonical: architecture\n---\n# Arch\n'})
        checks = [f['check'] for f in lint.check(root, TODAY)]
        self.assertIn('canonical-unverified', checks)

    def test_exit_code_gates_ci(self):
        root = self.make({'note.md': '[[missing]]\n'})
        self.assertEqual(lint.main([root, '--summary']), 1)


if __name__ == '__main__':
    unittest.main()
