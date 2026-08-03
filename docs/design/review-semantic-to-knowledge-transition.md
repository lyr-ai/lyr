# Design Review: the Semantic → Knowledge → Durable transition

**Status:** review / theory, frozen. Not being built. Triggered by a *convergence signal*, not a
new witness — the first time the backend work looks like optimization rather than architecture
discovery.

> **PI correction (the load-bearing revision).** An earlier draft ended: *"the next architecture is
> a Knowledge Object layer."* That sentence decides the answer. The honest form, which still lets the
> world answer, is:
>
> **The next research question is whether a single Knowledge-Object representation can unify
> concepts, themes, and evolving claims across domains.**
>
> The review found the **gap** (Durable ≠ Knowledge). It did **not** find the **object** — it
> assumed one. See "The gap is found; the object is not" below. We do **not** name a layer or open
> "M3.2" now. This is **Knowledge-Object *Exploration***, not a Knowledge-Object *Layer*. Same
> discipline that built the resolver: we did not design an "Identity Layer" from the first
> `Elizabeth / Elizabeth Bennet` observation — identity *grew out* of P&P → 红楼梦 → DeepSeek. A
> layer earns its name only *after* independent worlds converge on one representation.

## Why this review exists

The last three backend changes, in order:

    Pride & Prejudice → identity resolver (the generic resolution layer)
    红楼梦            → document parser + extractor source-fidelity + CJK name-expansion
    DeepSeek          → version discriminator (digit-only prefix gating)

None overturned the architecture. Each only **refined the Semantic Layer** — more generic signal in
the same layer. Two independent cross-domain witnesses (红楼梦, DeepSeek) both resolved
**deterministically**; the gated v0.2 LLM proposer still has *no forcing case*. The residuals that
remain (metadata-aware variant resolution; component abbreviation aliasing) are **optimizations**,
not architecture.

Read as a second derivative: the resolver has moved from *discovery* to *optimization*. A Kimi run
would, ~90% likely, buy one more generic signal (metadata variants), not a leap. That is the moment
to stop and ask the question a third resolver tweak would postpone: **if Knowledge is not People,
what is it — and does that layer exist yet?**

## The actual layer map (from the code, not the pitch)

    Source → Semantic → Durable            (LYR core)
                            │
                            ▼
                    knowledge.json → Canonicalization → Explorer

- **Semantic** (`lyr/semantic`): `SEMANTIC_KINDS = (entity, event, relationship)`. Extract → version
  → resolve identity. This is everything the Explorer shows: People · Timeline · Evidence.
