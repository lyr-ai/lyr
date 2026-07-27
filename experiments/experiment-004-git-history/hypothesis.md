# Experiment 004 — Git history: hypothesis & what to watch

**Question:** same unchanged builder, on commit history — can it find a durable
"fragile area" pattern, respect a revert, and ignore version-bump noise?

| Records | Case | Hoped-for behavior |
|---|---|---|
| 0, 9 | duplicate (feature commit + its merge commit) | grouped as **one** evidence — a single durable **decision**: migrated to gRPC |
| 1, 2, 3 | three independent auth fixes | durable **lesson/pattern**: the auth/session module is fragile and repeatedly patched |
| 4, 5, 6 | routine version bumps | **NO_OP** — recurs but trivial |
| 7, 8 | change then its **revert** | net **NO_OP** or an explicit "tried and reverted" note; must **not** land as a durable "we use a Redis catalog cache" |
| 0/9 | significant one-off architectural decision | durable **without recurrence** |

**Watch for:** does it read the merge commit (9) as extra support for the gRPC
migration (it shouldn't — same change)? Does it net out the Redis revert instead of
asserting the cache exists? Do version bumps leak into a durable claim?

## Runs & observations

_(none yet)_
