"""End-to-end: the LYR facade across the M1 + M2 vertical slice."""

from lyr import LYR


def test_ingest_builds_semantic_and_traces_to_source():
    lyr = LYR()  # defaults: in-memory store, text ingestor, rule-based extractor
    nodes = lyr.ingest(
        "The Payments Service failed at 02:00 during the London deploy.",
        origin="incident-42",
    )
    assert nodes

    entity = next(n for n in nodes if n.label == "Payments Service")
    records = lyr.explain(entity)
    assert records
    assert "Payments Service" in records[0].content
    assert records[0].origin == "incident-42"


def test_ingest_source_then_rebuild_is_idempotent():
    lyr = LYR()
    lyr.ingest_source("Grace Hopper found the first bug.", origin="history")

    first = lyr.rebuild_semantic()
    versions_before = {n.identity: len(lyr.history(n)) for n in first}

    lyr.rebuild_semantic()  # nothing new to learn
    for identity, count in versions_before.items():
        node = next(n for n in lyr.semantic_nodes() if n.identity == identity)
        assert len(lyr.history(node)) == count  # minimal change: no new versions


def test_semantic_nodes_returns_current_heads_only():
    lyr = LYR()
    lyr.ingest("The Analytical Engine was designed by Babbage.", origin="doc", position=0)
    lyr.ingest("The Analytical Engine was never completed.", origin="doc2")

    heads = list(lyr.semantic_nodes())
    # one head per identity
    assert len({n.identity for n in heads}) == len(heads)


def test_multiple_experiences_accumulate_evidence():
    lyr = LYR()
    lyr.ingest("Ada worked on the Analytical Engine.", origin="a")
    lyr.ingest("Ada wrote the first algorithm.", origin="b")

    ada = next(n for n in lyr.semantic_nodes() if n.label == "Ada")
    origins = {r.origin for r in lyr.explain(ada)}
    assert origins == {"a", "b"}  # evidence gathered from both experiences
