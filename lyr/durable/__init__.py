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
from .judgment import (
    ERROR,
    KEEP,
    REJECT,
    SUCCESS,
    UNSURE,
    VERDICT_DECISIONS,
    EngineAction,
    EvidenceGroup,
    JudgmentRecord,
    JudgmentResult,
    ModelProposal,
    Verdict,
    new_judgment_id,
)
from .verifier import (
    VERIFIER_PROMPT,
    VERIFIER_PROMPT_VERSION,
    DurabilityVerifier,
    LLMDurabilityVerifier,
    ThresholdDurabilityVerifier,
)
from .judgment_builder import PROMPT, PROMPT_VERSION, JudgmentBuilder
from .decomposition import (
    DECOMPOSER_PROMPT,
    DECOMPOSER_PROMPT_VERSION,
    Decomposer,
    JudgmentUnit,
    LLMDecomposer,
    SingletonDecomposer,
    WholeBatchDecomposer,
)
from .pipeline import JudgmentPipeline
from .llm import LLMConsolidator
from .recurrence import RecurrenceConsolidator

__all__ = [
    "Consolidator",
    "DurableProposal",
    "DURABLE_OPS",
    "RETIRED",
    "REJECT",
    "is_active",
    "RecurrenceConsolidator",
    "LLMConsolidator",
    "DurableBuilder",
    "JudgmentBuilder",
    "JudgmentRecord",
    "JudgmentResult",
    "ModelProposal",
    "EngineAction",
    "EvidenceGroup",
    "new_judgment_id",
    "PROMPT",
    "PROMPT_VERSION",
    "Decomposer",
    "JudgmentUnit",
    "WholeBatchDecomposer",
    "SingletonDecomposer",
    "LLMDecomposer",
    "DECOMPOSER_PROMPT",
    "DECOMPOSER_PROMPT_VERSION",
    "JudgmentPipeline",
    "Verdict",
    "KEEP",
    "UNSURE",
    "SUCCESS",
    "ERROR",
    "VERDICT_DECISIONS",
    "DurabilityVerifier",
    "LLMDurabilityVerifier",
    "ThresholdDurabilityVerifier",
    "VERIFIER_PROMPT",
    "VERIFIER_PROMPT_VERSION",
]
