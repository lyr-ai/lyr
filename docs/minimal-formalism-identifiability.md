# Minimal Formalism for Identifiability under Unknown Measurement Processes

*Internal note. No related work, motivation, or discussion — only the objects, the
audit schema, and two worked examples. If these do not compute cleanly, the theory is
not ready.*

*Organizing claim: **identification is not a property of an explanation; it is the output
of an auditable procedure.** Everything below is that procedure and its objects; every
corollary — target-specificity, witnesses, visible measurement assumptions, formalization
sets — follows from taking that claim literally.*

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
- **Formalization set** (witnessed in §6). A natural-language description `d` admits a
  **set** `F(d) = {f₁, f₂, …}` of admissible compilations into `(H, M, Q)` — *not* a
  function, since one phrase may legitimately formalize several ways. `F` is an open
  class, audited exactly like `H`/`M`: a formalization is excluded only by a witnessed
  constraint, and stays multi-valued until one does.
- **F-robust identified set.** `I_Q(d) = ⋃_{f ∈ F(d)} I_Q(Θₙ^{(f)})`. `Q` is
  *F-robustly identified* iff every `f ∈ F(d)` yields the same singleton.
- **Joint candidate space** (witnessed in §7). `F` is a *third open dimension*, not a new
  primitive: `Θ* = H × M × F`, pruned jointly by
  `Θ*ₙ = {(h,m,f) : f(d) ⊢ (h,m,Q), r ⊨_m h} ∩ ⋂ᵢ Sᵢ`. Formalization uncertainty is just
  another unidentified dimension.
- **Coverage witness.** Like `H`/`M`, `F` is trusted complete only if *witnessed* so;
  otherwise `Q`'s identification is reported as *coverage-unestablished*. The union grows
  monotonically, so **under-coverage spuriously over-identifies** — that is `F`'s only
  failure mode, and it is `H`/`M`'s existing open-atlas problem, not a new one.
- **No free identification** (witnessed in §8). The output-constant map `m*(w)=r` lies in
  an unrestricted `M`, so **no non-trivial target is identified without an explicit
  `M`-restriction.** Such a restriction is a constraint like any other: *structural
  assumption only* until a witness *independent of `r`* makes it *empirical under
  commitments*. Identification is never assumption-free; the schema's job is to keep the
  assumption visible.

Identifiability is always of a **target `Q`**, relative to `(H, M, {cᵢ}, F)` — never of
the whole `Θ`, and never relative to a single silently-chosen formalization.

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

The `✗` cell rests on a **closure premise** `A₀`: the record is generated *only* by
(attitude × framing) — no exogenous third driver (e.g. real family events) can raise the
family share under constant attitude *and* constant framing. Without `A₀` the cell is
`underspecified`, not forbidden. `A₀` is therefore the *first* constraint, logged before
`c₁`; three independent executors of this note re-invented it unprompted (reproduction
experiment 1), which is why it is now stated rather than assumed.

`C(r) = { (h_change, m_stable), (h_change, m_change), (h_stable, m_change) }`, `|C(r)| = 3`
(under `A₀`).

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
| `h_notX` (failure caused by a logged call) | consistent → ✓ | **`F`-split** (below) |

The `(h_notX, m_censored)` cell is **not a bare `✓`** — it is a formalization split.
Whether a failure "caused by a logged call" is consistent with a process that "drops failed
calls" turns on an undefined predicate: *does the causing call itself count as "failed"?* So
`d` = "caused by a logged call" admits `F(d) = {f_fail, f_nofail}`:
- `f_fail` — the cause is a *failed* call: under `m_censored` it is dropped ⇒ **not logged** ⇒
  contradicts "logged" ⇒ cell **incompatible ✗**.
- `f_nofail` — a call can trigger terminal failure while itself returning success ⇒ not
  dropped ⇒ stays logged ⇒ cell **compatible ✓**.

Per formalization the compatible set differs:
`C(r)^{f_fail}  = { (h_X, m_cens), (h_notX, m_complete) }`  (`|·| = 2`);
`C(r)^{f_nofail} = { (h_X, m_cens), (h_notX, m_complete), (h_notX, m_cens) }`  (`|·| = 3`).
Only the **compatibility relation** is used — no probabilities.

**Q = "was the failure caused by `X`?"** The `F`-robust identified set unions over `F(d)`:
`I_Q^{f_fail}(C(r)) = {yes, no}`, `I_Q^{f_nofail}(C(r)) = {yes, no}`, so
`I_Q(d) = {yes,no} ∪ {yes,no} = {yes, no}` → **not identified** (X-absent ≡ X-censored *or*
X-innocent), robustly across both readings.

