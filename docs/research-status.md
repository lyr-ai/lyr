# Research Status — Auditable Identification Protocol

**State: Research complete. Awaiting external evidence.**

This is not "paper accepted." It is a statement about *where the uncertainty now lives*: no
longer in the internal soundness or the executability of the protocol, but in whether someone
outside this research process can use it. The paper is no longer the bottleneck — external use
is.

## The three lines (current structure)

The project is now three mutually supporting, mutually non-interfering lines:

- **① Theory — frozen.** Answers *what is auditable identification?* Reopens only on a real-world
  witness (the three triggers below).
- **② Method — the paper.** Answers *how does someone else execute the protocol?* Open to
  reader-clarity / positioning / reproducibility edits until reviewers and a human execution
  respond.
- **③ Applications — continuous.** Answers *is the protocol useful in the real world?* Accumulates
  real cases; see `applications/`.

They form a feedback loop whose one invariant is that **only the real world may reopen Theory**:

```
Theory (frozen)
    │
    ▼
Method (paper)
    │
    ▼
Applications (real cases)
    │
    ▼
Real contradiction the protocol cannot express?
    │
 ┌──┴──┐
 │ No  │ → continue applications
 │ Yes │ → Theory reopens (trigger #3), on a NEW branch from `research-complete`
 └─────┘
```

An author may improve the Method line and extend the Applications line at will. Neither may reach
back and edit Theory. That privilege belongs to the world.

## The arc (four phases, now complete)

- **I — Discovery.** *What is cognition? What is the right ontology?* The object kept changing.
- **II — Stabilization.** The falsifier program. Objects entered only with witnesses; the
  protocol became internally coherent.
- **III — Operationalization.** Minimal formalism, worked examples, independent execution. The
  object became executable by strangers.
- **IV — Communication.** Narrative freeze, positioning, reviewer classification. The object
  stopped changing; only the paper changed.

Transition complete. The paper matured by adding **evidence, not layers**: nearly every concept
in it now has a corresponding experiment, falsifier, reproduction, or protocol run.

## Frozen artifacts

- `docs/minimal-formalism-identifiability.md` — the note: definitions, witness schema, two
  worked examples, three structural falsifiers.
- `docs/reproduction-experiment-1.md` — three rounds / nine independent executions; Phase-1
  gate met (exact reproduction, empty invention list).
- `docs/paper-narrative.md` — the locked narrative (what is in the paper, what stays out).
- `docs/paper-auditable-identification.md` — the paper draft. **Frozen at the theory level.**

## Re-open triggers — the ONLY reasons to make a conceptual change

The theory is frozen. A conceptual commit to the paper is warranted **only** if:

1. **Human reproduction** uncovers a genuine ambiguity (LLM executors are a proxy; a human is
   the stronger test).
2. **A reviewer** finds a concrete counterexample — a real mathematical error, *not* a
   classification objection (those are answered by placement, see paper §7).
3. **A real application** forces a contradiction the protocol cannot express.

Anything else is a *new paper* (see `docs/applications.md`), not an edit to this one.

## The frozen snapshot is immutable

The `research-complete` tag does not move. If a re-open trigger fires, start a **new branch from
the tag** — do not amend history. The point is to preserve an honest snapshot of what the theory
looked like *before it met the world*. Rewriting history until it appears the authors "always
knew" is the exact failure the witness discipline exists to prevent; preserving the frozen state
is the final act of that discipline.

The three transitions the project crossed, for the record:

- **Discovery** — "Can I think of a new object?" (objects were easy to invent)
- **Research** — "Can I justify introducing this object?" (every object needed a witness)
- **Science** — "Can someone else reproduce the consequences of this object?" (the protocol
  became executable by others without author intervention)

The tag marks the crossing of the third. It is a fact about a moment, and moments are not edited.

## The research discipline (not a paper contribution — recorded because it is durable)

The rules that produced the object, worth keeping independent of it:

- Don't add an object without a witness.
- Don't claim a limitation without a witness.
- Stop arguing once arguments stop generating witnesses.
- Separate discovery notebooks from paper narratives (how you found it ≠ what it is).
- Freeze theory before optimizing communication.

These are methodological rules for *doing* research, not the paper's contribution. They are
recorded here because they outlast this paper.
