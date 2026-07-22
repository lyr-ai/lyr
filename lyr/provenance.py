"""Provenance — expand any abstraction back to its supporting evidence.

LYR's third principle: no generated knowledge exists without evidence, and every
node must be expandable back to the Source Records that justify it. Because all
layers share the ``Node`` shape and cite ``evidence`` one layer down, that
expansion is a single recursive walk — the same code traces a cognitive
principle to durable lessons to semantic facts to source paragraphs.

``trace`` returns the full evidence tree; ``explain`` flattens it to just the
Source Records at the bottom — the direct answer to "why does the system believe
this?"
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import Node, SourceRecord
from .store.base import Store


@dataclass
class ProvenanceTree:
    """A node together with the evidence tree beneath it.

    Exactly one of ``node`` / ``source`` is set at each level: interior levels
    are ``Node``s (semantic/durable/cognitive), leaves are ``SourceRecord``s.
    """

    node: Node | None = None
    source: SourceRecord | None = None
    children: list["ProvenanceTree"] = field(default_factory=list)

    @property
    def is_source(self) -> bool:
        return self.source is not None


def trace(node: Node, store: Store, *, _seen: set[str] | None = None) -> ProvenanceTree:
    """Expand ``node`` into its full evidence tree, down to Source Records.

    Cycles (which shouldn't occur, but a bad build could create one) are broken
    by tracking visited ids, so the walk always terminates.
    """
    seen = _seen if _seen is not None else set()
    tree = ProvenanceTree(node=node)
    if node.id in seen:
        return tree
    seen.add(node.id)

    for evidence_id in node.evidence:
        source = store.get_source(evidence_id)
        if source is not None:
            tree.children.append(ProvenanceTree(source=source))
            continue
        child = store.get_node(evidence_id)
        if child is not None:
            tree.children.append(trace(child, store, _seen=seen))
        # An evidence id resolving to nothing is dropped silently here; use
        # `dangling_evidence` to audit for it.
    return tree


def explain(node: Node, store: Store) -> list[SourceRecord]:
    """The Source Records ultimately supporting ``node``, de-duplicated.

    This is the "show me the receipts" query: whatever layer ``node`` lives at,
    you get back the raw observations underneath it, in a stable order.
    """
    found: dict[str, SourceRecord] = {}

    def walk(tree: ProvenanceTree) -> None:
        if tree.source is not None:
            found.setdefault(tree.source.id, tree.source)
        for child in tree.children:
            walk(child)

    walk(trace(node, store))
    return sorted(found.values(), key=lambda s: (s.origin, s.position))


def supporters(target_id: str, store: Store, *, layer: str | None = None) -> list[Node]:
    """Nodes that cite ``target_id`` as evidence — provenance walked *upward*.

    The inverse of ``trace``: given a Source Record or a lower-layer node, find
    the higher-layer knowledge it supports. This is what lets a semantic record
    answer "which Durable Memories do I support?" (an M3 invariant) — pass the
    semantic node's id and ``layer="durable"``.
    """
    found = [
        node
        for node in store.nodes(layer=layer)
        if target_id in node.evidence
    ]
    return sorted(found, key=lambda n: (n.layer, n.identity, n.version))


def dangling_evidence(node: Node, store: Store) -> list[str]:
    """Evidence ids on ``node`` that resolve to neither a record nor a node.

    A non-empty result means provenance is broken — knowledge citing evidence
    the store can't produce. Useful as an integrity check after a build or load.
    """
    missing: list[str] = []
    for evidence_id in node.evidence:
        if store.get_source(evidence_id) is None and store.get_node(evidence_id) is None:
            missing.append(evidence_id)
    return missing
