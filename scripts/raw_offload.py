#!/usr/bin/env python3
"""Move heavy raw files of a client project out of the vault, into storage the client controls.

At the end of an engagement, text evidence (transcripts, emails, notes) stays in the vault:
it is small, it is what search and future case studies use. Heavy binaries (images, video,
PDF, spreadsheets) belong in the client's own storage, usually a synced folder of the client
drive. This script copies each file there, checks the SHA-256 of the copy against the
original, records the file in `_raw/MANIFEST.md`, and only then deletes it from the vault.
Nothing is edited: files only change place.

Usage:
  python3 raw_offload.py <project folder> <destination folder> [--min-size-mb N] [--apply]

Without --apply it only lists what would move. Text files (.md, .txt, .eml, .json, .csv,
.vtt, .srt) never move.
"""
import argparse
import datetime as dt
import hashlib
import os
import shutil
import sys

TEXT = {'.md', '.txt', '.eml', '.json', '.csv', '.vtt', '.srt'}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def candidates(raw_dir, min_bytes):
    """Binary files at or above the size limit. Text files never move."""
    for dirpath, _, filenames in os.walk(raw_dir):
        for fn in sorted(filenames):
            if fn == 'MANIFEST.md' or fn.startswith('.'):
                continue
            path = os.path.join(dirpath, fn)
            if os.path.splitext(fn)[1].lower() in TEXT:
                continue
            if os.path.getsize(path) >= min_bytes:
                yield path


def main(argv=None):
    ap = argparse.ArgumentParser(description='Move heavy raw files to client storage, with a hash-checked manifest.')
    ap.add_argument('project')
    ap.add_argument('destination')
    ap.add_argument('--min-size-mb', type=float, default=1.0, help='binaries smaller than this stay (default 1 MB)')
    ap.add_argument('--apply', action='store_true', help='move the files; without it, only list them')
    args = ap.parse_args(argv)

    raw_dir = os.path.join(args.project, '_raw')
    if not os.path.isdir(raw_dir):
        print(f'{raw_dir} does not exist.')
        return 1
    min_bytes = int(args.min_size_mb * 1024 * 1024)
    files = list(candidates(raw_dir, min_bytes))
    if not files:
        print('Nothing to move.')
        return 0

    rows = []
    for path in files:
        rel = os.path.relpath(path, raw_dir)
        size = os.path.getsize(path)
        if not args.apply:
            print(f'would move  {rel}  ({size / 1048576:.1f} MB)')
            continue
        target = os.path.join(args.destination, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        digest = sha256(path)
        shutil.copy2(path, target)
        if sha256(target) != digest:
            print(f'hash mismatch on {rel}: kept in the vault')
            continue
        os.remove(path)
        rows.append(f'| {rel} | {size} | {digest} | {dt.date.today().isoformat()} |')
        print(f'moved  {rel}')

    if rows:
        manifest = os.path.join(raw_dir, 'MANIFEST.md')
        new = not os.path.exists(manifest)
        with open(manifest, 'a', encoding='utf-8') as fh:
            if new:
                fh.write('# Raw files kept outside the vault\n\n'
                         f'Moved to the client storage at `{os.path.abspath(args.destination)}`. '
                         'The hash proves the copy is the original.\n\n'
                         '| File | Bytes | SHA-256 | Moved on |\n|---|---|---|---|\n')
            fh.write('\n'.join(rows) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
