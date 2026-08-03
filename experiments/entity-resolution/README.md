# Entity Resolution — generic identity, driven by a real corpus defect

The first real corpus (a full novel, run through LYR) exposed a **generic backend defect**: keying
semantic identity on the extracted label fragments one real entity into several nodes
(a given name vs a full name; a bare surname vs a titled or named form). That is a
**semantic-identity** problem, not a presentation one — so the fix is a **domain-independent
resolver** (`lyr/semantic/resolution.py`), not a per-book patch.

## Status

- **Resolver:** implemented, generic, verified. Proposes `LINK` / `UNSURE`, never silently commits;
  conservative (false split tolerable, false merge not); zero book-specific names in core.
- **Gold fixture (`pnp-gold.json`):** the hand-reviewed merges/non-merges from the first real run,
  **reclassified** from a runtime patch into *evaluation data*. 7 positive groups, 2 negative pairs.
- **Phase 4 (`validate_pnp.py`):** the generic resolver **passes** the fixture — recovers all 7
  groups (incl. the 3-way Wickham cluster) and rejects both title-conflict pairs — with no
  book-specific logic.

## The generic signals (no domain knowledge)

| decision | signal |
|---|---|
| `REJECT` | title/gender conflict (Mr./Sir vs Mrs./Miss/Lady); or the two are the endpoints of one relationship (distinct) |
| `LINK` | **name expansion** — a token-prefix, or a titleless short form whose significant tokens ⊆ the other's (a bare surname bridges titled/named forms) |
| `UNSURE` | shared surname only — surfaced as a candidate to review, **never merged** |

Transitive grouping additionally **refuses to bridge a rejected pair** (a bare form can't merge a
Miss/Mr conflict via transitivity).

## Run

```bash
python -m pytest tests/test_resolution.py -q          # generic unit tests (CI-safe)
python experiments/entity-resolution/validate_pnp.py  # against the real run + gold fixture
```

## Roadmap (from the review)

- **Phase 1–4 (done):** deterministic candidate generation + contextual guards + verifier, validated
  against the fixture.
- **Phase 5 (next):** smoke-test another domain (git/incident aliases: service name vs abbreviation,
  person vs username) — if the same resolver helps with no per-domain code, it's generic progress.
- **Wire-in:** once the resolver matches/exceeds the fixture (it does), the hand-written alias
  adapter leaves the Explorer's runtime path and remains here as evaluation data only.
- **Later:** contextual scoring may add an LLM *proposer* (structured, evidence-linked) for the
  harder `UNSURE` cases; identity-over-time (`Child → Student → Founder`) becomes a core semantic
  capability (see `docs/design/canonicalization-and-identity.md`).
