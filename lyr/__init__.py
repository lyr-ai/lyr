"""LYR: living knowledge layers.

LYR transforms evolving information into layered, explorable knowledge. Rather
than storing flat documents or embeddings, it continuously builds and maintains
multiple layers of abstraction over immutable observations, while preserving
complete provenance back to the original evidence.

Five principles shape the engine:

1. Information evolves — update knowledge in place, don't rebuild from scratch.
2. Knowledge is layered — Source → Semantic → Durable → Cognitive.
3. Every abstraction is traceable — no node without evidence back to source.
4. Knowledge has identity — nodes evolve v1 → v2 → v3, keeping their identity.
5. Minimal change — small evidence produces small updates.

The engine ships the Source (M1), Semantic (M2), and Durable (M3) layers with
provenance tracing — both downward (any node → its source evidence) and upward
(a record → the durable memories it supports). The Cognitive layer (M4) is
representable in the model and slots in behind the same store and provenance
machinery.
"""

from .durable import (
    Consolidator,
    DurableBuilder,
    DurableProposal,
    LLMConsolidator,
    RecurrenceConsolidator,
)
from .engine import LYR
from .ids import content_id, normalize
from .ingestion import Document, Ingestor, TextIngestor
from .models import LAYERS, Node, SourceRecord
from .provenance import (
    ProvenanceTree,
    dangling_evidence,
    explain,
    supporters,
    trace,
)
from .semantic import (
    ExtractedNode,
    ExtractionResult,
    Extractor,
    LLMExtractor,
    RuleBasedExtractor,
    SemanticBuilder,
)
from .store import InMemoryStore, Store

__version__ = "0.1.0"

__all__ = [
    "LYR",
    "__version__",
    # models
    "SourceRecord",
    "Node",
    "LAYERS",
    # ingestion
    "Document",
    "Ingestor",
    "TextIngestor",
    # semantic
    "Extractor",
    "ExtractedNode",
    "ExtractionResult",
    "RuleBasedExtractor",
    "LLMExtractor",
    "SemanticBuilder",
    # durable (M3)
    "Consolidator",
    "DurableProposal",
    "RecurrenceConsolidator",
    "LLMConsolidator",
    "DurableBuilder",
    # store
    "Store",
    "InMemoryStore",
    # provenance
    "trace",
    "explain",
    "supporters",
    "dangling_evidence",
    "ProvenanceTree",
    # ids
    "content_id",
    "normalize",
]
