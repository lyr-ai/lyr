# Proposer-behind-verifier measurement

The question a paid run must answer — the one the baseline verifier and the four hand-probes could
**not**:

> When a generative model actively manufactures candidate claims and relations, can the verifier stop
> the plausible-but-unsupported ones from entering Knowledge?

Deliberately **narrow**: this first round tests only **relation proposal under evidence** — not full
knowledge-object formation (that would test candidate search + clustering + schema-filling + retrieval
+ generation + verifier all at once, and a failure could not be attributed).

    semantic objects + evidence packet
        → LLM proposes candidate (subject, predicate, object)   [proposer.py]
        → deterministic evidence-grounded verifier              [claim_verifier.py]
        → SUPPORTED / CONTRADICTED / UNKNOWN / NOT_EVALUATED

## Corpus roles (frozen)

| corpus | role | why |
|--------|------|-----|
| DeepSeek | development / debug | crisp technical relations; unstated lineage is the fabrication bait |
| P&P / Elizabeth | dev sanity, second structure | softer evidence → watch **over-abstention**; clean antonym contradiction (accepts/refuses) |
| **Kimi** | **HELD-OUT evaluation** | not used to build the verifier; the stated `MuonClip→Muon` is the positive control |

**Do not** tune the verifier on Kimi and still call it held-out. The first held-out result is
frozen; if the verifier must change afterward, Kimi becomes development and a new corpus becomes the
holdout.

## Gold set (`gold.py`) — three categories, not just the easy claims

`SUPPORTED_TRUTH` (expect SUPPORTED) · `PLAUSIBLE_UNSUPPORTED` (expect UNKNOWN — the real test) ·
`CONTRADICTED` (expect CONTRADICTED). Free LLM proposal (tests recall) **and** these pre-constructed
adversarial candidates (tests verifier defense) are both run.

## Metrics (`experiment.py`)

- **Fabrication acceptance** — unsupported/contradicted accepted as SUPPORTED. **Gate: 0.**
- **Supported retention** — of truly-supported claims, how many kept (else the verifier "wins" by
  abstaining everything).
- **Over-abstention** — supported → UNKNOWN.
- **Contradiction detection** — clearly-false marked CONTRADICTED (not merely UNKNOWN).
- **Evidence precision** — an accepted claim's cited passage genuinely supports it (baseline: SUPPORTED
  requires both endpoints + a matching cue in one passage, so citations are relevant by construction;
  the LLM verifier would tighten this).
- **Proposal novelty** — SUPPORTED proposals *not* in the gold/hand-probes (proof the proposer isn't
  just echoing given answers).

Two baselines: **proposer-only** (raw fabrication) vs **proposer+verifier** (what the verifier
removed vs wrongly deleted). The product story is that difference.

## Part A result — deterministic, real (no LLM)

`python experiment.py` runs the verifier against the adversarial gold set:

    fabrication acceptance:  0/10     ← GATE metric, PASS
    supported retention:     5/5      (100%; not abstaining-to-win)
    over-abstention:         0/5
    contradiction detected:  1/3      (contradicted-as-SUPPORTED: 0)

The verifier accepts **zero** unsupported or contradicted claims as SUPPORTED, on three corpora,
while retaining all real ones. **Honest bound:** contradiction detection is 1/3 — the baseline catches
the clean antonym case (Elizabeth accepts↔refuses) but **misses inferential/precedence** contradictions
(`MLA is sparse` — implied only by "DSA is sparse for the first time"; `K2 introduces INT4` — implied
by "absent from previous versions"). Those degrade to `UNKNOWN` — **safe** (never accepted), but
imprecise. Closing that gap is a job for the LLM verifier, not the deterministic baseline.

## Part B — the paid proposer run (needs a key)

Built and self-tested with a canned `FakeClient` (`python experiment.py --fake` — harness self-test,
NOT a measurement). The real run:

    OPENAI_API_KEY=...   python experiment.py --client openai   --model <model>   --label openai-1
    ANTHROPIC_API_KEY=... python experiment.py --client anthropic --model <model> --label claude-1

Every proposal, verdict, evidence set, and model id is logged to `runs/<label>.json` for
attribution and reproducibility.

## The gate — when this earns the name "Knowledge Claim Layer"

Promote the working hypothesis to a layer only if the proposer-behind-verifier run satisfies **all**:

1. runs on ≥2 heterogeneous corpora;
2. holds on the held-out corpus (Kimi);
3. fabrication acceptance = 0 (or every residual cleanly classified);
4. not achieved by abstaining everything (real supported retention);
5. each committed claim carries precise evidence;
6. no corpus-specific rule introduced;
7. proposer/verifier responsibilities cleanly separated;
8. `UNKNOWN` is a decision, not a parse failure;
9. contradictions distinguished from unknowns where feasible (else disclosed, as above);
10. runs are reproducible with proposal + verdict + evidence + model version saved.

If it passes, the commit unit is the **claim**, so the accurate name is **Knowledge Claim Layer**
(a "Knowledge Object" is a projection view over these claims). Until then: no layer declared, no
pipeline, no UI, no schema expansion.

## Explicitly out of scope (this round)

**Cross-corpus concept identity.** `DeepSeek::MLA` and `Kimi::MLA` stay separate; cross-corpus sameness
is `NOT_EVALUATED`. Same name ≠ merge. That is the next layer up (entity resolution for knowledge
objects) and must not contaminate this experiment.
