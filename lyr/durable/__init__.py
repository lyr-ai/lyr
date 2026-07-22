"""Durable layer (M3): maintain long-term knowledge over the semantic layer.

The Durable layer is where LYR stops merely extracting and starts *maintaining*
knowledge — consolidating semantic records into stable Durable Memories that keep
their identity and version history as evidence accumulates.

**What is "durable" is a policy, not a fixed rule.** The engine deliberately
takes no position on it. It supplies the trustworthy substrate — identity,
version history, provenance, and the ADD/UPDATE/MERGE/NO_OP lifecycle — and
defers the *judgment* of what deserves to be long-term knowledge to a pluggable
``Consolidator``:

    Model proposes meaning.  Engine commits identity, history, and provenance.

``RecurrenceConsolidator`` is a **deterministic structural baseline** — it treats
cross-record recurrence as a cheap proxy signal. It is useful offline, as a test
control, and as a comparison baseline, but it is explicitly *not* LYR's
definition of durability: recurrence is not the same as importance, and a
significant one-off can be durable while repeated noise is not. Real durability
judgment (evidence independence, significance) is model-driven and is the subject
of the next design milestone.
"""

from .base import DURABLE_OPS, RETIRED, Consolidator, DurableProposal, is_active
from .builder import DurableBuilder
from .llm import LLMConsolidator
from .recurrence import RecurrenceConsolidator

__all__ = [
    "Consolidator",
    "DurableProposal",
    "DURABLE_OPS",
    "RETIRED",
    "is_active",
    "RecurrenceConsolidator",
    "LLMConsolidator",
    "DurableBuilder",
]