**`c₁` — schema continuity** (shrinks `Θ`; `F`-robustly does *not* identify `Q`):

| field | content |
|---|---|
| Constraint `c₁` | a call was omitted |
| Restriction `S₁` | `M = {m_censored}` |
| Witness | ID gap: `[1,2,4]` is missing `3` |
| Type | empirical, under commitment |
| Background commitments | `A_schema`: IDs are assigned consecutively |
| Target affected | `Q` (formalization-dependently — see `Δ_Q`) |
| Excluded joint hyps | `(h_notX, m_complete)` |
| `Δ_Q` | `f_fail`: `{yes,no}→{yes}` (identified) · `f_nofail`: `{yes,no}→{yes,no}` · **`F`-robust: `{yes,no}` unchanged** |

`Θ₁^{f_fail} = { (h_X, m_cens) }`; `Θ₁^{f_nofail} = { (h_X, m_cens), (h_notX, m_cens) }`.
So `c₁` **identifies `Q` under `f_fail` alone** — the reading in which the omitted call is the
failed cause — but not `F`-robustly: under `f_nofail`, knowing *that* censoring happened does
not identify *what* was censored. The honest report names the formalization its identification
depends on (exactly as §6). This makes B a **second `F` example**, not only the
"no-likelihood" one.

**`c₂` — independent channel:**

| field | content |
|---|---|
| Constraint `c₂` | the omitted call at position 3 was `X`, and it caused the failure |
| Restriction `S₂` | `H = {h_X}` |
| Witness | an **external audit log** (separate channel) recording `deploy failed @ 3` |
| Type | empirical, under commitments |
| Background commitments | `A_audit`: audit channel is independent / non-colluding with the self-log · `A_cause`: the failed call `X` is the *terminal* cause — the audit witnesses `X` *failed*, not that it *caused*, so `S₂ = {h_X}` needs this bridge |
| Target affected | `Q` |
| Excluded joint hyps | `(h_notX, m_censored)` (live only under `f_nofail`; already absent under `f_fail`) |
| `Δ_Q` | `f_fail`: `{yes}→{yes}` · `f_nofail`: `{yes,no}→{yes}` · **`F`-robust: `{yes,no}→{yes}`** |

`Θ₂^{f} = { (h_X, m_cens) }` for **both** `f ∈ F(d)`. **`Q` is `F`-robustly identified
(`yes`) — under `{A_schema, A_audit, A_cause}`.** The independent channel closes the split:
whichever way "caused" is formalized, the audit pins the cause to `X`.

**What B computes:** the whole pipeline runs on `⊨_m` with **no likelihood** (censoring is a
deterministic, adversarial-leaning `m`); `F` reappears here — whether "caused" implies
"failed" — so `c₁` identifies `Q` under one formalization yet *not* `F`-robustly;
`F`-robust identification arrives only with an **independent channel**, reported *under its
non-collusion (`A_audit`) and causal-bridge (`A_cause`) assumptions* — never as raw data.

---

## 5. What this note establishes

The claim is **not** "the theory is validated." It is stronger and more precise: **the
formalism is operationalizable.** In both examples — structurally different — every
object the protocol needs (`Θ, Q, C(r), Sᵢ, I_Q`, and the witness table) **already
existed before computation began. Nothing new had to be invented.** That is the real
readiness criterion; "the examples worked" is weaker.

*Corrected by reproduction experiment 1.* This claim was true for the **authors** and false
for **strangers**: three premises the authors supplied tacitly were not on the page — the
closure premise `A₀` (§3), and the `F`-split plus the causal bridge `A_cause` (§4). Three
independent executors re-invented exactly those three. §3/§4 above are the **patched**
versions; "nothing new had to be invented" is honest only of the patched note, and only if a
re-run reproduces with an empty invention list. Self-assessment of "self-contained" is
precisely the thing an author cannot do — which is why Phase 1 is external execution, not
re-reading.

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

---

## 6. Falsifier 1 — auditor determinism, and the formalization layer

**Setup.** `r` = *"After that day I no longer worry about her. I just started doing what
needs to be done."* `h₁` = worry decreased; `h₂` = still worries, may express otherwise.
`m₁` (natural language) = "reports current subjective state directly"; `m₂` = "after
conflict, rewrites vulnerable emotion into duty-narrative". `Q` = "did real worry decrease?"

