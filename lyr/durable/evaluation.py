"""Evaluation *harness* for durable consolidation — scaffolding, not yet a benchmark.

This module measures properties of a consolidation round. Some of them are
objective and need no labels — they check the engine's substrate:

- **identity preservation** — do durable memories keep a single, well-formed
  version chain (no rival identities for the same knowledge)?
- **provenance completeness** — does every durable memory's evidence resolve?
- **minimal change** — how much of the proposal set is NO_OP (stability)?
- **reproducibility** — same inputs + config → same proposals?

**Update precision / recall are different: they need ground truth.** There is no
agreed definition yet of what *should* be durable (that is the open research
question — recurrence is not durability), so this harness cannot supply gold
labels. ``update_precision_recall`` scores predictions against a ``gold`` set the
caller provides; ``evaluate`` reports precision/recall as ``None`` when no gold is
given rather than inventing a passing score.

A real durability benchmark — human-labeled "is this durable?" / "are these
independent evidence?" cases — is future work. Do not read a high score here as
evidence that the consolidation *judgments* are correct; the labelled parts only
attest that the *substrate* (identity, history, provenance) held.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..models import Node
from ..provenance import dangling_evidence
from ..store.base import Store
from .base import NO_OP, Consolidator, DurableProposal


@dataclass
class EvalReport:
    identity_preservation: float
    minimal_change: float
    provenance_completeness: float
    # None when no gold labels were supplied — the harness will not invent a
    # score for a judgment it cannot ground.
    update_precision: float | None
    update_recall: float | None
    reproducible: bool

    def as_dict(self) -> dict[str, float | bool | None]:
        return {
            "identity_preservation": self.identity_preservation,
            "minimal_change": self.minimal_change,
            "provenance_completeness": self.provenance_completeness,
            "update_precision": self.update_precision,
            "update_recall": self.update_recall,
            "reproducible": self.reproducible,
        }


def _changes(proposals: Iterable[DurableProposal]) -> set[tuple[str, str]]:
    """The (identity, op) grain of the *changing* proposals (NO_OP excluded)."""
    return {p.key() for p in proposals if p.op != NO_OP}


def update_precision_recall(
    predicted: list[DurableProposal], gold: list[DurableProposal]
) -> tuple[float, float]:
    """Precision/recall of changing operations against a gold proposal set.

    A prediction is correct when a gold proposal shares its identity *and*
    operation. NO_OPs are ignored on both sides — the benchmark measures the
    changes a maintainer proposed, not the silence between them.
    """
    pred, want = _changes(predicted), _changes(gold)
    if not pred and not want:
        return 1.0, 1.0
    correct = len(pred & want)
    precision = correct / len(pred) if pred else 0.0
    recall = correct / len(want) if want else 0.0
    return precision, recall


def minimal_change(proposals: list[DurableProposal]) -> float:
    """Fraction of proposals that are NO_OP — higher means more stable."""
    if not proposals:
        return 1.0
    noops = sum(1 for p in proposals if p.op == NO_OP)
    return noops / len(proposals)


def identity_preservation(store: Store) -> float:
    """Fraction of durable identities with a well-formed version chain.

    A chain is well-formed when versions run 1..n and each version links to its
    predecessor via ``parent_id``. A broken chain means an update forked the
    identity instead of preserving it.
    """
    identities = {n.identity for n in store.nodes(layer="durable")}
    if not identities:
        return 1.0
    good = 0
    for identity in identities:
        chain = store.versions(identity)
        expected_versions = list(range(1, len(chain) + 1))
        if [n.version for n in chain] != expected_versions:
            continue
        links_ok = chain[0].parent_id is None and all(
            chain[i].parent_id == chain[i - 1].id for i in range(1, len(chain))
        )
        if links_ok:
            good += 1
    return good / len(identities)


def provenance_completeness(store: Store) -> float:
    """Fraction of durable nodes whose evidence all resolves (nothing dangling)."""
    durable = list(store.nodes(layer="durable"))
    if not durable:
        return 1.0
    complete = sum(1 for n in durable if not dangling_evidence(n, store))
    return complete / len(durable)


def is_reproducible(
    consolidator: Consolidator,
    semantic_nodes: list[Node],
    existing_durable: list[Node],
) -> bool:
    """True if two consolidation runs over identical inputs match exactly."""
    first = consolidator.consolidate(semantic_nodes, existing_durable)
    second = consolidator.consolidate(semantic_nodes, existing_durable)
    return first == second


def evaluate(
    *,
    store: Store,
    predicted: list[DurableProposal],
    consolidator: Consolidator,
    semantic_nodes: list[Node],
    existing_durable: list[Node],
    gold: list[DurableProposal] | None = None,
) -> EvalReport:
    """Score a consolidation round across every M3 maintenance metric.

    ``predicted`` are the proposals under test (already applied to ``store``);
    ``gold`` is an optional set of human-labeled expected operations. When
    omitted, precision/recall are ``None`` — the harness does not fabricate a
    score for judgments it cannot ground.
    """
    precision: float | None
    recall: float | None
    if gold is None:
        precision = recall = None
    else:
        precision, recall = update_precision_recall(predicted, gold)

    return EvalReport(
        identity_preservation=identity_preservation(store),
        minimal_change=minimal_change(predicted),
        provenance_completeness=provenance_completeness(store),
        update_precision=precision,
        update_recall=recall,
        reproducible=is_reproducible(consolidator, semantic_nodes, existing_durable),
    )
