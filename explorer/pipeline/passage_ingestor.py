"""Fine, sentence-aware, LOSSLESS passage ingestor (harness-level, generic).

A drop-in ``Ingestor`` for LYR (injected via ``LYR(ingestor=...)``) for long
documents whose paragraphs are NOT blank-line separated — Classical Chinese,
transcripts, some technical docs. It splits into sentence units (on newlines +
sentence punctuation), then **packs** adjacent sentences into passage-sized
Source Records:

- never cuts a sentence in half;
- passages are **contiguous slices that tile the whole text** → lossless
  (concatenating passage contents reproduces the source, up to trailing
  whitespace only);
- each record carries its precise ``char_start`` / ``char_end`` / ``passage_index``.

**No language or case logic** — only text structure and size. Chinese is merely
where the blank-line assumption first broke. Size targets are configurable.
"""
from __future__ import annotations

import re

from lyr.models import SourceRecord

# sentence-ending punctuation (CJK + ASCII) and semicolons; newline is also a break
_ENDERS = "。．！？；.!?;"
_CHUNK = re.compile(rf"[^{re.escape(_ENDERS)}\n]*(?:[{re.escape(_ENDERS)}\n]|$)")
_WS = re.compile(r"\s")


class PassageIngestor:
    """Ingestor protocol: ``ingest(document) -> list[SourceRecord]``."""

    def __init__(self, target: int = 800, maximum: int = 1500) -> None:
        self.target = target      # aim to flush a passage once it has this many non-space chars
        self.maximum = maximum    # hard cap on passage length (only a lone longer sentence may exceed)

    def ingest(self, document) -> list[SourceRecord]:
        text = document.text
        chunks = [m.group(0) for m in _CHUNK.finditer(text) if m.group(0)]

        # 1. pack chunks into contiguous [start, end) passages
        passages: list[tuple[int, int]] = []
        buf_start = offset = cur_len = cur_ns = 0
        for ch in chunks:
            clen = len(ch)
            if cur_ns > 0 and cur_len + clen > self.maximum:
                passages.append((buf_start, offset))
                buf_start, cur_len, cur_ns = offset, 0, 0
            offset += clen
            cur_len += clen
            cur_ns += len(_WS.sub("", ch))
            if cur_ns >= self.target:
                passages.append((buf_start, offset))
                buf_start, cur_len, cur_ns = offset, 0, 0
        if buf_start < len(text):
            passages.append((buf_start, len(text)))
        # fold a trailing whitespace-only passage back into the previous one
        if len(passages) >= 2 and not text[passages[-1][0]:passages[-1][1]].strip():
            s, _ = passages[-2]
            passages[-2] = (s, passages[-1][1])
            passages.pop()

        # 2. emit records (skip a purely-whitespace slice — only possible for a blank section)
        base = dict(document.metadata)
        records: list[SourceRecord] = []
        pi = 0
        for s, e in passages:
            content = text[s:e]
            if not content.strip():
                continue
            records.append(SourceRecord(
                content=content, origin=document.origin, position=pi, kind=document.kind,
                metadata={**base, "passage_index": pi, "char_start": s, "char_end": e},
            ))
            pi += 1
        return records


def reassemble(records) -> str:
    """Concatenate record contents in order — for the lossless check."""
    return "".join(r.content for r in sorted(records, key=lambda r: r.metadata.get("char_start", 0)))
