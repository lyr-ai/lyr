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

v0.1 ships the M1 (Source) + M2 (Semantic) vertical slice with working
provenance tracing across both layers. The Durable and Cognitive layers are
representable in the model and slot in behind the same store and provenance
machinery in later milestones.
"""

from .engine import LYR
from .ids import content_id, normalize
from .ingestion import Document, Ingestor, TextIngestor
from .models import LAYERS, Node, SourceRecord
from .provenance import ProvenanceTree, dangling_evidence, explain, trace
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
    # store
    "Store",
    "InMemoryStore",
    # provenance
    "trace",
    "explain",
    "dangling_evidence",
    "ProvenanceTree",
    # ids
    "content_id",
    "normalize",
]
