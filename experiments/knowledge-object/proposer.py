"""LLM proposer — the generative half of the proposer-behind-verifier experiment.

Deliberately encouraged to OVER-propose (state the plausible, not only the certain) so the
experiment can measure how much narrative it invents and how much the verifier stops. It emits
free-form (subject, predicate, object) candidates; the deterministic verifier grades each.

Runs against any `LLMClient` (lyr.llm.openai / anthropic with a key; FakeClient for a dry run).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from grounding import Passage

PROMPT = """\
You are proposing candidate knowledge for a knowledge base, using ONLY the evidence passages below.
Propose relations between named things as (subject, predicate, object). Propose BOTH what is clearly
stated AND what seems plausible given the passages — each candidate will be verified against the
evidence separately, so do not self-censor plausible-but-uncertain relations.

Return ONLY a JSON array; each element:
  {{"subject": "..", "predicate": "..", "object": "..", "scope": "..", "rationale": ".."}}

Evidence passages:
{passages}

JSON array:"""


@dataclass
class Proposed:
    subject: str
    predicate: str
    object: str
    scope: str = ""
    rationale: str = ""


def _parse(text: str) -> list[Proposed]:
    s, e = text.find("["), text.rfind("]")
    if s == -1 or e == -1:
        return []
    try:
        arr = json.loads(text[s:e + 1])
    except (json.JSONDecodeError, ValueError):
        return []
    out = []
    for it in arr:
        if isinstance(it, dict) and it.get("subject") and it.get("predicate") and it.get("object"):
            out.append(Proposed(str(it["subject"]), str(it["predicate"]), str(it["object"]),
                                str(it.get("scope", "")), str(it.get("rationale", ""))))
    return out


def propose(client, passages: list[Passage]) -> list[Proposed]:
    rendered = "\n".join(f"[{p.id}] {p.text}" for p in passages)
    return _parse(client.complete(PROMPT.format(passages=rendered)))
