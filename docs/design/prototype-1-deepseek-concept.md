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
      unifying claim:  successive attention mechanisms, each introduced in a specific version,
                       all targeting inference / long-context / KV-cache efficiency
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
3. `member_relation`: an explicit, evidence-gated field that can be `shared_goal` **and must be able
   to say `derivation: unknown/abstained`.** *Without a first-class abstention value here, the layer
   will manufacture lineage.* ← the sharpest finding.
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

## Early convergence hint (to TEST in Prototype 3, not to conclude now)

Forming this Concept required a `claim_state_over_versions` field (the 27% / 10% claim). That is the
**State** candidate appearing *inside* a Concept. It hints Concept and State may be one object seen
statically vs over time — but one prototype cannot establish convergence. Recorded as a hypothesis
for Prototype 3 (Family → State); explicitly **not** a conclusion. The rule stands: three
independent worlds must agree before anything earns the name "Knowledge Object."

## What Prototype 1 does NOT claim

- Not that the *system* formed this (a human did, from evidence) — the probe discovers the
  representation, it does not implement it.
- Not a schema. Fields above are what the evidence *forced*, to be reconciled with 2 and 3, not
  frozen now.
- Not that a paid LLM run is warranted yet — that decision waits until all three probes are in.
