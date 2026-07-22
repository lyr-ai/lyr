"""Durable provenance: trace down to source, and discover supporters upward."""

from lyr import LYR
from lyr.provenance import supporters


def _corpus():
    """An engine where one subject recurs across two experiences."""
    lyr = LYR()  # rule-based extractor + recurrence consolidator (min_support=2)
    lyr.ingest("The Payments Service failed during the London deploy.", origin="incident-1")
    lyr.ingest("The Payments Service failed again overnight.", origin="incident-2")
    lyr.build_durable()
    return lyr


def test_durable_memory_traces_to_source():
    lyr = _corpus()
    durables = list(lyr.durable_memories())
    assert durables, "expected a durable memory for the recurring subject"

    payments = next(d for d in durables if "Payments Service" in d.label)
    records = lyr.explain(payments)
    # durable → semantic → source, flattened to the originating records
    assert {r.origin for r in records} == {"incident-1", "incident-2"}


def test_semantic_record_discovers_durables_it_supports():
    lyr = _corpus()
    entity = next(n for n in lyr.semantic_nodes() if n.label == "Payments Service")

    # upward provenance: which durable memories does this semantic record support?
    durables = lyr.supporters(entity, layer="durable")
    assert durables
    assert all(entity.id in d.evidence for d in durables)


def test_supporters_is_the_inverse_of_evidence():
    lyr = _corpus()
    durable = next(iter(lyr.durable_memories()))
    for semantic_id in durable.evidence:
        semantic = lyr.store.get_node(semantic_id)
        assert durable.id in {d.id for d in supporters(semantic.id, lyr.store, layer="durable")}
