"""M3.1-B — the minimal LLM durable builder (JudgmentBuilder).

Exercises the one-step judgment pipeline with a scripted FakeClient (the repo's
offline LLM path), asserting the M3.1-A/B contract: every attempt is recorded,
committed versions carry a judgment_id back-reference, and the engine invariants
(identity guard, minimal-change, reference validation) still hold.
"""

from __future__ import annotations

import json

from lyr.durable import JudgmentBuilder
from lyr.durable.base import ADD, MERGE, NO_OP, UPDATE
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
    assert intent.evidence == tuple(sorted([s0.id, s1.id]))
    assert intent.confidence == 0.7
    assert result.judgment_record.evidence_groups[0].records == (0, 1)
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


# ══════════════════════════════════════════════════════════════════════════
# M3.1-B.1 — Judgment Contract Hardening
# ══════════════════════════════════════════════════════════════════════════

# ── 4.1 attempt identity vs. semantic fingerprint ------------------------
def test_judgment_id_is_unique_per_execution_fingerprint_is_stable():
    store = InMemoryStore()
    s0 = _semantic("event", "x", ["src_1"])
    store.add_node(s0)
    # identical inputs + identical model response, run twice
    resp = _resp(operation="ADD", statement="a claim", kind="lesson", evidence=[0])
    b = JudgmentBuilder(store, FakeClient([resp, resp]))
    r1 = b.update([s0], [])
    r2 = b.update([s0], [])

    # execution ids never collide...
    assert r1.judgment_record.judgment_id != r2.judgment_record.judgment_id
    # ...but the semantic fingerprint is identical (duplicate-detectable)
    assert r1.judgment_record.judgment_fingerprint == r2.judgment_record.judgment_fingerprint
    # both attempts are preserved; neither overwrote the other
    assert len(list(store.judgments())) == 2
    assert {j.judgment_id for j in store.judgments()} == {
        r1.judgment_record.judgment_id, r2.judgment_record.judgment_id
    }


def test_judgment_ids_are_time_ordered():
    store = InMemoryStore()
    s0 = _semantic("event", "x", ["src_1"])
    store.add_node(s0)
    b = JudgmentBuilder(store, FakeClient(_resp(operation="NO_OP", evidence=[])))
    ids = [b.update([s0], []).judgment_record.judgment_id for _ in range(3)]
    # The 10-char millisecond-timestamp prefix (after "jdg_") is non-decreasing.
    # (Within one millisecond the random suffix breaks ties, so we compare the
    # time prefix, not the whole id.)
    prefixes = [i[4:14] for i in ids]
    assert prefixes == sorted(prefixes)


# ── 4.2 raw output + parsed payload preserved ----------------------------
def test_raw_completion_and_parsed_payload_are_preserved():
    store = InMemoryStore()
    s0 = _semantic("event", "x", ["src_1"])
    store.add_node(s0)
    raw = "here you go:\n```json\n" + _resp(
        operation="ADD", statement="claim", kind="lesson", evidence=[0]
    ) + "\n```\nhope that helps"
    rec = JudgmentBuilder(store, FakeClient(raw)).update([s0], []).judgment_record
    # exact model output kept, chatter and fences included
    assert rec.raw_completion == raw
    # the parsed JSON is kept separately from the normalized intent
    assert rec.parsed_payload["operation"] == "ADD"
    assert rec.model_intent.statement == "claim"


def test_malformed_output_still_preserves_raw_and_null_payload():
    store = InMemoryStore()
    s0 = _semantic("event", "x", ["src_1"])
    store.add_node(s0)
    rec = JudgmentBuilder(store, FakeClient("total nonsense")).update([s0], []).judgment_record
    assert rec.raw_completion == "total nonsense"
    assert rec.parsed_payload is None
    assert rec.final_engine_action.operation == REJECT


# ── 4.3 structural immutability ------------------------------------------
def test_judgment_record_is_frozen():
    import dataclasses
    import pytest

    store = InMemoryStore()
    s0 = _semantic("event", "x", ["src_1"])
    store.add_node(s0)
    rec = JudgmentBuilder(store, FakeClient(_resp(
        operation="ADD", statement="claim", kind="lesson", evidence=[0]
    ))).update([s0], []).judgment_record

    with pytest.raises(dataclasses.FrozenInstanceError):
        rec.judgment_id = "tampered"
    with pytest.raises(dataclasses.FrozenInstanceError):
        rec.model_intent.operation = "MERGE"
    # tuple-backed collections, not mutable lists
    assert isinstance(rec.model_intent.evidence, tuple)
    assert isinstance(rec.candidate_semantic_ids, tuple)
    assert isinstance(rec.evidence_groups, tuple)


