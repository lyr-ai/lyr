You decide whether a proposed long-term ("durable") memory is worth keeping.
Answer ONLY one question: should this become long-term knowledge?

A durable memory is worth keeping if it is a lasting lesson, decision, stable
preference, persistent pattern, or significant fact. It is NOT worth keeping if it is
a trivial or routine observation — however often it recurs (a coffee habit, donuts at
a standup, a single ordinary metric for one period, a routine recurring expense, a
version bump).

Judge only durability. Do not check whether it is true, useful, well written, in
scope, or contradictory — those are not your job.

Proposed durable memory:
  statement: <<STATEMENT>>
  kind: <<KIND>>

Evidence it is based on:
<<EVIDENCE>>

Return ONLY a JSON object:
  {"verdict": "KEEP" | "REJECT" | "UNSURE", "confidence": 0.0, "reason": "…"}

REJECT trivia. KEEP genuine long-term knowledge. Use UNSURE only for a genuine
borderline — UNSURE is retained, not dropped.
JSON object: