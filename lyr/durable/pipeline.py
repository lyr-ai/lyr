"""JudgmentPipeline (M3.1-B.2) — decompose, then run the unchanged builder per unit.

The whole of M3.1-B.2's new behavior lives here, and it is deliberately thin: a
``Decomposer`` splits the semantic batch into judgment units, and a single,
**unmodified** ``JudgmentBuilder`` is looped over them — one ``update()``, one
``JudgmentRecord`` per unit (G1, G3).

    pipeline.run(semantic, candidates)
        → decomposer.decompose(...)          → [Unit A, Unit B, …]
        → builder.update(unitA…)             → JudgmentResult A
        → builder.update(unitB…)             → JudgmentResult B
        → […]

Units are judged independently against the *original* candidate set: a fresh batch's
topics are disjoint, so a durable created for one unit is not offered to the next.
(Re-reading heads between units — for the case where decomposition wrongly splits one
topic — is a deliberate non-goal here.)

Design: docs/design/M3.1-B.2-judgment-decomposition.md.
"""

from __future__ import annotations

from typing import Iterable

from ..llm.base import LLMClient
from ..models import Node
from ..store.base import Store
from .decomposition import Decomposer, WholeBatchDecomposer
from .judgment import JudgmentResult
from .judgment_builder import JudgmentBuilder


class JudgmentPipeline:
    """Decompose a semantic batch into topics, then judge each with the builder."""

    def __init__(
        self, store: Store, client: LLMClient, decomposer: Decomposer | None = None
    ) -> None:
        # The builder is used verbatim — no subclassing, no new entry point (G3).
        self._builder = JudgmentBuilder(store, client)
        # Default to the control decomposer, so a pipeline with no decomposer behaves
        # exactly like a single pre-M3.1-B.2 update().
        self._decomposer: Decomposer = decomposer or WholeBatchDecomposer()

    def run(
        self,
        semantic_nodes: Iterable[Node],
        candidate_durable_nodes: Iterable[Node],
    ) -> list[JudgmentResult]:
        """Return one ``JudgmentResult`` per topic unit (empty if no records)."""
        units = self._decomposer.decompose(list(semantic_nodes), list(candidate_durable_nodes))
        return [
            self._builder.update(u.semantic_nodes, u.candidate_durable_nodes) for u in units
        ]
