"""RuleBasedExtractor — deterministic, zero-dependency semantic extraction.

This is the fallback and the test workhorse. It does not need an API key and it
gives the same answer every time, which makes the whole ingest → semantic →
provenance pipeline exercisable offline and in CI.

It is deliberately naive: it surfaces **entities** as capitalized proper-noun
runs, and emits one **event** per record capturing "something was observed here"
with a short summary. That is enough to demonstrate layered abstraction and
traceable provenance without pretending to be an NLP system — for real
relationship and event extraction, inject an ``LLMExtractor``.
"""

from __future__ import annotations

import re
from typing import Iterable

from ..models import SourceRecord
from .base import ExtractedNode, ExtractionResult

# A run of Capitalized words, optionally joined by short connectors ("of", "and"),
# e.g. "Payments Service", "Bank of England". Anchored to avoid matching a lone
# capitalized word that merely starts a sentence is impossible without a parser,
# so we keep single capitalized words only when they look like names (length ≥ 3).
_PROPER_RUN = re.compile(
    r"\b[A-Z][a-zA-Z0-9]+(?:\s+(?:of|and|the|for)\s+[A-Z][a-zA-Z0-9]+|\s+[A-Z][a-zA-Z0-9]+)*\b"
)

# Extremely common sentence-openers that are capitalized but almost never a
# proper noun on their own — filtered to cut the worst false positives.
_STOPWORDS = {
    "The", "This", "That", "These", "Those", "It", "We", "They", "I", "A", "An",
    "In", "On", "At", "For", "And", "But", "Or", "If", "When", "While", "As",
    "There", "Here", "Then", "So", "To", "Of", "By", "With", "From", "Our",
}


# Lowercase connectors that can appear *inside* a proper run but must never
# lead or trail it (e.g. strip them off "London and Payments").
_CONNECTORS = {"of", "and", "the", "for"}


def _summary(text: str, limit: int = 80) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 1].rstrip() + "…"


def _trim(name: str) -> str:
    """Strip leading sentence-openers and dangling connectors from a run.

    The regex can absorb a capitalized sentence-opener ("The Payments Service")
    or a connector at an edge; identity should be the proper noun itself.
    """
    tokens = name.split()
    while tokens and (tokens[0] in _STOPWORDS or tokens[0].casefold() in _CONNECTORS):
        tokens.pop(0)
    while tokens and tokens[-1].casefold() in _CONNECTORS:
        tokens.pop()
    return " ".join(tokens)


class RuleBasedExtractor:
    def extract(self, records: Iterable[SourceRecord]) -> ExtractionResult:
        out: ExtractionResult = []
        for record in records:
            # Entities: proper-noun runs, de-duped within the record.
            seen: set[str] = set()
            for match in _PROPER_RUN.finditer(record.content):
                name = _trim(match.group(0).strip())
                if not name or name in _STOPWORDS or name in seen:
                    continue
                # Drop single short capitalized tokens that are likely just a
                # sentence opener slipping past the stopword list.
                if " " not in name and len(name) < 3:
                    continue
                seen.add(name)
                out.append(
                    ExtractedNode(
                        kind="entity",
                        label=name,
                        evidence=[record.id],
                        attributes={"entity_type": "unknown"},
                    )
                )

            # Event: one per record — "this was observed."
            out.append(
                ExtractedNode(
                    kind="event",
                    label=_summary(record.content),
                    evidence=[record.id],
                    attributes={"mentions": sorted(seen)},
                )
            )
        return out
