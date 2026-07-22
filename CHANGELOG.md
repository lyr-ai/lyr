# Changelog

All notable changes to LYR are documented here. This project adheres to
[Semantic Versioning](https://semver.org/).

## [0.2.0] — unreleased (M3: Durable Layer)

Adds the **Durable Layer** — the first layer of long-term knowledge. LYR now
moves beyond extraction to *maintaining* knowledge: consolidating semantic
records that recur across independent experiences into stable Durable Memories,
with the same identity, versioning, and provenance guarantees as the layers
below.

### Added

- **Durable consolidation** — the `Consolidator` protocol and the four update
  operations (`ADD` / `UPDATE` / `MERGE` / `NO_OP`) as `DurableProposal`s.
  - `RecurrenceConsolidator` — deterministic default; promotes a topic to durable
    once ≥ `min_support` distinct source records back it (measured from semantic
    records' provenance only — never the source layer). Exactly reproducible.
  - `LLMConsolidator` — model-driven policy over any `LLMClient`; the model
    references existing memories by index and LYR owns identity resolution.
- **`DurableBuilder`** — separates `propose` from `apply`; enforces stable
  identity, minimal change (an inert UPDATE downgrades to NO_OP), and history
  retention on MERGE.
- **Bidirectional provenance** — `supporters()` walks provenance *upward*, so a
  semantic record can discover the durable memories it supports (M3 invariant).
- **Evaluation suite** (`lyr.durable.evaluation`) — the first knowledge-
  maintenance benchmark: identity preservation, minimal change, provenance
  completeness, update precision/recall, and reproducibility.
- **Engine** — `build_durable`, `propose_durable`, `durable_memories`,
  `supporters`, plus a `consolidator=` injection point on `LYR(...)`.

### Notes

- Durable confidence and support live in `Node.attributes` (no change to the
  `Node` model); confidence is a monotonic function of supporting evidence.
- Layer isolation is enforced by construction: consolidators consume `Node`s and
  their provenance ids, never `store.get_source`.
- Open M3 research questions (consolidation threshold, contradiction handling)
  are deliberately left to the pluggable consolidator, not baked into the engine.

## [0.1.0] — unreleased

First cut of the knowledge engine: the **M1 (Source) + M2 (Semantic)** vertical
slice, with provenance tracing working across both layers.

### Added

- **Models**
  - `SourceRecord` — immutable, content-addressed observations (the ground layer).
  - `Node` — one unit of derived knowledge at any layer (semantic/durable/cognitive),
    carrying `evidence`, stable `identity`, and a `version`/`parent_id` revision chain.
- **Ingestion (M1)** — `Document`, the `Ingestor` protocol, and `TextIngestor`
  (paragraph splitting with markdown-section metadata).
- **Semantic layer (M2)** — the `Extractor` protocol with two implementations:
  - `RuleBasedExtractor` — deterministic, zero-dependency (fallback + tests).
  - `LLMExtractor` — protocol-driven, works against any `LLMClient`.
  - `SemanticBuilder` — assigns identity, deduplicates, and applies **minimal
    change** (evolve to a new version only when evidence or meaning changes).
- **Provenance** — `trace` (full evidence tree), `explain` (flatten to Source
  Records), and `dangling_evidence` (integrity check).
- **Store** — the `Store` protocol and `InMemoryStore` reference backend, with
  full version history (`versions`, `head`).
- **LLM seam** — one-method `LLMClient` protocol; `AnthropicClient` (defaults to
  Claude Opus 4.8) and `FakeClient` for offline tests.
- **Engine** — the `LYR` facade (`ingest`, `ingest_source`, `rebuild_semantic`,
  `explain`, `trace`, `semantic_nodes`, `history`).

### Notes

- Core engine has **no runtime dependencies**; the Anthropic backend is an
  optional extra (`pip install 'lyr[anthropic]'`).
- The Durable and Cognitive layers are already representable via `Node` and will
  land behind the same store and provenance machinery in M3/M4.
