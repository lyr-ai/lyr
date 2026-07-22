"""Durable layer (M3): consolidate recurring semantic records into long-term knowledge.

The Durable Builder answers one question — *what deserves to become long-term
knowledge?* — by consolidating semantic records that recur across multiple
independent experiences into stable Durable Memories.

It obeys the M3 invariants: stable identity (memories evolve v1 → v2 → v3, never
regenerated), minimal change (small evidence → small update; NO_OP is the common
outcome), provenance (every durable memory cites its supporting semantic
records, and every semantic record can discover the durables it supports), layer
isolation (only semantic records are consumed — never raw source), and
reproducibility (identical inputs + config → identical proposals).
"""

from .base import DURABLE_OPS, Consolidator, DurableProposal
from .builder import DurableBuilder
from .llm import LLMConsolidator
from .recurrence import RecurrenceConsolidator

__all__ = [
    "Consolidator",
    "DurableProposal",
    "DURABLE_OPS",
    "RecurrenceConsolidator",
    "LLMConsolidator",
    "DurableBuilder",
]
