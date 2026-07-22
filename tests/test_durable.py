"""Durable layer (M3): consolidation, operations, identity, minimal change."""

import json

from lyr import InMemoryStore, LLMConsolidator, Node
from lyr.durable import DurableBuilder, RecurrenceConsolidator
from lyr.durable.base import ADD, MERGE, NO_OP, UPDATE, DurableProposal
from lyr.llm import FakeClient


def _semantic(kind, label, identity, evidence, **attrs):
    return Node(
        layer="semantic", kind=kind, label=label, identity=identity,
        evidence=list(evidence), attributes=attrs,
    )


# ── recurrence consolidator: threshold ----------------------------------
def test_topic_below_threshold_is_not_durable():
    # entity backed by a single source record → not recurring
    sem = [_semantic("entity", "Payments", "idn_e", ["src_1"], entity_type="system")]
    proposals = RecurrenceConsolidator(min_support=2).consolidate(sem, [])
    assert [p for p in proposals if p.op != NO_OP] == []


def test_topic_meeting_threshold_becomes_add():
    # same entity corroborated by two distinct source records
    entity = _semantic("entity", "Payments", "idn_e", ["src_1", "src_2"], entity_type="system")
    proposals = RecurrenceConsolidator(min_support=2).consolidate([entity], [])
    adds = [p for p in proposals if p.op == ADD]
    assert len(adds) == 1
    assert adds[0].evidence == [entity.id]  # durable cites the semantic record
    assert adds[0].attributes["support"] == 2  # 2 distinct source records
    assert 0 < adds[0].attributes["confidence"] < 1


def test_relationship_recurrence_produces_a_lesson():
    rel = _semantic(
        "relationship", "Hard routing causes retrieval failures", "idn_r",
        ["src_1", "src_2", "src_3"],
        subject="hard routing", predicate="causes", object="retrieval failures",
    )
    proposals = RecurrenceConsolidator(min_support=2).consolidate([rel], [])
    add = next(p for p in proposals if p.op == ADD)
    assert add.kind == "lesson"
    assert "routing" in add.statement.lower()


# ── builder: apply operations -------------------------------------------
def test_build_adds_then_no_ops_on_rerun():
    store = InMemoryStore()
    rel = _semantic(
        "relationship", "Small releases reduce risk", "idn_r",
        ["src_1", "src_2"], subject="small releases", predicate="reduce", object="risk",
    )
    store.add_node(rel)
    builder = DurableBuilder(store, RecurrenceConsolidator(min_support=2))

    first = builder.build()
    assert any(p.op == ADD for p in first)
    durable = [n for n in store.nodes(layer="durable")]
    assert len(durable) == 1 and durable[0].version == 1

    second = builder.build()
    assert all(p.op == NO_OP for p in second)  # nothing changed → all NO_OP
    assert len(list(store.nodes(layer="durable"))) == 1  # no churn


def test_new_evidence_updates_durable_preserving_identity():
    store = InMemoryStore()
    consolidator = RecurrenceConsolidator(min_support=2)
    builder = DurableBuilder(store, consolidator)

    rel_v1 = _semantic(
        "relationship", "Caching cuts latency", "idn_r", ["src_1", "src_2"],
        subject="caching", predicate="cuts", object="latency",
    )
    store.add_node(rel_v1)
    builder.build()
    durable_v1 = next(iter(store.nodes(layer="durable")))
    assert durable_v1.version == 1

    # the same relationship now corroborated by a third source (semantic evolves)
    rel_v2 = rel_v1.evolved(evidence=["src_1", "src_2", "src_3"])
    store.add_node(rel_v2)
    proposals = builder.build()

    assert any(p.op == UPDATE for p in proposals)
    head = store.head(durable_v1.identity)
    assert head.version == 2
    assert head.identity == durable_v1.identity  # identity preserved
    assert head.parent_id == durable_v1.id
    assert head.attributes["support"] == 3


# ── builder: MERGE -------------------------------------------------------
def test_merge_folds_evidence_and_keeps_history():
    store = InMemoryStore()
    a = Node(layer="durable", kind="lesson", label="Retry on 5xx",
             identity="idn_a", evidence=["sem_1"], attributes={"support": 1})
    b = Node(layer="durable", kind="lesson", label="Retry transient errors",
             identity="idn_b", evidence=["sem_2"], attributes={"support": 1})
    store.add_node(a)
    store.add_node(b)

    merge = DurableProposal(
        op=MERGE, identity="idn_a", statement="Retry transient (5xx) errors",
        kind="lesson", evidence=["sem_1"], superseded=["idn_b"],
    )
    # a trivial consolidator that just returns our hand-built proposal
    class _Fixed:
        def consolidate(self, semantic_nodes, existing_durable):
            return [merge]

    DurableBuilder(store, _Fixed()).build()

    head = store.head("idn_a")
    assert head.version == 2
    assert set(head.evidence) == {"sem_1", "sem_2"}  # b's evidence folded in
    assert head.attributes["merged_from"] == ["idn_b"]
    # b's history is preserved
    assert store.head("idn_b").label == "Retry transient errors"


# ── LLM consolidator -----------------------------------------------------
def test_llm_consolidator_add_maps_evidence_and_derives_identity():
    semantic = [
        _semantic("relationship", "A causes B", "idn_1", ["s1"]),
        _semantic("relationship", "A causes B again", "idn_2", ["s2"]),
    ]
    canned = json.dumps([
        {"op": "ADD", "target": None, "statement": "A reliably causes B",
         "kind": "lesson", "evidence": [0, 1], "confidence": 0.8, "reason": "recurs"},
        {"op": "NO_OP", "target": None, "statement": "ignored", "evidence": []},
    ])
    proposals = LLMConsolidator(FakeClient(canned)).consolidate(semantic, [])
    add = next(p for p in proposals if p.op == ADD)
    assert add.statement == "A reliably causes B"
    assert add.evidence == sorted([semantic[0].id, semantic[1].id])
    assert add.attributes["confidence"] == 0.8
    # NO_OP with no target is dropped (nothing to reference)
    assert all(p.op != NO_OP for p in proposals)


def test_llm_consolidator_update_reuses_existing_identity():
    semantic = [_semantic("relationship", "A causes B", "idn_1", ["s1", "s2"])]
    existing = [Node(layer="durable", kind="lesson", label="A causes B",
                     identity="idn_dur", evidence=["idn_1"])]
    canned = json.dumps([
        {"op": "UPDATE", "target": 0, "statement": "A causes B (confirmed)",
         "evidence": [0], "confidence": 0.9},
    ])
    proposals = LLMConsolidator(FakeClient(canned)).consolidate(semantic, existing)
    upd = next(p for p in proposals if p.op == UPDATE)
    assert upd.identity == "idn_dur"  # identity comes from the referenced target
