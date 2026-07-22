# LYR

**Living knowledge layers — transform evolving information into layered, traceable, continuously-maintained knowledge.**

Modern AI systems treat information as flat documents or vector embeddings. LYR
instead models how knowledge *forms over time*: it continuously builds and
maintains multiple layers of abstraction over immutable observations, while
preserving complete provenance back to the original evidence.

It answers the questions flat retrieval can't:

- Why do we believe this today?
- What evidence changed our understanding?
- How has this idea evolved over months or years?

---

## The layers

```
Source Records     what happened?            (immutable observations)
      ↓
Semantic Memory    what do sources describe? (entities, events, relationships)
      ↓
Durable Memory     what stays important?     (lessons, decisions, preferences)
      ↓
Cognitive Memory   how does it shape reasoning? (principles, patterns)
```

Every layer above Source is made of the same `Node` shape: a labelled claim that
cites its **evidence** one layer down. That uniformity makes provenance a single
recursive walk — a cognitive principle traces to durable lessons to semantic
facts to the source paragraphs that justify them.

## Five principles

1. **Information evolves** — update knowledge in place, don't rebuild from scratch.
2. **Knowledge is layered** — Source → Semantic → Durable → Cognitive.
3. **Every abstraction is traceable** — no node exists without evidence back to source.
4. **Knowledge has identity** — a node evolves v1 → v2 → v3, keeping its identity.
5. **Minimal change** — small evidence produces small updates.

---

## Status

The engine ships the **Source (M1)**, **Semantic (M2)**, and **Durable (M3)**
layers, with provenance tracing in **both** directions — downward (any node → its
source evidence) and upward (a record → the durable memories it supports). The
Cognitive layer (M4) is already representable in the model and slots in behind
the same store and provenance machinery.

## Install

```bash
pip install -e .            # core engine, zero dependencies
pip install -e '.[anthropic]'  # + the Anthropic-backed LLM extractor
pip install -e '.[test]'    # + pytest
```

## Quickstart

```python
from lyr import LYR

lyr = LYR()  # in-memory store, text ingestor, rule-based extractor

# Ingest an experience → immutable Source Records → semantic nodes
nodes = lyr.ingest(
    "The Payments Service failed at 02:00 during the London deploy.",
    origin="incident-42",
)

# "Why does the system believe this?" — trace any node back to evidence
entity = next(n for n in nodes if n.label == "Payments Service")
for record in lyr.explain(entity):
    print(record.origin, "→", record.content)
```

### With an LLM extractor (better entities, events, relationships)

```python
from lyr import LYR
from lyr.llm.anthropic import AnthropicClient
from lyr.semantic import LLMExtractor

lyr = LYR(extractor=LLMExtractor(AnthropicClient()))  # defaults to Claude Opus 4.8
lyr.ingest(open("design-doc.md").read(), origin="design-doc")
```

The extractor is a plug point: `RuleBasedExtractor` (deterministic, zero-dep) and
`LLMExtractor` (any `LLMClient`) both just emit `ExtractedNode`s. Swap the
`store`, `ingestor`, or `extractor` on `LYR(...)` without touching anything else.

### Durable layer — consolidate recurring knowledge (M3)

The Durable Builder consolidates semantic records that recur across independent
experiences into stable, long-term memories. It proposes a small set of
operations (`ADD` / `UPDATE` / `MERGE` / `NO_OP`), preserves identity, and applies
minimal change — `NO_OP` is the common outcome.

```python
lyr.ingest("The Payments Service failed during the London deploy.", origin="incident-1")
lyr.ingest("The Payments Service failed again overnight.",          origin="incident-2")

for proposal in lyr.build_durable():          # consolidate + apply
    print(proposal.op, proposal.statement)    # ADD  'Payments Service recurs ...'

durable = next(iter(lyr.durable_memories()))
print(lyr.explain(durable))                   # durable → semantic → source
print(lyr.supporters(entity, layer="durable"))  # record → durables it supports
```

The consolidation policy is pluggable: `RecurrenceConsolidator` (deterministic,
`min_support`-thresholded) is the default; `LLMConsolidator` drives the same
operations with a model. `lyr.durable.evaluation` provides the M3 knowledge-
maintenance benchmark (identity preservation, minimal change, provenance
completeness, precision/recall, reproducibility).

### Evolution & version history

Re-ingesting the same observation changes nothing (content-addressed ids,
minimal-change builds). New evidence evolves a node to a new version while
preserving its identity:

```python
lyr.ingest("Payments Service is healthy.", origin="check-1")   # entity v1
lyr.ingest("Payments Service was restarted.", origin="check-2") # entity v2

node = next(n for n in lyr.semantic_nodes() if n.label == "Payments Service")
for v in lyr.history(node):
    print(f"v{v.version}: {len(v.evidence)} supporting records")
```

---

## Architecture

```
Experience → Ingestion → Source Records → Semantic Builder → Semantic Memory
                              │                                     │
                              └──────────── Provenance ─────────────┘
                                     (trace any node to source)
```

| Module | Responsibility |
|---|---|
| `lyr.ingestion` | heterogeneous experiences → normalized, immutable Source Records (M1) |
| `lyr.semantic` | Source Records → entities/events/relationships, with identity + versioning (M2) |
| `lyr.durable` | consolidate recurring semantic records → long-term memories; ADD/UPDATE/MERGE/NO_OP; evaluation suite (M3) |
| `lyr.provenance` | expand any node down to source, or find what a record supports upward |
| `lyr.store` | pluggable persistence (`InMemoryStore` in v0.1) |
| `lyr.llm` | one-method `LLMClient` seam (`AnthropicClient`, `FakeClient`) |
| `lyr.engine` | the `LYR` facade tying it together |

## Roadmap

- **M1 — Source Layer** ✅ ingest, normalize, immutable records
- **M2 — Semantic Layer** ✅ entities/events/relationships, provenance, versioning
- **M3 — Durable Layer** ✅ consolidate recurring knowledge; ADD/UPDATE/MERGE/NO_OP; bidirectional provenance; evaluation suite
- **M4 — Cognitive Layer** derive higher-level reasoning patterns from durable knowledge
- **M5 — Interactive Explorer** navigate layers, visualize provenance, expand to source (`explorer/`, TypeScript)

## Development

```bash
pip install -e '.[test]'
pytest
```

## License

MIT
