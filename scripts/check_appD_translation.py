#!/usr/bin/env python3
"""Check the Handbook Appendix D OpenPGP Keys (D-pgpkeys) translation."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from check_jails_translation import markdown_blocks

ROOT = Path(__file__).resolve().parents[1]
BLOCK = re.compile(r'^(?P<delimiter>\.{4,}|-{4,})\n(?P<code>[\s\S]*?)^(?P=delimiter)[ \t]*$', re.M)


def source_sections(source: str, chapter_id: str):
    masked = BLOCK.sub(lambda m: re.sub(r'[^\n]', ' ', m[0]), source)
    headings = list(re.finditer(r'^(=+) ([^\n]+)', masked, re.M))
    boundaries = []
    for index, heading in enumerate(headings):
        explicit = re.search(r'^\[\[([^\]]+)\]\]\n$', source[:heading.start()], re.M)
        anchor = explicit[1] if explicit else f'appendix-{chapter_id}-heading-{index + 1:02d}'
        boundaries.append((anchor, explicit.start() if explicit else heading.start()))
    sections = []
    for index, heading in enumerate(headings):
        end = boundaries[index + 1][1] if index + 1 < len(headings) else len(source)
        body = source[heading.end():end]
        sections.append((boundaries[index][0], len(heading[1]), body))
    return sections


def verify(source: str, translation: str, entry: dict, upstream_commit: str):
    errors = []
    if hashlib.sha256(source.encode()).hexdigest() != entry['source_sha256']:
        errors.append('Source SHA-256 mismatch')
    try:
        _, prose = markdown_blocks(translation)
    except ValueError as error:
        return [str(error)], {}
    source_parts = source_sections(source, entry['id'])
    source_prose = BLOCK.sub('', source)
    expected_anchors = re.findall(r'\[\[([^\]]+)\]\]', source_prose)
    expected_anchors += [a for a, _, _ in source_parts if a not in expected_anchors]
    actual_anchors = re.findall(r'^<a id="([^"]+)"></a>$', prose, re.M)
    if sorted(actual_anchors) != sorted(expected_anchors):
        errors.append('Original/generated anchors missing, extra, or duplicated')
    positions = []
    totals = {'headings': len(source_parts), 'anchors': len(expected_anchors), 'code_blocks': 0, 'images': 0, 'tables': 0}
    for anchor, level, body in source_parts:
        marker = '<a id="' + anchor + '"></a>'
        start = translation.find(marker)
        if start < 0:
            continue
        positions.append(start)
    if positions != sorted(positions):
        errors.append('Source heading order changed')
    for index, (anchor, level, body) in enumerate(source_parts):
        start = translation.find('<a id="' + anchor + '"></a>')
        if start < 0:
            continue
        end = len(translation)
        if index + 1 < len(source_parts):
            end = translation.find('<a id="' + source_parts[index + 1][0] + '"></a>')
        translated = translation[start:end]
        blocks, section_prose = markdown_blocks(translated)
        heading = re.search(r'^(#{1,6}) (.+)$', section_prose, re.M)
        if not heading or len(heading[1]) != level:
            errors.append(anchor + ': missing/wrong heading level')
        text = re.sub(r'^#{1,6} .+$|^<a id=.*$', '', section_prose, flags=re.M)
        text = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', text)
        if not re.search(r'[\u3040-\u30ff\u3400-\u9fff]', text):
            errors.append(anchor + ': Japanese explanation missing')
        expected_blocks = [re.sub(r'[ \t]*<\.>', '', m['code'].rstrip()).rstrip() for m in BLOCK.finditer(body)]
        if blocks != expected_blocks:
            errors.append(anchor + ': code/output blocks differ from source')
        images = re.findall(r'^image::([^\[]+)\[', body, re.M)
        expected_images = [
            'https://raw.githubusercontent.com/freebsd/freebsd-doc/'
            + upstream_commit
            + '/documentation/static/images/books/handbook/'
            + entry['slug']
            + '/'
            + name
            for name in images
        ]
        actual_images = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', section_prose)
        if actual_images != expected_images:
            errors.append(anchor + ': source screenshots missing/reordered or not pinned')
        totals['code_blocks'] += len(expected_blocks)
        totals['images'] += len(images)
    for target in re.findall(r'\]\(#([^)]+)\)', prose):
        if target not in actual_anchors:
            errors.append('Broken internal link: #' + target)
    if re.search(
        r'^\[\[|^\[source(?:,|\])|^\[\.|^\|===|^\.{4}$|^={2,}(?: |$)|crossref:|extref:|man:\w+\[\d+\]|package:\S+\[\]',
        prose,
        re.M,
    ):
        errors.append('AsciiDoc structure remains in prose')
    plain = re.sub(r'`[^`\n]*`', '', prose)
    if re.search(r'⟦\d+⟧|\{(?:rel-|pgpkeys|security-officer|core-secretary|portmgr-secretary|doceng-secretary)[^}]*\}', plain):
        errors.append('Unresolved translation/attribute placeholder in prose')
    if any(re.search(r'[ \t]+$', line) for line in translation.splitlines()):
        errors.append('Trailing whitespace')
    if not translation.endswith('\n') or translation.endswith('\n\n'):
        errors.append('Expected exactly one final newline')
    if entry.get('counts') != totals:
        errors.append(f"Manifest counts mismatch: expected {totals}, got {entry.get('counts')}")
    return errors, totals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'docs/translation-appD.json').read_text())
    errors, pending = [], []
    if [(e['id'], e['slug']) for e in manifest['chapters']] != [('D', 'pgpkeys')]:
        errors.append('Expected Appendix D (id D, slug pgpkeys) only')
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
