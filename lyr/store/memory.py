"""In-memory store — the reference backend for v0.1.

Everything lives in dicts. It is complete (satisfies the whole ``Store``
protocol including version history) and fast, which makes it the right default
for tests, notebooks, and small corpora. Persistence backends land in a later
milestone; they implement the same protocol.
"""

from __future__ import annotations

from typing import Iterable

from ..models import Node, SourceRecord


class InMemoryStore:
    def __init__(self) -> None:
        self._sources: dict[str, SourceRecord] = {}
        self._nodes: dict[str, Node] = {}
        # identity -> version ids in insertion (== version) order
        self._by_identity: dict[str, list[str]] = {}

    # ── source layer ------------------------------------------------------
    def add_source(self, record: SourceRecord) -> SourceRecord:
        # Content-addressed ids make this idempotent: the same observation
        # re-ingested does not create a duplicate.
        self._sources.setdefault(record.id, record)
        return self._sources[record.id]

    def get_source(self, source_id: str) -> SourceRecord | None:
        return self._sources.get(source_id)

    def sources(self) -> Iterable[SourceRecord]:
        return list(self._sources.values())

    # ── node layers -------------------------------------------------------
    def add_node(self, node: Node) -> Node:
        if node.id in self._nodes:
            return self._nodes[node.id]
        self._nodes[node.id] = node
        chain = self._by_identity.setdefault(node.identity, [])
        chain.append(node.id)
        # Keep the chain ordered by version so head()/versions() are cheap even
        # if nodes arrive out of order.
        chain.sort(key=lambda nid: self._nodes[nid].version)
        return node

    def get_node(self, node_id: str) -> Node | None:
        return self._nodes.get(node_id)

    def nodes(self, layer: str | None = None) -> Iterable[Node]:
        if layer is None:
            return list(self._nodes.values())
        return [n for n in self._nodes.values() if n.layer == layer]

    def versions(self, identity: str) -> list[Node]:
        return [self._nodes[nid] for nid in self._by_identity.get(identity, [])]

    def head(self, identity: str) -> Node | None:
        chain = self._by_identity.get(identity)
        if not chain:
            return None
        return self._nodes[chain[-1]]
