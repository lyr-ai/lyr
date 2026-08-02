"""JudgmentBuilder — the minimal LLM-driven durable builder (M3.1-B).

One reasoning step, no retries, no verifier/challenger:

    semantic records + candidate durables
        → durability prompt → LLM → ONE structured judgment
        → validate → commit (reusing the engine invariants) → JudgmentRecord

This is the *orchestration* layer. It owns none of the trustworthy substrate: the
identity guard, MERGE lifecycle, and minimal-change downgrade all come from the
existing ``DurableBuilder`` (reused, unchanged). The model proposes one operation
and its reasoning; the engine decides what — if anything — is actually committed,
and every stage (raw output → parsed payload → intent → engine action) is recorded
in an immutable ``JudgmentRecord``.

    Model proposes meaning.  Engine commits identity, history, and provenance.

``update`` is the stable interface for all future durable builders (M3.1-C adds a
verifier stage *around* it, not a redesign of it).

The prompt is loaded from a single canonical, versioned source
(``lyr/durable/prompts/durable_builder_v1.md``) so it evolves in exactly one place.
"""

from __future__ import annotations

import json
import re
from importlib.resources import files
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
    EvidenceGroup,
    JudgmentRecord,
    JudgmentResult,
    ModelProposal,
    new_judgment_id,
)

# The one canonical builder prompt. Versioned by filename; loaded once at import.
PROMPT_VERSION = "durable_builder_v1"
PROMPT = files("lyr.durable").joinpath("prompts").joinpath(f"{PROMPT_VERSION}.md").read_text(
    encoding="utf-8"
)


class JudgmentBuilder:
    def __init__(
        self,
        store: Store,
        client: LLMClient,
        *,
        prompt: str = PROMPT,
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
        raw_completion = self._client.complete(prompt)
        parsed = _parse_object(raw_completion)

        intent, error = self._interpret(parsed, semantic, candidates)
        groups = self._evidence_groups(parsed, semantic)

        # A globally unique execution id (never repeats) vs. a content-derived
        # fingerprint of the judgment (may repeat across executions).
        judgment_id = new_judgment_id()
        fingerprint = content_id(
            "jfp",
            intent.operation,
            intent.statement,
            *sorted(intent.evidence),
            *sorted(n.identity for n in candidates),
        )

        node, action = self._commit(intent, error, judgment_id)

        record = JudgmentRecord(
            judgment_id=judgment_id,
            judgment_fingerprint=fingerprint,
            model_intent=intent,
            final_engine_action=action,
            raw_completion=raw_completion,
            parsed_payload=parsed,
            candidate_semantic_ids=tuple(n.id for n in semantic),
            candidate_durable_identities=tuple(n.identity for n in candidates),
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

        Always returns a (best-effort) frozen ``ModelProposal`` — so the intent is
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
        target_identity: str | None = None
        superseded: tuple[str, ...] = ()

        def make(**over: Any) -> ModelProposal:
            fields: dict[str, Any] = dict(
                operation=op if op in DURABLE_OPS else NO_OP,
                statement=statement,
                kind=kind,
                evidence=evidence,
                target_identity=target_identity,
                superseded=superseded,
                rationale=rationale,
                counter_evidence=counter,
                confidence=confidence,
            )
            fields.update(over)
            return ModelProposal(**fields)

        if op not in DURABLE_OPS:
            return make(), f"unknown operation {op!r}"

        if op == NO_OP:
            target = _index(parsed.get("target"), candidates)
            target_identity = candidates[target].identity if target is not None else None
            return make(target_identity=target_identity), None

        if op in (UPDATE, MERGE):
            target = _index(parsed.get("target"), candidates)
            if target is None:
                return make(), f"{op} target does not reference a candidate durable memory"
            target_identity = candidates[target].identity
            if not statement:
                statement = candidates[target].label
            if op == MERGE:
                superseded = _merge_identities(parsed.get("merge"), candidates, target_identity)
        elif op == ADD:
            if not statement:
                return make(), "ADD requires a statement"
            target_identity = content_id("idn", "durable", "judgment", normalize(statement))

        if not evidence:
            return make(statement=statement, target_identity=target_identity), (
                f"{op} requires at least one valid evidence reference"
            )
        return make(statement=statement, target_identity=target_identity, superseded=superseded), None

    # ── evidence groups (validated) ---------------------------------------
    def _evidence_groups(
        self, parsed: dict[str, Any] | None, semantic: list[Node]
    ) -> tuple[EvidenceGroup, ...]:
        """Validate the model's evidence groups into immutable, id-resolved form.

        Drops out-of-range indices, de-duplicates while preserving order, and
        resolves each index to a real semantic id — so an audit artifact can never
        cite a record that was not in the input.
        """
        if not isinstance(parsed, dict):
            return ()
        raw_groups = parsed.get("evidence_groups")
        if not isinstance(raw_groups, list):
            return ()

        groups: list[EvidenceGroup] = []
        for g in raw_groups:
            if not isinstance(g, dict):
                continue
            records: list[int] = []
            seen: set[int] = set()
            for idx in g.get("records") or []:
                if isinstance(idx, int) and 0 <= idx < len(semantic) and idx not in seen:
                    seen.add(idx)
                    records.append(idx)
            groups.append(
                EvidenceGroup(
                    records=tuple(records),
                    same_observation=bool(g.get("same_observation", False)),
                    note=_clean_str(g.get("note")),
                    semantic_ids=tuple(semantic[i].id for i in records),
                )
            )
        return tuple(groups)

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


def _map_evidence(raw: Any, semantic: list[Node]) -> tuple[str, ...]:
    out: list[str] = []
    for idx in raw or []:
        if isinstance(idx, int) and 0 <= idx < len(semantic):
            out.append(semantic[idx].id)
    return tuple(sorted(set(out)))


def _merge_identities(raw: Any, candidates: list[Node], target_identity: str) -> tuple[str, ...]:
    superseded: list[str] = []
    seen: set[str] = set()
    for idx in raw or []:
        m = _index(idx, candidates)
        if m is not None:
            ident = candidates[m].identity
            if ident != target_identity and ident not in seen:
                seen.add(ident)
                superseded.append(ident)
    return tuple(superseded)


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
