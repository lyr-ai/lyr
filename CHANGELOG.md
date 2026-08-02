# Changelog

All notable changes to LYR are documented here. This project adheres to
[Semantic Versioning](https://semver.org/).

## [0.3.0] — unreleased (M3.1: model-driven durable consolidation)

A complete research cycle over the durable layer — model-driven judgment with a
frozen benchmark and frozen evaluation. See
[`docs/M3.1-research-arc.md`](docs/M3.1-research-arc.md) for the full story.

### Added

- **`JudgmentBuilder`** — one LLM proposal → one immutable `JudgmentRecord`
  (proposal + engine action; **B.1** hardening: unique execution ids vs. content
  fingerprints, frozen/tuple records, preserved raw output).
- **Judgment decomposition** (`JudgmentPipeline`, `LLMDecomposer` /
  `WholeBatchDecomposer` / `SingletonDecomposer`) — split a batch so each judgment
  covers one topic (fixes the F7 candidate-coverage failure found in M3.1-E).
- **Durability verifier** (`DurabilityVerifier`, `LLMDurabilityVerifier`,
  `ThresholdDurabilityVerifier`) — a stateless `KEEP / REJECT / UNSURE` gate on
  whether a proposed durable should persist; verdict recorded on
  `JudgmentRecord.verification` (execution `ERROR` kept distinct from a semantic
  `UNSURE`). Task frozen up front in M3.1-C0.
- **`OpenAIClient`** — OpenAI/ChatGPT behind the one-method `LLMClient` seam.
- **`durability-v1` benchmark** + a scorer frozen before results; primary result:
  benchmark false-positives → 0, one narrow false-negative.

### Notes

- Public `JudgmentBuilder.update()` signature unchanged across B.1/B.2/C.
- On `durability-v1` the observed F4 over-promotions were eliminated — a
  demonstration on 19 cases, not a general claim.

## [0.2.0] — unreleased (M3: Durable Layer — substrate)

Adds the **Durable Layer** — the trustworthy substrate for long-term knowledge
maintenance. LYR moves beyond extraction to *maintaining* knowledge, with the
same identity, versioning, and provenance guarantees as the layers below. The
guiding split:

> **Model proposes meaning. Engine commits identity, history, and provenance.**

This release delivers the engine's half (deterministic, auditable) plus a
deterministic *baseline* policy. Defining durability as a semantic judgment
(evidence independence, significance) is deferred to M3.1 — recurrence is **not**
LYR's definition of durable.

### Added

- **Durable lifecycle** — the `Consolidator` protocol and the four update
  operations (`ADD` / `UPDATE` / `MERGE` / `NO_OP`) as `DurableProposal`s.
  - `RecurrenceConsolidator` — deterministic **structural baseline** (promotes a
    topic once ≥ `min_support` distinct source records back it). Explicitly a
    proxy/control, not the definition of durability. Reproducible.
  - `LLMConsolidator` — model-driven policy over any `LLMClient`; the model
    proposes which existing memory to match, and the engine owns identity.
- **`DurableBuilder`** — separates `propose` from `apply`; the engine enforces
  the invariants regardless of the operation a consolidator names:
  - **identity guard** — an `ADD` onto an existing identity evolves it rather
    than minting a second `v1` (chains stay `1..n`), including within one batch.
  - **MERGE lifecycle** — superseded memories are *tombstoned* (`status=retired`,
    `merged_into` recorded), their evidence folded into the target; history and
    provenance are retained, and they drop out of active queries.
  - **minimal change** — an inert UPDATE downgrades to NO_OP (syntactic; semantic
    equivalence is a model judgment, out of scope for the substrate).
- **Bidirectional provenance** — `supporters()` walks provenance *upward*, so a
  semantic record can discover the durable memories it supports.
- **Evaluation harness** (`lyr.durable.evaluation`) — scores identity
  preservation, minimal change, provenance completeness, and reproducibility
  without labels; update precision/recall require caller-supplied ground truth
  and are reported as `None` otherwise. Not yet a validated durability benchmark.
- **Engine** — `build_durable`, `propose_durable`, `durable_memories`
  (`include_retired=` opt-in), `supporters`, plus a `consolidator=` injection
  point on `LYR(...)`.

### Notes

- Durable confidence/support live in `Node.attributes` (no `Node` model change).
- Layer isolation is enforced by construction: consolidators consume `Node`s and
  their provenance ids, never `store.get_source`.
- No document/episode/run "support unit" is baked into the schema — evidence
  independence is a semantic judgment left to the model-driven policy (M3.1).

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
