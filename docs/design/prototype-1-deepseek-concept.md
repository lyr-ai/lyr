# Prototype 1 — DeepSeek → Concept (representation probe)

**Status:** research probe, done by hand from the real corpus. Purpose is **not** to build a feature
— it is to discover *what a Concept knowledge object's representation must be*, and to test
falsifiably whether one forms honestly. Chosen first because a technical concept **cannot be
hallucinated** the way a theme can: if the object is not really in the evidence, it shows at once.

Target concept: **DeepSeek's line of attention mechanisms for inference / long-context efficiency**
— the candidate the review wrote as `MLA → DSA → CSA → HCA`.

## Step 1 — what the corpus actually supports (with citations)

Only the five official docs in `explorer/cases/deepseek/`:

- **MLA — Multi-head Latent Attention** (V3). "DeepSeek-V3 adopts Multi-head Latent Attention (MLA)
  … for efficient inference." — `v3-technical-report.md`, `v3-readme.md`. Later still present:
  "MLA module … RoPE implementation details." — `v3_2-model-card.md`.
- **DSA — DeepSeek Sparse Attention** (V3.2-Exp). "builds upon V3.1-Terminus by introducing DeepSeek
  Sparse Attention … fine-grained sparse attention **for the first time**, delivering substantial
  improvements in long-context training and inference efficiency." — `v3_2-model-card.md`.
- **CSA + HCA — Compressed / Heavily Compressed Attention** (V4). "a hybrid attention architecture
  that combines Compressed Sparse Attention (CSA) and Heavily Compressed Attention (HCA) to improve
  long-context efficiency." — `v4-technical-report.md`.
- **Quantified cross-version claim.** "DeepSeek-V4-Pro requires only 27% of single-token inference
  FLOPs and 10% of KV cache compared with DeepSeek-V3.2." — `v4-technical-report.md`.

## Step 2 — the object that forms honestly

    CONCEPT: attention mechanism for inference / long-context efficiency  (DeepSeek)
      members (each an extracted concept entity, with its anchor version + evidence):
        · MLA  — V3        efficient inference                     [v3-report, v3-readme, v3.2-card]
        · DSA  — V3.2-Exp  first fine-grained sparse; long-context [v3.2-card]
        · CSA  — V4        hybrid, long-context efficiency          [v4-report]
        · HCA  — V4        hybrid, long-context efficiency          [v4-report]
      unifying claim:  version-anchored attention mechanisms documented across successive
                       DeepSeek releases, grouped by their shared inference / long-context /
                       KV-cache efficiency goal   ("successive" modifies the RELEASES, not the
                       mechanisms — no lineage is asserted)
      claim-state over versions (quantified, with provenance):
        · V4-Pro vs V3.2: 27% of single-token FLOPs, 10% of KV cache   [v4-report]
        · (V3 → V3.2 magnitude: not quantified in corpus → abstain)

This holds. Every field cites a passage; nothing is invented.

## Step 3 — where an honest system MUST abstain (this is the whole point)

