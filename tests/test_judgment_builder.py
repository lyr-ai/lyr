"""M3.1-B — the minimal LLM durable builder (JudgmentBuilder).

Exercises the one-step judgment pipeline with a scripted FakeClient (the repo's
offline LLM path), asserting the M3.1-A/B contract: every attempt is recorded,
committed versions carry a judgment_id back-reference, and the engine invariants
(identity guard, minimal-change, reference validation) still hold.
"""

from __future__ import annotations

import json

from lyr.durable import JudgmentBuilder
from lyr.durable.base import ADD, NO_OP, UPDATE
from lyr.durable.judgment import REJECT
from lyr.llm.fake import FakeClient
from lyr.models import Node
from lyr.store import InMemoryStore


def _semantic(kind: str, label: str, evidence: list[str]) -> Node:
    return Node(layer="semantic", kind=kind, label=label, identity=f"idn_{label}", evidence=evidence)


def _durable(label: str, identity: str, evidence: list[str]) -> Node:
    return Node(layer="durable", kind="lesson", label=label, identity=identity, evidence=evidence)


def _resp(**obj) -> str:
    return json.dumps(obj)


# ── ADD ------------------------------------------------------------------
def test_add_commits_node_records_judgment_and_backreference():
    store = InMemoryStore()
    s0 = _semantic("event", "failed in London", ["src_1"])
    s1 = _semantic("event", "failed in Tokyo", ["src_2"])
    for s in (s0, s1):
        store.add_node(s)

    client = FakeClient(_resp(
        operation="ADD",
        statement="The payments service fails during regional deploys.",
        kind="lesson",
        evidence=[0, 1],
        target=None,
        merge=[],
        evidence_groups=[{"records": [0, 1], "same_observation": False, "note": "two regions"}],
        rationale="Two independent regional failures.",
        counter_evidence="",
        confidence=0.7,
    ))

    result = JudgmentBuilder(store, client).update([s0, s1], [])

    # committed a durable v1
    node = result.updated_durable
    assert node is not None and node.layer == "durable" and node.version == 1
    assert set(node.evidence) == {s0.id, s1.id}
    # the one back-reference
    assert node.attributes["judgment_id"] == result.judgment_record.judgment_id
    # engine action
    assert result.engine_action.operation == ADD
    assert result.engine_action.node_id == node.id
    # model intent preserved verbatim (with resolved evidence ids)
    intent = result.judgment_record.model_intent
    assert intent.operation == ADD
    assert intent.evidence == sorted([s0.id, s1.id])
    assert intent.confidence == 0.7
    assert result.judgment_record.evidence_groups[0]["records"] == [0, 1]
    # persisted, append-only
    assert store.get_judgment(result.judgment_record.judgment_id) is result.judgment_record
    assert len(list(store.judgments())) == 1


# ── NO_OP ----------------------------------------------------------------
def test_no_op_commits_nothing_but_records_the_attempt():
    store = InMemoryStore()
    s0 = _semantic("event", "had coffee", ["src_1"])
    store.add_node(s0)

    client = FakeClient(_resp(operation="NO_OP", statement="", kind="lesson",
                              evidence=[], rationale="trivial", confidence=0.1))
    result = JudgmentBuilder(store, client).update([s0], [])

    assert result.updated_durable is None
    assert result.engine_action.operation == NO_OP
    assert list(store.nodes(layer="durable")) == []
    # the refusal is still on the record
    assert len(list(store.judgments())) == 1
    assert result.judgment_record.model_intent.rationale == "trivial"


