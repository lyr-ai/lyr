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
from .base import ADD, MERGE, NO_OP, UPDATE, Consolidator, DurableProposal


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
        """Ask the consolidator for operations, without touching the store."""
        return self._consolidator.consolidate(
            self._heads("semantic"), self._heads("durable")
        )

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
    def _apply_one(self, proposal: DurableProposal) -> Node | None:
        head = self._store.head(proposal.identity)

        if proposal.op == NO_OP:
            return None

        if proposal.op == ADD or (proposal.op in (UPDATE, MERGE) and head is None):
            node = Node(
                layer="durable",
                kind=proposal.kind,
                label=proposal.statement,
                identity=proposal.identity,
                evidence=sorted(set(proposal.evidence)),
                attributes=dict(proposal.attributes),
            )
            return self._store.add_node(node)

        if proposal.op == UPDATE:
            return self._evolve(head, proposal, dict(proposal.attributes))

        if proposal.op == MERGE:
            # Fold the superseded memories' evidence into the target, and record
            # where it came from. The superseded chains stay in the store, so
            # their history remains discoverable.
            evidence = set(proposal.evidence)
            merged_from: list[str] = list(proposal.superseded)
            for identity in proposal.superseded:
                other = self._store.head(identity)
                if other is not None:
                    evidence.update(other.evidence)
            attributes = dict(proposal.attributes)
            if merged_from:
                attributes["merged_from"] = sorted(merged_from)
            merged_proposal = DurableProposal(
                op=UPDATE, identity=proposal.identity, statement=proposal.statement,
                kind=proposal.kind, evidence=sorted(evidence), attributes=attributes,
            )
            return self._evolve(head, merged_proposal, attributes)

        return None

    def _evolve(
        self, head: Node, proposal: DurableProposal, attributes: dict[str, Any]
    ) -> Node | None:
        """Evolve ``head`` to a new version — or NO_OP if nothing changed."""
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
