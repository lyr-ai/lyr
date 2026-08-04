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

# NEUTRAL by design: the proposer must behave like an ordinary model building a knowledge base —
# NOT be primed with the verifier's rules. No mention of downstream verification, no "abstain when
# unsupported", no "lineage is risky", no "don't self-censor". Any such hint would bias the
# proposer-only baseline and hide the verifier's actual contribution. It is only asked to propose
# grounded candidates and cite the passages it relied on; the verifier alone decides admissibility.
PROMPT = """\
You are building a knowledge base from the evidence passages below. Propose candidate relations
between the named things in these passages, each as (subject, predicate, object). For each
candidate, list the ids of the passages it is based on.

Return ONLY a JSON array; each element:
  {{"subject": "..", "predicate": "..", "object": "..", "scope": "..", "evidence": ["<id>", ..], "rationale": ".."}}

Evidence passages:
{passages}

JSON array:"""


@dataclass
class Proposed:
    subject: str
    predicate: str
    object: str
    scope: str = ""
    evidence: list[str] = None  # passage ids the PROPOSER cites (its own claim of support)
    rationale: str = ""

    def __post_init__(self) -> None:
        if self.evidence is None:
            self.evidence = []


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
            ev = it.get("evidence") or []
            ev = [str(x) for x in ev] if isinstance(ev, list) else []
            out.append(Proposed(str(it["subject"]), str(it["predicate"]), str(it["object"]),
                                str(it.get("scope", "")), ev, str(it.get("rationale", ""))))
    return out


def render_prompt(passages: list[Passage]) -> str:
    return PROMPT.format(passages="\n".join(f"[{p.id}] {p.text}" for p in passages))


def propose(client, passages: list[Passage]) -> tuple[str, list[Proposed]]:
    """Returns (raw_completion, parsed) so the raw model output can be logged for audit."""
    raw = client.complete(render_prompt(passages))
    return raw, _parse(raw)
