#!/usr/bin/env python3
"""Stop hook: warn when the session leaves the vault with uncommitted or unpushed work.

"Every session ends with commit and push" is a rule that holds only while someone
remembers it. This hook turns it into a signal at the end of every turn. It is
silent when everything is committed and pushed, and outside a vault.
"""
import json
import os
import subprocess
import sys

MARKER = '.llm-wiki'


def find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(d, MARKER)):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def git(root, *args):
    return subprocess.run(['git', '-C', root, *args], capture_output=True, text=True, timeout=30)


def main():
    root = find_root(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))
    if not root or git(root, 'rev-parse', '--git-dir').returncode != 0:
        return 0
    dirty = len([l for l in git(root, 'status', '--porcelain').stdout.splitlines() if l.strip()])
    ahead = git(root, 'log', '--oneline', '@{u}..HEAD')
    unpushed = len(ahead.stdout.splitlines()) if ahead.returncode == 0 else 0
    if not dirty and not unpushed:
        return 0
    parts = []
    if dirty:
        parts.append(f'{dirty} file(s) not committed')
    if unpushed:
        parts.append(f'{unpushed} commit(s) not pushed')
    print(json.dumps({'systemMessage': 'Vault pending: ' + ', '.join(parts) +
                      '. Commit the paths this session touched and push before closing.'}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
