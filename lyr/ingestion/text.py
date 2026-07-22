"""Text ingestor — splits prose into paragraph records.

The default, zero-dependency ingestor. It segments on blank lines (the natural
paragraph boundary in prose, markdown, notes, and most transcripts), preserving
order via ``position``. Markdown headings are captured in each record's
metadata as the ``section`` it falls under, so later layers and the explorer can
group by section without a separate parser.

Segmentation deliberately stays simple: a record should be a unit a human would
cite as "one thing that was said." Finer-grained splitting (sentences, clauses)
belongs to the semantic layer, not here.
"""

from __future__ import annotations

import re

from ..models import SourceRecord
from .base import Document

_HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


def _blocks(text: str) -> list[str]:
    # Split on one-or-more blank lines; trim and drop empties.
    return [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]


class TextIngestor:
    """Segment prose/markdown into ordered paragraph Source Records."""

    def ingest(self, document: Document) -> list[SourceRecord]:
        records: list[SourceRecord] = []
        section: str | None = None
        position = 0

        for block in _blocks(document.text):
            heading = _HEADING.match(block)
            if heading:
                # Track the current section, but don't emit the heading itself as
                # a record — it's structure, not observation. Its text still
                # becomes provenance context via the `section` metadata below.
                section = heading.group(2)
                continue

            metadata = dict(document.metadata)
            if section is not None:
                metadata["section"] = section

            records.append(
                SourceRecord(
                    content=block,
                    origin=document.origin,
                    position=position,
                    kind="paragraph" if document.kind == "document" else document.kind,
                    metadata=metadata,
                )
            )
            position += 1

        return records
