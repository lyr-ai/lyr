# LYR Explorer Design — Beyond RAG

**Status:** Proposed — **the long-term product vision (north star).**

This describes the *destination*, not today's validated capability. Separating the two keeps the
repo honest without constraining the vision:

- **Validated now:** durable knowledge **formation + provenance + verification** (the
  `durability-v1` benchmark; the Judgment Explorer over real records) — and, on the theory side,
  auditable **identification** (frozen, reproduced), which is the "harder to fool" property this
  vision names.
- **Still to build:** the **living knowledge space** — organization, relationships, the navigable
  structure, the Cognitive layer. Current evidence for the organization step is the *negative*
  result [`M3.2-A`](../../experiments/navigation/EXPERIMENT-M3.2-A.md); this is a build target, not
  a shipped capability. Tracked in [`../research-status.md`](../research-status.md).
- **Guardrail (from the project's discipline):** when the "knowledge forming" experience (§7, §12)
  is built, it must run on a **real** source — no mocked entity/relationship counts.

---

## 1. Motivation

Most AI knowledge systems are retrieval systems: `Source → Chunking → Retrieval → LLM → Answer`.
This is **question-driven** — knowledge is reconstructed for every query and disappears when the
conversation ends. The system becomes no smarter than before.

LYR takes the opposite approach: instead of retrieving information to answer questions, it
continuously transforms information into a persistent, evolving knowledge space. Questions become
one way of interacting with that knowledge, not the mechanism that creates it.

## 2. Core Thesis

> **RAG retrieves information. LYR builds knowledge.**

The goal is not a better retrieval engine — it is a system that continuously forms, maintains, and
evolves knowledge over time. Knowledge exists independently of any particular question.

## 3. Product Vision

LYR Explorer is **not** a Book / Paper / GitHub / YouTube Explorer — those are validation domains.
The product is **a Living Knowledge Explorer**: users connect a knowledge source, and LYR
continuously transforms it into an explorable knowledge space.

## 4. Supported Knowledge Sources

Eventually any long-form source — books, research papers, YouTube, podcasts, git repos,
documentation, community forums, personal journals, medical histories. Every source enters the same
pipeline; the representation never changes.

## 5. User Journey

Not `Upload PDF → Ask Question → Answer`, but:

```
Connect Source → Knowledge Begins Growing → Explore Knowledge → Ask Questions → Knowledge Continues To Evolve
```

The conversation happens **after** knowledge exists.

## 6. Product Architecture

```
Source → Source Layer → Semantic Layer → Durable Layer → Living Knowledge Space → Conversation
```

Conversation is built **on top of** knowledge; it never replaces it.

## 7. Knowledge Formation

Users should immediately see knowledge forming — not a spinner, not a chat box. E.g.:

```
Chapter 1 processed → 14 people discovered → 9 relationships identified → 6 durable ideas emerging → 3 unresolved conflicts
```

*(Real run only — see the guardrail in the status header.)*

## 8. Knowledge Explorer

Expose knowledge directly: People · Events · Relationships · Timeline · Durable Knowledge · Claims ·
Supporting Evidence · Alternative Interpretations · Remaining Uncertainty. Every object stays fully
traceable back to source evidence.

## 9. Conversation

One interaction mode, not the product. Not `Question → Answer`, but:

```
Question → Knowledge → Evidence → Answer → Knowledge Persists
```

The answer never becomes the primary artifact — knowledge does.

## 10. Difference from RAG

- **RAG:** `Source → Retrieve → Answer → Finished`. Every question starts over.
- **LYR:** `Source → Semantic → Durable → Living Knowledge → Conversation → Knowledge Updates`.
  Knowledge continues to evolve after every interaction.

## 11. First Impression

The homepage answers one question immediately — *"Why is this fundamentally different from RAG?"* —
before asking users to upload anything.

**Hero:** *RAG retrieves documents. LYR builds knowledge.*
**Subtitle:** *Transform books, papers, videos, repositories, and communities into living knowledge
that continuously evolves.*

## 12. Visual Principle

The first visual is **knowledge growing** — not conversation, retrieval, or search. Users watch
entities appear, relationships connect, events accumulate, durable knowledge emerge, and conflicts
remain unresolved until evidence arrives. The visual system communicates that knowledge is alive.

## 13. Product Philosophy

Never answer directly from documents; always answer from maintained knowledge: `Source → Knowledge
→ Answer`, never `Source → Answer`.

## 14. Applications

Books first; then research papers, YouTube, git repos, forums, diaries, medical records, parenting
logs. Applications validate the representation; they never redefine it.

## 15. Product Positioning

After two minutes users should say *"I've never seen knowledge represented like this before,"* not
*"this is another Chat-with-PDF."*

## 16. Design Principles

1. Knowledge first.
2. Conversation follows knowledge.
3. Knowledge survives beyond individual conversations.
4. Every source follows the same representation.
5. Applications validate the representation.
6. Knowledge formation should be visible.
7. Every knowledge object remains traceable to evidence.
8. The product communicates its difference from RAG before users ask their first question.

## 17. Long-term Vision

Today's AI systems retrieve information; tomorrow's will maintain living knowledge. LYR Explorer is
designed to make that knowledge visible — not a better retrieval system, a continuously evolving
knowledge system.

---

> **RAG helps AI answer your next question.**
> **LYR helps AI build knowledge that survives after the question is over** — and that becomes
> harder to fool over time.
