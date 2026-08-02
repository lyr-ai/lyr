# Experiment 002 — Meeting notes: hypothesis & what to watch

**Question:** does the *same* durable builder, unchanged from the memoir run,
behave sensibly on a completely different domain (engineering meetings)?

| Records | Case | Hoped-for behavior |
|---|---|---|
| 0, 1 | duplicate description of one decision | grouped as **one** evidence; a single durable decision, not two |
| 0/1 | significant one-off **decision** | may be durable **without recurrence** (sunset the billing API) |
| 2, 3 | reversal / contradiction over time | **not** a flat "use Postgres"; the later DynamoDB reversal should win, or be scoped by date — the contradiction must not be silently dropped |
| 4, 5, 6 | genuinely recurring blocker across 3 meetings | durable **lesson**: payments CI flakiness is a persistent release risk |
| 7, 8 | trivial recurring noise (donuts) | **NO_OP** — recurs but not durable |
| 9 | one-off staffing action | probably not durable on its own; watch how it's treated |

**Watch for:** does it conflate records 0 & 1 (same decision) as two supports? Does
it handle the Postgres→DynamoDB reversal as a contradiction rather than averaging
them? Does donuts survive into a durable claim (it shouldn't)?

## Runs & observations

_(none yet)_