The tempting demo-narrative is a **derivation lineage** `MLA → DSA → CSA → HCA` ("each evolved from
the previous"). The corpus does **not** support it:

- **No derivation is stated.** V3.2 says DSA "builds upon V3.1-Terminus" (a *model*), not upon MLA.
  V4 says it "combines CSA and HCA" — not that they descend from DSA. The `→` arrows are fabrication.
- **MLA is not sparse.** DSA is "sparse attention for the first time" — which means MLA was *not*
  sparse. MLA is latent/compressed; DSA is sparse; CSA/HCA are compressed-sparse. Grouping them as a
  "sparse-attention lineage" is **wrong**. The only honest grouping is by **shared goal**
  (efficiency), explicitly labeled as such.
- **Coexist vs replace: unknown.** MLA is still referenced at V3.2; whether V4 retains MLA alongside
  CSA/HCA is not stated → abstain.

DeepSeek exposed this immediately. A P&P "Pride" theme has no falsifiable derivation structure, so it
could never have surfaced the distinction between *shared-goal grouping* (real) and *lineage*
(fabricated). That is why this corpus was the right first probe.

## Step 4 — representation requirements this probe surfaces

A Concept knowledge object needs, at minimum:

1. `members`: a set of semantic (concept) nodes — **not** a mention; the object is over the graph.
2. `unifying_claim`: a statement + its **coverage evidence** (the passages that instantiate it).
3. `member_relation`: **not a free field but a committed judgment.** Each relation the object could
   assert (e.g. `derivation`) carries a *status* the system has actually decided:

       relation_type: derivation
       status:        ABSTAINED        # one of SUPPORTED / CONTRADICTED / UNKNOWN / NOT_EVALUATED
       reason:        no supporting evidence in corpus

   `ABSTAINED`/`UNKNOWN` is stronger than `null`: `null` may mean *not yet processed*
   (`NOT_EVALUATED`); `ABSTAINED` means the system *checked and refused to commit*. Without this
   distinction the layer manufactures lineage. ← the sharpest finding. (Schema not frozen; the
   four-way status distinction must survive into later prototypes.)
4. per-member: `(label, anchor_version, role_in_claim, evidence)`.
5. `claim_state_over_versions`: quantified deltas with provenance, where the corpus gives them;
   abstain where it does not.
6. `abstentions`: a **first-class list** of what the object deliberately does not assert, and why.

## Step 5 — falsifiability verdict

**A Concept object partially forms — honestly.** The evidence supports a goal-grouped set of
version-anchored mechanisms with one quantified cross-version claim. It does **not** support the
lineage narrative, which must be abstained. The object is real; the story about it is not. Good — a
representation that can hold both (assert the group, abstain the lineage) is exactly what "no
fabrication" requires.

**Prototype 1 closed — compressed conclusion:**

> A higher-order grouping can form honestly only when membership, grouping basis, inter-member
> relations, version-scoped claims, and abstentions are represented **separately**. **Sharing a goal
> does not license a lineage.**

## The minimal structure Prototype 1 forced

Not a full schema — four constituents that could not be collapsed without either losing information
or inviting fabrication:

    higher-order grouping
    ├── members                    (the semantic objects grouped)
    ├── grouping claim             (on what basis they are one group — with coverage evidence)
    ├── typed relation assertions  (each with a committed status, per requirement 3)
    └── explicit abstentions       (what is deliberately NOT asserted, and why)

And every assertion — grouping claim or relation — must carry:

    target · relation/predicate · value · scope · evidence · status

This starts to pull Concept, Theme, and State toward one lower unit: **a scoped, evidenced,
status-bearing claim.** Candidate primitive (still just a candidate, but more explanatory than
"Concept/Theme/State are three node kinds"):

> **Knowledge Object = a maintained set of scoped claims and relations over semantic objects.**

## What did NOT converge (tightened)

An earlier draft said the `claim_state_over_versions` field showed **State living inside Concept**,
hinting the two are one object. That over-reads the evidence. An equally-valid reading: the Concept
itself does **not** change from V3 to V4 — what changes is a **claim *about* the concept**
("mechanism X has cost/performance property Y", compared across versions). So the evidence supports
at most:

> **Higher-order objects require version-indexed claims.**

It does **not** yet support *"Concept and State are one object."* The tighter, carried-forward
statement is:

> **Concept formation required version-scoped claims, suggesting that claim maintenance — not object
> type — may be the common substrate.**

Prototype 3 then tests the sharper question directly (not assumes it): *for a fixed target claim,
when is a change in its committed value licensed by evidence?* (target = **Elizabeth**, not "Family").

## What Prototype 1 does NOT claim

- Not that the *system* formed this (a human did, from evidence) — the probe discovers the
  representation, it does not implement it.
- Not a schema. Fields above are what the evidence *forced*, to be reconciled with 2 and 3, not
  frozen now.
- Not that a paid LLM run is warranted yet — that decision waits until all three probes are in.
