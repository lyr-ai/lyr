# Canonicalization Layer & the Identity Roadmap

**Status:** v0.1 implemented (Explorer-side). Records the architectural rule so a domain never
leaks into core.

## The rule

> **Never hard-code a validation domain into the core. Always allow a validation domain to
> configure the *presentation*.**

Two different things, kept apart:

- **Core (LYR).** Semantic nodes and their identities are content-addressed and domain-agnostic.
  A book, a repo, a paper all produce the same `Node` shape. Core is **never** edited to make one
  book look right.
- **Canonicalization (Explorer).** A presentation pass that decides *how* to display those nodes —
  e.g. that "Elizabeth" and "Elizabeth Bennet" are one person. It reads core output plus a
  per-domain **adapter** and emits a canonical *view*. Core is not touched; every original node id,
  label, version chain, evidence link, and chapter span is preserved inside the canonical entity,
  with merge provenance.

```
Source → Semantic → Durable            (LYR core — unchanged)
                        │
                        ▼
        knowledge.json  (raw core output)
                        │
                        ▼
        Canonicalization Layer  ← per-book alias adapter (validation data)
                        │
                        ▼
        knowledge.canonical.json  →  Explorer
```

The adapter (`explorer/adapters/<domain>.aliases.json`) is **validation data**, not code. Swap it
to canonicalize a different source; the Explorer code does not change. That is
*generic representation, domain-specific validation* applied to identity.

## v0.1 — book adapter + guarded merge (done)

- Adapter lists high-confidence aliases only (`Elizabeth → Elizabeth Bennet`, `Wickham / Mr.
  Wickham → George Wickham`, …).
- Every merge is re-checked at canonicalization time, even though the adapter is curated:
  1. **No title conflict** — a male honorific (Mr./Sir/Colonel/Lord) vs a female one
     (Mrs./Miss/Lady) is refused. This keeps *Miss Darcy* ≠ *Mr. Darcy*, *Miss Bingley* ≠
     *Mr. Bingley*.
  2. **Evidence link** — allowed only on full-name expansion (token subset) or a shared
     significant token. No bare-surname merges.
  3. **Ambiguous stays split** — a refused merge is reported and kept as two entities. Duplication
     is safer than a wrong merge, which is harder to detect and more damaging to credibility.
- Result on Pride and Prejudice: 32 raw → 24 canonical, 7 groups merged, 0 false merges.

## v0.2 — general identity resolver (later)

Replace the hand-written adapter with a generic resolver, still Explorer-side:
`exact match → alias dictionary → LLM proposes merge → evidence verifier → canonical group`.
Works across books, git, papers, forums with no per-domain code.

## v1 — identity as a core semantic capability (research)

Eventually, "is this the same entity over time?" is itself part of *living knowledge* — a person is
`Child → Student → Engineer → Founder` as one identity. That is generic, not book-specific, and
belongs in the semantic layer, not the Explorer. Treated as future research; **not** in scope now,
and not a reason to touch core today.

## Ideas / themes in v0.1

Dropped. The durable layer produced 0 ideas here because its consolidator is deliberately
conservative ("prefer NO_OP") — the right behavior for incremental memory, the wrong tool for
"surface a novel's themes." We do **not** loosen that prompt (that would let a validation domain
redefine core), and we do **not** add a book-specific themes pass yet (that would change two lines
at once and blur where the Explorer's value comes from). The Explorer ships People · Relationships ·
Events · Evolution · Evidence — all real — and simply omits Themes until there is real durable
output. `meta.themes = "not_yet_derived"`.
