# Witness: Part B — the verifier is predicate-closed, not relation-general

**Status:** recorded result. The proposer-behind-verifier measurement ran (gpt-4o-mini, two seeds,
`experiments/knowledge-object/runs/openai-1.json`, `openai-2.json`, commit `39f0905`). It did its job:
it located a frontier. It did **not** validate a layer.

## 1. Gate verdict — FAILED (not "mixed", not "promising")

> **Part B failed the Knowledge Claim Layer gate.**

Do not read `fabrication acceptance = 0` as a pass. On the free-proposal path the verifier committed
**~1 of every 36** proposed claims, and the ~35 it withheld were, in the majority, **true and
corpus-supported.** The zero-fabrication number is a product of **mass abstention**, not defense.

Failed gate conditions (`EXPERIMENT.md`):

- **4 — zero fabrication only via mass abstention.** ~1/36 committed.
- **5 — true-claim retention.** Near-zero on the open path: faithful restatements like
  `DeepSeek-V3 utilizes MLA`, `DeepSeek-V3 employs MoE`, `DeepSeek-V4-Pro has 1.6T parameters`,
  `DeepSeek-V4 supports one-million-token context` were all withheld as `UNKNOWN`.
- **6 — precise evidence on commits.** The one Kimi commit (`MuonClip improves upon Muon`) had
  `evidence_precise = False` — proposer cited p7/p9, the claim was groundable in p2.
- **8 — `UNKNOWN` is a verdict, not a parse failure.** Kimi seed-1 returned 0 proposals: a truncated /
  malformed JSON completion, not a decision.
- **2 — stable on held-out Kimi.** Kimi went 0 → 9 proposals across the two seeds.

## 2. Root cause — a *generic relation grounding gap*

Not the model, not the prompt. The verifier's grounding is **predicate-closed, not relation-general.**
It recognizes a small hardcoded set:

    derives_from · accepts · refuses · married · engaged · introduces · grouping · quantified

Free proposers produce an open predicate space:

    utilizes · employs · has · supports · features · achieves · is_a · was_pretrained_on · rivals · ...

Any predicate outside the set falls through to a default `UNKNOWN` **regardless of whether the
evidence supports it** — safe, but blind. The fix is **not** adding a dozen more predicate cues; it is
**generic relation grounding over an open predicate space**, a distinct and substantial research
program. Named here so it is not mistaken for a tuning task.

## 3. Why Part A gave false security

Part A (adversarial gold set) passed 0/10 — worth keeping as a self-correction:

> The gold set was adversarial on **evidence difficulty**, but not on **predicate coverage.**

So Part A actually measured *"can the verifier judge within its known predicates?"* (yes). It did
**not** measure *"can the verifier handle the open relation space a real proposer generates?"* (no).
Part A was not worthless — its scope was narrower than it appeared when written.

## 4. The proposer's unexpected result

Recorded as-is, because it matters for the product decision:

> On these clean, official, structured corpora, gpt-4o-mini's free proposals were **mostly faithful**;
> fabrication was **not severe.**

The dominant failure was the verifier failing to *recognize truth*, not the proposer *inventing
narrative*. So the more urgent product question is **not** "how do we stop mass hallucination" but:
how to organize real knowledge, let users explore it, form a valuable experience, and **discover on
which real data fabrication actually becomes blocking.** That is a reason to pause verifier research,
not extend it.

## Disposition

- The verifier is **not** being fixed (no predicate-cue patching).
- **Generic relation grounding over an open predicate space** is filed as a deferred research frontier
  (see `research-v1-frozen.md`), with this witness attached.
- Research is frozen; the Explorer becomes the next witness generator.

Evidence: `experiments/knowledge-object/runs/openai-1.json`, `openai-2.json` (raw completions,
per-proposal verdicts, proposer-vs-verifier evidence, corpus hashes, model id).
