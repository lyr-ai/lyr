"""Source Records — the immutable ground floor.

A Source Record answers exactly one question: *what happened?* It is a verbatim
observation — a paragraph, a transcript turn, a log line, an email, a document
section — captured without interpretation. Everything LYR builds on top of it
(entities, events, lessons, principles) must trace back down to records like
these, so records are treated as immutable evidence: once created, they are
never edited. New understanding produces new records or new higher-layer nodes,
never a rewrite of what was observed.

The id is content-addressed from ``(origin, position, content)`` so re-ingesting
the same document yields the same record ids — the substrate for LYR's
minimal-change principle.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from ..ids import content_id


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class SourceRecord:
    """One immutable observation.

    ``origin`` names where it came from (a document id, a meeting name, a file
    path); ``position`` is its ordinal within that origin, so records can be
    re-assembled in order and cited precisely ("paragraph 4 of design-doc.md").
    """

    content: str
    origin: str
    position: int = 0
    kind: str = "paragraph"  # paragraph | transcript | log | email | section | ...
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_now)
    id: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("SourceRecord.content must be a non-empty string")
        if not isinstance(self.origin, str) or not self.origin:
            raise ValueError("SourceRecord.origin must be a non-empty string")
        if self.id == "":
            # frozen dataclass: assign the derived id through object.__setattr__
            object.__setattr__(
                self, "id", content_id("src", self.origin, self.position, self.content)
            )

    # ── serialization ------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SourceRecord":
        data = dict(d)
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        valid = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in valid})
