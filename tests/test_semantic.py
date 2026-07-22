"""Semantic layer (M2): extraction, identity, minimal-change versioning."""

import json

from lyr import InMemoryStore, LLMExtractor, RuleBasedExtractor, SourceRecord
from lyr.llm import FakeClient
from lyr.semantic import SemanticBuilder


def _record(content, origin="doc", position=0):
    return SourceRecord(content=content, origin=origin, position=position)


# ── rule-based extractor -------------------------------------------------
def test_rule_based_extracts_entities_and_events():
    records = [_record("The Payments Service failed during the London deploy.")]
    nodes = RuleBasedExtractor().extract(records)
    kinds = {n.kind for n in nodes}
    assert "entity" in kinds and "event" in kinds
    labels = {n.label for n in nodes if n.kind == "entity"}
    assert "Payments Service" in labels
    # every extracted node cites evidence
    assert all(n.evidence for n in nodes)


# ── builder: identity + dedup -------------------------------------------
def test_same_entity_across_records_is_one_identity():
    store = InMemoryStore()
    builder = SemanticBuilder(store, RuleBasedExtractor())
    r1 = _record("Payments Service is healthy.", position=0)
    r2 = _record("Payments Service was restarted.", position=1)
    store.add_source(r1)
    store.add_source(r2)

    builder.build([r1, r2])

    entities = [n for n in store.nodes("semantic") if n.kind == "entity"]
    payments = [n for n in entities if n.label == "Payments Service"]
    # one identity for the entity, even though it appeared in two records
    assert len({n.identity for n in payments}) == 1
    head = store.head(payments[0].identity)
    assert set(head.evidence) == {r1.id, r2.id}


# ── builder: minimal change ---------------------------------------------
def test_no_new_version_when_nothing_changes():
    store = InMemoryStore()
    builder = SemanticBuilder(store, RuleBasedExtractor())
    r = _record("Payments Service is healthy.")
    store.add_source(r)

    builder.build([r])
    builder.build([r])  # identical rebuild

    for identity in {n.identity for n in store.nodes("semantic")}:
        assert len(store.versions(identity)) == 1  # no churn


def test_new_evidence_evolves_to_v2_preserving_identity():
    store = InMemoryStore()
    builder = SemanticBuilder(store, RuleBasedExtractor())
    r1 = _record("Payments Service is healthy.", position=0)
    store.add_source(r1)
    builder.build([r1])

    entity = next(n for n in store.nodes("semantic") if n.label == "Payments Service")
    assert entity.version == 1

    r2 = _record("Payments Service is healthy again.", position=1)
    store.add_source(r2)
    builder.build([r2])

    head = store.head(entity.identity)
    assert head.version == 2
    assert head.identity == entity.identity  # identity preserved across revision
    assert head.parent_id == entity.id
    assert set(head.evidence) == {r1.id, r2.id}


# ── LLM extractor with a fake client ------------------------------------
def test_llm_extractor_maps_evidence_indices_to_ids():
    records = [
        _record("Ada founded the Analytical Engine project.", position=0),
        _record("The project shipped in 1843.", position=1),
    ]
    canned = json.dumps(
        [
            {"kind": "entity", "label": "Ada", "evidence": [0],
             "attributes": {"entity_type": "person"}},
            {"kind": "relationship", "label": "Ada founded the project",
             "evidence": [0], "attributes": {"subject": "Ada",
             "predicate": "founded", "object": "Analytical Engine project"}},
            {"kind": "event", "label": "Project shipped", "evidence": [1],
             "attributes": {"when": "1843"}},
        ]
    )
    extractor = LLMExtractor(FakeClient(canned))
    nodes = extractor.extract(records)

    assert {n.kind for n in nodes} == {"entity", "relationship", "event"}
    ada = next(n for n in nodes if n.label == "Ada")
    assert ada.evidence == [records[0].id]  # index 0 → real record id
    shipped = next(n for n in nodes if n.kind == "event")
    assert shipped.evidence == [records[1].id]


def test_llm_extractor_drops_claims_without_evidence():
    records = [_record("Something happened.")]
    canned = json.dumps(
        [
            {"kind": "entity", "label": "Ghost", "evidence": [], "attributes": {}},
            {"kind": "entity", "label": "OutOfRange", "evidence": [7], "attributes": {}},
        ]
    )
    nodes = LLMExtractor(FakeClient(canned)).extract(records)
    assert nodes == []  # no valid evidence → no knowledge


def test_llm_extractor_tolerates_fenced_json_and_prose():
    records = [_record("Grace debugged the Mark II.")]
    messy = "Here you go:\n```json\n" + json.dumps(
        [{"kind": "entity", "label": "Grace", "evidence": [0],
          "attributes": {"entity_type": "person"}}]
    ) + "\n```\nHope that helps!"
    nodes = LLMExtractor(FakeClient(messy)).extract(records)
    assert len(nodes) == 1 and nodes[0].label == "Grace"
