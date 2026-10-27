#!/usr/bin/env python3
"""Source-lock lint for a consulting LLM wiki.

The costly mistake in a consulting knowledge base is not a broken link. It is an
old decision read as if it were still valid. This lint checks the locks that
prevent that, and nothing else is required to run it besides Python 3.

Checks:
  ERROR  superseded callout without a date or without a successor link
  ERROR  superseded callout whose successor does not exist
  ERROR  decision that says it supersedes another, while the old one is unmarked
  ERROR  heavy project (many curated notes) without a canonical sources map
  ERROR  current state not re-verified after the latest ingest or decision in the log
  ERROR  broken wikilink
  WARN   canonical document without verified-on, or verified too long ago
  INFO   open [PENDING] markers

Usage:
  python3 lint.py [vault] [--json] [--summary] [--today YYYY-MM-DD]

Exit code is 1 when there is at least one ERROR, so it can gate CI.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

DEFAULTS = {
    'projects_dir': '1-Projects',
    'stale_after_days': 45,
    'heavy_project_notes': 15,
    'skip_dirs': ['.git', '.obsidian', 'node_modules', '.trash'],
    'raw_dir': '_raw',
    'superseded_dir': '_superseded',
}

FENCE = re.compile(r'^\s*(```|~~~)')
WIKILINK = re.compile(r'\[\[([^\]]+)\]\]')
DATE = re.compile(r'\d{4}-\d{2}-\d{2}')
DECISION_HEADING = re.compile(r'^#{2,4}\s+(D\d+)\b')
SUPERSEDES = re.compile(r'\b(?:supersedes|replaces|revokes)\b[^.\n]{0,80}?\b(D\d+)\b', re.I)
LOG_ENTRY = re.compile(r'^##\s+\[(\d{4}-\d{2}-\d{2})\]\s+(\w+)', re.M)


def load_config(root):
    cfg = dict(DEFAULTS)
    path = os.path.join(root, '_meta', 'llm-wiki.json')
    if os.path.isfile(path):
        with open(path, encoding='utf-8') as fh:
            cfg.update(json.load(fh))
    return cfg


def frontmatter(text):
    if not text.startswith('---'):
        return ''
    end = text.find('\n---', 3)
    return text[3:end] if end != -1 else ''


def fm_value(fm, key):
    m = re.search(r'^' + re.escape(key) + r':\s*(.*)$', fm, re.M)
    return m.group(1).strip().strip('"\'') if m else None


INLINE_CODE = re.compile(r'`[^`]*`')


def live_lines(text):
    """Yield (line_number, line) outside fenced code blocks, with inline code removed."""
    fenced = False
    for i, line in enumerate(text.split('\n'), 1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            yield i, INLINE_CODE.sub('', line)


def is_placeholder(target):
    return any(ch in target for ch in '<>{}') or target.strip() in ('', '...')


class Vault:
    def __init__(self, root, cfg):
        self.root = os.path.abspath(root)
        self.cfg = cfg
        self.files = {}
        self.names = {}
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in cfg['skip_dirs']]
            for fn in filenames:
                if not fn.endswith('.md'):
                    continue
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, self.root)
                with open(full, encoding='utf-8', errors='replace') as fh:
                    self.files[rel] = fh.read()
                self.names.setdefault(fn[:-3].lower(), []).append(rel)
            for fn in filenames:
                if not fn.endswith('.md'):
                    self.names.setdefault(fn.lower(), []).append(os.path.relpath(os.path.join(dirpath, fn), self.root))

    def is_raw(self, rel):
        return ('/' + self.cfg['raw_dir'] + '/') in ('/' + rel)

    def is_superseded_dir(self, rel):
        return ('/' + self.cfg['superseded_dir'] + '/') in ('/' + rel)

    def resolves(self, target, rel):
        target = target.split('|', 1)[0]
        name, _, anchor = target.partition('#')
        name = name.strip()
        if not name:
            return self.has_heading(self.files[rel], anchor)
        key = os.path.basename(name).lower()
        if key.endswith('.md'):
            key = key[:-3]
        if key not in self.names:
            return False
        if anchor:
            return any(self.has_heading(self.files.get(p, ''), anchor) for p in self.names[key])
        return True

    @staticmethod
    def has_heading(text, anchor):
        anchor = anchor.strip().lower()
        for _, line in live_lines(text):
            m = re.match(r'^#{1,6}\s+(.*)$', line)
            if not m:
                continue
            heading = m.group(1).strip().lower()
            slug = re.sub(r'[^\w\s-]', '', heading).strip().replace(' ', '-')
            if anchor in (heading, slug) or heading.startswith(anchor + ' ') or heading.split(' ', 1)[0] == anchor:
                return True
        return False


def check(root, today=None):
    cfg = load_config(root)
    today = today or dt.date.today()
    v = Vault(root, cfg)
    findings = []

    def add(sev, code, rel, line, msg):
        findings.append({'severity': sev, 'check': code, 'file': rel, 'line': line, 'message': msg})

    for rel, text in sorted(v.files.items()):
        raw = v.is_raw(rel)
        archived = v.is_superseded_dir(rel)

        # superseded callouts
        if not raw and not archived:
            for i, line in live_lines(text):
                if not line.lstrip().startswith('>') or '[!superseded]' not in line.lower():
                    continue
                head = line.split('[!superseded]', 1)[-1] if '[!superseded]' in line else line.lower().split('[!superseded]', 1)[-1]
                missing = []
                if not DATE.search(head):
                    missing.append('date')
                links = WIKILINK.findall(head)
                if not links:
                    missing.append('successor link')
                if missing:
                    add('ERROR', 'superseded-incomplete', rel, i,
                        'superseded callout without ' + ' and '.join(missing) + ': say when it died and what replaced it')
                elif not v.resolves(links[0], rel):
                    add('ERROR', 'superseded-dangling', rel, i, f'successor [[{links[0]}]] does not exist')

        # broken wikilinks
        if not raw:
            for i, line in live_lines(text):
                for target in WIKILINK.findall(line):
                    if is_placeholder(target):
                        continue
                    if not v.resolves(target, rel):
                        add('ERROR', 'broken-link', rel, i, f'[[{target}]] does not resolve')

        # canonical freshness
        fm = frontmatter(text)
        canonical = fm_value(fm, 'canonical')
        if canonical and canonical.lower() not in ('false', 'no') and not archived and '/_template/' not in '/' + rel:
            verified = fm_value(fm, 'verified-on')
            if not verified or not DATE.fullmatch(verified):
                add('WARN', 'canonical-unverified', rel, 1, f'canonical "{canonical}" has no verified-on date')
            else:
                age = (today - dt.date.fromisoformat(verified)).days
                if age > cfg['stale_after_days']:
                    add('WARN', 'canonical-stale', rel, 1,
                        f'canonical "{canonical}" last verified {age} days ago (limit {cfg["stale_after_days"]})')

        # pending markers (templates hold them on purpose)
        if not raw and not archived and '/_template/' not in '/' + rel and '/templates/' not in '/' + rel:
            for i, line in live_lines(text):
                if '[PENDING' in line:
                    add('INFO', 'pending', rel, i, line.strip()[:100])

    # decisions that supersede others without marking them
    for rel, text in sorted(v.files.items()):
        if v.is_raw(rel) or v.is_superseded_dir(rel):
            continue
        blocks, current = {}, None
        for i, line in live_lines(text):
            m = DECISION_HEADING.match(line)
            if m:
                current = m.group(1)
                blocks[current] = {'line': i, 'body': []}
            elif current:
                blocks[current]['body'].append(line)
        if len(blocks) < 3:
            continue
        for new_id, block in blocks.items():
            body = '\n'.join(block['body'])
            for old_id in set(SUPERSEDES.findall(body)):
                old = blocks.get(old_id)
                if old is None or old_id == new_id:
                    continue
                old_body = '\n'.join(old['body'])
                marked = '[!superseded]' in old_body.lower() and re.search(r'\b' + new_id + r'\b', old_body)
                if not marked:
                    add('ERROR', 'supersession-unmarked', rel, old['line'],
                        f'{new_id} supersedes {old_id}, but {old_id} has no [!superseded] callout pointing to {new_id}')

    # project-level checks
    pdir = os.path.join(v.root, cfg['projects_dir'])
    if os.path.isdir(pdir):
        for project in sorted(os.listdir(pdir)):
            ppath = os.path.join(pdir, project)
            if not os.path.isdir(ppath) or project.startswith(('_', '.')):
                continue
            prel = os.path.join(cfg['projects_dir'], project)
            curated = [r for r in v.files if r.startswith(os.path.join(prel, '_curated') + os.sep)
                       and not v.is_superseded_dir(r)]
            schema = v.files.get(os.path.join(prel, 'CLAUDE.md'), '')
            if len(curated) >= cfg['heavy_project_notes'] and not re.search(r'^#+\s*Canonical sources', schema, re.M | re.I):
                add('ERROR', 'no-canonical-map', os.path.join(prel, 'CLAUDE.md'), 1,
                    f'{len(curated)} curated notes and no "Canonical sources" table: a reader cannot tell which note is the truth')
            state_rel = os.path.join(prel, '_curated', 'current-state.md')
            log_text = v.files.get(os.path.join(prel, 'log.md'), '')
            if state_rel in v.files and log_text:
                verified = fm_value(frontmatter(v.files[state_rel]), 'verified-on')
                changes = [d for d, kind in LOG_ENTRY.findall(log_text) if kind.lower() in ('ingest', 'decision')]
                latest = max(changes) if changes else None
                if latest and (not verified or verified < latest):
                    add('ERROR', 'state-behind-log', state_rel, 1,
                        f'current state verified on {verified or "never"}, but the log records an ingest or decision on {latest}')

    return findings


def main(argv=None):
    ap = argparse.ArgumentParser(description='Source-lock lint for a consulting LLM wiki.')
    ap.add_argument('vault', nargs='?', default=os.environ.get('CLAUDE_PROJECT_DIR', '.'))
    ap.add_argument('--json', action='store_true', help='print findings as JSON')
    ap.add_argument('--summary', action='store_true', help='print one line with the counts')
    ap.add_argument('--today', help='reference date, for reproducible runs')
    args = ap.parse_args(argv)
    today = dt.date.fromisoformat(args.today) if args.today else None
    findings = check(args.vault, today)
    counts = {s: sum(f['severity'] == s for f in findings) for s in ('ERROR', 'WARN', 'INFO')}
    if args.json:
        print(json.dumps({'counts': counts, 'findings': findings}, indent=2))
    elif args.summary:
        print(f"{counts['ERROR']} error(s), {counts['WARN']} warning(s), {counts['INFO']} open [PENDING]")
    else:
        for sev in ('ERROR', 'WARN', 'INFO'):
            items = [f for f in findings if f['severity'] == sev]
            if not items:
                continue
            print(f'\n{sev} ({len(items)})')
            for f in items:
                print(f"  {f['file']}:{f['line']}  [{f['check']}] {f['message']}")
        if not findings:
            print('No findings. Every lock holds.')
    return 1 if counts['ERROR'] else 0


if __name__ == '__main__':
    sys.exit(main())
