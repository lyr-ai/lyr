"""JudgmentRecord — the immutable audit artifact of one durable judgment.

Records *how* a single automated consolidation attempt reached a durable
operation: the semantic evidence it considered, the model's proposed meaning, the
evidence grouping it saw, and the action the engine actually committed. Per the
M3.1-A Judgment Contract it is **not** a ``Node`` — it has no ``layer``, no
identity/version chain, and is never returned by durable queries. It is
scaffolding *for* a durable decision, stored append-only alongside nodes.

Two halves are kept distinct on purpose (the M3 principle, sharpened):

    Model proposes meaning   → ``model_intent`` (stored verbatim)
    Engine commits identity  → ``final_engine_action`` (what actually happened)

Recording both is what lets an audit see where model intent and engine invariant
diverged (e.g. an ADD onto an existing identity that the engine evolved instead).

Design: docs/design/M3.1-A-judgment-contract.md, M3.1-B-minimal-durable-builder.md.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from ..models import Node

# Engine actions that commit no durable version (in addition to base's NO_OP).
REJECT = "REJECT"


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ModelProposal:
    """The model's half — what it proposed, preserved exactly as interpreted.

    ``evidence`` and ``target_identity`` are already resolved from the model's
    indices to real ids by the builder; the model never invents ids itself.
    """

    operation: str
    statement: str
    kind: str
    evidence: list[str] = field(default_factory=list)
    target_identity: str | None = None
    superseded: list[str] = field(default_factory=list)
    rationale: str = ""
    counter_evidence: str = ""
    confidence: float | None = None


@dataclass
class EngineAction:
    """The engine's half — what was actually committed.

    ``operation`` is ADD / UPDATE / MERGE / NO_OP / REJECT. NO_OP and REJECT commit
    no durable version, so ``node_id`` / ``identity`` / ``version`` stay ``None``.
    ``operation`` may differ from the model's proposal (e.g. an ADD the identity
    guard evolved into an UPDATE, or an inert UPDATE downgraded to NO_OP).
    """

    operation: str
    node_id: str | None = None
    identity: str | None = None
    version: int | None = None
    rejection_reason: str | None = None


@dataclass
class JudgmentRecord:
    """One immutable record of a durable judgment attempt (accepted or not)."""

    judgment_id: str
    model_intent: ModelProposal
    final_engine_action: EngineAction
    candidate_semantic_ids: list[str] = field(default_factory=list)
    candidate_durable_identities: list[str] = field(default_factory=list)
    evidence_groups: list[dict[str, Any]] = field(default_factory=list)
    model_config: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_now)

    @property
    def id(self) -> str:
        """Alias so the store keys judgments like sources and nodes."""
        return self.judgment_id

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        return d


@dataclass
class JudgmentResult:
    """Return value of ``JudgmentBuilder.update`` — the stable M3.1-B interface."""

    judgment_record: JudgmentRecord
    engine_action: EngineAction
    updated_durable: Node | None
