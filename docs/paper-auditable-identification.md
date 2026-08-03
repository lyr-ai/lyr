# When Does an Explanation Refer to the World?

### An Auditable Identification Protocol

*Working draft — v1. A methodological paper. It introduces a protocol, not a theorem; it is
demonstrated on finite classes, not proven in general. The organizing claim is that
identification is something you **do**, and the protocol's defining property is that doing it
**externalizes hidden assumptions** — including the authors' own.*

---

## Abstract

Given a record — a diary, a system log, a model's explanation of its own behavior — we often
want a *world-level* claim: did the person's attitude change; did call `X` cause the failure;
does this explanation refer to what actually happened. The record, however, is produced by an
**unknown measurement process** mapping world to representation, and that process can be
lossy, inverted, or adversarial. When it is unknown, an explanation that *fits* the record is
not thereby *identified*: a different world seen through a different measurement can produce
the same record. Fit is not reference.

We take a deliberately modest position. We do not offer a criterion that certifies when an
explanation refers to the world. We offer a **protocol** that computes, for a specific
question `Q`, the set of answers still compatible with the record and a stated set of
constraints — and that **forces every constraint to arrive with a witness.** Identification
is then not a property an explanation has; it is the output of running the protocol, reported
together with the ledger of assumptions the run depended on.

The protocol's objects are a joint hypothesis space `Θ = H × M` (world × measurement), a
likelihood-free compatibility relation, constraints tagged empirical-or-assumption by an
explicit witness schema, per-question identified sets, and a multi-valued formalization class
`F` for natural language. We demonstrate it on two hand-computed examples, subject it to three
structural falsifiers (each of which it survives by *externalizing* a hidden step rather than
patching over it), and — unusually for a methodological note — turn it on **itself**: a
**self-audit** in which strangers execute the protocol to find the assumptions its own authors
could not see. Across three rounds and nine independent executions it reproduced its results
exactly and drove its "places I had to invent something" list to empty — each round converting
a tacit authorial premise into a written one. The reproduction is only the mechanism; the
result is that the protocol externalized the assumptions of its own makers, which is exactly the
property it claims. The scope is finite
classes and executability; scaling and a general theorem are explicitly future work.

---

## 1. Problem — why explanation is not enough

Fix a record `r`: the text of a diary, a sequence of tool-call log lines, a language model's
post-hoc account of why it did something. We want a claim about the world behind `r` — call it
the **target** `Q`. *Did her attitude actually change? Did `X` actually cause the failure? Is
this account of the world true of the world?*

The obstacle is that `r` is not the world. It is the image of the world under a **measurement
process** `m`: how the underlying state was selected, framed, filtered, possibly censored,
into the representation we hold. In the cases we care about most — self-reports, audit trails,
AI self-explanations — `m` is exactly what is uncertain, and sometimes exactly what is
motivated to mislead.

This breaks a tempting inference. An explanation `h` that *fits* `r` seems to earn credence.
But fit is a joint property of `(h, m)`, not of `h`. A world where the attitude changed, seen
through faithful framing, and a world where nothing changed, seen through drifting framing,
can produce the *same* rising family-vs-career content. A log missing a failed deployment is
equally consistent with "the deploy never ran" and "it ran, failed, and was censored." This is
**world/measurement compensation**: the two unknowns trade off along the exact directions the
record cannot see.

So "does this explanation refer to the world?" has no answer readable off the explanation. It
depends on what you are willing to assume about `m` — and the honest failure of most accounts
is that they bound `m` *silently*, then present the resulting certainty as though it came from
the data. The problem this paper addresses is not "find the true explanation." It is: **make
the assumptions that any world-level claim rests on impossible to hide.**

## 2. Claim

> Identification is not a property of an explanation; it is the output of executing an
> auditable procedure that progressively externalizes hidden assumptions.

Read literally, this claim already contains its own corollaries — each is just what it means
for identification to be the *output of a procedure* rather than a property:

- **Target-specific.** The procedure computes an identified *set* for a particular `Q`. Two
  questions about the same record can have different identifiability; "is the explanation
  identified?" is malformed until `Q` is named.
- **Witnessed.** The procedure may only shrink the space of possibilities by a constraint that
  carries a witness. It cannot help itself to a restriction; it must show the artifact or name
  the assumption.
- **Measurement-visible.** The procedure cannot silently bound the measurement class. Bounding
  `M` is itself a step it must perform *on the record*, tagged as assumption or as
  empirical-under-commitments.
