"""Node — one unit of derived knowledge, at any layer of abstraction.

Above the immutable Source layer, LYR maintains three layers of abstraction:

    Semantic   — what the sources describe (entities, events, relationships)
    Durable    — what stays important after many experiences (lessons, decisions)
    Cognitive  — how accumulated knowledge shapes future reasoning (principles)

They are the *same shape*. A ``Node`` at any layer is a labelled claim that
points to its evidence one layer below — a semantic node cites source records,
a durable node cites semantic nodes, a cognitive node cites durable nodes. That
uniformity is what makes provenance a single recursive walk (see
``lyr.provenance``) and lets the higher builders reuse one mechanism.

Three fields carry LYR's non-obvious principles:

- ``evidence`` — ids one layer down. No node exists without it (principle 3).
- ``identity`` — stable across revisions; a node evolves v1 → v2 → v3 while
  keeping the same identity (principle 4). Two nodes with the same ``identity``
  are the same knowledge at different points in time.
- ``version`` / ``parent_id`` — the revision chain, so evolution is inspectable
  (a node is only re-versioned when its meaning actually changes — principle 5).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from ..ids import content_id

# The abstraction layers a Node can live at, ordered ground-up. The Source layer
# is not here — it is modelled separately by SourceRecord because it is
# immutable and unversioned.
LAYERS: tuple[str, ...] = ("semantic", "durable", "cognitive")


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Node:
    """A labelled claim with provenance and identity.

    ``kind`` is layer-specific vocabulary — ``entity`` / ``event`` /
    ``relationship`` at the semantic layer, ``lesson`` / ``decision`` /
    ``preference`` at the durable layer, ``principle`` / ``pattern`` at the
    cognitive layer. ``attributes`` holds the structured payload for that kind
    (e.g. an entity's ``entity_type``, a relationship's ``subject`` /
    ``predicate`` / ``object``).
    """

    layer: str
    kind: str
    label: str
    identity: str
    evidence: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    parent_id: str | None = None
    created_at: datetime = field(default_factory=_now)
    id: str = ""

    def __post_init__(self) -> None:
        if self.layer not in LAYERS:
            raise ValueError(f"Node.layer must be one of {LAYERS}, got {self.layer!r}")
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("Node.label must be a non-empty string")
        if not isinstance(self.identity, str) or not self.identity:
            raise ValueError("Node.identity must be a non-empty string")
        if self.version < 1:
            raise ValueError(f"Node.version must be >= 1, got {self.version}")
        if self.id == "":
            # A node's id is unique per *version*: same identity + version + the
            # meaning-bearing content collapses to the same id (idempotent
            # rebuilds), while a genuine revision gets a fresh id.
            self.id = content_id(
                "sem" if self.layer == "semantic" else self.layer[:3],
                self.identity,
                self.version,
                self.label,
                sorted(self.evidence),
            )

    def evolved(
        self,
        *,
        label: str | None = None,
        attributes: dict[str, Any] | None = None,
        evidence: list[str] | None = None,
    ) -> "Node":
        """Return the next version of this node, preserving identity.

        This is how knowledge changes in LYR: not a fresh node, but a child that
        keeps the same ``identity`` and links back via ``parent_id``. Callers
        decide *when* to evolve (see the builders' minimal-change logic); this
        method just makes the successor correctly.
        """
        return Node(
            layer=self.layer,
            kind=self.kind,
            label=label if label is not None else self.label,
            identity=self.identity,
            evidence=list(evidence if evidence is not None else self.evidence),
            attributes=dict(attributes if attributes is not None else self.attributes),
            version=self.version + 1,
            parent_id=self.id,
        )

    # ── serialization ------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Node":
        data = dict(d)
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        valid = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in valid})
