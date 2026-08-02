"""JudgmentRecord — the immutable audit artifact of one durable judgment.

Records *how* a single automated consolidation attempt reached a durable
operation: the raw model output, the builder's interpretation, the evidence
grouping it saw, and the action the engine actually committed. Per the M3.1-A
Judgment Contract it is **not** a ``Node`` — it has no ``layer``, no
identity/version chain, and is never returned by durable queries. It is
scaffolding *for* a durable decision, stored append-only alongside nodes.

Four stages are kept distinct so debugging never has to guess what the model
produced (M3.1-B.1):

    raw_completion       → the LLM's exact output string
    parsed_payload       → the JSON the builder parsed out of it (or None)
    model_intent         → the normalized, id-resolved proposal
    final_engine_action  → what the engine actually committed

Recording all four is what lets an audit see where model intent and engine
invariant diverged (e.g. an ADD onto an existing identity that the engine evolved
instead) — and re-parse old outputs if the parsing rules later change.

**Identity vs. fingerprint (M3.1-B.1).** ``judgment_id`` identifies an *execution
attempt* and is globally unique — two runs never share one, so history is never
overwritten. ``judgment_fingerprint`` is content-derived from the semantic
judgment and *may* repeat across executions, which is how duplicate attempts are
detected without conflating them.

Every record is a **frozen** dataclass with tuple fields: once built and appended
to the store it cannot be mutated.

Design: docs/design/M3.1-A-judgment-contract.md, M3.1-B-minimal-durable-builder.md,
M3.1-B.1-judgment-contract-hardening.md.
"""

from __future__ import annotations

import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from ..models import Node

# Engine actions that commit no durable version (in addition to base's NO_OP).
REJECT = "REJECT"

# Durability-verifier verdict axes (M3.1-C).
#   decision — what it judged;  status — whether it judged at all.
KEEP = "KEEP"
UNSURE = "UNSURE"
VERDICT_DECISIONS: tuple[str, ...] = (KEEP, REJECT, UNSURE)
SUCCESS = "SUCCESS"
ERROR = "ERROR"

# Crockford base32 (no I, L, O, U) — the ULID alphabet.
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _b32(value: int, length: int) -> str:
    out = []
    for _ in range(length):
        value, rem = divmod(value, 32)
        out.append(_CROCKFORD[rem])
    return "".join(reversed(out))


def new_judgment_id() -> str:
    """A globally unique, time-ordered execution id (ULID-style, zero-dep).

    48-bit millisecond timestamp + 80 bits of randomness, Crockford-base32
    encoded. Lexicographically sortable by creation time, and unique per
    execution — different judgment runs never collide, so an attempt can never
    overwrite another in the append-only log (M3.1-B.1 G1).
    """
    ms = time.time_ns() // 1_000_000
    rand = int.from_bytes(os.urandom(10), "big")  # 80 bits
    return f"jdg_{_b32(ms, 10)}{_b32(rand, 16)}"


@dataclass(frozen=True)
class EvidenceGroup:
    """The model's judgment that a set of records is one observation, validated.

    ``records`` are semantic-record indices (validated in range and de-duplicated
    by the builder); ``semantic_ids`` are those indices resolved to real ids, so
    the grouping stays meaningful even out of the original list's context.
    """

    records: tuple[int, ...] = ()
    same_observation: bool = False
    note: str = ""
    semantic_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ModelProposal:
    """The model's half — what it proposed, normalized and id-resolved.

    ``evidence`` and ``target_identity`` are already resolved from the model's
    indices to real ids by the builder; the model never invents ids itself.
    """

    operation: str
    statement: str
    kind: str
    evidence: tuple[str, ...] = ()
    target_identity: str | None = None
    superseded: tuple[str, ...] = ()
    rationale: str = ""
    counter_evidence: str = ""
    confidence: float | None = None


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class Verdict:
    """A durability verifier's judgment of one proposed durable memory (M3.1-C).

    Two independent axes: ``decision`` (KEEP / REJECT / UNSURE — what it judged) and
    ``status`` (SUCCESS / ERROR — whether it judged at all). A failed run (timeout,
    unparseable output, illegal verdict) is ``status=ERROR`` and must never be
    treated as a semantic UNSURE — the engine does not commit on ERROR.
    """

    decision: str
    status: str = SUCCESS
    rationale: str = ""
    confidence: float | None = None
    raw_completion: str = ""
    parsed_payload: dict[str, Any] | None = None
    error_reason: str | None = None
    model_config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class JudgmentRecord:
    """One immutable record of a durable judgment attempt (accepted or not).

    Frozen and tuple-backed: append-only in practice *and* in structure. The store
    keeps these; nothing mutates one after it is created.
    """

    judgment_id: str
    judgment_fingerprint: str
    model_intent: ModelProposal
    final_engine_action: EngineAction
    raw_completion: str = ""
    parsed_payload: dict[str, Any] | None = None
    # The durability verifier's verdict (M3.1-C). None when no verifier ran.
    verification: Verdict | None = None
    candidate_semantic_ids: tuple[str, ...] = ()
    candidate_durable_identities: tuple[str, ...] = ()
    evidence_groups: tuple[EvidenceGroup, ...] = ()
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


@dataclass(frozen=True)
class JudgmentResult:
    """Return value of ``JudgmentBuilder.update`` — the stable M3.1-B interface.

    ``updated_durable`` is the live committed ``Node`` (or ``None`` for NO_OP /
    REJECT); it is intentionally not frozen — only the audit ``judgment_record``
    is immutable.
    """

    judgment_record: JudgmentRecord
    engine_action: EngineAction
    updated_durable: Node | None
