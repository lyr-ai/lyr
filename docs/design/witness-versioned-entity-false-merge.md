# Witness: versioned-entity false merge (DeepSeek corpus)

**Status:** recorded witness, deterministic fix not yet built. Second independent
identity witness (after 红楼梦). Surfaced a failure the literary corpora could not:
the generic resolver **false-merges a version chain**.

## Observation (free — no extraction needed)

Running the generic resolver on the real entity set of the DeepSeek evolution
corpus (V3 → V3.2 → V4), with each model typed `model`:

    20 raw entities -> 14 canonical groups

    [DeepSeek-V3.1-Terminus]  <- DeepSeek-V3, DeepSeek-V3-Base,
                                 DeepSeek-V3.1-Terminus, DeepSeek-V3.2-Exp,
                                 DeepSeek-V3.2, DeepSeek-V3.2-Speciale   (FALSE MERGE)
    [DeepSeek-V4-Pro-Max]     <- DeepSeek-V4-Pro, DeepSeek-V4-Pro-Max    (FALSE MERGE)
    [DeepSeek-V4-Flash]       (distinct)
    [DeepSeek-V2]             (distinct)
    ...components each distinct...

Six distinct model releases collapsed into one canonical entity. This is a
**false merge** — the project's one intolerable error class (`resolution.py`:
"a false split is tolerable; a false merge is not").

## Located failure boundary

The `name expansion (prefix)` rule (`resolution.py` pass 1, via `_prefix_of`).

- `_tokens("DeepSeek-V3")`        = `[deepseek, v3]`
- `_tokens("DeepSeek-V3.2-Exp")`  = `[deepseek, v3, 2, exp]`  (`.`/`-` are separators)
- `_prefix_of` → the first is a contiguous token-prefix of the second → **LINK**.

For a **person**, short ⊂ full (`Elizabeth` ⊂ `Elizabeth Bennet`) correctly means
*same entity*. For a **versioned artifact**, `V3` ⊂ `V3.2-Exp` means the
**opposite** — a sibling release, a *different* entity. The signal is structurally
identical; the semantics are inverted by entity type. This is the same shape as
the already-handled person-vs-service split (`_weak_subset` gated on type;
`test_bare_form_links_person_but_not_component`), but for the *prefix* rule, which
is currently **not** type-gated.

Why the novels never showed it: people have no version suffix. The failure is
specific to versioned / released artifacts (models, software, specs, datasets).

## Distinguishing "expansion" from "sibling version" (deterministic signal)

A longer label is a **sibling version, not an expansion**, when the tokens it adds
beyond the shorter label include a **version discriminator** — a token that
contains a digit (`v3`, `3`, `2`, `4`) or is a known release qualifier
(`base`, `pro`, `flash`, `exp`, `terminus`, `speciale`, `max`, `mini`, `lite`).
For non-person types, such an "expansion" should be **UNSURE / REJECT**, never an
auto-LINK. (`V4-Pro` ⊂ `V4-Pro-Max` is the same case: `max` is a variant
qualifier → sibling, not expansion.)

This mirrors fix A's logic: a structural containment that is a merge for one
entity type is a non-merge for another. Call it **fix D — type-gated
version-prefix**: prefix name-expansion links only when the added tokens are NOT
version discriminators, or when both entities are `person`.

## Why this is NOT a v0.2 trigger

The second witness was supposed to decide whether the gated v0.2 LLM proposer is
warranted. It says the opposite: the headline failure is a **deterministic**
resolver defect (a type-unsafe prefix rule), fixable for free like C+A were — not
a semantic-alias problem needing the proposer. The only genuinely v0.2-shaped
residue here is component abbreviation aliasing (`MLA` ↔ `Multi-head Latent
Attention`, `MoE` ↔ `DeepSeekMoE`), which currently under-merges (a tolerable
false split), so it still does not force v0.2.

## Recorded capability boundary (separate from the bug)

Even with fix D keeping V3/V3.2/V4 distinct, LYR represents them as
*related-but-distinct entities*, not as **one entity evolving** where a V4 claim
revises a V3 claim. That is the standing `stateful semantic claims` gap
(`capability-gap-stateful-claims.md`). Fix D makes the identities correct; it does
not add interpretation-change modeling. Both statements stay honest in the demo.

## Next admissible steps (deterministic first, per the 红楼梦 discipline)

1. Record this witness (done).
2. **Fix D** — type-gated version-prefix in the resolver; add fixtures
   (V3/V3.2/V4 stay distinct; `Elizabeth ⊂ Elizabeth Bennet` still merges;
   person/service/model all covered). Free, deterministic re-run.
3. Re-run the resolver on the corpus; confirm the 6-way merge is gone and no new
   false split appears on P&P / 红楼梦 / Git.
4. Only then decide whether a paid `llm` extraction run adds anything the free
   resolver witness has not already established.
