#!/usr/bin/env python3
"""Check the official Localization (26) and Updating (27) translations."""
import argparse
import hashlib
import json
import re
from pathlib import Path

from check_handbook_translations import verify
from check_jails_translation import markdown_blocks

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'docs/translation-ch26-ch27.json').read_text())
    errors, pending = [], []
    if [(e['id'], e['slug']) for e in manifest['chapters']] != [(26, 'l10n'), (27, 'cutting-edge')]:
        errors.append('Expected official chapter 26 Localization and chapter 27 Updating')
    for entry in manifest['chapters']:
        source = (ROOT / entry['source_path']).read_text()
        if hashlib.sha256(source.encode()).hexdigest() != entry['source_sha256']:
            errors.append(f"{entry['id']}: source hash mismatch")
        if entry['status'] == 'pending':
            pending.append(entry['id'])
            continue
        if entry['status'] != 'translated':
            errors.append(f"{entry['id']}: invalid status")
            continue
        path = ROOT / entry['translation_path']
        if not path.is_file():
            errors.append(f"{entry['id']}: missing translation")
            continue
        text = path.read_text()
        failures, counts = verify(source, text, entry, manifest['upstream_commit'])
        errors.extend(f"{entry['id']}: {failure}" for failure in failures)
        _, prose = markdown_blocks(text)
        for target in re.findall(r'\]\(([^)]+)\)', prose):
            if re.match(r'^[a-z]+:|^#', target):
                continue
            filename, _, fragment = target.partition('#')
            linked = path.parent / filename
            if not linked.is_file():
                errors.append('Missing linked file: ' + target)
            elif fragment:
                _, linked_prose = markdown_blocks(linked.read_text())
                if f'<a id="{fragment}"></a>' not in linked_prose:
                    errors.append('Missing linked anchor: ' + target)
        print(f"{entry['id']}: {counts}")
    if args.require_complete and pending:
        errors.append('Incomplete chapters: ' + ', '.join(map(str, pending)))
    for error in errors:
        print('FAIL:', error)
    print('Pending:', pending)
    print('Checks source and structure; does not prove prose accuracy or runtime behavior.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
