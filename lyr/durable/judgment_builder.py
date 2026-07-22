"""JudgmentBuilder — the minimal LLM-driven durable builder (M3.1-B).

One reasoning step, no retries, no verifier/challenger:

    semantic records + candidate durables
        → durability prompt → LLM → ONE structured judgment
        → validate → commit (reusing the engine invariants) → JudgmentRecord

This is the *orchestration* layer. It owns none of the trustworthy substrate: the
identity guard, MERGE lifecycle, and minimal-change downgrade all come from the
existing ``DurableBuilder`` (reused, unchanged). The model proposes one operation
and its reasoning; the engine decides what — if anything — is actually committed,
and both halves are recorded in an immutable ``JudgmentRecord``.

    Model proposes meaning.  Engine commits identity, history, and provenance.

``update`` is the stable interface for all future durable builders (M3.1-C adds a
verifier stage *around* it, not a redesign of it).
"""

from __future__ import annotations

import json
import re
from typing import Any, Iterable

from ..ids import content_id, normalize
from ..llm.base import LLMClient
from ..models import Node
from ..store.base import Store
from .base import ADD, DURABLE_OPS, MERGE, NO_OP, UPDATE, DurableProposal
from .builder import DurableBuilder
from .judgment import (
    REJECT,
    EngineAction,
    JudgmentRecord,
    JudgmentResult,
    ModelProposal,
)

PROMPT_VERSION = "durable_builder_v1"

_PROMPT = """\
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
JSON object:"""


class JudgmentBuilder:
    def __init__(
        self,
        store: Store,
        client: LLMClient,
        *,
        prompt: str = _PROMPT,
        model_config: dict[str, Any] | None = None,
    ) -> None:
        self._store = store
        self._client = client
        self._prompt = prompt
        self._extra_config = dict(model_config or {})
        # Reuse the engine substrate for commits; the null consolidator is never
        # consulted (only _apply_one is used), so no policy leaks in here.
        self._engine = DurableBuilder(store, _NullConsolidator())

    # ── public interface --------------------------------------------------
    def update(
        self,
        semantic_nodes: Iterable[Node],
        candidate_durable_nodes: Iterable[Node],
    ) -> JudgmentResult:
        """Perform one durable-maintenance judgment and record it immutably."""
        semantic = list(semantic_nodes)
        candidates = list(candidate_durable_nodes)

        prompt = self._render(semantic, candidates)
        completion = self._client.complete(prompt)
        parsed = _parse_object(completion)

        intent, error = self._interpret(parsed, semantic, candidates)
        groups = _evidence_groups(parsed)

        judgment_id = content_id(
            "jdg",
            intent.operation,
            intent.statement,
            *sorted(intent.evidence),
            *sorted(n.identity for n in candidates),
        )

        node, action = self._commit(intent, error, judgment_id)

        record = JudgmentRecord(
            judgment_id=judgment_id,
            model_intent=intent,
            final_engine_action=action,
            candidate_semantic_ids=[n.id for n in semantic],
            candidate_durable_identities=[n.identity for n in candidates],
            evidence_groups=groups,
            model_config=self._model_config(),
        )
        self._store.add_judgment(record)
        return JudgmentResult(judgment_record=record, engine_action=action, updated_durable=node)

    # ── commit (reuses the engine invariants) -----------------------------
    def _commit(
        self, intent: ModelProposal, error: str | None, judgment_id: str
    ) -> tuple[Node | None, EngineAction]:
        if error is not None:
            return None, EngineAction(operation=REJECT, rejection_reason=error)
        if intent.operation == NO_OP:
            return None, EngineAction(operation=NO_OP, identity=intent.target_identity)

        proposal = DurableProposal(
            op=intent.operation,
            identity=intent.target_identity or "",
            statement=intent.statement,
            kind=intent.kind,
            evidence=list(intent.evidence),
            superseded=list(intent.superseded),
        )
        node = self._engine._apply_one(proposal)

        if node is None:
            # The engine's minimal-change guard downgraded an inert UPDATE.
            return None, EngineAction(operation=NO_OP, identity=intent.target_identity)

        # The one back-reference: this durable version cites the judgment that
        # produced it. Set after commit so it never perturbs the minimal-change
        # comparison (attributes are not part of a node's content id).
        node.attributes["judgment_id"] = judgment_id

        # Report what the engine *did*, which may differ from what was proposed:
        # an ADD onto an existing identity is evolved (identity guard), landing as
        # a higher version — record that as an UPDATE.
        committed = intent.operation
        if intent.operation == ADD and node.version > 1:
            committed = UPDATE
        return node, EngineAction(
            operation=committed, node_id=node.id, identity=node.identity, version=node.version
        )

    # ── model output → validated intent -----------------------------------
    def _interpret(
        self, parsed: dict[str, Any] | None, semantic: list[Node], candidates: list[Node]
    ) -> tuple[ModelProposal, str | None]:
        """Resolve the model's indices to real ids and validate the proposal.

        Returns the (best-effort) ``ModelProposal`` always — so the intent is
        recorded even on rejection — plus an error string when the proposal is
        malformed or references something that does not exist.
        """
        if not isinstance(parsed, dict):
            return _empty_intent(), "malformed model output (no JSON object found)"

        op = parsed.get("operation")
        statement = (parsed.get("statement") or "").strip()
        kind = _clean_kind(parsed.get("kind"))
        evidence = _map_evidence(parsed.get("evidence"), semantic)
        rationale = _clean_str(parsed.get("rationale"))
        counter = _clean_str(parsed.get("counter_evidence"))
        confidence = _clean_confidence(parsed.get("confidence"))

        base = ModelProposal(
            operation=op if op in DURABLE_OPS else NO_OP,
            statement=statement,
            kind=kind,
            evidence=evidence,
            rationale=rationale,
            counter_evidence=counter,
            confidence=confidence,
        )

        if op not in DURABLE_OPS:
            return base, f"unknown operation {op!r}"

        if op == NO_OP:
            target = _index(parsed.get("target"), candidates)
            base.target_identity = candidates[target].identity if target is not None else None
            return base, None

        if op in (UPDATE, MERGE):
            target = _index(parsed.get("target"), candidates)
            if target is None:
                return base, f"{op} target does not reference a candidate durable memory"
            base.target_identity = candidates[target].identity
            if not base.statement:
                base.statement = candidates[target].label
            if op == MERGE:
                base.superseded = _merge_identities(parsed.get("merge"), candidates, base.target_identity)
        elif op == ADD:
            if not statement:
                return base, "ADD requires a statement"
            base.target_identity = content_id("idn", "durable", "judgment", normalize(statement))

        if not evidence:
            return base, f"{op} requires at least one valid evidence reference"
        return base, None

    # ── rendering & config ------------------------------------------------
    def _render(self, semantic: list[Node], candidates: list[Node]) -> str:
        return self._prompt.replace("<<DURABLE>>", _render_durable(candidates)).replace(
            "<<SEMANTIC>>", _render_semantic(semantic)
        )

    def _model_config(self) -> dict[str, Any]:
        cfg: dict[str, Any] = {
            "prompt_version": PROMPT_VERSION,
            "provider": type(self._client).__name__,
        }
        model = getattr(self._client, "model", None)
        if model:
            cfg["model"] = model
        cfg.update(self._extra_config)
        return cfg