**(a) Un-formalized `m₁` → auditors diverge.** On the four pairs, two competent auditors
agreed on three; on `(h₂, m₁)` they split — A: *incompatible* (a faithful reporter who
still worries would not write "I stopped worrying"); B: *compatible* ("current state" = a
momentary lull, consistent with a persisting disposition).
`C_A = {(h₁,m₁),(h₁,m₂),(h₂,m₂)}`, `C_B = {all four}`. The split is **not** about reading
the diary (both read it identically) — it is about what `m₁` *allows*.

**(b) The divergence is target-dependent.** For `Q` ("worry↓"): `I_Q^A = I_Q^B = {yes,no}`
— the disputed pair carries `no`, already present via `(h₂,m₂)`, so it washes out. For
`Q'' = "(h₂ ∧ direct-report)"`: `I_{Q''}^A = {no}` (identified), `I_{Q''}^B = {yes,no}`
(not) — the auditors return **different identification verdicts**. So falsifier #2 *can*
bite.

**(c) Positive control — pre-formalize `m₁`, evaluation re-agrees.** Compile `m₁` into two
explicit input→allowed-output relations: `m₁ˢᵗᵃᵗᵉ` (permits "stopped_worry" whenever a
momentary lull is possible — allowed under `h₁` and `h₂`) and `m₁ᵈⁱˢᵖ` (permits it only if
the disposition is low — **forbids** it under `h₂`). Judgment is now membership against a
fixed relation, and `C_A = C_B` under **each** formalization (table above in the cover
note). The divergence of (a) is therefore **not** in compatibility evaluation.

**(d) The witnessed addition — `F`, multi-valued.** The disagreement relocates, with a
witness, to natural-language→formal compilation. `F` enters as a **set**
`F(d) = {m₁ˢᵗᵃᵗᵉ, m₁ᵈⁱˢᵖ}`, and the F-robust identified set is the union
`I_Q(d) = ⋃_{f∈F(d)} I_Q^{(f)}`:
- `Q` (worry↓): `{yes,no} ∪ {yes,no} = {yes,no}` — robustly *not* identified.
- `Q''`: `{no} ∪ {yes,no} = {yes,no}` — identified under `m₁ᵈⁱˢᵖ` **only**; the honest
  output names the formalization its identification depends on.

**Consequence.** Natural-language formalization is itself an **open hypothesis class**,
audited like `H` and `M` — multi-valued, shrunk only by witnessed constraints, never
silently collapsed. The formalism now has **three** open classes — world `H`, measurement
`M`, formalization `F` — under one discipline, and the union over `F` is the
formalization-honest verdict.

Falsifier #2 did not break the system: it *located* the disagreement (formalization, not
evaluation) and forced a witnessed extension, not an arbitrary patch. My earlier guess
that #2 was "survivable by design" was wrong — it bites, and the bite is productive.

---

## 7. Falsifier 2 — is `F` itself auditor-stable, and does it fold into the joint space?

**Test (tightened).** Not "do two auditors propose the same `F(d)`?" (too strong). The
falsifier is whether their formalization sets yield **different target results**:
`I_Q^A(d) = ⋃_{f∈F_A} I_Q^{(f)}` vs `I_Q^B(d)`. Same admissibility protocol: explicit
allowed-output relation · no mechanism without linguistic basis · a realization · an
exclusion witness vs another formalization · wording-only variants with the *same*
compatibility relation collapse to one class.

**(a) The quotient is finite and stable.** On the fixed `(h,m)` grid the only free choice
is the disputed pair `(h₂, m₁)`: a formalization either **permits** "stopped_worry" under
`h₂` (*state* reading) or **forbids** it (*disposition* reading). Every candidate induces
one of these two relations; rule 5 collapses the rest. So `F(d)/∼ = {[permit],[forbid]}`
— finite, enumerable, and the **same** for both auditors. They cannot diverge on *what*
the admissible classes are; distinct compatibility relations on a finite grid are finite.

**(b) Target-stable under full coverage.** With `F_A/∼ = F_B/∼ = {[permit],[forbid]}`:
`I_Q(worry↓) = {yes,no}∪{yes,no} = {yes,no}`;
`I_{Q''}(h₂∧direct) = {yes,no}∪{no} = {yes,no}` (identified under `[forbid]` only). Both
auditors compute the **same** `I_Q`, `I_{Q''}`. The falsifier does not bite when both
apply the full protocol.

