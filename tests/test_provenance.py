"""Provenance: every node expands back to its supporting Source Records."""

from lyr import InMemoryStore, Node, SourceRecord
from lyr.provenance import dangling_evidence, explain, trace


def test_semantic_node_explains_to_its_source():
    store = InMemoryStore()
    src = SourceRecord(content="Payments Service failed.", origin="incident")
    store.add_source(src)
    node = Node(
        layer="semantic", kind="entity", label="Payments Service",
        identity="idn_x", evidence=[src.id],
    )
    store.add_node(node)

    records = explain(node, store)
    assert [r.id for r in records] == [src.id]


def test_trace_walks_multiple_layers_to_source():
    store = InMemoryStore()
    src = SourceRecord(content="A recurring outage in Payments.", origin="postmortem")
    store.add_source(src)

    semantic = Node(
        layer="semantic", kind="event", label="Payments outage",
        identity="idn_s", evidence=[src.id],
    )
    store.add_node(semantic)
    durable = Node(
        layer="durable", kind="lesson", label="Payments needs redundancy",
        identity="idn_d", evidence=[semantic.id],
    )
    store.add_node(durable)

    # explain() flattens a durable node straight to the source underneath it
    assert [r.id for r in explain(durable, store)] == [src.id]

    # trace() preserves the layered structure
    tree = trace(durable, store)
    assert tree.node.layer == "durable"
    assert tree.children[0].node.layer == "semantic"
    assert tree.children[0].children[0].is_source


def test_dangling_evidence_flags_broken_provenance():
    store = InMemoryStore()
    node = Node(
        layer="semantic", kind="entity", label="Orphan",
        identity="idn_o", evidence=["src_missing"],
    )
    store.add_node(node)
    assert dangling_evidence(node, store) == ["src_missing"]
