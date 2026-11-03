#!/usr/bin/env python3
"""Check chapter 16 against the recorded English snapshot; no third-party dependencies."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/jails-source.json"


def source_sections(text):
    headings = list(re.finditer(r"^\[\[([^\]]+)\]\]\n(=+) ([^\n]+)", text, re.M))
    if not headings:
        raise ValueError("English source has no anchored headings")
    sections = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        section = text[heading.start():end]
        if heading[1] in sections:
            raise ValueError("Duplicate source anchor: " + heading[1])
        if len(re.findall(r"^\.\.\.\.[ \t]*$", section, re.M)) % 2:
            raise ValueError("Unclosed AsciiDoc block: " + heading[1])
        blocks = [
            re.sub(r" <\.>", "", match[1].rstrip())
            for match in re.finditer(r"^\.\.\.\.\n([\s\S]*?)^\.\.\.\.[ \t]*$", section, re.M)
        ]
        sections[heading[1]] = (len(heading[2]), blocks)
    return sections


def markdown_blocks(text):
    """Return code blocks and prose, rejecting mismatched/unclosed fences."""
    blocks, prose = [], []
    fence = None
    body = []
    for number, line in enumerate(text.splitlines(), 1):
        if fence is None:
            opening = re.fullmatch(r"(\x60{3,}|~{3,})(.*)", line)
            if opening:
                fence = opening[1]
                body = []
            else:
                prose.append(line)
        elif re.fullmatch(re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*", line):
            blocks.append("\n".join(body).rstrip())
            fence = None
        elif re.match(r"^(\x60{3,}|~{3,})", line):
            raise ValueError(f"Unexpected fence inside code at line {number}")
        else:
            body.append(line)
    if fence is not None:
        raise ValueError("Unclosed Markdown code fence")
    return blocks, "\n".join(prose)


def verify(source, translation, expected_sha=None):
    errors = []
    if expected_sha and hashlib.sha256(source.encode("utf-8")).hexdigest() != expected_sha:
        errors.append("Source SHA-256 differs from docs/jails-source.json; review the new source first")
    try:
        sections = source_sections(source)
        blocks, prose = markdown_blocks(translation)
    except ValueError as error:
        return [str(error)], {}
    anchors = list(re.finditer(r'^<a id="([^"]+)"></a>$', translation, re.M))
    ids = [anchor[1] for anchor in anchors]
    if ids != list(sections):
        errors.append("Translation anchors must match source headings exactly, in order, without duplicates")
    for index, anchor in enumerate(anchors):
        anchor_id = anchor[1]
        if anchor_id not in sections:
            continue
        end = anchors[index + 1].start() if index + 1 < len(anchors) else len(translation)
        section = translation[anchor.end():end]
        level, expected_blocks = sections[anchor_id]
        try:
            actual_blocks, section_prose = markdown_blocks(section)
        except ValueError as error:
            errors.append(f"{anchor_id}: {error}")
            continue
        heading = re.search(r"^(#{1,6}) (.+)$", section_prose, re.M)
        if not heading or len(heading[1]) != level:
            errors.append(f"{anchor_id}: missing heading or wrong heading level")
        if actual_blocks != expected_blocks:
            errors.append(f"{anchor_id}: code/output blocks differ from source (callouts excluded)")
        body = re.sub(r"^#{1,6} .+$", "", section_prose, flags=re.M).strip()
        if not re.search(r"[\u3040-\u30ff\u3400-\u9fff]", body):
            errors.append(f"{anchor_id}: missing Japanese prose")
    expected_total = sum(len(items) for _, items in sections.values())
    if len(blocks) != expected_total:
        errors.append(f"Expected {expected_total} code/output blocks, found {len(blocks)}")
    if re.search(r"^\[\[|^\[source(?:,|\])|^\[\.|^\|===|^\.{4}$|^={2,}(?: |$)|crossref:|man:\w+\[\d+\]|package:\S+\[\]", prose, re.M):
        errors.append("AsciiDoc syntax remains outside code")
    for target in re.findall(r"\]\(#([^)]+)\)", prose):
        if target not in ids:
            errors.append("Broken internal link: #" + target)
    plain = re.sub(r"\x60[^\x60\n]*\x60", "", prose)
    if re.search(r"⟦\d+⟧|\{rel-[^}]+\}", plain):
        errors.append("Unresolved translation/release placeholder outside code")
    if any(re.search(r"[ \t]+$", line) for line in translation.splitlines()):
        errors.append("Trailing whitespace")
    if not translation.endswith("\n") or translation.endswith("\n\n"):
        errors.append("Translation must end with exactly one newline")
    return errors, {"headings": len(sections), "code_blocks": expected_total}


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source = (ROOT / manifest["source_path"]).read_text(encoding="utf-8")
    translation = (ROOT / manifest["translation_path"]).read_text(encoding="utf-8")
    errors, counts = verify(source, translation, manifest["source_sha256"])
    if errors:
        for error in errors:
            print("FAIL:", error, file=sys.stderr)
        return 1
    print(f"PASS: {counts['headings']} headings, {counts['code_blocks']} code/output blocks, "
          "fences, anchor order, internal links, source hash, and Markdown syntax")
    print("This checks structure and code fidelity, not prose accuracy or FreeBSD runtime behavior.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
