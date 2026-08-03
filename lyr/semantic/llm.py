"""LLMExtractor — protocol-driven semantic extraction via any ``LLMClient``.

The default, higher-quality extractor. It presents the Source Records to the
model as a numbered list, asks for structured entities / events / relationships
in JSON, and maps each claim's cited record numbers back to real record ids so
provenance stays exact.

The client is injected, so the same extractor works against Anthropic, a fake,
or anything else satisfying ``LLMClient`` — LYR never hard-codes a provider.
"""

from __future__ import annotations

import json
import re
from typing import Any, Iterable

from ..llm.base import LLMClient
from ..models import SourceRecord
from .base import SEMANTIC_KINDS, ExtractedNode, ExtractionResult

_PROMPT = """\
You extract structured knowledge from source records. Below are numbered records.

Return ONLY a JSON array. Each element is an object with:
  - "kind": one of "entity", "event", "relationship"
  - "label": a short human-readable name (entity) or summary (event/relationship)
  - "evidence": a list of the record numbers (integers) that support this item
  - "attributes": an object with kind-specific fields:
       entity       -> {{"entity_type": "person|org|concept|system|place|..."}}
       event        -> {{"when": "<time phrase or null>", "participants": [..]}}
       relationship -> {{"subject": "..", "predicate": "..", "object": ".."}}

Rules:
  - Every item MUST cite at least one record number in "evidence".
  - Do not invent facts that are not supported by the records.
  - Prefer a few high-quality items over many noisy ones.
  - SOURCE FIDELITY: write each "label" (and a relationship's "subject"/"object") using the
    name EXACTLY as it appears in the cited source passage — same script and same language.
    Do NOT translate, transliterate, simplify, traditionalize, expand, or invent a canonical
    name. If the passage says 寶玉, output 寶玉 (never 宝玉 or "Baoyu"). Deciding whether two
    differently-written mentions are the same entity is done downstream, not here.

Records:
{records}

JSON array:"""


def _render(records: list[SourceRecord]) -> str:
    return "\n".join(f"[{i}] {r.content}" for i, r in enumerate(records))


def _parse_json_array(text: str) -> list[dict[str, Any]]:
    """Best-effort extraction of a JSON array from a model completion.

    Tolerates ```json fences and leading/trailing prose by locating the outer
    brackets. Returns [] on anything unparseable rather than raising — a bad
    completion should degrade to "no claims", not crash the pipeline.
    """
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1 or end < start:
        return []
    try:
        data = json.loads(text[start : end + 1])
    except (json.JSONDecodeError, ValueError):
        return []
    return data if isinstance(data, list) else []


class LLMExtractor:
    def __init__(self, client: LLMClient) -> None:
        self._client = client

    def extract(self, records: Iterable[SourceRecord]) -> ExtractionResult:
        record_list = list(records)
        if not record_list:
            return []

        completion = self._client.complete(_PROMPT.format(records=_render(record_list)))
        raw = _parse_json_array(completion)

        out: ExtractionResult = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            kind = item.get("kind")
            label = item.get("label")
            if kind not in SEMANTIC_KINDS or not isinstance(label, str) or not label.strip():
                continue

            # Map cited record indices back to ids; drop out-of-range indices.
            evidence: list[str] = []
            for idx in item.get("evidence", []) or []:
                if isinstance(idx, int) and 0 <= idx < len(record_list):
                    evidence.append(record_list[idx].id)
            if not evidence:
                # No supporting record → violates the evidence rule; skip it.
                continue

            attributes = item.get("attributes")
            out.append(
                ExtractedNode(
                    kind=kind,
                    label=label.strip(),
                    evidence=evidence,
                    attributes=attributes if isinstance(attributes, dict) else {},
                )
            )
        return out
