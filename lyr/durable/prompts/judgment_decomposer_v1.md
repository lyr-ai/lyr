You split semantic records into independent TOPICS for long-term ("durable")
knowledge maintenance. Each topic is one coherent subject that would become at most
one durable memory — a lesson, decision, preference, pattern, or fact.

Rules:
  - Assign EVERY record to exactly one topic group.
  - Put records about the same subject, event, decision, or recurring pattern in the
    same group; separate genuinely different subjects.
  - Records that merely repeat or re-describe one event belong to the same group.
  - Prefer a small number of meaningful topics over many tiny ones.

Semantic records:
<<SEMANTIC>>

Return ONLY a JSON array. Each element is a JSON object:
  {"topic": "short label", "records": [record indices in this topic]}

Every index from 0 to N-1 must appear in exactly one group.
JSON array: