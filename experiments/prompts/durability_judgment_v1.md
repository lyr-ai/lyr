You are studying how long-term ("durable") knowledge forms from accumulated
observations. Reason openly and honestly — we care about *how you think* at least
as much as your final answer.

## What "durable" means here

Durable knowledge is a claim worth keeping after many experiences: a lesson, a
decision, a stable preference, a persistent pattern, a lasting fact about someone
or something.

Three things are easy to get wrong, so hold them explicitly:

1. **Recurrence is not durability.** Something can repeat and still be trivial
   noise; something can happen once and be durable (a major decision, an
   irreversible event).
2. **Evidence independence matters.** Several passages describing the *same* event
   are **one** piece of evidence, not many. Do not mistake repetition of a
   description for accumulation of support.
3. **Scope is part of the claim.** If evidence only holds in one phase, place,
   role, or relationship — say so in the statement. Prefer a qualified truth over
   an overreaching one.

## Inputs

Existing durable memories (may be empty):

<<EXISTING_DURABLE>>

New semantic records (each: index, kind, statement, and the source passage it came
from — same source ≈ possibly the same underlying observation):

<<SEMANTIC_RECORDS>>

## Your task

Work through these steps out loud, then give a structured summary.

### Step 1 — Evidence grouping

Partition the records into groups by *underlying observation*. Which records
describe the **same** event/fact (one piece of evidence)? Which are **independent**?
For each group, list the record indices and say why they are (or aren't) the same
evidence.

### Step 2 — Durability judgment

For each candidate piece of durable knowledge you see, give:

- **statement** — the durable claim, scoped/qualified as the evidence warrants
- **kind** — your own word for what sort of knowledge this is (lesson, decision,
  preference, pattern, fact, …) — do not force it into a fixed list
- **supporting evidence** — record indices, counting *independent* evidence groups
- **why durable** — why it is worth keeping long-term
- **counter-evidence / scope limits / contradictions** — actively look for these;
  what would narrow, qualify, or refute the claim?
- **confidence (0–1)** — and what would raise or lower it
- **proposed operation** — ADD / UPDATE / MERGE / NO_OP, relative to the existing
  durable memories above

### Step 3 — What is NOT durable

List records that recur or look salient but should **not** become durable, and say
why (trivial noise, a single unremarkable event, insufficient or non-independent
support, …). Being explicit about refusals is as important as the additions.

### Step 4 — Structured summary

End with a single JSON object of this shape:

{
  "evidence_groups": [
    {"records": [0, 3], "same_observation": true, "note": "..."}
  ],
  "proposals": [
    {"operation": "ADD", "statement": "...", "kind": "...",
     "evidence": [0, 3], "why": "...", "counter_evidence": "...",
     "confidence": 0.0}
  ],
  "no_ops": [
    {"records": [5], "reason": "..."}
  ]
}

If the evidence genuinely conflicts, prefer a qualified statement or preserving two
competing durable claims over inventing a false synthesis. If you are unsure, say
so and choose NO_OP rather than an unsupported strong claim.
