"""Closing a project: heavy raw files leave with a hash-checked manifest, and the lint asks for a dossier."""
import datetime as dt
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import lint  # noqa: E402
import raw_offload  # noqa: E402


class RawOffload(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.project = os.path.join(self.dir, 'Acme')
        self.dest = os.path.join(self.dir, 'client-drive')
        raw = os.path.join(self.project, '_raw', 'photos')
        os.makedirs(raw)
        with open(os.path.join(raw, 'whiteboard.png'), 'wb') as fh:
            fh.write(os.urandom(2 * 1024 * 1024))
        with open(os.path.join(raw, 'tiny.png'), 'wb') as fh:
            fh.write(os.urandom(1024))
        with open(os.path.join(self.project, '_raw', 'transcript.md'), 'w') as fh:
            fh.write('long transcript\n' * 200000)

    def test_dry_run_moves_nothing(self):
        raw_offload.main([self.project, self.dest])
        self.assertTrue(os.path.exists(os.path.join(self.project, '_raw', 'photos', 'whiteboard.png')))
        self.assertFalse(os.path.exists(self.dest))

    def test_apply_moves_heavy_binaries_only_and_writes_the_manifest(self):
        raw_offload.main([self.project, self.dest, '--apply'])
        self.assertTrue(os.path.exists(os.path.join(self.dest, 'photos', 'whiteboard.png')))
        self.assertFalse(os.path.exists(os.path.join(self.project, '_raw', 'photos', 'whiteboard.png')))
        self.assertTrue(os.path.exists(os.path.join(self.project, '_raw', 'photos', 'tiny.png')))
        self.assertTrue(os.path.exists(os.path.join(self.project, '_raw', 'transcript.md')))
        manifest = open(os.path.join(self.project, '_raw', 'MANIFEST.md')).read()
        self.assertIn('photos/whiteboard.png', manifest)
        self.assertIn(raw_offload.sha256(os.path.join(self.dest, 'photos', 'whiteboard.png')), manifest)


class ArchivedDossier(unittest.TestCase):
    def test_archived_project_without_dossier_warns(self):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root)
        os.makedirs(os.path.join(root, '4-Archive', 'Acme', '_curated'))
        checks = [f['check'] for f in lint.check(root, dt.date(2026, 11, 19))]
        self.assertIn('archived-without-dossier', checks)


if __name__ == '__main__':
    unittest.main()
