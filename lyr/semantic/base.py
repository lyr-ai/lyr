"""The Extractor contract and its output shape.

An ``Extractor`` reads Source Records and proposes semantic claims — entities,
events, relationships — each tagged with the records that support it. It does
*not* assign ids, identity, or versions; that is the builder's job. Keeping
extraction free of those concerns is what lets a naive rule-based extractor and
an LLM extractor be swapped freely (both just emit ``ExtractedNode``s).

Every ``ExtractedNode`` must carry ``evidence`` — the ids of the records it came
from. An extractor that invents a claim with no supporting record violates
LYR's first rule (no knowledge without evidence), so the builder rejects it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Protocol

from ..models import SourceRecord

# Semantic-layer vocabulary. Extractors should tag each node with one of these.
SEMANTIC_KINDS: tuple[str, ...] = ("entity", "event", "relationship")


@dataclass
class ExtractedNode:
    """A proposed semantic claim, before it becomes a versioned ``Node``.

    ``label`` is the human-facing name/summary. ``attributes`` holds the
    kind-specific payload (an entity's ``entity_type``; a relationship's
    ``subject``/``predicate``/``object``). ``evidence`` lists the ids of the
    Source Records this claim was drawn from.
    """

    kind: str
    label: str
    evidence: list[str]
    attributes: dict[str, Any] = field(default_factory=dict)


ExtractionResult = list[ExtractedNode]


class Extractor(Protocol):
    def extract(self, records: Iterable[SourceRecord]) -> ExtractionResult:
        """Propose semantic claims from ``records``, each citing its evidence."""
        ...