# ── UPDATE reuses an existing identity -----------------------------------
def test_update_reuses_existing_durable_identity():
    store = InMemoryStore()
    s0 = _semantic("event", "failed again", ["src_3"])
    store.add_node(s0)
    existing = _durable("Payments fails on deploy", "idn_pay", ["src_0"])
    store.add_node(existing)

    client = FakeClient(_resp(
        operation="UPDATE", statement="Payments fails on deploy (confirmed).",
        kind="lesson", evidence=[0], target=0, merge=[],
        rationale="new supporting incident", confidence=0.8,
    ))
    result = JudgmentBuilder(store, client).update([s0], [existing])

    node = result.updated_durable
    assert node is not None
    assert node.identity == "idn_pay"        # identity reused from the target
    assert node.version == 2                  # evolved, not forked
    assert result.engine_action.operation == UPDATE
    assert node.attributes["judgment_id"] == result.judgment_record.judgment_id


# ── invalid reference → REJECT, no commit --------------------------------
def test_out_of_range_evidence_is_rejected():
    store = InMemoryStore()
    s0 = _semantic("event", "only record", ["src_1"])
    store.add_node(s0)

    client = FakeClient(_resp(operation="ADD", statement="claim", kind="lesson",
                              evidence=[5], target=None))  # index 5 does not exist
    result = JudgmentBuilder(store, client).update([s0], [])

    assert result.updated_durable is None
    assert result.engine_action.operation == REJECT
    assert "evidence" in (result.engine_action.rejection_reason or "")
    assert list(store.nodes(layer="durable")) == []
    # rejected attempts are still recorded
    assert len(list(store.judgments())) == 1


def test_update_without_valid_target_is_rejected():
    store = InMemoryStore()
    s0 = _semantic("event", "x", ["src_1"])
    store.add_node(s0)
    client = FakeClient(_resp(operation="UPDATE", statement="y", evidence=[0], target=None))
    result = JudgmentBuilder(store, client).update([s0], [])
    assert result.engine_action.operation == REJECT
    assert "target" in (result.engine_action.rejection_reason or "")


# ── malformed model output → REJECT --------------------------------------
def test_malformed_output_is_rejected_not_crashed():
    store = InMemoryStore()
    s0 = _semantic("event", "x", ["src_1"])
    store.add_node(s0)
    result = JudgmentBuilder(store, FakeClient("not json at all")).update([s0], [])
    assert result.engine_action.operation == REJECT
    assert "malformed" in (result.engine_action.rejection_reason or "")
    assert len(list(store.judgments())) == 1


# ── identity guard: model ADD onto existing identity is evolved ----------
def test_add_statement_matching_existing_judgment_identity_evolves():
    store = InMemoryStore()
    s0 = _semantic("event", "a", ["src_1"])
    s1 = _semantic("event", "b", ["src_2"])
    for s in (s0, s1):
        store.add_node(s)
    builder = JudgmentBuilder(store, FakeClient([
        _resp(operation="ADD", statement="Same durable claim.", kind="lesson", evidence=[0]),
        _resp(operation="ADD", statement="Same durable claim.", kind="lesson", evidence=[0]),
    ]))
    first = builder.update([s0], [])
    second = builder.update([s1], [])

    assert first.updated_durable.version == 1
    # second ADD hits the same content-derived identity → engine evolves it
    assert second.updated_durable.version == 2
    assert second.updated_durable.identity == first.updated_durable.identity
    assert second.engine_action.operation == UPDATE  # reported as what the engine did
    assert second.updated_durable.attributes["judgment_id"] == second.judgment_record.judgment_id


# ── record serialization --------------------------------------------------
def test_judgment_record_serializes():
    store = InMemoryStore()
    s0 = _semantic("event", "x", ["src_1"])
    store.add_node(s0)
    result = JudgmentBuilder(store, FakeClient(_resp(
        operation="ADD", statement="a durable claim", kind="fact", evidence=[0], confidence=0.5,
    ))).update([s0], [])
    d = result.judgment_record.to_dict()
    assert d["final_engine_action"]["operation"] == ADD
    assert d["model_intent"]["kind"] == "fact"
    assert isinstance(d["created_at"], str)
    assert d["model_config"]["prompt_version"]