**(c) The real failure mode is coverage, not identity.** The union grows monotonically, so
an auditor who **under-covers** (omits an admissible class) gets a *smaller* union and
**spuriously over-identifies**: if A proposes only `{[forbid]}`, `I_{Q''}^A = {no}`
(identified) while `I_{Q''}^B = {yes,no}` (not). A real divergence — but a **coverage
failure**, identical to `H`/`M`'s open-atlas problem, fixed by the coverage witness (§1).
No new object.

**(d) `F` folds into `Θ* = H×M×F` — no regress.** Formalization uncertainty is another
unidentified dimension, absorbed by the same identified-set machinery; `F` needs no higher
adjudicator, and — like `H`,`M` — keeps multiple candidates until a witness excludes one.
The framework is **closed over its own modeling step.**

**Two recordable conclusions:** *target-stable despite formalization disagreement* (b);
*target-sensitive to formalization **coverage*** (c). Both are handled by existing
machinery. `F` is not the start of a regress — it is a test the framework passed on itself.

---

## 8. Falsifier 3 — unbounded `M`: exposed, not solved

**Sharper test.** Not "can the framework delete `m*`?" (it cannot) but: **can it
distinguish "not identified because `M` is open" from "identified only after an analyst
silently bounded `M`"?**

`r` = "the switch was off at 10:00" · `h_off, h_on` · `Q` = "was it off?".
`m_faithful` (reports the state), `m_inverted` (reports the opposite), `m*` (outputs `r`
for every world). Compatibility = does `(h,m)` produce the report "off"?

| stage | `M` | `C(r)` | `I_Q` |
|---|---|---|---|
| 0 | `{faithful, inverted}` | `{(h_off,faithful),(h_on,inverted)}` | `{yes,no}` — not identified |
| 1 | `+ m*` (+ constant maps) | `+ (h_off,m*),(h_on,m*)` | `{yes,no}` — **still** not identified |

**Stage 1 is the point:** *more complete* `M` did not create certainty. Completing `M`
only preserves or enlarges `I_Q`; identifying `Q` requires **shrinking** `M`, never growing it.

**Stage 2 — analyst restriction, no witness.** `S_copy = {(h,m) : m = faithful}` →
`C(r) ∩ S_copy = {(h_off, faithful)}`, `I_Q = {yes}`.

| Constraint | Witness | Type | Background | `Δ_Q` |
|---|---|---|---|---|
| `M = {faithful}` | **none** | **structural assumption only** | `A_copy`: sensor is faithful (asserted) | `{yes,no}→{yes}` |

**Stage 3 — calibration witness.** Independent record `Z`: on states known by a *separate*
channel, the sensor's output *matched*. The **same** restriction is now:

| Constraint | Witness | Type | Background | `Δ_Q` |
|---|---|---|---|---|
| `M = {faithful}` | calibration `Z` (independent of `r`) | **empirical, under commitments** | `A1` integrity · `A2` non-tampering · `A3` stationarity | `{yes,no}→{yes}` |

`I_Q = {yes}` — **the same set as Stage 2**, different epistemic status. *That difference is
the payoff.*

**Decisive falsifier — passed.** The framework (i) does **not** report Stage 2 and 3
identically (same `I_Q`, different Type/witness); (ii) does **not** drop `m_inverted`/`m*`
because the record "looks obvious" — they survive until a *tagged* constraint removes them.

**Control (`Q_M` = "is the sensor faithful?").** Stage 2: `I_{Q_M} = {yes}` *only because it
was assumed* — tagged assumption-only, so "trustworthy" cannot be smuggled in as fact.
Stage 3: calibration is *direct* evidence for faithfulness on the calibration states, but
`Q_M` **at 10:00** still needs `A2, A3` to transport. Identification is target-*and-time*-
specific — faithful-at-calibration is witnessed; faithful/off-at-10:00 are
witnessed-then-transported.

**Self-witness defense.** `r` cannot witness its own `m_faithful` (equally produced by
`(h_on, m_inverted)`); the witness must be independent of `r`, and `Z` rests on `A1`,
extending the §6 dependency graph and terminating at declared assumptions. No new regress.

**Conclusion.** The formalism does **not** solve unbounded `M`; it makes every solution to
it **visible** as an assumption or a witnessed restriction. *Bounding `M` is itself an
auditable identification act* — the first genuine **structural** requirement (unlike #1/#2,
which were procedural), met by the **existing** constraint–witness machinery, no new
primitive. There is no assumption-free identification; the schema's whole value is to keep
that assumption visible.
