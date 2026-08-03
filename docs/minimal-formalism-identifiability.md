# Minimal Formalism for Identifiability under Unknown Measurement Processes

*Internal note. No related work, motivation, or discussion — only the objects, the
audit schema, and two worked examples. If these do not compute cleanly, the theory is
not ready.*

---

## 1. Definitions

- **Joint model space.** `Θ₀ = H × M`, where `H` is a class of world hypotheses and
  `M` a class of measurement processes (the unknown, possibly non-invertible map from
  world to record).
- **Record.** `r` — the observed representation.
- **Compatibility.** A relation `r ⊨_m h` : the pair `(h, m)` does not *forbid* `r`
  (there exists a world-state consistent with `h` that `m` can map to `r`). Logical
  consistency, not similarity — no metric on `Θ`.
- **Compatible set.** `C(r) = { (h, m) ∈ Θ₀ : r ⊨_m h }`.
- **Constraint.** An auditable `cᵢ` picks an allowed subset `Sᵢ ⊆ Θ₀`. Accumulation:
  `Θₙ = C(r) ∩ ⋂ᵢ Sᵢ`.
- **Target.** A functional `Q : Θ₀ → 𝒬` (the question actually being asked).
- **Identified set.** `I_Q(Θₙ) = { Q(θ) : θ ∈ Θₙ }`.
- **Point-identification.** `Q` is identified iff `|I_Q(Θₙ)| = 1`. Otherwise `I_Q`
  gives partial identification (a set, bound, or ordering).

Identifiability is always of a **target `Q`**, relative to `(H, M, {cᵢ})` — never of
the whole `Θ`.

---

## 2. Constraint-Witness Schema

Every constraint used in any example must be filled into this fixed template. It is the
theory's audit interface.

| field | content |
|---|---|
| **Constraint `cᵢ`** | what it asserts |
| **Restriction `Sᵢ`** | the allowed subset it keeps |
| **Witness** | the observation/artifact that triggers it (with provenance) |
| **Type** | `empirical` (has an observation-witness) or `assumption` (structural commitment) |
| **Background commitments** | assumptions the witness itself depends on → `constraint ← witness ← commitments` |
| **Target(s) affected** | which `Q` |
| **Excluded joint hypotheses** | which `(h, m)` pairs it removes |
| **Identification gain `Δ_Q`** | `I_Q` before → after |

`empirical` vs `assumption` is **not a binary label**: an observation-witness carries
its own background commitments, so the honest report is one of *direct empirical* /
*empirical under `A₁,A₂`* / *structural assumption only*.

---

## 3. Example A — Diary: world / measurement compensation

**Record `r`:** over the diary's span, the share of family-vs-career content **rises**.

**`H` × `M`** (2 × 2):

| | `m_stable` (framing constant) | `m_change` (framing shifts to family) |
|---|---|---|
| `h_change` (attitude shifts to family) | `r` forbidden? **no** → ✓ | **no** → ✓ |
| `h_stable` (attitude constant) | content should be constant, but rises → **forbidden ✗** | **no** → ✓ |

`C(r) = { (h_change, m_stable), (h_change, m_change), (h_stable, m_change) }`, `|C(r)| = 3`.

**Q₁ = "did her attitude change?"**
`I_{Q₁}(C(r)) = { yes, yes, no } = {yes, no}` → **not identified.**
The observed shift is compatible with *"she didn't change; only her writing did"*
`(h_stable, m_change)`. This is the world/measurement compensation, and it means even
*did she change at all?* is underdetermined from the record alone.

**Constraint `c₁`** to break it:

| field | content |
|---|---|
| Constraint `c₁` | measurement framing is stable |
| Restriction `S₁` | `M = {m_stable}` |
| Witness | stylometry (function-word rates, sentence length, structure) is **constant** over the diary's span — an artifact of the text itself |
| Type | empirical, **under** a background commitment |
| Background commitments | `A₁`: stable stylometry ⟹ stable framing |
| Target affected | `Q₁` |
| Excluded joint hyps | `(h_change, m_change)`, `(h_stable, m_change)` |
| `Δ_{Q₁}` | `{yes, no}` → `{yes}` |

`Θ₁ = { (h_change, m_stable) }`. **`Q₁` is now identified (`yes`) — under `A₁`.**

