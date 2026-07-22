"""LYR — the knowledge engine facade.

One object wires together the v0.1 vertical slice: ingest experiences into
immutable Source Records (M1), build/maintain the semantic layer over them (M2),
and trace any node back to its evidence. Higher layers (durable, cognitive) plug
in here later behind the same store and provenance machinery.

    from lyr import LYR
    from lyr.semantic import RuleBasedExtractor

    lyr = LYR(extractor=RuleBasedExtractor())
    nodes = lyr.ingest("The Payments Service failed at 02:00.", origin="incident-42")
    for record in lyr.explain(nodes[0]):
        print(record.content)
"""

from __future__ import annotations

from typing import Iterable

from .durable import (
    Consolidator,
    DurableBuilder,
    DurableProposal,
    RecurrenceConsolidator,
    is_active,
)
from .ingestion import Document, Ingestor, TextIngestor
from .models import Node, SourceRecord
from .provenance import ProvenanceTree, explain, supporters, trace
from .semantic import Extractor, RuleBasedExtractor, SemanticBuilder
from .store import InMemoryStore, Store


class LYR:
    """The knowledge engine: ingestion + semantic building + provenance.

    Everything is injectable — swap the ``store`` for a persistent backend, the
    ``ingestor`` for a domain-specific splitter, or the ``extractor`` for an
    LLM-backed one — but the defaults give a working, zero-dependency engine.
    """

    def __init__(
        self,
        *,
        store: Store | None = None,
        ingestor: Ingestor | None = None,
        extractor: Extractor | None = None,
        consolidator: Consolidator | None = None,
    ) -> None:
        self.store: Store = store or InMemoryStore()
        self.ingestor: Ingestor = ingestor or TextIngestor()
        self.extractor: Extractor = extractor or RuleBasedExtractor()
        self.consolidator: Consolidator = consolidator or RecurrenceConsolidator()
        self.builder = SemanticBuilder(self.store, self.extractor)
        self.durable_builder = DurableBuilder(self.store, self.consolidator)

    # ── M1: ingest ---------------------------------------------------------
    def ingest_source(
        self, text: str, *, origin: str, kind: str = "document", **metadata: object
    ) -> list[SourceRecord]:
        """Normalize an experience into stored Source Records (no building)."""
        document = Document(text=text, origin=origin, kind=kind, metadata=dict(metadata))
        records = self.ingestor.ingest(document)
        return [self.store.add_source(r) for r in records]

    # ── M1 + M2: ingest then build semantic --------------------------------
    def ingest(
        self, text: str, *, origin: str, kind: str = "document", **metadata: object
    ) -> list[Node]:
        """Ingest an experience and build/maintain the semantic layer over it.

        Returns the semantic nodes touched by this experience — new nodes and
        any that evolved to a new version because of it.
        """
        records = self.ingest_source(text, origin=origin, kind=kind, **metadata)
        return self.builder.build(records)

    def rebuild_semantic(self) -> list[Node]:
        """Re-run semantic building over every stored Source Record.

        Idempotent by design: because ids and identities are content-addressed
        and building applies minimal change, running this on an unchanged corpus
        produces no new versions.
        """
        return self.builder.build(list(self.store.sources()))

    # ── M3: durable layer --------------------------------------------------
    def build_durable(self) -> list[DurableProposal]:
        """Consolidate recurring semantic knowledge into durable memory.

        A maintenance pass over accumulated semantic knowledge — run it
        periodically, not on every ingest. Returns the proposals made (ADD /
        UPDATE / MERGE / NO_OP), which the builder has already applied.
        """
        return self.durable_builder.build()

    def propose_durable(self) -> list[DurableProposal]:
        """The durable proposals for the current state, without applying them."""
        return self.durable_builder.propose()

    def durable_memories(self, *, include_retired: bool = False) -> Iterable[Node]:
        """Active durable memories (latest version of each identity).

        Retired memories — those folded into another by MERGE — are excluded by
        default; pass ``include_retired=True`` to see them (their history and
        provenance are always retained in the store).
        """
        heads: dict[str, Node] = {}
        for node in self.store.nodes(layer="durable"):
            current = heads.get(node.identity)
            if current is None or node.version > current.version:
                heads[node.identity] = node
        memories = heads.values()
        if not include_retired:
            memories = [n for n in memories if is_active(n)]
        return list(memories)

    # ── provenance ---------------------------------------------------------
    def explain(self, node: Node) -> list[SourceRecord]:
        """The Source Records that justify ``node`` (any layer)."""
        return explain(node, self.store)

    def trace(self, node: Node) -> ProvenanceTree:
        """The full evidence tree beneath ``node``."""
        return trace(node, self.store)

    def supporters(self, node: Node | SourceRecord, *, layer: str | None = None) -> list[Node]:
        """Higher-layer nodes that cite ``node`` as evidence.

        The upward provenance query: e.g. which durable memories a semantic
        record supports (``layer="durable"``).
        """
        return supporters(node.id, self.store, layer=layer)

    # ── retrieval (hierarchical, thin for v0.1) ----------------------------
    def semantic_nodes(self) -> Iterable[Node]:
        """Current semantic nodes (latest version of each identity)."""
        heads: dict[str, Node] = {}
        for node in self.store.nodes(layer="semantic"):
            current = heads.get(node.identity)
            if current is None or node.version > current.version:
                heads[node.identity] = node
        return list(heads.values())

    def history(self, node: Node) -> list[Node]:
        """Every version of ``node``'s identity, oldest first."""
        return self.store.versions(node.identity)
