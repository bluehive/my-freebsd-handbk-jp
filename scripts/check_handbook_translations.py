#!/usr/bin/env python3
"""Check source/structure fidelity for the chapter 1-14 translation project."""
from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import sys
from pathlib import Path

from check_jails_translation import markdown_blocks

ROOT = Path(__file__).resolve().parents[1]
BLOCK = re.compile(r'^(?P<delimiter>\.{4,}|-{4,})\n(?P<code>[\s\S]*?)^(?P=delimiter)[ \t]*$', re.M)


def source_sections(source, chapter):
    # Preserve offsets while excluding heading-like text inside code listings.
    masked = BLOCK.sub(lambda m: re.sub(r'[^\n]', ' ', m[0]), source)
    headings = list(re.finditer(r'^(=+) ([^\n]+)', masked, re.M))
    boundaries = []
    for index, heading in enumerate(headings):
        explicit = re.search(r'^\[\[([^\]]+)\]\]\n$', source[:heading.start()], re.M)
        anchor = explicit[1] if explicit else f'chapter-{chapter:02d}-heading-{index + 1:02d}'
        boundaries.append((anchor, explicit.start() if explicit else heading.start()))
    sections = []
    for index, heading in enumerate(headings):
        end = boundaries[index + 1][1] if index + 1 < len(headings) else len(source)
        body = source[heading.end():end]
        sections.append((boundaries[index][0], len(heading[1]), body))
    return sections


def verify(source, translation, entry, upstream_commit):
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
    totals = {'headings': len(source_parts), 'code_blocks': 0, 'images': 0}
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
        expected_blocks = [re.sub(r'[ \t]*<\.>', '', m['code'].rstrip()) for m in BLOCK.finditer(body)]
        if blocks != expected_blocks:
            errors.append(anchor + ': code/output blocks differ from source')
        images = re.findall(r'^image::([^\[]+)\[', body, re.M)
        expected_images = ['https://raw.githubusercontent.com/freebsd/freebsd-doc/' + upstream_commit
                           + '/documentation/static/images/books/handbook/' + entry['slug'] + '/' + name
                           for name in images]
        actual_images = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', section_prose)
        if actual_images != expected_images:
            errors.append(anchor + ': source screenshots missing/reordered or not pinned')
        totals['code_blocks'] += len(expected_blocks)
        totals['images'] += len(images)
    for target in re.findall(r'\]\(#([^)]+)\)', prose):
        if target not in actual_anchors:
            errors.append('Broken internal link: #' + target)
    if re.search(r'^\[\[|^\[source(?:,|\])|^\[\.|^\|===|^\.{4}$|^={2,}(?: |$)|crossref:|man:\w+\[\d+\]|package:\S+\[\]', prose, re.M):
        errors.append('AsciiDoc structure remains in prose')
    plain = re.sub(r'`[^`\n]*`', '', prose)
    if re.search(r'⟦\d+⟧|\{rel-[^}]+\}', plain):
        errors.append('Unresolved translation/release placeholder in prose')
    if any(re.search(r'[ \t]+$', line) for line in translation.splitlines()):
        errors.append('Trailing whitespace')
    if not translation.endswith('\n') or translation.endswith('\n\n'):
        errors.append('Expected exactly one final newline')
    return errors, totals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-complete', action='store_true', help='Fail until all 14 chapters are translated')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'docs/translation-through-ch14.json').read_text())
    errors, translated, pending = [], 0, []
    if [entry['id'] for entry in manifest['chapters']] != list(range(1, 15)):
        errors.append('Manifest must contain chapters 1 through 14 exactly once, in order')
    releases = manifest['release_attributes']
    if hashlib.sha256((ROOT / releases['path']).read_bytes()).hexdigest() != releases['sha256']:
        errors.append('Release attribute snapshot hash mismatch')
    for entry in manifest['chapters']:
        if entry['status'] not in {'pending', 'translated'}:
            errors.append(f"{entry['id']:02d}: unknown translation status")
        source = (ROOT / entry['source_path']).read_text()
        if hashlib.sha256(source.encode()).hexdigest() != entry['source_sha256']:
            errors.append(f"{entry['id']:02d}: source hash mismatch")
        if entry['status'] != 'translated':
            pending.append(entry['id'])
            continue
        path = ROOT / entry['translation_path']
        if not path.is_file():
            errors.append('Missing translation: ' + entry['translation_path'])
            continue
        translation = path.read_text()
        failures, counts = verify(source, translation, entry, manifest['upstream_commit'])
        errors.extend(f"{entry['id']:02d}: {failure}" for failure in failures)
        _, prose = markdown_blocks(translation)
        for target in re.findall(r'\]\(([^)]+)\)', prose):
            if re.match(r'^[a-z]+:|^#', target):
                continue
            relative = posixpath.normpath(posixpath.join(posixpath.dirname(entry['translation_path']), target.split('#')[0]))
            if not (ROOT / relative).is_file():
                errors.append('Missing relative link: ' + relative)
        translated += 1
        print(f"{entry['id']:02d}: {counts}")
    if args.require_complete and pending:
        errors.append('Not translated yet: ' + ', '.join(map(str, pending)))
    for error in errors:
        print('FAIL:', error, file=sys.stderr)
    print(f'{translated}/14 chapters translated; pending: {pending}')
    print('Structural checks do not prove prose accuracy or runtime behavior.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
