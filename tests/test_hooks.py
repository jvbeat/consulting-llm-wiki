"""The session hooks act only inside a vault, and the stop hook reports pending work."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, 'scripts')


def run(script, cwd):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=cwd)
    out = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)], input='{}',
                         capture_output=True, text=True, env=env, cwd=cwd).stdout.strip()
    return json.loads(out) if out else None


class Hooks(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)

    def test_both_hooks_are_silent_outside_a_vault(self):
        self.assertIsNone(run('session_start.py', self.dir))
        self.assertIsNone(run('stop_check.py', self.dir))

    def test_stop_reports_uncommitted_files(self):
        subprocess.run(['git', 'init', '-q', self.dir], check=True)
        open(os.path.join(self.dir, '.llm-wiki'), 'w').close()
        with open(os.path.join(self.dir, 'note.md'), 'w') as fh:
            fh.write('# Note\n')
        msg = run('stop_check.py', self.dir)
        self.assertIn('not committed', msg['systemMessage'])

    def test_new_vault_creates_a_clean_vault(self):
        target = os.path.join(self.dir, 'vault')
        subprocess.run([sys.executable, os.path.join(SCRIPTS, 'new_vault.py'), target], check=True, capture_output=True)
        self.assertTrue(os.path.exists(os.path.join(target, '.llm-wiki')))
        lint = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'lint.py'), target, '--summary'],
                              capture_output=True, text=True)
        self.assertEqual(lint.returncode, 0, lint.stdout)


if __name__ == '__main__':
    unittest.main()