- **Durable** (`lyr/durable`): a `Consolidator` proposes `ADD / UPDATE / MERGE / NO_OP` over durable
  **memories**. The recurrence baseline promotes a recurring entity/relationship ("*Elizabeth recurs
  across multiple experiences*", kind `subject`); the LLM builder asks for "*a lesson, decision,
  stable preference, persistent pattern, or lasting fact* … worth keeping after many experiences."
- **Canonicalization** (Explorer-side): presentation only — merges aliases into a view.

The durable layer **is** wired into every case (`export_knowledge` runs `build_durable()` and emits
`ideas`). It is not unwired. It produces **≈0 usable ideas** on books and on the DeepSeek corpus.

## The finding: two different things are conflated

Durable and Knowledge are being treated as one layer. They are not.

| | **Durable** (what LYR built) | **Knowledge Object** (what the Explorer needs) |
|---|---|---|
| question | *what should I keep after many experiences?* | *what is this body of evidence about?* |
| unit | a promoted semantic **claim/record** | a **higher-order node over the semantic graph** |
| vocabulary | lesson / decision / preference / pattern / fact | theme / concept / idea / claim-as-understanding |
| truth condition | recurrence / persistence | evidence **coverage + coherence** |
| origin model | **agent long-term memory** (experiences → lessons) | **synthesis** (graph → abstractions) |

The pipeline pipes `Semantic → Durable` and labels the durable output `ideas`. That is a category
error. `ideas = 0` / `themes = not_yet_derived` is not an unbuilt *feature* — it is the honest
symptom of an **absent layer**. The project already sensed this: the canonicalization doc calls the
durable consolidator "**the wrong tool for surfacing a novel's themes.**" Right instinct, filed as a
missing feature; it is a missing layer.

## This unifies the two recorded capability gaps

Two gaps were recorded separately. They are two faces of the same absent layer:

- **`ideas = 0`** — the layer applied to a *whole corpus*: themes/concepts as synthesis
  (Prejudice, the marriage market; MoE-as-efficiency-strategy, the attention-compression lineage).
- **stateful semantic claims** (`capability-gap-stateful-claims.md`) — the layer applied to a
  *single object over time*: an interpretation/state that is proposed per new evidence and revised
  (Elizabeth's understanding shifting; DeepSeek-V4-Pro *revising* the efficiency claim of V3.2 —
  "27% of FLOPs, 10% of KV cache").

Both need a substrate that does not exist: **knowledge objects** — nodes whose members are other
semantic nodes, carrying an evidence-backed claim that can be *held statically* (theme) and
*revised over time* (state). Neither Semantic (mentions → entities) nor Durable (records →
retained memory) is that substrate.

## What a Knowledge Object is (grounded definition)

A node whose **members are semantic nodes** (entities / events / relationships / passages), not a
mention of a name. It still obeys LYR's first rule — every knowledge object **cites the passages
that instantiate it** — but its truth condition is *coverage + coherence over the graph*, not
recurrence.

Per case, the objects the current pipeline cannot form:

- **Pride & Prejudice:** Prejudice · the marriage market · class & propriety — each organizes many
  scenes, relationships, and characters; none is a single named entity.
- **DeepSeek:** MoE-as-efficiency-strategy · the attention-compression lineage
  (MLA → DSA → CSA → HCA) · the reasoning-first turn · the million-token-context goal — each
  organizes many components, claims, and versions.

Note the subtlety: some knowledge objects *are* already extracted as `concept`-type **entities**
(`MLA`, `MoE`). But only as **mentions** — the layer would **promote** them into synthesis objects
that link every version, claim, and passage instantiating them, and (for the stateful case) track
how the claim about them changes across the version chain. Mention ≠ synthesized object.

## Two operations live inside the new layer

1. **Abstraction (static):** cluster/lift the semantic graph into evidence-backed concept/theme
   objects. Answers *"what is this about?"*
2. **State over time (dynamic):** a knowledge object's claim proposed and revised per new evidence
   (`ADD / UPDATE / CONTRADICT / NO_OP` over *interpretation state*). Answers *"what changed in our
   understanding?"* — the recorded stateful-claims gap.

Both mirror the durable layer's **propose-vs-commit** discipline, but operate on a *different unit*
(the graph, not records) with a *different truth condition*. They must not be faked by loosening the
durability prompt — the canonicalization doc's warning stands: that would let a validation domain
redefine core.

## Honest counter-arguments (and why the gap holds)

- *"Just write a better durable/LLM prompt."* No — durable's input is records → a persisted claim;
  a knowledge object's input is the **graph** → an abstraction. Different unit, different truth
  condition, different output. A looser prompt would hallucinate themes, the exact failure the
  honest framing forbids.
- *"Concepts are already entities."* As mentions, yes; as synthesis objects that link their
  instances and carry a revisable claim, no.
- *"Themes are book-specific — this violates generic-core."* The **operation** is generic (lift a
  graph into evidence-backed concepts + track their claim-state); only the **output** is
  domain-flavored — exactly like identity resolution. Generic representation, domain-specific
  validation.
- **The real risk:** laundering interpretation as system output. The knowledge-object layer must
  keep the evidence rule, propose/commit, and honest **abstention** (`not_yet_derived` until it can
  cite instances). That difficulty is *why this is research, not a quick pass* — and why it was
  right to omit Themes rather than fake them.

## Implications

- **Kimi's role flips.** It is no longer a third resolver witness. It becomes the **first validation
  corpus for a Knowledge Object layer**: do MoE / MLA / reasoning / sparse-routing synthesize
  generically the way Prejudice / marriage / class do? If yes, the operation is generic; if the
  synthesis needs per-domain scaffolding, that is the new architecture's real boundary.
- **`themes` tab, `ideas = 0`, and stateful-claims are all downstream of this one layer** — they
  stop being three loose ends and become one milestone.
- **v0.1 framing is unchanged and stays honest** ("a traceable knowledge space formed from the
  text") until the layer exists.

## The gap is found; the object is not

The review unified `ideas = 0` and stateful-claims into one "Knowledge Object." That was a step too
far. There are at least **three candidate objects**, and it is an open question whether they share a
representation:

| candidate | example | shape |
|-----------|---------|-------|
| **Theme**   | Marriage · Class · Pride (P&P)      | an abstraction organizing many scenes/relationships; often never stated as one span |
| **Concept** | MoE · MLA · the DSA→CSA→HCA lineage | a named technical object whose instances/claims/versions must be linked and traced |
| **State**   | Elizabeth → *current understanding* | an entity's interpretation, revised as evidence accrues over time |

A Theme is not a Concept is not a State. Declaring them one "Knowledge Object" *before* building each
is the same mistake as declaring an "Identity Layer" from one alias pair. The whole point of the
exploration is to find out — empirically — whether one representation covers all three, or whether
the review conflated three different things.

## Recommendation: exploration, not a layer

Do **not** design a schema or open M3.2. Run **three independent prototypes**, then ask the only
question that matters:

    Prototype 1  DeepSeek  → Concept   ✓ done — prototype-1-deepseek-concept.md
    Prototype 2  P&P       → Theme     ✓ done — prototype-2-pnp-theme.md
    Prototype 3  Elizabeth → State     ✓ done — prototype-3-elizabeth-state.md
                    │
                    ▼
         Is there a COMMON representation?

## Convergence result (after three probes) — candidate, not a declared layer

All three worlds reduced to the **same primitive**:

> a **scoped, evidenced, status-bearing claim** over semantic objects, positioned on an index
> (Concept: *version* · State: *chapter/time* · Theme: *none*), where relations and transitions are
> **committed** assertions each carrying a status (`SUPPORTED / CONTRADICTED / UNKNOWN /
> NOT_EVALUATED`).

And in all three the failure mode was **identical** — an *organizing narrative beyond the evidence*,
which must be abstained:

    Concept → derivation lineage      (MLA → DSA → CSA → HCA)
    Theme   → thematic argument       (the novel critiques the marriage market)
    State   → single inner arc        (prejudice → love)

So the candidate the review reached for — "Concept / Theme / State are three kinds of node" — is
**not** what the evidence supports. The better-supported statement is the tightened one from
Prototype 1, now confirmed twice more:

> **Knowledge Object = a maintained set of scoped claims and relations over semantic objects.**
> The three "types" are just different *index/scope profiles* over one claim primitive — claim
> maintenance, not object type, is the common substrate.

### Fourth world (falsification) — Kimi did not break it

Kimi was run next (`prototype-4-kimi-falsification.md`) as an **untouched** corpus, to try to break
the primitive rather than confirm it. It held, and strengthened the claim:

- It **exercised the previously-untested `SUPPORTED` derivation** — `MuonClip improves upon Muon` is
  *explicitly stated*, the mirror of DeepSeek's *unstated* attention lineage (which was `ABSTAINED`).
  Same relation type, opposite status, driven by evidence. The status enum is real, not theater.
- Version-departure and over-general comparative claims fit the same two-layer, status-bearing shape.
- The one new thing Kimi added is a **boundary, not a counterexample:** `MLA` appears in *both* the
  DeepSeek and Kimi corpora, and the within-corpus primitive says nothing about whether they are the
  same object. **Cross-corpus concept identity** is a layer *above* the primitive — the knowledge-
  object analogue of entity resolution, lifted across corpora. Recorded as the next open question.

Four independent worlds now converge on the scoped-claim substrate.

### What this does and does NOT establish

- **Does:** four independent probes (DeepSeek Concept, P&P Theme, Elizabeth State, Kimi
  optimizer/claims) converge on one *representation* — the research question answered in the
  affirmative **at the representation level.**
- **Does NOT:** (1) these were **manual** representation-discovery probes, not system runs — no
  automated formation exists; (2) no **zero-fabrication measurement at scale** — abstention was done
  by hand; a system must do it and be graded; (3) the **cross-corpus identity boundary** Kimi
  surfaced is unbuilt; (4) a **representation surviving four worlds is a strong working hypothesis,
  not a validated layer.** It earns "layer" only when a *system* forms it honestly and is graded.

### The decision this leaves for the PI

The scoped-claim / claim-maintenance substrate is now a working hypothesis validated across four
worlds at the representation level. The open fork is no longer "which corpus" but **build vs. keep
exploring**: (a) a first minimal **build + zero-fabrication measurement** (a system forms scoped
claims on one corpus, graded against the hand-probe), or (b) probe the newly-surfaced **cross-corpus
concept-identity** boundary before any build. Naming the substrate a layer / opening "M3.2" is earned
by (a), not by the probes.

Each prototype held to the resolver's bar: strict evidence coverage, propose/commit, honest
abstention, **zero fabrication**.

**First prototype: DeepSeek → Concept — chosen for falsifiability, not ease.** Themes (Pride, Class,
Marriage) are *too easy to hallucinate* — an LLM will happily emit them whether or not a real object
formed, so they cannot falsify anything. A concept like the attention-compression lineage
`MLA → DSA → CSA → HCA` cannot be faked: if the Knowledge Object did not genuinely form from the
evidence, it shows immediately. DeepSeek is the *harder*, more *research-honest* first probe.

**Kimi's role** is deferred accordingly: it is neither a resolver witness nor a given for this
layer — it becomes a later cross-domain check on whatever representation (if any) the three
prototypes converge on.
