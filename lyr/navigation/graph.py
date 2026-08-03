"""NavigationGraph — the data model for M3.2 knowledge organization.

Deliberately domain-agnostic and **overlap-ready**: a durable memory may appear in
several groups (real knowledge crosses topics), so groups hold member-id lists rather
than partitioning the durables. The Evidence-Connectivity Baseline happens to produce
disjoint components, but the schema does not assume that — a future overlapping
organizer needs no schema change.

Every connection carries the structural reason it exists, so the graph is itself
explainable (M3.2 P4).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

# Connection relations (both are generic — neither needs to know the domain).
SHARED_SEMANTIC = "shared_semantic"   # two durables cite a common semantic record
SHARED_SOURCE = "shared_source"       # their evidence traces to a common source/origin


@dataclass(frozen=True)
class NavConnection:
    """A durable ↔ durable edge, with the evidence that justifies it."""

    frm: str
    to: str
    relation: str
    support: tuple[str, ...]


@dataclass
class NavGroup:
    """A navigation cluster. `members` MAY overlap with other groups (by design)."""

    id: str
    label: str
    members: list[str]


@dataclass
class NavigationGraph:
    """Durable memories organized for navigation — built only from generic facets."""

    durables: list[dict[str, Any]]
    groups: list[NavGroup]
    connections: list[NavConnection]
    entry_points: dict[str, Any] = field(default_factory=dict)

    # ── metrics (M3.2-A §6) -----------------------------------------------
    @property
    def n_durables(self) -> int:
        return len(self.durables)

    @property
    def n_groups(self) -> int:
        return len(self.groups)

    @property
    def compression(self) -> float:
        """durables ÷ groups. 1.0 = all singletons = generic but no organization value."""
        return round(self.n_durables / self.n_groups, 3) if self.groups else 0.0

    @property
    def singletons(self) -> int:
        return sum(1 for g in self.groups if len(g.members) == 1)

    @property
    def largest_group(self) -> int:
        return max((len(g.members) for g in self.groups), default=0)

    def to_dict(self) -> dict[str, Any]:
        return {
            "durables": self.durables,
            "groups": [asdict(g) for g in self.groups],
            "connections": [asdict(c) for c in self.connections],
            "entry_points": self.entry_points,
            "metrics": {
                "n_durables": self.n_durables, "n_groups": self.n_groups,
                "compression": self.compression, "singletons": self.singletons,
                "largest_group": self.largest_group,
            },
        }