# ── 4.5 evidence-group validation ----------------------------------------
def test_evidence_groups_validated_deduped_and_resolved():
    store = InMemoryStore()
    s0 = _semantic("event", "a", ["src_1"])
    s1 = _semantic("event", "b", ["src_2"])
    for s in (s0, s1):
        store.add_node(s)
    rec = JudgmentBuilder(store, FakeClient(_resp(
        operation="ADD", statement="claim", kind="lesson", evidence=[0, 1],
        evidence_groups=[
            {"records": [0, 0, 1, 99], "same_observation": True, "note": "dupes + out of range"},
            {"records": [5], "same_observation": False},  # entirely invalid → empty
        ],
    ))).update([s0, s1], []).judgment_record

    g0 = rec.evidence_groups[0]
    assert g0.records == (0, 1)                       # 0 de-duped, 99 dropped
    assert g0.semantic_ids == (s0.id, s1.id)          # resolved to real ids
    assert g0.same_observation is True
    assert rec.evidence_groups[1].records == ()       # 5 was out of range


# ── 4.6 complete MERGE coverage ------------------------------------------
def _durable_with(store, label, identity, evidence):
    n = _durable(label, identity, evidence)
    store.add_node(n)
    return n


def test_merge_valid_folds_and_retires_superseded_with_provenance():
    from lyr.durable import is_active

    store = InMemoryStore()
    s0 = _semantic("event", "e", ["src_9"])
    store.add_node(s0)
    a = _durable_with(store, "A fails on deploy", "idn_a", ["semA"])
    b = _durable_with(store, "A fails at night", "idn_b", ["semB"])

    rec = JudgmentBuilder(store, FakeClient(_resp(
        operation="MERGE", statement="A fails on deploy (incl. nightly).",
        kind="lesson", evidence=[0], target=0, merge=[1],
    ))).update([s0], [a, b]).judgment_record

    assert rec.final_engine_action.operation == MERGE
    head_a = store.head("idn_a")
    assert head_a.version == 2
    # target absorbed the superseded evidence + the new semantic evidence
    assert {"semA", "semB", s0.id}.issubset(set(head_a.evidence))
    assert head_a.attributes["merged_from"] == ["idn_b"]
    # superseded memory is retired (tombstoned), not deleted; history retained
    head_b = store.head("idn_b")
    assert not is_active(head_b)
    assert head_b.attributes["merged_into"] == "idn_a"
    assert [v.version for v in store.versions("idn_b")] == [1, 2]
    # provenance: committed target carries the judgment back-reference
    assert head_a.attributes["judgment_id"] == rec.judgment_id


def test_merge_invalid_target_is_rejected():
    store = InMemoryStore()
    s0 = _semantic("event", "e", ["src_9"])
    store.add_node(s0)
    a = _durable_with(store, "A", "idn_a", ["semA"])
    rec = JudgmentBuilder(store, FakeClient(_resp(
        operation="MERGE", statement="x", evidence=[0], target=None, merge=[0],
    ))).update([s0], [a]).judgment_record
    assert rec.final_engine_action.operation == REJECT
    assert "target" in (rec.final_engine_action.rejection_reason or "")


def test_merge_dedups_superseded_and_ignores_self_and_invalid():
    store = InMemoryStore()
    s0 = _semantic("event", "e", ["src_9"])
    store.add_node(s0)
    a = _durable_with(store, "A", "idn_a", ["semA"])
    b = _durable_with(store, "B", "idn_b", ["semB"])
    # merge references b twice, the target itself (0), and an out-of-range index
    rec = JudgmentBuilder(store, FakeClient(_resp(
        operation="MERGE", statement="A+B", kind="lesson", evidence=[0],
        target=0, merge=[1, 1, 0, 42],
    ))).update([s0], [a, b]).judgment_record

    # superseded resolved to just idn_b, once (self and invalid dropped)
    assert rec.model_intent.superseded == ("idn_b",)
    assert rec.final_engine_action.operation == MERGE
    assert store.head("idn_a").attributes["merged_from"] == ["idn_b"]