- **Formalization-honest.** The procedure cannot silently compile a natural-language phrase
  into one formal reading. Ambiguity is carried as a set of readings until a witness removes
  one.

The rest of the paper is these four corollaries made mechanical, then stress-tested.

## 3. Protocol — objects, witness, audit

### 3.1 Objects

- **Joint space.** `Θ₀ = H × M`, `H` a class of world hypotheses, `M` a class of measurement
  processes (world → record; possibly non-invertible).
- **Compatibility.** `r ⊨_m h`: the pair `(h, m)` does not *forbid* `r` — some world-state
  consistent with `h` can be mapped by `m` to `r`. This is logical consistency, **not**
  similarity and **not** likelihood. There is no metric and no probability on `Θ`. (Example B
  runs entirely on this relation; probability is never secretly required.)
- **Compatible set.** `C(r) = { (h,m) ∈ Θ₀ : r ⊨_m h }`.
- **Constraint.** An auditable `cᵢ` selects an allowed subset `Sᵢ ⊆ Θ₀`. Constraints
  accumulate: `Θₙ = C(r) ∩ ⋂ᵢ Sᵢ`.
- **Target and identified set.** `Q : Θ₀ → 𝒬`; `I_Q(Θₙ) = { Q(θ) : θ ∈ Θₙ }`. `Q` is
  point-identified iff `|I_Q| = 1`; otherwise `I_Q` *is* the answer (a set, bound, or ordering).
- **Formalization set.** A natural-language description `d` admits a **set**
  `F(d) = {f₁, f₂, …}` of admissible compilations into `(H, M, Q)` — not a function, since one
  phrase may legitimately formalize several ways. The **`F`-robust identified set** is the
  union `I_Q(d) = ⋃_{f∈F(d)} I_Q(Θₙ^{(f)})`; `Q` is `F`-robustly identified iff every reading
  yields the same singleton.
- **Closure premise.** A cell may be declared *forbidden* (rather than merely *underspecified*)
  only under a stated premise fixing which factors generate the record. Absent it, "forbidden"
  is not licensed — the honest verdict is `underspecified`, which routes into `F`.
- **No free identification.** The output-constant map `m*(w) = r` lies in an unrestricted `M`,
  so **no non-trivial target is identified without an explicit `M`-restriction.** Such a
  restriction is a constraint like any other.

### 3.2 The witness (the audit interface)

Every constraint used anywhere must be filled into one fixed template:

| field | content |
|---|---|
| Constraint `cᵢ` | what it asserts |
| Restriction `Sᵢ` | the subset it keeps |
| **Witness** | the observation/artifact that triggers it, with provenance — or **none** |
| **Type** | `empirical` (has an observation-witness) or `assumption` (structural) |
| Background commitments | what the witness itself depends on: `constraint ← witness ← commitments` |
| Target(s) affected | which `Q` |
| Excluded joint hyps | which `(h,m)` it removes |
| Identification gain `Δ_Q` | `I_Q` before → after |

`empirical` vs `assumption` is not a binary stamp: an observation-witness carries its own
commitments, so the honest report is *direct empirical* / *empirical under `A₁,A₂`* /
*structural assumption only*. The output of the protocol is never `I_Q` alone; it is `I_Q`
**plus this ledger**.

### 3.3 The audit

Running the protocol is: enumerate `Θ`; evaluate `⊨_m` on every pair (splitting into `F` where
a phrase is ambiguous); form `C(r)`; apply each constraint through the schema; read off `I_Q`.
Every contraction of `Θ` is tagged with its witness and commitments. What makes it an *audit*
rather than a calculation is that a reader can point to any singleton in the output and trace
it back to either an artifact or a named assumption — and can see, when identification fails,
*which* missing constraint would restore it.

## 4. Worked examples

### 4.1 Example A — a diary (world/measurement compensation)

