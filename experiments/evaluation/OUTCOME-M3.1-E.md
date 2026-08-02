# M3.1-E Outcome — Cross-Domain Judgment Validation

**Decision: Outcome B — the Builder interface is insufficient for multi-topic batches.**
Investigate **M3.1-B.2 (Judgment Decomposition)** before introducing a Verifier.

## Run

- Provider/model: **OpenAI `gpt-4o`**, prompt `durable_builder_v1` — uniform across
  all four domains (verified by `evaluate.py summarize`; the frozen-builder rule §4 held).
- Four live runs, one `JudgmentRecord` each, preserved in `records/`, reviewed in
  `reviews/` (`reviewer: assistant-draft` — proposed classifications adopted when the
  Outcome-B decision was taken; open to human revision).

## Result

| Domain | Failures | The single judgment it did make |
|---|---|---|
| memoir | **F7** | family-over-career pattern — strong, duplicate correctly excluded |
| meeting | **F7** | recurring CI-flakiness blocker — good |
| financial | **F7** | Northwind acquisition fact — duplicate correctly grouped |
| git history | **F7, F2** | REST→gRPC migration — grouped correctly but statement over-generalized |

Failure totals: **F7 ×4** (candidate coverage), **F2 ×1** (over-generalization).

## Reading

F7 was dominant in **every** domain, and it was **not** a model-reasoning failure:
`gpt-4o` produced grounded, well-scoped judgments and correctly identified duplicate
evidence (0&3, 0&1, 0&9 all flagged `same_observation`). The failure is structural —
each multi-topic batch contains several independent durable candidates, but
`update() → one JudgmentRecord` can represent only one, silently dropping the rest
(letters + emigration; billing-API decision + DB reversal; guidance reversal +
dividend + impairment; auth-fragility pattern).

Per M3.1-E §9 this is the definition of **Outcome B**.

## Caveat

The fixtures are deliberately multi-topic, which stacks the deck toward F7. The
honest claim is *"one judgment per multi-topic batch is insufficient"* — a real
interface finding. Whether the fix is decomposition **or** narrower candidate
retrieval (§5) is exactly the M3.1-B.2 design question.

## Next

→ [M3.1-B.2 — Judgment Decomposition](../../docs/design/M3.1-B.2-judgment-decomposition.md)
