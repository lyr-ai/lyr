# EXPERIMENT — M3.1-B.2 (Judgment Decomposition)

*An observation, not a final conclusion: changing the Builder abstraction changed
the failure distribution.*

## Setup

Same four domains, same model (`gpt-4o`), same builder prompt as M3.1-E. The only
change: a **judgment-decomposition** stage before the builder (M3.1-B.2). We
re-measured the failure distribution.

## Findings

### Finding 1 — F7 solved

```
F7 (Candidate Coverage):   4/4 domains  →  0/4 domains
```

Coverage rose from **1** durable per batch to **3–5**. The candidates M3.1-E flagged
as dropped — letters, auth-fragility pattern, the guidance and DB reversals,
dividend policy, impairment — all surfaced. The Builder coverage problem is solved.

### Finding 2 — F4 became dominant

```
F4 (Durability Judgment):  latent  →  dominant
```

With every candidate now surfacing, the model over-promotes trivia:
`coffee → ADD`, `donuts → ADD`, `cloud-growth-31% → ADD` — while correctly rejecting
other trivia: `rent → NO_OP`, `version-bumps → NO_OP`. Durability judgment is now the
limiting factor.

### Finding 3 — decomposition did not improve judgment quality

It **isolated** judgment quality from interface quality. The Builder's durability
reasoning is unchanged; it was simply never observable before, because most
candidates never reached it.

## The deeper result

The headline is **not** *"decomposition works."* It is:

> **Judgment quality was previously masked by interface limitations.**

Before decomposition, one batch produced one output, so you could not tell whether
the model could judge durability — most candidates never appeared. After
decomposition, every candidate appears, and the real question finally surfaces:

```
"Which one should I pick?"   (interface-limited)
        →
"Should this be durable?"    (the actual research question)
```

`coffee → ADD ❌`, `donuts → ADD ❌`, `rent → NO_OP ✅` shows the model has *started*
answering the second question — which is exactly what M3.1-C exists to study.

## The experiment chain

```
M3.1-B     One Judgment          → F7 dominates (candidate coverage)
   ↓
M3.1-B.2   Judgment Decomposition → F7 disappears → F4 dominates (durability judgment)
   ↓
M3.1-C     Durability Verifier    → (next)
```

This is not feature-stacking. Each architectural change **eliminated one dominant
failure mode, exposing the next.**

## Conclusion

**Proceed to M3.1-C.** The remaining failures are judgment quality (F4), not
interface design (F7) — which satisfies the M3.1-B.2 exit criteria. The 19 proposed
durables from this run are preserved as
[`benchmark/durability-v1/`](./benchmark/durability-v1/) — the first durability
benchmark a Verifier can be scored against.

## One-line narrative

> Rather than continually increasing model sophistication, LYR progressively removed
> architectural bottlenecks. Each experiment eliminated one dominant failure mode,
> exposing the next. Candidate coverage (F7) was resolved by Judgment Decomposition,
> revealing Durability Judgment (F4) as the next limiting factor. This progression
> justifies the introduction of a Durability Verifier as the next architectural stage.
