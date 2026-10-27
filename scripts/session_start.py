#!/usr/bin/env python3
"""SessionStart hook: sync the vault and tell the agent the state of the locks.

Runs only inside a vault (a folder with a .llm-wiki marker at its root), so the
plugin never touches other repositories. When the vault is a git repository with
an upstream, it pulls with --rebase --autostash before any writing happens: a
scheduled job or a second machine may have pushed while this one was idle, and
writing on top of a stale copy is how digests and decisions get lost.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
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
    return subprocess.run(['git', '-C', root, *args], capture_output=True, text=True, timeout=60)


def main():
    root = find_root(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))
    if not root:
        return 0
    notes = []
    if git(root, 'rev-parse', '--git-dir').returncode == 0 and git(root, 'rev-parse', '@{u}').returncode == 0:
        pull = git(root, 'pull', '--rebase', '--autostash')
        out = (pull.stdout + pull.stderr).strip()
        if pull.returncode != 0:
            notes.append('Vault: git pull --rebase failed; resolve it before writing. ' + out.splitlines()[-1] if out else '')
        elif 'conflict' in out.lower():
            notes.append('Vault: pulled, but local work conflicted when coming back from the stash (git stash list).')
        elif out and 'up to date' not in out.lower():
            notes.append('Vault: synced with the remote.')
    lint = subprocess.run([sys.executable, os.path.join(HERE, 'lint.py'), root, '--summary'],
                          capture_output=True, text=True, timeout=60)
    summary = lint.stdout.strip()
    if lint.returncode != 0:
        notes.append(f'Source locks: {summary}. Run the lint skill before trusting a canonical answer.')
    if notes:
        msg = ' '.join(n for n in notes if n)
        print(json.dumps({'systemMessage': msg,
                          'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': msg}}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
