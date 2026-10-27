"""The writing gate must block the configured errors, warn on the rest and ignore code."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import writing_gate  # noqa: E402

GATE = os.path.join(ROOT, 'scripts', 'writing_gate.py')


def check(text, packs):
    return writing_gate.check_text(text, writing_gate.load_packs(None, packs))


class EnglishPack(unittest.TestCase):
    def test_em_dash_is_an_error(self):
        errors, _ = check('The plan — simple as it is — works.\n', ['en'])
        self.assertTrue(errors)

    def test_bold_label_with_period_is_an_error(self):
        errors, _ = check('- **Scope.** The pilot covers one store.\n', ['en'])
        self.assertTrue(errors)

    def test_inflated_wording_is_a_warning(self):
        errors, warnings = check('This is a game-changer for the team.\n', ['en'])
        self.assertEqual(errors, [])
        self.assertTrue(warnings)

    def test_code_and_frontmatter_are_ignored(self):
        text = '---\ntitle: a — b\n---\n```\nx — y\n```\nPlain sentence.\n'
        self.assertEqual(check(text, ['en']), ([], []))


class PortuguesePack(unittest.TestCase):
    def test_travessao_and_definition_pattern_are_errors(self):
        errors, _ = check('O plano — simples — funciona.\nÉ a aba que vira o controle.\n', ['pt-BR'])
        self.assertEqual(len(errors), 2)

    def test_living_verb_is_a_warning(self):
        _, warnings = check('O dado nasce no e-commerce.\n', ['pt-BR'])
        self.assertTrue(warnings)


class Hook(unittest.TestCase):
    def setUp(self):
        self.vault = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.vault)
        open(os.path.join(self.vault, '.llm-wiki'), 'w').close()

    def run_hook(self, path):
        payload = {'tool_name': 'Write', 'tool_input': {'file_path': path}}
        out = subprocess.run([sys.executable, GATE], input=json.dumps(payload),
                             capture_output=True, text=True, check=True).stdout.strip()
        return json.loads(out) if out else None

    def test_blocks_inside_a_vault(self):
        path = os.path.join(self.vault, 'note.md')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write('A plan — with a dash.\n')
        self.assertEqual(self.run_hook(path)['decision'], 'block')

    def test_silent_outside_a_vault(self):
        outside = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, outside)
        path = os.path.join(outside, 'note.md')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write('A plan — with a dash.\n')
        self.assertIsNone(self.run_hook(path))


if __name__ == '__main__':
    unittest.main()
