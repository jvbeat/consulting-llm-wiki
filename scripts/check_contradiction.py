#!/usr/bin/env python3
"""Check whether a new decision makes any recorded decision false.

The design follows the edge deduplication prompt of Graphiti (github.com/getzep/graphiti):
two decisions contradict only when they cannot hold at the same time. Progress,
detail or a new status never contradicts anything.

Usage:
    python3 check_contradiction.py <decisions file> <file with the new decision, or ->

Prints one line per earlier decision that stopped holding, with the part that
died. Every line is checked against the text of both decisions before it becomes
a superseded callout. Requires the Claude Code CLI (`claude`) on the PATH. Always
exits 0: it warns, and the session doing the ingest decides.
"""
import json
import re
import subprocess
import sys
import tempfile

MODEL = 'haiku'
TIMEOUT = 300
MAX_CHARS = 200_000

RULES = """You check the decision log of a consulting project. You receive the earlier decisions and a new decision. Return the earlier decisions that the new one makes false.

Rules:
1. Flag an earlier decision only when it and the new one cannot both hold: whoever follows the new one must stop following the earlier one, entirely or in part.
2. Not a contradiction: detailing, complementing, implementing or executing the earlier decision; recording progress, status, deadline or owner; deciding on another subject, even with shared words.
3. If the new decision changes only part of the earlier one, flag it and say which part stopped holding.
4. A passage that already carries a [!superseded] callout does not count.
5. When in doubt, do not flag.

Use the identifier as it appears in the file (D20, ADR-002). Answer only with JSON: {"contradicted": [{"id": "D7", "part": "what stopped holding, in one sentence"}]}. Empty list when nothing stopped holding."""


def strip_frontmatter(text):
    if text.startswith('---') and text.count('---') >= 2:
        return text.split('---', 2)[2]
    return text


def ask(decisions, new):
    body = ('<EARLIER_DECISIONS>\n' + decisions.strip() + '\n</EARLIER_DECISIONS>\n\n'
            '<NEW_DECISION>\n' + new.strip() + '\n</NEW_DECISION>')
    cmd = ['claude', '-p', '--model', MODEL, '--tools', '', '--strict-mcp-config',
           '--no-session-persistence', '--output-format', 'json', '--system-prompt', RULES, body]
    with tempfile.TemporaryDirectory() as folder:
        r = subprocess.run(cmd, cwd=folder, capture_output=True, text=True, timeout=TIMEOUT)
    answer = json.loads(r.stdout).get('result', '')
    found = re.search(r'\{.*\}', answer, re.S)
    if not found:
        raise ValueError('answer without JSON')
    return json.loads(found.group(0)).get('contradicted', [])


def main(decisions_file, new_file):
    with open(decisions_file, encoding='utf-8') as fh:
        decisions = strip_frontmatter(fh.read())
    if new_file == '-':
        new = sys.stdin.read()
    else:
        with open(new_file, encoding='utf-8') as fh:
            new = fh.read()
    if len(decisions) > MAX_CHARS:
        print(f'Decisions file above {MAX_CHARS} characters: only its end was checked.')
        decisions = decisions[-MAX_CHARS:]
    try:
        found = ask(decisions, new)
    except (OSError, subprocess.TimeoutExpired, ValueError, json.JSONDecodeError) as err:
        print(f'Check not run ({err}). Compare by hand against the decisions file.')
        return 0
    if not found:
        print('No earlier decision stopped holding.')
    for item in found:
        print(f"{item.get('id', '?')}: {item.get('part', '').strip()}")
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(0)
    sys.exit(main(sys.argv[1], sys.argv[2]))
