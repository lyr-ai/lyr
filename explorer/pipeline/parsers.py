"""Document Parser Layer — turn a raw source into logical Sections, generically.

The witness (红楼梦's in-text 第X回) showed that segmentation is not "a regex" —
every source *type* has its own document structure. So parsing is a layer, not a
special-case:

    Connector (gets bytes) → DocumentParser (understands structure) → Sections
    → Passages (shared PassageIngestor) → Source Records → Semantic

A ``DocumentParser`` maps ``[(title, text), …]`` to an ordered list of ``Section``s.
Every parser outputs the **same** shape, so Semantic never learns whether the
source was a book, a paper, or a forum. The document type is chosen by the case
manifest's ``parser`` field (``novel`` / ``markdown`` / ``docs``), never by title —
no ``if case == "红楼梦"``, ever. New source types add a parser here; nothing
downstream changes.
"""

from __future__ import annotations

import re
from typing import Protocol

from segments import Segment, split_book  # low-level detectors live in segments.py

# markdown heading: "#"…"######" then text, on its own line
_MD_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)


class DocumentParser(Protocol):
    name: str
    def parse(self, docs: list[tuple[str, str]], case_id: str) -> list[Segment]: ...


class NovelParser:
    """Prose split on chapter headings — English (CHAPTER I) or Chinese (第X回).

    Heading *detection* (not a book special-case): a heading starts its line and
    the chapter marker is followed only by whitespace/end-of-line, so an in-text
    reference ("第四回中…") is not a boundary. Reusable for any novel — 三体,
    War and Peace, Pride and Prejudice — which is the test of "parser improvement"
    vs "book hack".
    """
    name = "novel"

    def __init__(self, language: str = "en") -> None:
        self.language = language

    def parse(self, docs: list[tuple[str, str]], case_id: str) -> list[Segment]:
        _, text = docs[0]  # a novel is a single document
        return split_book(text, language=self.language, case_id=case_id)


class DocsParser:
    """A collection of documents — one Section per document (report, model card,
    changelog, README). Order = manifest order."""
    name = "docs"

    def parse(self, docs: list[tuple[str, str]], case_id: str) -> list[Segment]:
        return [Segment(i + 1, f"{case_id}-doc{i + 1:02d}", title, text)
                for i, (title, text) in enumerate(docs) if text.strip()]


class MarkdownParser:
    """Markdown/technical docs split on `#`…`######` headings. Content before the
    first heading becomes a `(preamble)` section. Contiguous → lossless."""
    name = "markdown"

    def parse(self, docs: list[tuple[str, str]], case_id: str) -> list[Segment]:
        out: list[Segment] = []
        for title, text in docs:
            marks = list(_MD_HEADING.finditer(text))
            spans: list[tuple[str, str]] = []
            if not marks:
                spans = [(title, text)]
            else:
                if text[:marks[0].start()].strip():
                    spans.append((f"{title} (preamble)", text[:marks[0].start()]))
                for i, m in enumerate(marks):
                    end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
                    spans.append((m.group(2).strip(), text[m.start():end]))
            for heading, body in spans:
                if body.strip():
                    n = len(out) + 1
                    out.append(Segment(n, f"{case_id}-sec{n:03d}", heading, body.strip()))
        return out


_PARSERS = {"novel": NovelParser, "docs": DocsParser, "markdown": MarkdownParser}


def get_parser(manifest: dict) -> DocumentParser:
    """Choose a parser from the manifest — `parser` field, else from `source_type`."""
    name = manifest.get("parser") or ("novel" if manifest.get("source_type") == "book" else "docs")
    if name not in _PARSERS:
        raise SystemExit(f"unknown parser {name!r} (have: {', '.join(_PARSERS)})")
    cls = _PARSERS[name]
    return cls(manifest.get("language", "en")) if name == "novel" else cls()


if __name__ == "__main__":  # tiny self-check across parsers
    md = "# Title\nintro\n\n## Method\nwe do X.\n\n## Results\nit works."
    print("markdown:", [(s.title, s.text[:12]) for s in MarkdownParser().parse([("readme.md", md)], "k")])
    print("docs:", [s.title for s in DocsParser().parse([("report", "a"), ("card", "b")], "k")])
