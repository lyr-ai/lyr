"""SemanticBuilder — turns proposed claims into versioned, deduplicated Nodes.

This is where extraction output becomes maintained knowledge. The builder:

1. runs the injected ``Extractor`` over the records;
2. assigns each claim a stable **identity** (so the same entity mentioned in
   ten records is one node, not ten);
3. applies **minimal change** — if a claim adds nothing new to a node that
   already exists, nothing happens; if it brings genuinely new evidence or a
   changed meaning, the node **evolves** to a new version keeping its identity.

That last step is the heart of LYR: knowledge is updated in place with a visible
version history, not regenerated from scratch on every ingest.
"""

from __future__ import annotations

from typing import Any, Iterable

from ..ids import content_id, normalize
from ..models import Node, SourceRecord
from ..store.base import Store
from .base import Extractor, ExtractedNode


def _identity(kind: str, label: str, attributes: dict[str, Any]) -> str:
    """Stable identity for a semantic claim.

    Identity is what the claim is *about*, excluding evidence and phrasing so a
    node keeps its identity across revisions. Relationships are identified by
    their (subject, predicate, object) triple; entities and events by their
    normalized label.
    """
    if kind == "relationship":
        s = normalize(str(attributes.get("subject", "")))
        p = normalize(str(attributes.get("predicate", "")))
        o = normalize(str(attributes.get("object", "")))
        if s or p or o:
            return content_id("idn", kind, s, p, o)
    return content_id("idn", kind, normalize(label))


class _Claim:
    """A per-identity accumulation of extracted nodes during one build."""

    __slots__ = ("kind", "label", "attributes", "evidence")

    def __init__(self, node: ExtractedNode) -> None:
        self.kind = node.kind
        self.label = node.label
        self.attributes = dict(node.attributes)
        self.evidence: set[str] = set(node.evidence)

    def absorb(self, node: ExtractedNode) -> None:
        self.evidence.update(node.evidence)
        # First non-empty value wins per key — keeps the merge stable and avoids
        # a later noisy mention clobbering a good attribute.
        for k, v in node.attributes.items():
            if self.attributes.get(k) in (None, "", "unknown") and v not in (None, ""):
                self.attributes[k] = v


class SemanticBuilder:
    """Build/maintain the semantic layer from Source Records."""

    def __init__(self, store: Store, extractor: Extractor) -> None:
        self._store = store
        self._extractor = extractor

    def build(self, records: Iterable[SourceRecord]) -> list[Node]:
        record_list = list(records)

        # 1. Extract, then collapse by identity so repeated mentions merge.
        claims: dict[str, _Claim] = {}
        for extracted in self._extractor.extract(record_list):
            if not extracted.evidence:
                continue  # no evidence → not knowledge; drop it
            key = _identity(extracted.kind, extracted.label, extracted.attributes)
            if key in claims:
                claims[key].absorb(extracted)
            else:
                claims[key] = _Claim(extracted)

        # 2. Reconcile each claim against what the store already holds.
        results: list[Node] = []
        for identity, claim in claims.items():
            results.append(self._reconcile(identity, claim))
        return results

    def _reconcile(self, identity: str, claim: _Claim) -> Node:
        evidence = sorted(claim.evidence)
        head = self._store.head(identity)

        if head is None:
            node = Node(
                layer="semantic",
                kind=claim.kind,
                label=claim.label,
                identity=identity,
                evidence=evidence,
                attributes=claim.attributes,
            )
            return self._store.add_node(node)

        # Minimal change: only evolve if the claim actually adds something —
        # new supporting evidence, a changed label, or changed attributes.
        merged_evidence = sorted(set(head.evidence) | claim.evidence)
        merged_attributes = {**claim.attributes, **head.attributes}  # existing wins
        for k, v in claim.attributes.items():
            if head.attributes.get(k) in (None, "", "unknown") and v not in (None, ""):
                merged_attributes[k] = v

        unchanged = (
            merged_evidence == sorted(head.evidence)
            and claim.label == head.label
            and merged_attributes == head.attributes
        )
        if unchanged:
            return head  # nothing new — no version churn

        evolved = head.evolved(
            label=claim.label,
            attributes=merged_attributes,
            evidence=merged_evidence,
        )
        return self._store.add_node(evolved)
