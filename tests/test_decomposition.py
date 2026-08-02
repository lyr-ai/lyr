"""M3.1-B.2 — judgment decomposition.

The builder is used unchanged; these tests exercise the decomposers and the
pipeline that loops the builder over units. FakeClient scripts are ordered:
for LLMDecomposer the FIRST response is the decomposition, then one builder
response per unit.
"""

from __future__ import annotations

import json

from lyr.durable import (
    JudgmentPipeline,
    JudgmentUnit,
    LLMDecomposer,
    SingletonDecomposer,
    WholeBatchDecomposer,
)
from lyr.durable.base import ADD
from lyr.durable.decomposition import _parse_groups
from lyr.llm.fake import FakeClient
from lyr.models import Node
from lyr.store import InMemoryStore


def _sem(label: str) -> Node:
    return Node(layer="semantic", kind="event", label=label, identity=f"idn_{label}",
                evidence=[f"src_{label}"])


def _add(statement: str, evidence: list[int]) -> str:
    return json.dumps({"operation": "ADD", "statement": statement, "kind": "lesson",
                       "evidence": evidence, "target": None, "merge": []})


def _groups(*groups) -> str:
    return json.dumps([{"topic": t, "records": r} for t, r in groups])


# ── decomposers ----------------------------------------------------------
def test_whole_batch_is_one_unit():
    nodes = [_sem("a"), _sem("b"), _sem("c")]
    units = WholeBatchDecomposer().decompose(nodes, [])
    assert len(units) == 1
    assert units[0].semantic_nodes == nodes


def test_singleton_is_one_unit_per_record():
    nodes = [_sem("a"), _sem("b"), _sem("c")]
    units = SingletonDecomposer().decompose(nodes, [])
    assert len(units) == 3
    assert [u.semantic_nodes[0].label for u in units] == ["a", "b", "c"]


def test_llm_decomposer_partitions_into_topics():
    nodes = [_sem("a"), _sem("b"), _sem("c"), _sem("d")]
    client = FakeClient(_groups(("t1", [0, 1]), ("t2", [2, 3])))
    units = LLMDecomposer(client).decompose(nodes, [])
    assert len(units) == 2
    assert [n.label for n in units[0].semantic_nodes] == ["a", "b"]
    assert [n.label for n in units[1].semantic_nodes] == ["c", "d"]
    assert units[0].topic == "t1"


def test_llm_decomposer_malformed_output_falls_back_to_whole_batch():
    nodes = [_sem("a"), _sem("b")]
    units = LLMDecomposer(FakeClient("not json")).decompose(nodes, [])
    assert len(units) == 1
    assert len(units[0].semantic_nodes) == 2


def test_parse_groups_covers_all_indices_and_dedupes():
    # index 1 claimed twice (kept in first group), index 3 unassigned → trailing group
    text = json.dumps([{"topic": "x", "records": [0, 1]}, {"topic": "y", "records": [1, 2, 99]}])
    groups = _parse_groups(text, 4)
    assert groups[0] == ("x", [0, 1])
    assert groups[1] == ("y", [2])           # 1 de-duped, 99 out of range dropped
    assert groups[-1] == ("(unassigned)", [3])
    # every index 0..3 appears exactly once across groups
    allidx = [i for _, idxs in groups for i in idxs]
    assert sorted(allidx) == [0, 1, 2, 3]


# ── pipeline (builder unchanged) -----------------------------------------
def test_pipeline_singleton_produces_one_record_per_node():
    store = InMemoryStore()
    nodes = [_sem("a"), _sem("b")]
    # one builder response per unit (singleton → 2 units)
    client = FakeClient([_add("A durable", [0]), _add("B durable", [0])])
    results = JudgmentPipeline(store, client, SingletonDecomposer()).run(nodes, [])

    assert len(results) == 2
    assert all(r.engine_action.operation == ADD for r in results)
    # two distinct durable memories committed, two judgments recorded
    assert len({r.updated_durable.identity for r in results}) == 2
    assert len(list(store.judgments())) == 2


def test_pipeline_llm_surfaces_multiple_candidates_from_one_batch():
    """The F7 fix: one multi-topic batch → several durable candidates, not one."""
    store = InMemoryStore()
    nodes = [_sem("family1"), _sem("family2"), _sem("letters1"), _sem("letters2")]
    client = FakeClient([
        _groups(("family", [0, 1]), ("letters", [2, 3])),  # decomposition (1st call)
        _add("Prioritized family.", [0, 1]),               # unit 1 builder
        _add("Wrote letters for decades.", [0, 1]),        # unit 2 builder
    ])
    results = JudgmentPipeline(store, client, LLMDecomposer(client)).run(nodes, [])

    assert len(results) == 2                       # two topics → two durable candidates
    statements = {r.judgment_record.model_intent.statement for r in results}
    assert statements == {"Prioritized family.", "Wrote letters for decades."}
    assert len(list(store.nodes(layer="durable"))) == 2


def test_pipeline_default_decomposer_is_single_judgment():
    store = InMemoryStore()
    nodes = [_sem("a"), _sem("b")]
    client = FakeClient([_add("one durable", [0, 1])])
    results = JudgmentPipeline(store, client).run(nodes, [])  # default = WholeBatch
    assert len(results) == 1


def test_pipeline_empty_batch_yields_no_judgments():
    store = InMemoryStore()
    results = JudgmentPipeline(store, FakeClient("unused"), SingletonDecomposer()).run([], [])
    assert results == []
    assert list(store.judgments()) == []
