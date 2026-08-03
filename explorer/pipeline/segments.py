"""Generic, language-aware segmentation for the case harness.

A case's raw sources become an ordered list of ``Segment``s that the pipeline
ingests one at a time. Two source types, no per-title code:

- ``book``  — split on chapter markers. English ("CHAPTER I."), Chinese
  ("第一回" / "第十二章"), or plain numbered headings. Falls back to the whole
  text as one segment if no markers are found.
- ``docs``  — each source document is its own segment (a technical corpus:
  report + model card + changelog + README). Ordered as listed in the manifest.

The point is that 红楼梦, a technical report, and Pride and Prejudice all reach
the same downstream pipeline through here — segmentation is the only place the
source *shape* is handled.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# English "CHAPTER <roman>" (any case, tolerant of a trailing "]") …
_EN_CHAP = re.compile(r"^[^\S\n]*CHAPTER\s+([IVXLCDM]+|\d+)\.?\]?[^\S\n]*$", re.I | re.M)
# … Chinese 第X回 / 第X章 (numerals 一二三…百千 or digits), on its own line.
_ZH_CHAP = re.compile(r"^[^\S\n]*第[零一二三四五六七八九十百千两0-9]+[回章][^\S\n]*.*$", re.M)
_GUTEN_START = re.compile(r"\*\*\*\s*START OF .*?\*\*\*", re.I | re.S)
_GUTEN_END = re.compile(r"\*\*\*\s*END OF .*?\*\*\*", re.I | re.S)


@dataclass
class Segment:
    number: int          # sequential 1..N
    origin: str          # stable id used as SourceRecord origin, e.g. "seg-03"
    title: str           # human label ("Chapter III", "第三回", "model_card.md")
    text: str


def _strip_gutenberg(raw: str) -> str:
    s, e = _GUTEN_START.search(raw), _GUTEN_END.search(raw)
    return raw[s.end(): e.start()] if s and e else raw


def split_book(raw: str, *, language: str = "en", case_id: str = "case") -> list[Segment]:
    body = _strip_gutenberg(raw)
    pat = _ZH_CHAP if language.startswith("zh") else _EN_CHAP
    marks = list(pat.finditer(body))
    if not marks:  # no chapter markers → one segment
        return [Segment(1, f"{case_id}-seg01", "Full text", body.strip())] if body.strip() else []
    segs: list[Segment] = []
    for i, m in enumerate(marks):
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        text = body[start:end].strip()
        if text:
            n = len(segs) + 1
            title = m.group(0).strip() or f"Chapter {n}"
            segs.append(Segment(n, f"{case_id}-seg{n:03d}", title, text))
    return segs


def split_docs(docs: list[tuple[str, str]], *, case_id: str = "case") -> list[Segment]:
    """docs: list of (title, text) — one segment per document."""
    return [Segment(i + 1, f"{case_id}-doc{i+1:02d}", title, text)
            for i, (title, text) in enumerate(docs) if text.strip()]


if __name__ == "__main__":  # tiny self-check
    zh = "第一回\n甄士隐梦幻识通灵。\n\n第二回\n贾夫人仙逝扬州城。\n\n第三回\n林黛玉抛父进京都。"
    s = split_book(zh, language="zh", case_id="hlm")
    print(f"zh: {len(s)} segments ->", [(x.title, x.text[:8]) for x in s])
    en = "CHAPTER I.\nIt is a truth.\n\nCHAPTER II.\nMr. Bennet was among."
    print(f"en: {len(split_book(en, language='en', case_id='pnp'))} segments")
