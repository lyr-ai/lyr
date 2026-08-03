# Design Note: LYR Explorer — Product Positioning

**Status:** Proposal — **not adopted.** This repositions the product away from the current live
site (auditable identification — *"does the explanation refer to the world?"*) toward a
RAG-alternative / knowledge-building framing (*"RAG retrieves, LYR builds knowledge"*). Two things
are unresolved before adoption, recorded honestly here so the repo does not imply this is decided:

1. **Relationship to the identification framing.** These are two different front doors. The
   strongest resolution may *nest* them (their own positioning statement below already does:
   *"knowledge that becomes harder to fool over time"*), but the homepage's first screen must pick
   an emphasis.
2. **Evidence asymmetry.** The knowledge-*organization* claims here (a "living knowledge space,"
   relationships, knowledge "forming in real time") rest on the durable→cognitive line, where the
   project has a **documented negative result** ([`M3.2-A`](../../experiments/navigation/EXPERIMENT-M3.2-A.md):
   provenance could not organize; 0 shared-semantic links) and the Cognitive layer is **unbuilt**.
   The identification protocol is by contrast the frozen, falsifier-tested, independently
   reproduced result. Leading with the less-validated line would cut against the project's own
   discipline (*real, validated demos only*). See [`../research-status.md`](../research-status.md).

What *is* validated in this line: durable judgment **formation with provenance and verification**
(the `durability-v1` benchmark, the Judgment Explorer over real records). What is **not**:
organization into a navigable knowledge space (M3.2-A failed) and the Cognitive layer (not built).
A "knowledge forming in real time" demo must be backed by a **real** run, and must not show the
organization output as working until it is.

---

*(Proposal text as authored, preserved verbatim below.)*

---

# Problem

Most AI systems today treat external knowledge as something to **retrieve**:
`Source → Chunks → Retrieval → LLM → Answer`. The retrieved information disappears once the
conversation ends. The system answers questions; it does **not** become more knowledgeable.

# Observation

People do not learn this way. Humans gradually build concepts, relationships, long-term beliefs,
evolving understanding, stable knowledge. Questions happen **after** knowledge exists.

# Core Thesis

> **RAG retrieves information. LYR builds knowledge.**

The goal of LYR is not better retrieval. It is to continuously transform evolving information into
living knowledge.

# Product Vision

The product is not a Book / YouTube / GitHub Explorer — those are validation domains. The product
is a **Knowledge Explorer**. Users connect any long-form knowledge source (book, paper, transcript,
repo, forum thread, journal, medical record); the same pipeline operates on all of them.

# User Flow

`Connect Source → Knowledge Growing → Explore Knowledge → Ask Questions → Knowledge Continues To
Evolve`. The conversation is built **on top of** knowledge; it is not the mechanism that creates it.

# Difference from RAG

- **RAG:** `Source → Retrieve → Answer → Done`. Knowledge does not persist; the next question
  starts over.
- **LYR:** `Source → Semantic → Durable → Living Knowledge Space → Questions → Knowledge Updates`.
  Knowledge exists independently of any particular question.

# Product Principle

Questions come **after** knowledge, not before. The system improves its understanding regardless of
whether a user asks anything.

# Home Page

The landing page should immediately answer *"Why is this not another RAG?"* before explaining what
users can upload.

**Suggested hero:** *RAG retrieves documents. LYR builds knowledge.*
**Subtitle:** *Turn books, papers, videos, forums, and repositories into living knowledge that
continues to evolve.*

# Product Experience

The first thing users see is **knowledge growing**, not a chat box. E.g. `Chapter 1 processed → 14
people discovered → 9 relationships proposed → 6 durable ideas emerging → 3 unresolved conflicts`.
*(Any such figures must come from a real run — see the status note above.)*

# Conversation

Conversation is not the product; it is one way to explore existing knowledge. The workflow is
`Question → Knowledge → Evidence → Answer → Knowledge remains`.

# Knowledge Representation

Expose knowledge, not documents: people, events, relationships, durable knowledge, claims,
supporting evidence, alternative interpretations, remaining uncertainty. Every object links back to
source evidence.

# Product Philosophy

Never appear to answer directly from documents; answer from continuously maintained knowledge. The
visible interaction is always `Source → Knowledge → Answer`, never `Source → Answer`.

# Validation Domains

Books first; then research papers, YouTube, git repos, forums, diaries, medical records, parenting
logs. Demonstrations of the same representation — never the design center.

# Product Goal

After two minutes, users should say *"I've never seen knowledge represented like this before,"* not
*"this is another Chat-with-PDF."*

# Positioning Statement

> **RAG helps AI answer your next question. LYR helps AI build knowledge that becomes harder to fool
> over time.**

# Design Principles

1. Knowledge first; conversation is built on top of knowledge.
2. Knowledge persists beyond individual conversations.
3. Every source follows the same pipeline.
4. Applications validate the representation; they never redefine it.
5. The product demonstrates living knowledge, not better retrieval.
6. Users should see knowledge forming in real time.
7. The first impression must communicate that LYR is fundamentally different from RAG, without
   requiring users to read the paper.
