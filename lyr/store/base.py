"""The Store contract.

A store holds two kinds of thing — immutable ``SourceRecord``s and versioned
``Node``s — and answers the queries the rest of LYR needs: fetch by id (for
provenance walks), enumerate a layer (for the builders), and look up every
version of one identity (for version history and minimal-change dedup).

It is a ``Protocol`` so a persistent backend (SQLite, JSONL, a vector store)
can be dropped in later without touching the engine. v0.1 ships one
implementation, ``InMemoryStore``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Protocol

from ..models import Node, SourceRecord

if TYPE_CHECKING:
    from ..durable.judgment import JudgmentRecord


class Store(Protocol):
    # ── source layer (immutable) ------------------------------------------
    def add_source(self, record: SourceRecord) -> SourceRecord:
        """Persist a record. Adding an id that already exists is a no-op —
        content-addressing makes re-ingestion naturally idempotent."""
        ...

    def get_source(self, source_id: str) -> SourceRecord | None: ...

    def sources(self) -> Iterable[SourceRecord]: ...

    # ── node layers (versioned) -------------------------------------------
    def add_node(self, node: Node) -> Node: ...

    def get_node(self, node_id: str) -> Node | None: ...

    def nodes(self, layer: str | None = None) -> Iterable[Node]:
        """Every node, optionally filtered to one layer. Includes historical
        versions — callers that want only current heads use ``head``."""
        ...

    def versions(self, identity: str) -> list[Node]:
        """All versions sharing an identity, oldest first."""
        ...

    def head(self, identity: str) -> Node | None:
        """The latest version for an identity, or None if unknown."""
        ...

    # ── judgment records (append-only audit log) --------------------------
    def add_judgment(self, record: "JudgmentRecord") -> "JudgmentRecord":
        """Append an immutable judgment record. Never mutates an existing one —
        a superseding judgment is a new record (M3.1-A Judgment Contract)."""
        ...

    def get_judgment(self, judgment_id: str) -> "JudgmentRecord | None": ...

    def judgments(self) -> Iterable["JudgmentRecord"]:
        """Every judgment record, in the order it was appended."""
        ...
