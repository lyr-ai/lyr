# Durability Benchmark v1

The first durability benchmark for LYR — the concrete artifact that lets a
**Durability Verifier (M3.1-C)** be measured instead of asserted.

## What it is

`records/` holds the **19 proposed durable memories** produced by the M3.1-B.2
decomposed runs (one `JudgmentRecord` per topic unit, `gpt-4o`, decomposer
`judgment_decomposer_v1`, builder `durable_builder_v1`). `labels.json` pairs each
one with a durability label:

```
deserves_persistence: yes | no | borderline
```

The labels are **assistant-draft**, open to human revision.

## Why it exists

M3.1-B.2 (judgment decomposition) surfaced *every* durable candidate in a batch,
which for the first time made the model's **durability judgment** observable. The
runs showed the model over-promoting trivia (`coffee → ADD`, `donuts → ADD`,
`cloud-growth-31% → ADD`) while correctly rejecting other trivia (`rent → NO_OP`,
`version-bumps → NO_OP`). Those cases are the benchmark's core.

## Composition

- 19 cases: **13 yes**, **5 no**, **1 borderline**.
- Includes 2 correct `NO_OP`s (true negatives: rent, version bumps).
- The model's **3 over-promotions** (`ADD` on a `no` case) are the F4 signal a
  Verifier must fix: coffee, donuts, single-quarter cloud growth.

## How a Verifier is scored against it

For each record in `records/`, a Durability Verifier decides keep vs. reject and is
scored against `deserves_persistence`:

- **false positive** = keeps a `no` case (the failure to fix — the 3 over-promotions)
- **false negative** = rejects a `yes` case (must not over-prune)
- `borderline` cases are excluded from strict scoring (or scored either way).

## Caveats

- Small (n=19), single model (`gpt-4o`), single prompt pair, fixtures deliberately
  multi-topic. It is a *starting* benchmark, not a validated one — enough to make a
  Verifier measurable and to catch regressions, not to certify general durability.
- Labels are one drafter's judgment; the `borderline` case (SRE hire) and the
  cloud-growth `no` are the most debatable.