`r`: over the diary's span the share of family-vs-career content rises. `H = {h_change,
h_stable}` (attitude shifts to family / constant); `M = {m_stable, m_change}` (framing constant
/ framing drifts to family regardless of attitude). Under the closure premise `A₀` (the share
is generated only by attitude × framing), the one forbidden cell is `(h_stable, m_stable)`, so
`C(r)` has three pairs.

**The protocol contradicts intuition.** For `Q₁` = "did her attitude change?",
`I_{Q₁}(C(r)) = {yes, no}` — *not identified*. The rising family content is equally explained
by "she changed" and by "only her writing did" `(h_stable, m_change)`. Even *did she change at
all* is undetermined from the record. Identification requires a **measurement** constraint:
`c₁` restricts `M` to `m_stable`, witnessed by constant stylometry across the span, under the
commitment `A₁` (stable stylometry ⟹ stable framing). Now `I_{Q₁} = {yes}` — **under `A₁`**.
For `Q₂` = "*why* did she change?" (refine into `{fear, duty, social}`), `I_{Q₂}` stays
`{fear, duty, social}` even after `c₁`: no available constraint separates motives that predict
the same record.

*What A demonstrates:* identifiability is per-target; a world-level claim can require a
measurement assumption to exist at all; and the protocol externalized an assumption the authors
did not know they were making (that the content rise reports a real change).

### 4.2 Example B — an agent log with censoring (no likelihood, and a formalization split)

`r`: a self-log with tool-call IDs `[1, 2, 4]`, terminal failure, and no `deploy` call `X`
visible. `H = {h_X, h_notX}` (failure caused by `X` / by a logged call);
`M = {m_complete, m_censored}` (logs all / drops failed calls). Under closure `A₀ᴮ` (the log is
generated only by which calls ran × the logging process), `(h_X, m_complete)` is forbidden.

The `(h_notX, m_censored)` cell is **not** a bare compatibility verdict — it is a
**formalization split**. Whether a failure "caused by a logged call" is consistent with a
process that "drops failed calls" turns on an undefined predicate: does the causing call itself
count as "failed"? So `F(d) = {f_fail, f_nofail}`: under `f_fail` the cause is dropped ⇒ not
logged ⇒ incompatible; under `f_nofail` a call can trigger failure while returning success ⇒
stays logged ⇒ compatible. (`(h_X, m_censored)` is not split: compatibility is existential, and
the "X caused *and* X failed ⇒ dropped" world satisfies it under both readings.)

`Q` = "was the failure caused by `X`?" is `F`-robustly `{yes, no}` on `C(r)` — not identified.
A schema-continuity constraint `c₁` (an ID gap at 3, witnessed, under `A_schema`: consecutive
IDs) excludes `m_complete`; it **identifies `Q` under `f_fail` alone** but not `F`-robustly —
under `f_nofail`, knowing censoring happened does not identify what was censored. Only an
**independent channel** `c₂` (an external audit recording `deploy failed @ 3`) closes it, and
only under two named commitments: `A_audit` (the channel is non-colluding) and `A_cause` (the
audit witnesses that `X` *failed*, not that it *caused* — the bridge to `h_X` is an assumption).
Then `Q` is `F`-robustly `{yes}` under `{A_schema, A_audit, A_cause}`.

*What B demonstrates:* the whole pipeline runs on compatibility with no likelihood; one
constraint can shrink `Θ` without moving `I_Q`; formalization re-enters and must be carried as
a set; identification arrives only with an independent channel and is reported under its
assumptions — never as raw data.

## 5. Structural falsifiers — why believe the protocol

We do not ask the reader to trust the protocol because its authors find it elegant. We tested
it three times against attacks aimed at its foundations. Each time it survived not by acquiring
a patch but by **externalizing** a step that had been hidden.

- **Falsifier 1 — auditor determinism.** Do independent auditors compute the same
  compatibility? On un-formalized natural language, no — they split on a single cell. But the
  split is not in *evaluation*: pre-compiling the phrase into explicit input→allowed-output
  relations makes them re-agree. The disagreement was **located**, with a witness, in
  natural-language → formal compilation. This *forced* the formalization class `F` — as a
  multi-valued, audited object, not an author's convenience. A falsifier produced a new object;
  the authors did not add it.
- **Falsifier 2 — is `F` a regress?** If formalization is itself uncertain, does auditing it
  require auditing the auditor, without end? No. On a finite grid the formalization quotient is
  finite and the same for both auditors; targets are stable under full coverage; the only real
  failure mode is *coverage* (under-covering `F` spuriously over-identifies) — which is exactly
  `H`/`M`'s existing open-class problem, fixed by the same coverage witness. `F` folds into a
  single joint space `Θ* = H × M × F`; it needs no higher adjudicator. The framework is closed
  over its own modeling step.
- **Falsifier 3 — unbounded `M`.** With the output-constant map `m*` in `M`, nothing is
  identified; can the protocol tell "not identified because `M` is open" from "identified only
  because an analyst silently bounded `M`"? Yes, and this is the decisive test. Completing `M`
  only preserves or enlarges `I_Q`; identifying `Q` requires *shrinking* `M`. The protocol does
  **not** solve unbounded `M` — it makes bounding it an auditable act: an assumption-only
  restriction and a calibration-witnessed restriction yield the *same* `I_Q` but are reported
  with *different* type and witness. Bounding `M` is the first genuinely **structural**
  requirement, met by the existing witness machinery — no new primitive.

The pattern across all three is one sentence: **the protocol survives attacks by externalizing
a previously hidden step, never by adding an unearned rule.** That is the strongest reason to
believe it — stronger than any example working.

## 6. Self-audit of the protocol

Here the protocol becomes the object of its own procedure. Its central claim is that executing
it externalizes hidden assumptions; the sharpest possible test of that claim is to run it on
**itself** and ask whether it externalizes the assumptions of its own authors. Most
methodological notes assert their self-containedness — and the authors, who share the context
that makes a note feel complete, are the worst possible judges of it. So we made the assessment
external. Executors with **no access** to the development were given the definitions, the
witness schema, and the example *inputs* (answers withheld), and asked to run the protocol and
to log every point where they could not continue without inventing something. Independent
reproduction is the **mechanism**; the **result** is a self-audit.

- **Round 1 (discovery).** Example A reproduced exactly — and all three executors independently
  re-derived the note's own background commitment `A₁`. Example B **diverged** at
  `(h_notX, m_censored)`. The invention lists localized three tacit premises: the closure
  premise `A₀`, the `F`-split on "caused", and the causal bridge `A_cause`.
- **Round 2 (patched).** With those written in, the numbers reproduced exactly, 3/3 — but the
  act of patching Example A's closure premise made the *absence* of one in Example B visible:
  executors, now required to cite a stated closure premise before forbidding a cell, correctly
  noticed B never stated one. Two more premises externalized (`A₀ᴮ`; a sharpened `A_schema`).
- **Round 3 (gate).** A packet faithfully mirroring the fully patched note: exact numerical
  reproduction 3/3, and the invention list came back **empty** 3/3.

By the pre-registered criterion — *a stranger executes both examples to the committed `I_Q`
without supplying a premise the note did not give* — the protocol passes. The result is not
merely "the note is clear." It is the paper's own claim turned on itself: **executing the
protocol externalized the authors' hidden assumptions**, one per round, until nothing tacit
remained. The reproduction experiment is therefore not an appendix; it is the primary evidence
that identification here is a procedure others can run, not a conviction the authors hold.

*Honest limit.* The strangers are independent language-model executors given clean packets.
This removes the authors' shared context — the thing that makes self-assessment unreliable —
but not model-shared priors. A human execution is the stronger version of this test and is
deferred to the reproduction package, not claimed here.

## 7. Scope

We state the boundaries plainly, because overclaiming would undo the paper's whole posture.

- **Finite classes.** Every example is a hand-computed 2×2 joint. What is established is
  **executability on finite `H`, `M`, `F`** — the protocol runs unambiguously to a definite
  `I_Q`. "Computable" would wrongly suggest a complexity claim; none is made.
- **No theorem.** We prove no general condition under which a class of explanations is
  identified. The contribution is a protocol and a discipline, demonstrated — not a theorem,
  proven.
- **No scaling.** Searching infinite or continuous `H`/`M`/`F`, and approximating `I_Q` when
  the classes are large, are named as future work and not attempted. (They are second-generation
  questions; they presuppose the first-generation object this paper introduces.)
- **Proxy executors.** Reproduction evidence is from language-model executors, a strong but not
  identical proxy for human first-time readers.

## Conclusion

Underneath the objects is a single constraint on the process that produced them — **every new
object must arrive with a witness.** `F` arrived with one (falsifier 1 located it); the
`M`-restriction arrived with one (the calibration channel of falsifier 3); each premise the note
now states arrived with one (an executor could not continue without it). That constraint is what
keeps an assumption *visible* rather than absorbed, and it is the whole recommendation of the
paper:

> Identification should not be reported as a property of an explanation. It should be reported
> as the result of an auditable procedure whose assumptions remain visible.

The protocol was first applied to its own development process, where it repeatedly exposed
assumptions held by its authors before they were exposed by anyone else. A method whose
signature property is that it externalizes hidden assumptions must, before anything, externalize
its makers' — and this one did.