**Q₂ = "*why* did she change?"** Refine `h_change` into `{fear, duty, social}`
(same predictions on `r`). `I_{Q₂}(Θ₁) = {fear, duty, social}` → **not identified**,
even after `c₁`. A discriminating natural experiment ("after the parents died, did the
pattern persist?") would be needed — and the diary may or may not contain it.

**What A computes:** identifiability is per-target (`Q₁` vs `Q₂` split `Θ₁` differently);
`Q₁` is identified only *after* a measurement constraint, and only *relative to `A₁`*;
`Q₂` stays partially identified. `|C(r)|` alone is not the criterion.

---

## 4. Example B — Agent log with censoring (no likelihood)

**Record `r`:** self-log with tool-call IDs `[1, 2, 4]`, terminal state = failure, no
`deploy` call (`X`) visible.

**`H` × `M`**:

| | `m_complete` (logs all) | `m_censored` (drops failed calls) |
|---|---|---|
| `h_X` (failure caused by `X`) | `X` failed ⇒ must appear, but absent → **forbidden ✗** | `X` failed ⇒ dropped ⇒ absent → ✓ |
| `h_notX` (failure caused by a logged call) | consistent → ✓ | consistent → ✓ |

`C(r) = { (h_X, m_censored), (h_notX, m_complete), (h_notX, m_censored) }`, `|C(r)| = 3`.
Only the **compatibility relation** is used — no probabilities.

**Q = "was the failure caused by `X`?"**
`I_Q(C(r)) = { yes, no, no } = {yes, no}` → **not identified** (X-absent ≡ X-censored *or* X-innocent).

**`c₁` — schema continuity** (a constraint that shrinks `Θ` but does *not* identify `Q`):

| field | content |
|---|---|
| Constraint `c₁` | a call was omitted |
| Restriction `S₁` | `M = {m_censored}` |
| Witness | ID gap: `[1,2,4]` is missing `3` |
| Type | empirical, under commitment |
| Background commitments | `A_schema`: IDs are assigned consecutively |
| Target affected | (none directly) |
| Excluded joint hyps | `(h_notX, m_complete)` |
| `Δ_Q` | `{yes, no}` → `{yes, no}` (unchanged) |

`Θ₁ = { (h_X, m_censored), (h_notX, m_censored) }`. Knowing *that* censoring happened
does not identify *what* was censored.

**`c₂` — independent channel:**

| field | content |
|---|---|
| Constraint `c₂` | the omitted call at position 3 was `X`, and it failed |
| Restriction `S₂` | `H = {h_X}` |
| Witness | an **external audit log** (separate channel) recording `deploy failed @ 3` |
| Type | empirical, under commitment |
| Background commitments | `A_audit`: audit channel is independent / non-colluding with the agent's self-log |
| Target affected | `Q` |
| Excluded joint hyps | `(h_notX, m_censored)` |
| `Δ_Q` | `{yes, no}` → `{yes}` |

`Θ₂ = { (h_X, m_censored) }`. **`Q` identified (`yes`) — under `{A_schema, A_audit}`.**

**What B computes:** the whole pipeline runs on `⊨_m` with **no likelihood** (censoring
is a deterministic, adversarial-leaning `m`); one constraint can shrink `Θ` without
moving `I_Q`; identification arrives only with an **independent channel**, and is
reported *under its non-collusion assumption* — never as raw data.

---

## 5. What this note establishes

The claim is **not** "the theory is validated." It is stronger and more precise: **the
formalism is operationalizable.** In both examples — structurally different — every
object the protocol needs (`Θ, Q, C(r), Sᵢ, I_Q`, and the witness table) **already
existed before computation began. Nothing new had to be invented.** That is the real
readiness criterion; "the examples worked" is weaker.

Three things, stated precisely:

- **Executable, not merely computable.** Given a *finite* hypothesis class, the audit
  protocol can be carried out unambiguously to a definite `I_Q`. ("Computable" would
  wrongly suggest a complexity-theoretic claim; none is made here.)
- **Compatibility is the primitive.** Example B ran entirely on `r ⊨_m h` — no
  likelihood, no Bayes, no metric, no embeddings. Probability was not secretly essential.
- **The formalism made a counterintuitive prediction.** Example A was *expected* to
  identify "did she change?"; it did not (world/measurement compensation). The framework
  corrected its own designers' intuition — it is no longer merely re-expressing prior
  belief. This gives the theory a fourth part beyond definitions, principles, and
  examples: **predictions that can surprise.**

So commit `1149ff4` is where the project's character changes: **from a conceptual
research program to a minimal formal system with an executable audit procedure.** That
is stronger and easier to defend than "we have a nice theory," and it does not overstate
what was done: the examples are hand-computed 2×2 joints, so what is established is
*executability on a finite class*, not scaling.

The paper is now an expansion of this note, not the proposal of an idea.
