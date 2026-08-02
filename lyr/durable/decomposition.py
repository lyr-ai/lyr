"""Judgment decomposition (M3.1-B.2) — split a semantic batch into topics.

M3.1-E found that one ``update()`` per multi-topic batch structurally drops all but
one durable candidate (failure F7). The fix is not a smarter builder but an explicit
stage *before* it: partition the semantic records into **judgment units**, each a
single coherent topic, and let the unchanged builder judge each one.

    Semantic Nodes → Decomposer → [Unit A, Unit B, …] → builder.update() per unit

Decomposition is *how many topics exist*; judgment is *what to do about one*. Keeping
them separate preserves one-record-one-decision (G1) and the builder API (G3).

Three strategies ship here:

- ``WholeBatchDecomposer`` — the whole batch is one unit. This is the M3.1-E control
  (identical to the pre-decomposition behavior).
- ``SingletonDecomposer`` — one unit per record; the over-decomposition floor.
- ``LLMDecomposer`` — a model partitions records into topics. The natural first fit
  for LYR's flat ``event`` fixtures, which have no relationship edges to cluster on.

Design: docs/design/M3.1-B.2-judgment-decomposition.md.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from importlib.resources import files
from typing import Iterable, Protocol

from ..llm.base import LLMClient
from ..models import Node

# One canonical, versioned decomposer prompt (mirrors the builder prompt, B.1 §4.7).
DECOMPOSER_PROMPT_VERSION = "judgment_decomposer_v1"
DECOMPOSER_PROMPT = (
    files("lyr.durable").joinpath("prompts").joinpath(f"{DECOMPOSER_PROMPT_VERSION}.md")
).read_text(encoding="utf-8")


@dataclass
class JudgmentUnit:
    """The minimal semantic context for one durable decision (one coherent topic)."""

    semantic_nodes: list[Node]
    candidate_durable_nodes: list[Node] = field(default_factory=list)
    topic: str = ""


class Decomposer(Protocol):
    def decompose(
        self, semantic_nodes: Iterable[Node], candidate_durable_nodes: Iterable[Node]
    ) -> list[JudgmentUnit]:
        """Partition semantic records into one-topic judgment units."""
        ...


class WholeBatchDecomposer:
    """Control: the whole batch is one unit (== the pre-M3.1-B.2 single-judgment path)."""

    def decompose(
        self, semantic_nodes: Iterable[Node], candidate_durable_nodes: Iterable[Node]
    ) -> list[JudgmentUnit]:
        nodes = list(semantic_nodes)
        cands = list(candidate_durable_nodes)
        if not nodes:
            return []
        return [JudgmentUnit(semantic_nodes=nodes, candidate_durable_nodes=cands, topic="(whole batch)")]


class SingletonDecomposer:
    """Floor: one unit per record (maximal decomposition)."""

    def decompose(
        self, semantic_nodes: Iterable[Node], candidate_durable_nodes: Iterable[Node]
    ) -> list[JudgmentUnit]:
        cands = list(candidate_durable_nodes)
        return [
            JudgmentUnit(semantic_nodes=[n], candidate_durable_nodes=list(cands), topic=n.label)
            for n in semantic_nodes
        ]


class LLMDecomposer:
    """A model partitions records into topics; each topic becomes a judgment unit.

    Every unit is given the full candidate-durable set (the builder does the
    matching). If the model output is unusable, falls back to a single whole-batch
    unit so the pipeline always produces at least one judgment.
    """

    def __init__(self, client: LLMClient, *, prompt: str = DECOMPOSER_PROMPT) -> None:
        self._client = client
        self._prompt = prompt

    def decompose(
        self, semantic_nodes: Iterable[Node], candidate_durable_nodes: Iterable[Node]
    ) -> list[JudgmentUnit]:
        nodes = list(semantic_nodes)
        cands = list(candidate_durable_nodes)
        if not nodes:
            return []

        rendered = self._prompt.replace("<<SEMANTIC>>", _render(nodes))
        groups = _parse_groups(self._client.complete(rendered), len(nodes))
        if not groups:
            return WholeBatchDecomposer().decompose(nodes, cands)

        return [
            JudgmentUnit(
                semantic_nodes=[nodes[i] for i in idxs],
                candidate_durable_nodes=list(cands),
                topic=topic,
            )
            for topic, idxs in groups
        ]


# ── helpers ---------------------------------------------------------------
def _render(nodes: list[Node]) -> str:
    return "\n".join(f"[{i}] ({n.kind}) {n.label}" for i, n in enumerate(nodes))


def _parse_array(text: str) -> list:
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


def _parse_groups(text: str, n: int) -> list[tuple[str, list[int]]]:
    """Validate the model's partition: in-range, each index assigned exactly once.

    An index claimed by two groups goes to the first; any index left unassigned is
    collected into a trailing "(unassigned)" group so coverage is never silently lost.
    """
    arr = _parse_array(text)
    if not arr:
        return []

    assigned: set[int] = set()
    groups: list[tuple[str, list[int]]] = []
    for el in arr:
        if not isinstance(el, dict):
            continue
        topic = el.get("topic")
        topic = topic.strip() if isinstance(topic, str) and topic.strip() else "topic"
        idxs: list[int] = []
        for i in el.get("records") or []:
            if isinstance(i, int) and 0 <= i < n and i not in assigned:
                assigned.add(i)
                idxs.append(i)
        if idxs:
            groups.append((topic, idxs))

    missing = [i for i in range(n) if i not in assigned]
    if missing:
        groups.append(("(unassigned)", missing))
    return groups
