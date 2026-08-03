"""Split the Project Gutenberg *Pride and Prejudice* into chapters.

Public-domain source (Gutenberg #1342). We keep only the body between the
START/END markers and split on the ``CHAPTER <roman>.`` headings, returning an
ordered list of chapters. No interpretation happens here — this is
ingestion-adjacent plumbing, kept deliberately dumb so the real work stays in
the LYR pipeline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_START = re.compile(r"\*\*\*\s*START OF .*?\*\*\*", re.I | re.S)
_END = re.compile(r"\*\*\*\s*END OF .*?\*\*\*", re.I | re.S)
# A chapter heading is a line that is *only* "CHAPTER <roman>." Chapter I in this
# edition is title-cased and inside an illustration caption ("Chapter I.]"), so
# we allow a trailing "]" and match case-insensitively.
_CHAP = re.compile(r"^[^\S\n]*CHAPTER\s+([IVXLCDM]+)\.?\]?[^\S\n]*$", re.I | re.M)


@dataclass
class Chapter:
    number: int   # sequential 1..N, in reading order
    roman: str    # the roman numeral as printed
    text: str


def split_chapters(raw: str) -> list[Chapter]:
    s, e = _START.search(raw), _END.search(raw)
    body = raw[s.end() : e.start()] if s and e else raw

    marks = list(_CHAP.finditer(body))
    chapters: list[Chapter] = []
    for i, m in enumerate(marks):
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        text = body[start:end].strip()
        if text:
            chapters.append(Chapter(number=len(chapters) + 1, roman=m.group(1).upper(), text=text))
    return chapters


if __name__ == "__main__":  # quick manual check
    import sys
    from pathlib import Path

    src = Path(sys.argv[1] if len(sys.argv) > 1 else "explorer/data/pride-and-prejudice.raw.txt")
    chs = split_chapters(src.read_text(encoding="utf-8", errors="replace"))
    print(f"{len(chs)} chapters")
    for c in (chs[0], chs[-1]):
        print(f"  ch{c.number} ({c.roman}): {len(c.text)} chars — {c.text[:60]!r}")
