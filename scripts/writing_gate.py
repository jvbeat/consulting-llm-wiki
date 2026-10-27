#!/usr/bin/env python3
"""Writing gate: a PostToolUse hook that applies the vault's writing rules to every
Markdown file Claude writes or edits.

A writing rule kept in prose is forgotten exactly when the text is being written.
This hook checks the new text the moment it lands and hands the offending lines
back to the agent. Errors block (the agent must fix them before moving on);
warnings are returned as context.

Rules come in packs (writing-rules/<pack>.json in the plugin, or
_meta/writing-rules/<pack>.json in the vault, which wins). The vault picks its
packs in _meta/llm-wiki.json, key "writing_packs". Raw material (_raw/) and code
blocks are never checked.

It also runs from the command line:  python3 writing_gate.py <file.md> [--packs en,pt-BR]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_RULES = os.path.join(os.path.dirname(HERE), 'writing-rules')
MARKER = '.llm-wiki'
FENCE = re.compile(r'^\s*(```|~~~)')


def find_root(path):
    d = os.path.dirname(os.path.abspath(path))
    while True:
        if os.path.exists(os.path.join(d, MARKER)):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def load_packs(root, names=None):
    if names is None:
        names = ['en']
        cfg = os.path.join(root, '_meta', 'llm-wiki.json') if root else None
        if cfg and os.path.isfile(cfg):
            with open(cfg, encoding='utf-8') as fh:
                names = json.load(fh).get('writing_packs', names)
    rules = []
    for name in names:
        for base in ([os.path.join(root, '_meta', 'writing-rules')] if root else []) + [PLUGIN_RULES]:
            path = os.path.join(base, name + '.json')
            if os.path.isfile(path):
                with open(path, encoding='utf-8') as fh:
                    for rule in json.load(fh)['rules']:
                        flags = re.I if 'i' in rule.get('flags', '') else 0
                        rules.append((rule['id'], re.compile(rule['pattern'], flags), rule['severity'], rule['message']))
                break
    return rules


def check_text(text, rules):
    errors, warnings = [], []
    fenced = False
    in_frontmatter = text.startswith('---')
    for i, line in enumerate(text.split('\n'), 1):
        if in_frontmatter:
            if i > 1 and line.strip() == '---':
                in_frontmatter = False
            continue
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        for rid, rx, sev, msg in rules:
            if rx.search(line):
                item = f'L{i} [{rid}] {msg}: {line.strip()[:90]}'
                (errors if sev == 'error' else warnings).append(item)
    return errors, warnings


def run_hook():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if payload.get('tool_name') not in ('Write', 'Edit', 'MultiEdit'):
        return 0
    path = (payload.get('tool_input') or {}).get('file_path', '')
    if not path.endswith('.md') or not os.path.isfile(path):
        return 0
    root = find_root(path)
    if not root or '/_raw/' in path:
        return 0
    with open(path, encoding='utf-8', errors='replace') as fh:
        errors, warnings = check_text(fh.read(), load_packs(root))
    name = os.path.relpath(path, root)
    if errors:
        print(json.dumps({'decision': 'block',
                          'reason': f'Writing gate in {name}: fix before moving on.\n' + '\n'.join(errors[:12])}))
    elif warnings:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PostToolUse',
                          'additionalContext': f'Writing gate in {name}, check:\n' + '\n'.join(warnings[:8])}}))
    return 0


def run_cli(argv):
    packs = None
    if '--packs' in argv:
        idx = argv.index('--packs')
        packs = argv[idx + 1].split(',')
        argv = argv[:idx] + argv[idx + 2:]
    status = 0
    for path in argv:
        root = find_root(path)
        with open(path, encoding='utf-8', errors='replace') as fh:
            errors, warnings = check_text(fh.read(), load_packs(root, packs))
        for e in errors:
            print(f'{path}: ERROR {e}')
        for w in warnings:
            print(f'{path}: WARN {w}')
        status = status or (1 if errors else 0)
    return status


if __name__ == '__main__':
    sys.exit(run_cli(sys.argv[1:]) if len(sys.argv) > 1 else run_hook())