# ── module helpers --------------------------------------------------------
class _NullConsolidator:
    def consolidate(self, semantic_nodes: Iterable[Node], existing_durable: Iterable[Node]) -> list:
        return []


def _empty_intent() -> ModelProposal:
    return ModelProposal(operation=NO_OP, statement="", kind="lesson")


def _render_semantic(nodes: list[Node]) -> str:
    if not nodes:
        return "(none)"
    return "\n".join(f"[{i}] ({n.kind}) {n.label}" for i, n in enumerate(nodes))


def _render_durable(nodes: list[Node]) -> str:
    if not nodes:
        return "(none)"
    return "\n".join(f"[{i}] {n.label}" for i, n in enumerate(nodes))


def _parse_object(text: str) -> dict[str, Any] | None:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        data = json.loads(text[start : end + 1])
    except (json.JSONDecodeError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _evidence_groups(parsed: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(parsed, dict):
        return []
    groups = parsed.get("evidence_groups")
    return [g for g in groups if isinstance(g, dict)] if isinstance(groups, list) else []


def _map_evidence(raw: Any, semantic: list[Node]) -> list[str]:
    out: list[str] = []
    for idx in raw or []:
        if isinstance(idx, int) and 0 <= idx < len(semantic):
            out.append(semantic[idx].id)
    return sorted(set(out))


def _merge_identities(raw: Any, candidates: list[Node], target_identity: str) -> list[str]:
    superseded: list[str] = []
    for idx in raw or []:
        m = _index(idx, candidates)
        if m is not None and candidates[m].identity != target_identity:
            superseded.append(candidates[m].identity)
    return superseded


def _index(value: Any, nodes: list[Node]) -> int | None:
    if isinstance(value, int) and 0 <= value < len(nodes):
        return value
    return None


def _clean_str(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _clean_kind(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else "lesson"


def _clean_confidence(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None
