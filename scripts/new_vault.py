#!/usr/bin/env python3
"""Create a new vault from the plugin template.

Usage:  python3 new_vault.py <target folder> [--force]

Copies the template, writes the .llm-wiki marker and initializes git when the
folder is not a repository yet. Refuses a non-empty folder unless --force is
given, and never overwrites a file that already exists.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(os.path.dirname(HERE), 'template')


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    target = os.path.abspath(argv[0])
    force = '--force' in argv
    if os.path.isdir(target) and os.listdir(target) and not force:
        print(f'{target} is not empty. Use --force to add the template around existing files.')
        return 1
    created = 0
    for dirpath, _, filenames in os.walk(TEMPLATE):
        rel = os.path.relpath(dirpath, TEMPLATE)
        dest_dir = os.path.join(target, rel) if rel != '.' else target
        os.makedirs(dest_dir, exist_ok=True)
        for fn in filenames:
            dest = os.path.join(dest_dir, fn)
            if not os.path.exists(dest):
                shutil.copy2(os.path.join(dirpath, fn), dest)
                created += 1
    if subprocess.run(['git', '-C', target, 'rev-parse', '--git-dir'], capture_output=True).returncode != 0:
        subprocess.run(['git', 'init', '-q', '-b', 'main', target])
    print(f'Vault ready at {target} ({created} files from the template).')
    print('Next: open it in Claude Code, read CLAUDE.md, and create your first client with the new-vault skill or by copying 1-Projects/_template.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
