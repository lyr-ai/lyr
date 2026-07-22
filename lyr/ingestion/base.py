"""The Ingestor contract.

Ingestion is where LYR's "all experiences are the same kind of thing" stance is
enforced. A book, a meeting transcript, a debug trace, a journal entry — each
enters as a ``Document`` and leaves as an ordered list of immutable
``SourceRecord``s. Different experiences differ only in *how they are split*
into records, which is exactly what an ``Ingestor`` implementation decides.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from ..models import SourceRecord


@dataclass
class Document:
    """A raw experience to be ingested.

    ``origin`` is the stable name this experience is cited by (a title, a file
    path, a meeting id); it flows onto every record so provenance can name its
    source. ``kind`` labels the experience type and becomes each record's kind
    unless the ingestor overrides it per-record.
    """

    text: str
    origin: str
    kind: str = "document"
    metadata: dict[str, Any] = field(default_factory=dict)


class Ingestor(Protocol):
    def ingest(self, document: Document) -> list[SourceRecord]:
        """Normalize ``document`` into ordered, immutable Source Records."""
        ...
