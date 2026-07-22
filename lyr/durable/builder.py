"""DurableBuilder — turn consolidation proposals into maintained durable memory.

The builder is the only component that writes the durable layer. It reads the
current semantic and durable heads from the store, asks the injected
``Consolidator`` for proposals, and applies them — enforcing the M3 invariants as
it goes:

- **stable identity** — UPDATE/MERGE evolve an existing memory (``Node.evolved``)
  rather than creating a rival with a fresh identity;
- **minimal change** — an UPDATE that wouldn't actually change anything is
  downgraded to NO_OP, so no version churn;
- **provenance** — durable nodes cite semantic ids, so ``lyr.provenance`` traces
  them straight down to source;
- **history** — MERGE keeps the superseded memories' prior versions in the store.

``propose`` and ``apply`` are separate entry points so proposals can be inspected
or benchmarked before (or without) being applied; ``build`` does both.
"""

from __future__ import annotations

from typing import Any

from ..models import Node
from ..store.base import Store
from .base import (
    MERGE,
    NO_OP,
    RETIRED,
    UPDATE,
    Consolidator,
    DurableProposal,
    is_active,
)


class DurableBuilder:
    def __init__(self, store: Store, consolidator: Consolidator) -> None:
        self._store = store
        self._consolidator = consolidator

    # ── head selection ----------------------------------------------------
    def _heads(self, layer: str) -> list[Node]:
        heads: dict[str, Node] = {}
        for node in self._store.nodes(layer=layer):
            current = heads.get(node.identity)
            if current is None or node.version > current.version:
                heads[node.identity] = node
        return list(heads.values())

    # ── propose / apply / build -------------------------------------------
    def propose(self) -> list[DurableProposal]:
        """Ask the consolidator for operations, without touching the store.

        Only *active* durable memories are offered to the consolidator — a
        retired (merged-away) memory is not a valid UPDATE/MERGE target.
        """
        active_durable = [n for n in self._heads("durable") if is_active(n)]
        return self._consolidator.consolidate(self._heads("semantic"), active_durable)

    def apply(self, proposals: list[DurableProposal]) -> list[Node]:
        """Apply proposals to the store; return the durable nodes affected."""
        affected: list[Node] = []
        for proposal in proposals:
            node = self._apply_one(proposal)
            if node is not None:
                affected.append(node)
        return affected

    def build(self) -> list[DurableProposal]:
        """Consolidate and apply in one call; return the proposals made."""
        proposals = self.propose()
        self.apply(proposals)
        return proposals

    # ── operation handlers ------------------------------------------------
    #
    # Model proposes meaning; the engine commits identity, history, and
    # provenance. Whatever a consolidator asks for, the builder guarantees the
    # invariants below — a consolidator can never fork an identity or lose
    # history through the operation it names.
    def _apply_one(self, proposal: DurableProposal) -> Node | None:
        if proposal.op == NO_OP:
            return None

        head = self._store.head(proposal.identity)

        if proposal.op == MERGE:
            return self._apply_merge(head, proposal)

        # ADD / UPDATE.
        if head is None:
            # A genuinely new identity → create v1. This covers an ADD, and an
            # UPDATE whose target no longer exists (nothing to evolve).
            return self._create_v1(proposal, sorted(set(proposal.evidence)), dict(proposal.attributes))

        # Identity guard (#6): an ADD onto an *existing* identity must never
        # mint a second v1 — it becomes an evolve, so the chain stays 1..n. This
        # also covers two same-identity ADDs within one batch (the first creates
        # v1, the second sees the head and evolves).
        return self._evolve(head, proposal, dict(proposal.attributes))

    def _apply_merge(self, head: Node | None, proposal: DurableProposal) -> Node | None:
        """Fold superseded memories into the target and retire them.

        Each superseded memory is *tombstoned* (a new version marked
        ``status=retired`` with ``merged_into`` set): its evidence moves to the
        target, its full history and provenance stay in the store, and active
        queries stop returning it. The merge does not delete anything.
        """
        evidence = set(proposal.evidence)
        merged_from: list[str] = []
        for identity in proposal.superseded:
            if identity == proposal.identity:
                continue
            other = self._store.head(identity)
            if other is None or not is_active(other):
                continue
            evidence.update(other.evidence)
            merged_from.append(identity)
            self._retire(other, into=proposal.identity)

        attributes = dict(proposal.attributes)
        if merged_from:
            attributes["merged_from"] = sorted(set(merged_from))

        if head is None:
            return self._create_v1(proposal, sorted(evidence), attributes)

        merged = DurableProposal(
            op=UPDATE, identity=proposal.identity, statement=proposal.statement,
            kind=proposal.kind, evidence=sorted(evidence), attributes=attributes,
        )
        return self._evolve(head, merged, attributes)

    def _retire(self, head: Node, *, into: str) -> Node:
        """Tombstone ``head`` — a new version marking it merged into ``into``.

        History is preserved (prior versions remain) and provenance is intact
        (evidence is carried over), so the retired memory stays fully traceable;
        it is simply excluded from active queries.
        """
        retired = head.evolved(
            attributes={**head.attributes, "status": RETIRED, "merged_into": into}
        )
        return self._store.add_node(retired)

    def _create_v1(
        self, proposal: DurableProposal, evidence: list[str], attributes: dict[str, Any]
    ) -> Node:
        return self._store.add_node(
            Node(
                layer="durable", kind=proposal.kind, label=proposal.statement,
                identity=proposal.identity, evidence=evidence, attributes=attributes,
            )
        )

    def _evolve(
        self, head: Node, proposal: DurableProposal, attributes: dict[str, Any]
    ) -> Node | None:
        """Evolve ``head`` to a new version — or NO_OP if nothing changed.

        Change is currently detected *syntactically*: the evidence set, the exact
        statement string, and attributes. That is stable for deterministic
        consolidators; detecting semantic equivalence (a paraphrase is "the same
        knowledge") is a model judgment and is out of scope for the substrate.
        """
        merged_evidence = sorted(set(head.evidence) | set(proposal.evidence))
        merged_attributes = {**head.attributes, **attributes}

        unchanged = (
            merged_evidence == sorted(head.evidence)
            and proposal.statement == head.label
            and merged_attributes == head.attributes
        )
        if unchanged:
            return None  # minimal change: no version churn

        evolved = head.evolved(
            label=proposal.statement,
            attributes=merged_attributes,
            evidence=merged_evidence,
        )
        return self._store.add_node(evolved)
