# Capability gap: stateful semantic claims / evolving interpretations

**Status:** recorded, not being solved now. The **first product→core capability gap exposed by the
Explorer** — and closer to the product center than `themes = 0`, because the homepage sells
*"knowledge evolves."*

## What the real run exposed

Running the full novel through the pipeline, the "Elizabeth Bennet" entity reached **36 versions** —
but on inspection **every version differs only in accumulated evidence**:

```
label changed across 36 versions:   0   (1 distinct label)
attributes changed:                 0   ({entity_type: person} throughout)
per-version change:                 evidence 2 → 4 → 7 → … → 128 passages
```

So the version chain is an **evidence-accumulation log, not an understanding arc.** The semantic
layer records *that* an entity keeps appearing with more support — not *how the interpretation of it
changes*. "Elizabeth: prejudiced → reconsidering → in love" is **not** in the data.

## What the current Semantic Layer can and cannot answer

Can: *Who appeared? What happened? Who relates to whom? Where is the evidence?*
Cannot: *What changed in our understanding of this entity over time?*

## The gap

A **stateful semantic claim** — an entity/topic carries an *interpretation/state* that is proposed
per new evidence and revised against the prior state. That is what would make "living knowledge"
literally true. It is generic (not book-specific): the same shape applies to a person in a git
history, a hypothesis in a paper, an incident's root cause over time.

## Consequences for v0.1 (honest framing)

- The Explorer view is **"Story / Evidence Timeline,"** not "Evolution." Each step is an
  **observation** (a relationship/event, chapter-stamped, with evidence) — never a psychological
  conclusion (no "prejudice", "belief revision", "reconsideration", "love", "current understanding",
  "character arc") unless the backend actually extracts and maintains such state.
- v0.1 is described as **"A traceable knowledge space formed from the text,"** not "living knowledge
  that evolves." The version count is shown honestly as *evidence accumulation*, not as changes.

## The future backend milestone (generic, when a real witness demands it)

Not book-specific character-arc extraction — a **generic evolving-claim/state formation**:

```
chapter evidence
    → state / claim proposal
    → compare with prior state
    → ADD / UPDATE / CONTRADICT / NO_OP
    → state history
```

This mirrors the durable layer's discipline (propose vs. commit) but for *interpretation state*,
which is a distinct operation from durable retention and must not be faked by loosening the
durability prompt. **Trigger to build it:** the frontend shows the Timeline + Evidence experience
still reads like "a knowledge graph with provenance" rather than something new — i.e. users need
evolving interpretation and the current layer cannot express it. Until then: recorded, not solved,
not hidden.
