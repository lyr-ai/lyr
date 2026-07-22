# Changelog

All notable changes to LYR are documented here. This project adheres to
[Semantic Versioning](https://semver.org/).

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
