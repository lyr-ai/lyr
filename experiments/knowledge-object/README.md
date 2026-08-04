# Knowledge-Object minimal build + measurement

The [Semantic → Knowledge review](../../docs/design/review-semantic-to-knowledge-transition.md)
and four hand-probes (`docs/design/prototype-1..4`) converged on one primitive:

> **Knowledge Object = a maintained set of scoped, evidenced, status-bearing claims and relations
> over semantic objects.**

The fabrication risk lives entirely in the **status**: a system that asserts an unsupported relation
(DeepSeek's `MLA → DSA → CSA → HCA` "lineage") manufactures narrative, not knowledge. This experiment
builds and measures the smallest thing that decides status **from the evidence**.

## What was built

- **`grounding.py`** — a deterministic **baseline verifier**. It grades a proposed claim/relation:
  a derivation is `SUPPORTED` only if one passage names **both** endpoints with a **derivation
  phrase** (`improves upon`, `builds upon`, …); otherwise `UNKNOWN` (abstained — checked and refused).
  Same role `RecurrenceConsolidator` plays for durable and the rule extractor plays for semantic: a
  transparent, offline control the eventual LLM verifier is measured against.
- **`measure.py`** — grades the verifier against the hand-probes' ground truth.
- **`test_grounding.py`** — 9 unit tests (incl. the `Muon` ⊄ `MuonClip` word-boundary guard and the
  bare-"improve" false-positive guard).

## The measurement (the discriminating test)

The same verifier must **abstain** DeepSeek's *unstated* lineage yet **support** Kimi's *stated*
`MuonClip improves upon Muon`. Result (`python experiments/knowledge-object/measure.py`):

    6/6 match the hand-probe ground truth
    fabrications (abstain expected, SUPPORTED got):     0
    DeepSeek MLA→DSA / DSA→CSA / CSA→HCA:               UNKNOWN  (abstained, correct)
    DeepSeek grouping by efficiency / quantified 27%:   SUPPORTED
    Kimi MuonClip→Muon:                                 SUPPORTED

One evidence rule produces the opposite status on the two corpora, driven only by what each states.
The abstention in Prototype 1 was a **judgment the system can reproduce**, not a hand-wave.

## What this PROVES — and what it does NOT

**Proves:** the abstention discipline is **mechanizable**; the hand-probe ground truth is
reproducible by a system; the `SUPPORTED / UNKNOWN` split tracks evidence across two independent
corpora with zero fabrication.

**Does NOT prove (the honest gap):**

- The verifier **grades** claims; it does **not propose** them. Candidate members/relations were
  hand-given. The fabrication risk in a full system is a **proposer** (an LLM) inventing a lineage —
  so the real next measurement is *proposer-behind-verifier*: let an LLM propose knowledge objects,
  and measure whether this verifier catches its unsupported relations. That needs a paid LLM run.
- The cue list is **crude and transparent** — false-negative-prone on paraphrased derivations
  (an LLM verifier would close that gap), guarded only against the main false positive.
- A baseline verifier passing is **necessary, not sufficient**, to call the substrate a "layer."
  That name is earned by the proposer-behind-verifier measurement, and remains the PI's call.

## Status

Minimal build + measurement: **done, PASS at the baseline level.** Not wired into `lyr/` core — this
is an experiment, not a declared layer.
