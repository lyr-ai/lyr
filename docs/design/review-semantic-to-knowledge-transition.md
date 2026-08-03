# Design Review: the Semantic → Knowledge → Durable transition

**Status:** review / theory, frozen for a charter decision. Not being built. Triggered by a
*convergence signal*, not a new witness — the first time the backend work looks like optimization
rather than architecture discovery.

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

## Recommendation

The charter question — *is the next architecture another Semantic refinement, or a new layer?* — is
answered by the code: **a Knowledge Object layer** (abstraction + state), distinct from Semantic
(mentions → entities) and Durable (records → memory).

Do **not** build yet. Confirm the charter, then the first experiment is a **single-case** knowledge-
object formation (P&P themes *or* DeepSeek concept-synthesis) held to the same bar the resolver
fixes were: strict evidence coverage, propose/commit, honest abstention, zero fabrication, fixtures.
Kimi is then the second witness for **this** layer — not the resolver.

If, instead, the charter review concludes there is no such gap (the Timeline+Evidence experience is
already "something new"), then Kimi resumes as the next resolver witness. This review's claim is
that the code says otherwise.
