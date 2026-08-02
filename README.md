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

**▶ Live demo — the [Judgment Explorer](https://lyr-ai.github.io/lyr/)** walks one durable
judgment end to end (`Source → Semantic → Builder → Verifier → Durable`) over real
records: see *why* [coffee was rejected](https://lyr-ai.github.io/lyr/explorer.html#coffee-ritual)
and [family-over-career was kept](https://lyr-ai.github.io/lyr/explorer.html#family-over-career).
No install.

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
source evidence) and upward (a record → the durable memories it supports).

The **Durable layer is now model-driven (M3.1)**: an LLM proposes durable knowledge,
a **decomposition** stage splits a batch into one topic per judgment, and a
**durability verifier** vetoes what should not persist — while the engine keeps
committing identity, history, and provenance. This was built as a *research
program*: each stage removed one measured failure mode and exposed the next
(coverage → judgment), evaluated against a frozen benchmark. See the write-up in
[`docs/M3.1-research-arc.md`](docs/M3.1-research-arc.md).

The Cognitive layer (M4) is already representable in the model and slots in behind
the same store and provenance machinery.

## Install

```bash
pip install -e .            # core engine, zero dependencies
pip install -e '.[anthropic]'  # + the Anthropic (Claude) LLM client
pip install -e '.[openai]'  # + the OpenAI (ChatGPT) LLM client
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
from lyr.llm import AnthropicClient, OpenAIClient  # pick a provider
from lyr.semantic import LLMExtractor

lyr = LYR(extractor=LLMExtractor(AnthropicClient()))       # Claude (defaults to Opus 4.8)
# lyr = LYR(extractor=LLMExtractor(OpenAIClient()))        # ...or ChatGPT (defaults to gpt-4o)
lyr.ingest(open("design-doc.md").read(), origin="design-doc")
```

Both clients implement the same one-method `LLMClient` seam
(`complete(prompt) -> str`), so anything that takes a client — `LLMExtractor`, the
durable `JudgmentBuilder`, the experiment harness — works with either provider
unchanged. `AnthropicClient` reads `ANTHROPIC_API_KEY`; `OpenAIClient` reads
`OPENAI_API_KEY`.

The extractor is a plug point: `RuleBasedExtractor` (deterministic, zero-dep) and
`LLMExtractor` (any `LLMClient`) both just emit `ExtractedNode`s. Swap the
`store`, `ingestor`, or `extractor` on `LYR(...)` without touching anything else.

### Durable layer — long-term knowledge maintenance (M3)

The Durable Builder maintains long-term memories over the semantic layer via a
small set of operations (`ADD` / `UPDATE` / `MERGE` / `NO_OP`). The engine owns the
trustworthy substrate; *what counts as durable* is a pluggable policy:

> **Model proposes meaning. Engine commits identity, history, and provenance.**

```python
lyr.ingest("The Payments Service failed during the London deploy.", origin="incident-1")
lyr.ingest("The Payments Service failed again overnight.",          origin="incident-2")

for proposal in lyr.build_durable():          # consolidate + apply
    print(proposal.op, proposal.statement)

durable = next(iter(lyr.durable_memories()))  # active memories (retired hidden)
print(lyr.explain(durable))                   # durable → semantic → source
print(lyr.supporters(entity, layer="durable"))  # record → durables it supports
```

**Consolidation policy is pluggable.** `RecurrenceConsolidator` remains a
*deterministic structural baseline* (recurrence as a cheap proxy) — **not** LYR's
definition of durability: recurrence is not importance, and a significant one-off
can be durable while repeated noise is not. **Model-driven durability judgment is
implemented (M3.1)** through the `JudgmentBuilder`, judgment **decomposition**, and
the **Durability Verifier** (see below).

`lyr.durable.evaluation` scores substrate properties without labels (identity
preservation, minimal change, provenance completeness, reproducibility). For the
*judgment* itself, the frozen
[`durability-v1`](experiments/evaluation/benchmark/durability-v1/) benchmark holds
the first reviewed cross-domain judgment set — an **experimental** benchmark (19
cases), not yet a broad, population-level measure of durability quality.

### Model-driven durable judgment (M3.1)

An LLM proposes durable knowledge; a **decomposer** splits a batch so each judgment
covers one topic; a **durability verifier** vetoes what should not persist — and the
engine still commits identity, history, and provenance. Every attempt is one
immutable `JudgmentRecord` (proposal → verdict → committed action).

```python
from lyr import LYR
from lyr.durable import JudgmentPipeline, LLMDecomposer, LLMDurabilityVerifier
from lyr.llm import OpenAIClient          # or AnthropicClient

lyr = LYR()
lyr.ingest("...accumulated experiences...", origin="doc-1")   # Source + Semantic
semantic = list(lyr.semantic_nodes())

client = OpenAIClient()
pipeline = JudgmentPipeline(
    lyr.store, client,
    decomposer=LLMDecomposer(client),           # batch → one topic per judgment (M3.1-B.2)
    verifier=LLMDurabilityVerifier(client),     # gate: should this persist? (M3.1-C)
)

for result in pipeline.run(semantic, candidate_durable_nodes=[]):
    rec = result.judgment_record
    verdict = rec.verification.decision if rec.verification else "—"   # KEEP / REJECT / UNSURE
    print(rec.model_intent.operation, "→", rec.final_engine_action.operation,
          "| verdict:", verdict, "|", rec.model_intent.statement)
```

On the frozen `durability-v1` benchmark this verifier drove trivia-over-promotion
(false positives) to **0**, with one narrow false-negative remaining. The full story
is in [`docs/M3.1-research-arc.md`](docs/M3.1-research-arc.md).

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
                                                                    │
                              ┌─────────────────────────────────────┘
                              ▼
                       Judgment Decomposer      (batch → one topic per judgment)
                              ▼
                        JudgmentBuilder          (propose one durable operation)
                              ▼
                      Durability Verifier        (KEEP / REJECT / UNSURE)
                              ▼
                        Durable Memory           committed by the engine
                              │
        JudgmentRecord: proposal → verdict → engine action   (immutable audit)
                              │
                    ◀──────── Provenance ────────▶
             (any node → its source; a record → what it supports)
```

| Module | Responsibility |
|---|---|
| `lyr.ingestion` | heterogeneous experiences → normalized, immutable Source Records (M1) |
| `lyr.semantic` | Source Records → entities/events/relationships, with identity + versioning (M2) |
| `lyr.durable` | long-term knowledge maintenance (M3/M3.1): ADD/UPDATE/MERGE/NO_OP lifecycle; recurrence baseline; **`JudgmentBuilder`** (one proposal → immutable `JudgmentRecord`); **decomposition** (batch → one topic per judgment); **durability verifier** (KEEP/REJECT/UNSURE gate) |
| `lyr.provenance` | expand any node down to source, or find what a record supports upward |
| `lyr.store` | pluggable persistence (`InMemoryStore` in v0.1) |
| `lyr.llm` | one-method `LLMClient` seam (`AnthropicClient`, `OpenAIClient`, `FakeClient`) |
| `lyr.engine` | the `LYR` facade tying it together |

## Roadmap

- **M1 — Source Layer** ✅ ingest, normalize, immutable records
- **M2 — Semantic Layer** ✅ entities/events/relationships, provenance, versioning
- **M3 — Durable Layer** ✅ substrate: identity/history/provenance + ADD/UPDATE/MERGE/NO_OP lifecycle; bidirectional provenance; deterministic recurrence *baseline*; evaluation harness
- **M3.1 — Model-driven durable consolidation** ✅ a completed research cycle:
  - **B** minimal `JudgmentBuilder` (one proposal → one immutable `JudgmentRecord`); **B.1** contract hardening
  - **E** cross-domain evaluation — falsified "one judgment per batch" (failure **F7**, candidate coverage)
  - **B.2** **judgment decomposition** — solved F7; exposed **F4** (durability judgment)
  - **C0/C** **durability verifier** (task frozen first) — drove benchmark false-positives to **0**; one narrow, characterized false-negative remains
  - a frozen [`durability-v1`](experiments/evaluation/benchmark/durability-v1/) benchmark future verifiers re-run against
- **M4 — Cognitive Layer** derive higher-level reasoning patterns from the now-stable durable layer
- **M5.0 — Judgment Explorer** ✅ a public site (`site/`, GitHub Pages) that walks one durable judgment's full lifecycle — `Source → Semantic → Builder → Verifier → Durable` — over real records; a landing page frames the project for first-time visitors

## Development

```bash
pip install -e '.[test]'
pytest
```

## License

MIT
