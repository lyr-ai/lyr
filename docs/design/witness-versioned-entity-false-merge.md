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

## Outcome of fix D (digit-only, shipped)

Fix D lands the narrow, fully-generic signal: for a non-person prefix expansion,
if the **added** tokens include a digit-bearing token, emit `UNSURE` (reason
`version discriminator`) instead of `LINK`. No wordlist.

Result on the corpus entity set (10 models): the cross-version blob is broken —

    before fix D: 4 groups  (V3..V3.2-Speciale all merged into one)
    after  fix D: 6 groups  (V3 | V3.1-Terminus | V3.2* | V2 | V4-Pro* | V4-Flash)

The three **version numbers** V3 / V3.1 / V3.2 are now distinct groups, and V4 is
separate. 红楼梦 (45 groups / 4 merges) and P&P are unchanged — no new false split.

### Residual (documented, deferred — NOT tolerated silently)

Within a single version point, **word-qualifier** variants still auto-LINK,
because the digit sits in the shared base, not the added token:

    [V3, V3-Base]                        (added "base")
    [V3.2-Exp, V3.2, V3.2-Speciale]      (added "exp" / "speciale")
    [V4-Pro, V4-Pro-Max]                 (added "max")

These are the same class the digit signal deliberately does not touch. The fix
here is **not** a `pro/max/flash/base/exp` wordlist in the generic resolver (that
would encode naming convention into structure). It waits for a non-wordlist
structural signal — official `base_model` metadata, a release/variant graph, a
model-card parent field, or a package/version schema — i.e. **metadata-aware
variant resolution**, gated until a second heterogeneous corpus shows the same
pattern with such metadata available.

## Next admissible steps

1. Record this witness (done).
2. **Fix D** — digit-only version-prefix gating, with fixtures (done; suite green).
3. Re-run the resolver on the corpus; 6-way merge gone, 红楼梦/P&P unchanged (done).
4. Decide whether a paid `llm` extraction run adds anything the free resolver
   witness has not already established (open — the identity verdict is already in
   hand; the paid run would add claim/evidence tracing + the Explorer package).
5. Kimi corpus later provides the potential second witness for metadata-aware
   variant resolution (the qualifier residual above).
