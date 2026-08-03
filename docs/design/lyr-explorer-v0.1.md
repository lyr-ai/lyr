# LYR Explorer v0.1 — Living Knowledge Formation

**Status:** Proposed → **building.**

**The one honesty checkpoint (Week 1).** The whole demo lives or dies on this: the "knowledge
growing" counts (§7: *18 entities, 7 events, 12 relationships, 4 durable ideas, 2 unresolved
conflicts*) and every object in §8–§12 must be **real outputs of a real extraction over the real
text of *Pride and Prejudice*** — never illustrative, never hand-authored. Week 1 produces
`knowledge.json` from an actual run; the frontend (Weeks 2–5) visualizes **only what that file
actually contains.** If the pipeline does not produce something, the explorer does not show it.

**Scope reality to verify in Week 1.** The existing LYR durable layer produces *durable judgments*
(claims/lessons with evidence + verdicts), not a character graph with temporal relationships and
belief revision. The rich views here (entity timelines, evolving relationships, unresolved
conflicts) are therefore **largely new extraction capability** — grounded in a real LLM pass over
the chapters, but not a free byproduct of the current layers. Week 1's real output is what tells us
which of §8–§12 are honestly buildable now and which are future work. See
[`../research-status.md`](../research-status.md).

---

## 1. Purpose

Build the first interactive demonstration of LYR. Not chat, not retrieval, not the identification
protocol directly — **knowledge forming, stabilizing, and evolving in real time.** First (and only)
validation domain: **Pride and Prejudice**. The product stays domain-agnostic; the book is only the
first demonstration.

## 2. Success metric

A first-time visitor understands the difference from RAG within two minutes and thinks *"I've never
seen knowledge represented like this,"* not *"interesting chatbot."*

## 3. Non-goals (v0.1)

No arbitrary uploads · no PDF/YouTube/GitHub · one book only · no accounts · no editing ·
no collaboration · no live identification protocol · no Cognitive layer. All future work.

## 4. Validation domain

**Pride and Prejudice** — public domain, recognizable, strong character evolution, evolving
relationships, rich evidence, reproducible.

## 5. User journey

`Landing → Open Demo → Knowledge grows → Explore → Ask → Return to knowledge.` Conversation never
becomes the center; knowledge does.

## 6. Homepage

Hero: *RAG retrieves documents. LYR builds knowledge.* + subtitle + **[ Explore Demo ]**.
Immediately below: **Knowledge Formation**, not a chat box.

## 7. Core experience

The first screen is **Knowledge Growing**, not chat:

```
Processing Chapter 1…
  ✓ 18 entities   ✓ 7 events   ✓ 12 relationships   ✓ 4 durable ideas   ⚠ 2 unresolved conflicts
```

*(Counts are real extraction outputs — placeholders until Week 1 runs.)*

## 8. Explorer layout — three columns

- **Left — Source:** chapters · timeline · original text.
- **Middle — Living Knowledge:** tabs People · Events · Relationships · Ideas · Timeline · Durable
  Knowledge.
- **Right — Inspector:** selected object · evidence · history · supporting passages · related
  knowledge.

## 9. Living Knowledge view (the heart)

Knowledge as persistent objects. E.g. *Elizabeth Bennet* → current understanding · relationships ·
history · supporting evidence · alternative interpretations · remaining uncertainty. Every object
explorable.

## 10. Timeline

Every object evolves. E.g. *Darcy*: Ch3 first impression → Ch8 misunderstood → Ch20 contradictory
evidence → Ch35 belief revision → Ch60 stable. **Knowledge changes, not answers.**

## 11. Relationships

Temporal, evidenced edges. E.g. *Elizabeth → Darcy*: initial prejudice → conflict → evidence
accumulates → trust. Every edge has evidence.

## 12. Durable knowledge

Not chapter summaries — long-term ideas (social status, marriage, pride, prejudice, family, duty),
each with evidence · history · supporting events · people involved.

## 13. Evidence

Every object links back to source; clicking highlights the original paragraphs. Users never wonder
*"where did this come from?"*

## 14. Conversation (optional)

Questions query the knowledge space: `Question → Knowledge → Evidence → Answer → Knowledge remains`,
never `Question → Document → Answer`.

## 15. Example questions

Why did Elizabeth change her opinion of Darcy? How did Darcy's behavior evolve? What evidence
supports this relationship? What alternative interpretation exists? Which ideas became durable?

## 16. Backend pipeline (offline)

`Book → Chunk → Source Layer → Semantic Layer → Durable Layer → knowledge.json → Explorer →
Conversation.` Everything before Explorer is offline; v0.1 has **no live ingestion**.

## 17. Frontend architecture

React. A single **Knowledge Store** feeds all Explorer components (People, Events, Relationships,
Timeline, Inspector, Conversation). Every component consumes the same knowledge model.

## 18. Visual language

Avoid force-directed-graph-everywhere. Prefer timelines, cards, progressive disclosure, relationship
transitions, evidence expansion, knowledge evolution. Communicate **growth, not complexity.**

## 19. Milestones

- **Week 1** — backend export → `knowledge.json` (the honesty checkpoint).
- **Week 2** — People · Relationships · Timeline.
- **Week 3** — Inspector · Evidence.
- **Week 4** — Conversation.
- **Week 5** — polish · demo · launch.

## 20. Future directions

After the interaction model is proven, swap the source (Paper → YouTube → GitHub → Forum) **without
changing the explorer.** Applications validate the representation; they never redefine it.

---

## Naming (UI rule)

Never say **"Book Explorer."** The product is the **Living Knowledge Explorer**; underneath, small:
**Demo source: Pride and Prejudice.** People should not remember a book app — they should remember
the first system where *knowledge itself is the product.*

> **Product principle: questions disappear, knowledge remains. That is the difference between RAG
> and LYR.**
