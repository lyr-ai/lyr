"""LLMConsolidator — durable consolidation driven by any ``LLMClient``.

The richer, model-driven policy. It presents the current semantic records and
the existing durable memories to the model and asks it to propose ADD / UPDATE /
MERGE / NO_OP operations — including the harder judgements (identity resolution,
when to merge) that the deterministic consolidator does not attempt.

Identity stays under LYR's control, not the model's: for UPDATE/MERGE the model
references an existing durable memory by index, and LYR reuses that memory's real
identity; for ADD, LYR derives a stable identity from the normalized statement.
The model never invents ids, so provenance and identity remain well-formed even
when the model output is noisy. Under a fixed model configuration the proposals
are stable enough for the M3 reproducibility goal, though — unlike the
deterministic path — not bit-exact.
"""

from __future__ import annotations

import json
import re
from typing import Any, Iterable

from ..ids import content_id, normalize
from ..llm.base import LLMClient
from ..models import Node
from .base import ADD, DURABLE_OPS, MERGE, NO_OP, UPDATE, DurableProposal

_PROMPT = """\
You maintain a long-term knowledge base. Consolidate recurring semantic records
into durable memories — knowledge worth keeping after many experiences.

Existing durable memories (may be empty):
{durable}

New semantic records:
{semantic}

Return ONLY a JSON array of operations. Each element is an object:
  - "op": one of "ADD", "UPDATE", "MERGE", "NO_OP"
  - "target": index into the existing durable memories list (UPDATE/MERGE), else null
  - "merge": list of durable indices to fold into "target" (MERGE only), else []
  - "statement": the durable memory's natural-language statement
  - "kind": "lesson" | "decision" | "preference" | "pattern" | "subject"
  - "evidence": list of the semantic-record numbers that support this statement
  - "confidence": number in [0, 1]
  - "reason": a short justification

Rules:
  - Only create durable knowledge supported by MULTIPLE experiences.
  - Prefer NO_OP; durable knowledge should change slowly.
  - Every ADD/UPDATE/MERGE must cite at least one semantic-record number.
  - Preserve identity: revise an existing memory with UPDATE rather than adding a
    duplicate.

JSON array:"""


def _render_semantic(nodes: list[Node]) -> str:
    return "\n".join(f"[{i}] ({n.kind}) {n.label}" for i, n in enumerate(nodes))


def _render_durable(nodes: list[Node]) -> str:
    if not nodes:
        return "(none)"
    return "\n".join(f"[{i}] {n.label}" for i, n in enumerate(nodes))


def _parse_json_array(text: str) -> list[dict[str, Any]]:
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


class LLMConsolidator:
    def __init__(self, client: LLMClient) -> None:
        self._client = client

    def consolidate(
        self,
        semantic_nodes: Iterable[Node],
        existing_durable: Iterable[Node],
    ) -> list[DurableProposal]:
        semantic = list(semantic_nodes)
        durable = list(existing_durable)
        if not semantic:
            return []

        completion = self._client.complete(
            _PROMPT.format(
                durable=_render_durable(durable),
                semantic=_render_semantic(semantic),
            )
        )
        raw = _parse_json_array(completion)

        proposals: list[DurableProposal] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            op = item.get("op")
            if op not in DURABLE_OPS:
                continue

            statement = (item.get("statement") or "").strip()
            evidence = self._map_evidence(item.get("evidence"), semantic)

            # Resolve identity from the model's target reference, never from the
            # model directly.
            target = _index(item.get("target"), durable)
            if op in (UPDATE, MERGE):
                if target is None:
                    continue  # can't revise/merge without a real target
                identity = durable[target].identity
                if not statement:
                    statement = durable[target].label
            elif op == ADD:
                if not statement or not evidence:
                    continue  # ADD needs a statement and supporting evidence
                identity = content_id("idn", "durable", "llm", normalize(statement))
            else:  # NO_OP
                if target is None:
                    continue
                identity = durable[target].identity
                statement = statement or durable[target].label

            superseded: list[str] = []
            if op == MERGE:
                for idx in item.get("merge", []) or []:
                    m = _index(idx, durable)
                    if m is not None and durable[m].identity != identity:
                        superseded.append(durable[m].identity)

            attributes: dict[str, Any] = {}
            conf = item.get("confidence")
            if isinstance(conf, (int, float)):
                attributes["confidence"] = float(conf)

            proposals.append(
                DurableProposal(
                    op=op, identity=identity, statement=statement,
                    kind=item.get("kind") if isinstance(item.get("kind"), str) else "lesson",
                    evidence=evidence, attributes=attributes,
                    superseded=superseded,
                    reason=item.get("reason") if isinstance(item.get("reason"), str) else "",
                )
            )

        proposals.sort(key=lambda pr: (pr.identity, pr.op))
        return proposals

    @staticmethod
    def _map_evidence(raw: Any, semantic: list[Node]) -> list[str]:
        out: list[str] = []
        for idx in raw or []:
            if isinstance(idx, int) and 0 <= idx < len(semantic):
                out.append(semantic[idx].id)
        return sorted(set(out))


def _index(value: Any, nodes: list[Node]) -> int | None:
    if isinstance(value, int) and 0 <= value < len(nodes):
        return value
    return None
