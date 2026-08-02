# EXPERIMENT — M3.1-C.1 (Durability Verifier evaluation)

Two evaluations, kept separate on purpose — they answer different questions and must
not be blended into one number.

- **Primary** = frozen `durability-v1` benchmark = **verifier quality** (the formal score).
- **Secondary** = fresh `decompose → build → verify` run = **end-to-end behavior** (an
  ecological-validity check, qualitative only).

Verifier: `durability_verifier_v1`, `gpt-4o`. No prompt/verifier changes were made
between freezing the scorer and running.

---

## Primary evaluation — frozen durability-v1 benchmark

The verifier was run over the **fixed** 19 benchmark proposals (isolating it from
builder/decomposer variation) and each verdict compared to the human label.

```
verdicts:  KEEP=13  REJECT=4  UNSURE=0    execution errors: 0
strict     (confirmed labels):  false_positives = 0   false_negatives = 1
provisional (incl. cloud-growth): false_positives = 0   false_negatives = 1
```

- **False positives = 0 — the result that matters.** Every trivial case was rejected:
  coffee, donuts, **and** the provisional cloud-growth. This is the M3.1-B.2 **F4
  over-promotion problem solved** — the reason the verifier exists.
- **One false negative:** the guidance-reversal (`"revenue guidance fluctuated…
  $9.4B → $8.8B…"`), a genuine durable, was over-pruned.
- Zero UNSURE, zero execution errors.

**Failure mode (precise):** the verifier cannot distinguish a *durable trend or
decision expressed in numbers* (a guidance revision = a real change in direction)
from a *transient single metric* (cloud-growth 31%). It drew the line at "financial
fluctuation = transient" — correct on cloud-growth, wrong on guidance.

Formal score (committed evidence):
`benchmark/durability-v1/scores/20260802T063320Z__openai_gpt-4o.json`.

---

## Secondary system check — fresh decompose → build → verify (all four domains)

Qualitative only; **not** part of the score (statements differ run-to-run, so they
don't line up 1:1 with the benchmark). Five checks:

| check | result |
|---|---|
| decomposition still complete | ✅ 4 / 5 / 6 / 4 units — same coverage as M3.1-B.2, no regression |
| verifier catches trivia | ✅ coffee → NO_OP, cloud-growth → NO_OP (via verifier); donuts / rent / version-bumps → NO_OP (via the *builder* this run). No trivia reached durable memory. |
| new false negatives | ✅ none new — the **same** guidance-reversal was rejected; every other durable (acquisition, family, API-sunset, gRPC, dividend, impairment, auth-fragility, letters, CI-flakiness, DB-reversal, Redis-lesson) was KEPT |
| execution errors | ✅ none |
| audit trail complete | ✅ every unit wrote model_intent + verification + final_engine_action |

**Cross-read:** the secondary run **reproduces** the primary's single failure
(guidance-reversal REJECT) and its single success mode (all trivia stopped). That the
one FN is stable across a fixed-proposal benchmark *and* a fresh end-to-end run is
strong evidence it is a real verifier behavior, not benchmark noise. (Note: which
component stops a given piece of trivia varies — the builder NO_OP'd donuts/rent/
version-bumps this run; the verifier caught coffee/cloud-growth. The *system* let no
trivia through either way.)

---

## Conclusion

The durability verifier **meets its primary objective**: false positives → 0, the F4
over-promotion problem is solved, with zero execution errors. It **misses the strict
`FN = 0` constraint by exactly one** — a single, reproducible over-prune on a
number-heavy durable (guidance reversal).

Net: a clear improvement. Before M3.1-C, isolated topics let trivia through (coffee,
donuts, cloud-growth all became durable). After, none do — at the cost of one
over-prune on a case that sits close to the benchmark's own borderline.

## Deferred to durability-v2 (only after this is recorded — do not act now)

- **Label review:** the guidance-reversal FN, like cloud-growth, is financial-number-
  heavy and arguably debatable. Candidate for re-labeling / `confirmed=false` in a
  future benchmark version — **not** retrofitted here.
- **Prompt refinement:** teach the verifier that *a lasting change in direction or
  policy is durable even when expressed as numbers* (the "numbers ≠ transient"
  distinction) — the precise fix for the one FN.

## The M3.1 chain, closed

```
M3.1-B     one judgment            → F7 dominates (coverage)
M3.1-B.2   decomposition           → F7 gone → F4 dominates (durability judgment)
M3.1-C     durability verifier     → F4 solved (FP=0); one reproducible over-prune remains
```

Each stage removed one dominant failure and exposed (or resolved) the next. The
verifier stage did what it was scoped to do; the remaining gap is a narrow,
well-characterized judgment case, not an architectural one.
