You maintain a long-term ("durable") knowledge base. Given new semantic records and
the durable memories that may be related, choose the SINGLE best maintenance
operation to perform right now.

Durable knowledge is worth keeping after many experiences: a lesson, decision,
stable preference, persistent pattern, or lasting fact. Hold three things:
  - Recurrence is not durability. A single significant event can be durable; a
    repeated trivial observation is not.
  - Several records describing the SAME event are ONE piece of evidence, not many.
  - Scope is part of the claim — qualify it by time, phase, or context when the
    evidence only holds there.

Existing durable memories (may be empty):
<<DURABLE>>

New semantic records:
<<SEMANTIC>>

Return ONLY one JSON object of this shape:
{
  "operation": "ADD" | "UPDATE" | "MERGE" | "NO_OP",
  "statement": "the durable claim, scoped/qualified as the evidence warrants",
  "kind": "your own word: lesson | decision | preference | pattern | fact | ...",
  "evidence": [semantic-record indices that INDEPENDENTLY support the statement],
  "target": durable-memory index for UPDATE/MERGE, else null,
  "merge": [durable indices to fold into target for MERGE, else []],
  "evidence_groups": [{"records": [0, 3], "same_observation": true, "note": "..."}],
  "rationale": "why this operation, in one or two sentences",
  "counter_evidence": "contradictions or scope limits you found, or empty",
  "confidence": 0.0
}

Prefer NO_OP when no durable change is warranted. Choose exactly one operation.
JSON object: