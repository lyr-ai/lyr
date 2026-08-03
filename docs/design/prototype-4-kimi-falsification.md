# Prototype 4 — Kimi, the untouched fourth world (falsification probe)

**Status:** research probe, by hand from the real Kimi corpus (`explorer/cases/kimi/`). Purpose is
**falsification**: the scoped-claim primitive was *discovered* on DeepSeek + P&P. Kimi was not used to
find it. If the primitive holds here, it is generic; if Kimi breaks it, the review conflated
something. The probe was run trying to break it, not to confirm it.

Primitive under test:

> **Knowledge Object = a maintained set of scoped, evidenced, status-bearing claims and relations
> over semantic objects.** Relations/transitions carry `SUPPORTED / CONTRADICTED / UNKNOWN /
> NOT_EVALUATED`.

## Test 1 — a SUPPORTED derivation (the mirror of DeepSeek)

DeepSeek's attention lineage `MLA → DSA → CSA → HCA` had to be **ABSTAINED** — no derivation was
stated. Kimi states one outright:

    CONCEPT: Kimi's training optimizer
      members:  Muon, MuonClip
      relation: MuonClip  --improves_upon-->  Muon
                value:  adds a QK-clip technique to address training instability, keeps Muon's
                        token efficiency
                scope:  training stability / optimization
                evidence: k2-technical-report.md ("improves upon Muon with a novel QK-clip
                        technique to address training instability while enjoying the advanced token
                        efficiency of Muon")
                status: SUPPORTED          ← committed, because the corpus states the derivation

**This is the decisive test.** If the primitive only ever `ABSTAINED` derivations, the `status` field
would be theater. Kimi shows the *same* relation type (`derivation/improves_upon`) reaching the
*opposite* status — `SUPPORTED` — driven purely by whether the corpus states it. The status enum is
real, and the abstention in Prototype 1 was a judgment, not a default. **The primitive holds and is
strengthened.**

## Test 2 — a version-scoped departure

    CLAIM: Kimi-K2-Thinking introduces native INT4 quantization (via QAT)
      target:   Kimi-K2-Thinking
      relation: introduces / novel-relative-to
      value:    native INT4 QAT, ~2x generation speed, no perf degradation
      scope:    K2-Thinking vs previous Kimi versions
      evidence: k2-thinking-model-card.md ("absent from previous Kimi versions")
      status:   SUPPORTED

A version-indexed claim with an explicit "departs from prior" marker. Fits the primitive exactly
(Concept's index was *version*; this is the same index doing supersession). Holds.

## Test 3 — a comparative / over-general claim (the Theme layering, again)

    CLAIM: Kimi K2 surpasses baselines in non-thinking settings
      on the CITED benchmarks (Tau2 66.1, SWE-Bench Verified 65.8, ...):  SUPPORTED (numbers given)
      "surpassing most open and closed-sourced baselines" (general):      UNKNOWN (object under-
                                                                          specified; not enumerated)

Same two-layer shape as Prototype 2's Marriage theme: the instance/measured layer is `SUPPORTED`, the
sweeping layer `ABSTAINED/UNKNOWN`. A third domain, same discipline. Holds.

## Test 4 — where Kimi does NOT break it, but finds a BOUNDARY

`MLA (Multi-head Latent Attention)` appears in **both** the DeepSeek corpus and the Kimi corpus.
Question: does the primitive say these are the same object?

**No — and that is correct, not a failure.** The scoped-claim primitive is defined *over semantic
objects within a corpus*. `MLA@Kimi` and `MLA@DeepSeek` are separate nodes; nothing in the primitive
links them. This is a **new boundary**, not a break:

> **Cross-corpus concept identity** — "is MLA-here the same idea as MLA-there?" — is a layer *above*
> the scoped-claim primitive, not inside it. It is the knowledge-object analogue of entity resolution,
> lifted from within-corpus to across-corpus. Recorded as the next open question; explicitly out of
> scope for the primitive, which remains sound within a corpus.

## Falsification verdict

**Kimi did not break the primitive.** Across four independent worlds (DeepSeek Concept, P&P Theme,
Elizabeth State, Kimi optimizer/claims) every higher-order object reduced to the same unit — a
scoped, evidenced, status-bearing claim — and the same failure mode (an organizing narrative beyond
the evidence) had to be abstained. Kimi additionally **exercised the previously-untested `SUPPORTED`
derivation**, proving the status enum commits and abstains by evidence, not by default.

The one thing Kimi added is a **boundary, not a counterexample**: cross-corpus concept identity sits
above the primitive. That is a genuinely new question — and, notably, it is the *same shape* as the
identity work that the Semantic layer already converged on, now one level up. The exploration set out
to see whether a single representation unifies concepts, themes, and evolving claims across domains.
Four worlds say: **at the representation level, yes** — the substrate is claim maintenance, not object
type.

## Still NOT established (unchanged, honest)

Four hand-probes discovered and stress-tested a *representation*. No *system* forms it; there is no
zero-fabrication measurement at scale; the cross-corpus-identity boundary is unbuilt. A representation
that survives four worlds is a strong working hypothesis — it earns the name "layer" only when a
system forms it honestly and is graded. That build/measure decision remains the PI's.
