"""The Consolidator contract and the durable update operations.

A ``Consolidator`` looks at the current semantic records (and the durable
memories that already exist) and *proposes* a small set of operations. It does
not touch the store — proposing and applying are deliberately separated so the
proposals are a first-class, inspectable output (the M3 evaluation benchmark
grades proposals, not side effects).

The four operations are the whole vocabulary of durable maintenance:

    ADD     create a new durable memory
    UPDATE  revise an existing one, preserving its identity
    MERGE   fold several durable memories into one (old versions kept in history)
    NO_OP   nothing meaningful changed — the common case

Keeping the *policy* (thresholds, identity resolution, contradiction handling —
all M3 open research questions) inside a pluggable ``Consolidator`` is what lets
those questions be answered differently later without touching the builder.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Protocol

from ..models import Node

# The complete set of durable update operations.
ADD = "ADD"
UPDATE = "UPDATE"
MERGE = "MERGE"
NO_OP = "NO_OP"
DURABLE_OPS: tuple[str, ...] = (ADD, UPDATE, MERGE, NO_OP)

# Lifecycle status carried in ``Node.attributes["status"]``. A memory folded into
# another by MERGE is *retired* — kept in the store for history and provenance,
# but excluded from active ("what do we currently believe?") queries.
RETIRED = "retired"


def is_active(node: Node) -> bool:
    """True unless the node has been retired (e.g. merged into another memory)."""
    return node.attributes.get("status") != RETIRED


@dataclass
class DurableProposal:
    """A proposed change to the durable layer — the unit the builder applies.

    ``identity`` is the durable memory the operation targets (stable across
    revisions). ``evidence`` lists the *semantic record* ids that support the
    statement. ``superseded`` is used only by MERGE: the other durable
    identities being folded into ``identity``. ``reason`` is a short,
    human-readable justification, carried for auditability and evaluation.
    """

    op: str
    identity: str
    statement: str
    kind: str = "lesson"
    evidence: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    superseded: list[str] = field(default_factory=list)
    reason: str = ""

    def __post_init__(self) -> None:
        if self.op not in DURABLE_OPS:
            raise ValueError(f"DurableProposal.op must be one of {DURABLE_OPS}, got {self.op!r}")

    def key(self) -> tuple[str, str]:
        """The (identity, op) pair — the grain the benchmark scores on."""
        return (self.identity, self.op)


class Consolidator(Protocol):
    def consolidate(
        self,
        semantic_nodes: Iterable[Node],
        existing_durable: Iterable[Node],
    ) -> list[DurableProposal]:
        """Propose durable operations from semantic records + existing durables.

        ``semantic_nodes`` are current semantic heads; ``existing_durable`` are
        current durable heads. The return value is a deterministic-ordered list
        of proposals (for reproducibility, implementations should sort stably).
        """
        ...
