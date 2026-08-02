# M3.1-E Evaluation Kit

Tooling for the **Cross-Domain Judgment Validation** experiment
([design](../../docs/design/M3.1-E-cross-domain-judgment-validation.md)). It does
**not** touch the Builder or the prompt — that is the whole point of the milestone
(the frozen-builder rule, §4). It only *collects, preserves, and classifies* the
evidence the frozen Builder produces.

## Why records here are committed (unlike `runs/`)

`experiments/*/runs/` holds scratch transcripts and is gitignored. M3.1-E instead
requires **every JudgmentRecord to be preserved as experimental evidence**, so the
`review` step copies the chosen record into `records/` (committed) alongside a
`reviews/` skeleton you fill in by hand.

```
experiments/evaluation/
  evaluate.py     review <exp> | summarize
  records/        preserved JudgmentRecords (committed evidence)
  reviews/        human classifications (committed)
```

## Workflow (per domain, Builder frozen)

```bash
# 1. Collect — live model (needs a key + `pip install -e '.[anthropic]'`):
python experiments/harness.py experiment-001-memoir --builder --model claude-opus-4-8

# 2. Preserve the record + generate a review skeleton:
python experiments/evaluation/evaluate.py review experiment-001-memoir

# 3. Open reviews/experiment-001-memoir__<jid>.json and fill in:
#      dimensions[*].rating  → ok | weak | fail   (design §7)
#      failures              → any of F1..F8       (design §8)
#      reviewer, verdict
#    The _context block is regenerated from the record — don't edit it.

# 4. After all four domains are reviewed:
python experiments/evaluation/evaluate.py summarize
```

`summarize` tallies failures per domain and overall, and **enforces §4**: it warns
if the preserved records were not all produced by the same prompt version / provider
/ model (a mid-experiment change would break comparability). It prints the Outcome
A/B/C decision *inputs* — the decision itself is a human call over the complete set
(§9), never auto-selected.

## Rule

**Do not change the Builder or prompt while collecting evidence.** If a change is
needed, that is itself a finding (Outcome B/C) — record it, finish the round, and
decide the architectural step afterward.
