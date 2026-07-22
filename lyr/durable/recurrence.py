"""RecurrenceConsolidator — the deterministic default durable policy.

Knowledge becomes durable when it recurs across *multiple independent
experiences*. This consolidator measures that recurrence purely from semantic
records and their provenance ids — it never reads the source layer, honoring M3
layer isolation — and promotes a topic to a durable memory once it is backed by
at least ``min_support`` distinct source records.

``min_support`` is the one tunable that encodes the M3 open question ("how much
evidence before something is durable?"). The default is deliberately modest and
clearly a *policy choice*, not a hidden assumption: LYR makes no claim it is the
right threshold — it is the knob you turn while investigating that question.

Being a pure function of (semantic records, config), the consolidator is exactly
reproducible: identical inputs yield an identical, stably-ordered proposal list.
"""

from __future__ import annotations

from typing import Any, Iterable

from ..ids import content_id, normalize
from ..models import Node
from .base import ADD, NO_OP, UPDATE, DurableProposal


def _topic(node: Node) -> tuple[str, ...] | None:
    """The durable topic a semantic node belongs to, or None to skip it.

    Relationships are grouped by their (subject, predicate, object) assertion;
    entities by their normalized name. Events are one-off observations and do
    not, on their own, constitute recurring knowledge — they are skipped.
    """
    if node.kind == "relationship":
        a = node.attributes
        s, p, o = (
            normalize(str(a.get("subject", ""))),
            normalize(str(a.get("predicate", ""))),
            normalize(str(a.get("object", ""))),
        )
        if s or p or o:
            return ("relationship", s, p, o)
        return ("relationship", normalize(node.label))
    if node.kind == "entity":
        return ("entity", normalize(node.label))
    return None


def _statement(members: list[Node]) -> tuple[str, str]:
    """A natural-language statement + durable kind for a topic group."""
    first = members[0]
    if first.kind == "relationship":
        return first.label, "lesson"
    # entity → a persistently significant subject
    return f"{first.label} recurs across multiple experiences.", "subject"


def _confidence(support: int) -> float:
    """A monotonic (0,1) confidence from the number of supporting experiences."""
    return round(support / (support + 1), 3)


class RecurrenceConsolidator:
    def __init__(
        self,
        *,
        min_support: int = 2,
        include_entities: bool = True,
        include_relationships: bool = True,
    ) -> None:
        if min_support < 1:
            raise ValueError("min_support must be >= 1")
        self.min_support = min_support
        self.include_entities = include_entities
        self.include_relationships = include_relationships

    def consolidate(
        self,
        semantic_nodes: Iterable[Node],
        existing_durable: Iterable[Node],
    ) -> list[DurableProposal]:
        existing = {n.identity: n for n in existing_durable}

        # 1. Group semantic records by durable topic.
        groups: dict[tuple[str, ...], list[Node]] = {}
        for node in semantic_nodes:
            if node.kind == "entity" and not self.include_entities:
                continue
            if node.kind == "relationship" and not self.include_relationships:
                continue
            topic = _topic(node)
            if topic is None:
                continue
            groups.setdefault(topic, []).append(node)

        proposals: list[DurableProposal] = []
        touched: set[str] = set()

        for topic, members in groups.items():
            # Support = distinct source records underpinning the topic, read from
            # the semantic records' own provenance (no source-layer access).
            support_sources: set[str] = set()
            for m in members:
                support_sources.update(m.evidence)
            support = len(support_sources)
            if support < self.min_support:
                continue  # not (yet) durable

            identity = content_id("idn", "durable", *topic)
            touched.add(identity)
            statement, kind = _statement(members)
            evidence = sorted({m.id for m in members})
            attributes: dict[str, Any] = {
                "confidence": _confidence(support),
                "support": support,
                "source_kind": members[0].kind,
                "subject": members[0].attributes.get("subject", members[0].label),
            }

            prior = existing.get(identity)
            if prior is None:
                proposals.append(
                    DurableProposal(
                        op=ADD, identity=identity, statement=statement, kind=kind,
                        evidence=evidence, attributes=attributes,
                        reason=f"supported by {support} experiences",
                    )
                )
            elif set(prior.evidence) == set(evidence) and prior.label == statement:
                proposals.append(
                    DurableProposal(
                        op=NO_OP, identity=identity, statement=prior.label,
                        kind=prior.kind, evidence=sorted(prior.evidence),
                        attributes=dict(prior.attributes),
                        reason="no change since last consolidation",
                    )
                )
            else:
                proposals.append(
                    DurableProposal(
                        op=UPDATE, identity=identity, statement=statement, kind=kind,
                        evidence=evidence, attributes=attributes,
                        reason=f"evidence grew to {support} experiences",
                    )
                )

        # 2. Existing durable memories whose topic is still present but no longer
        #    recomputed above stay put — emit an explicit NO_OP so the outcome is
        #    visible to the benchmark. (v0.1 does not retract durable knowledge.)
        for identity, node in existing.items():
            if identity not in touched:
                proposals.append(
                    DurableProposal(
                        op=NO_OP, identity=identity, statement=node.label,
                        kind=node.kind, evidence=sorted(node.evidence),
                        attributes=dict(node.attributes),
                        reason="no supporting evidence this round; retained",
                    )
                )

        # Stable order → reproducible output.
        proposals.sort(key=lambda pr: (pr.identity, pr.op))
        return proposals
