"""The M3 knowledge-maintenance benchmark."""

from lyr import InMemoryStore, Node
from lyr.durable import DurableBuilder, RecurrenceConsolidator
from lyr.durable.base import ADD, NO_OP, DurableProposal
from lyr.durable.evaluation import (
    evaluate,
    identity_preservation,
    is_reproducible,
    minimal_change,
    provenance_completeness,
    update_precision_recall,
)


def _semantic(label, identity, evidence, subject, predicate, obj):
    return Node(
        layer="semantic", kind="relationship", label=label, identity=identity,
        evidence=list(evidence),
        attributes={"subject": subject, "predicate": predicate, "object": obj},
    )


def test_precision_recall_on_changing_ops():
    gold = [DurableProposal(op=ADD, identity="idn_a", statement="x")]
    predicted_perfect = [DurableProposal(op=ADD, identity="idn_a", statement="x")]
    assert update_precision_recall(predicted_perfect, gold) == (1.0, 1.0)

    predicted_wrong = [DurableProposal(op=ADD, identity="idn_b", statement="y")]
    p, r = update_precision_recall(predicted_wrong, gold)
    assert p == 0.0 and r == 0.0

    # NO_OPs are ignored on both sides
    noisy = predicted_perfect + [DurableProposal(op=NO_OP, identity="idn_z", statement="z")]
    assert update_precision_recall(noisy, gold) == (1.0, 1.0)


def test_minimal_change_is_no_op_fraction():
    props = [
        DurableProposal(op=ADD, identity="a", statement="x"),
        DurableProposal(op=NO_OP, identity="b", statement="y"),
        DurableProposal(op=NO_OP, identity="c", statement="z"),
    ]
    assert minimal_change(props) == 2 / 3


def test_identity_and_provenance_are_intact_after_a_real_build():
    store = InMemoryStore()
    rel = _semantic("Caching cuts latency", "idn_r", ["src_1", "src_2"],
                    "caching", "cuts", "latency")
    store.add_node(rel)
    consolidator = RecurrenceConsolidator(min_support=2)
    builder = DurableBuilder(store, consolidator)
    proposals = builder.build()

    # evidence points at real semantic nodes → provenance complete
    assert provenance_completeness(store) == 1.0
    # single well-formed version chain → identity preserved
    assert identity_preservation(store) == 1.0
    # deterministic consolidator → reproducible
    assert is_reproducible(consolidator, builder._heads("semantic"), builder._heads("durable"))

    report = evaluate(
        store=store, predicted=proposals, consolidator=consolidator,
        semantic_nodes=builder._heads("semantic"),
        existing_durable=[],  # this round started from no durable memories
        gold=[p for p in proposals if p.op == ADD],
    )
    assert report.reproducible is True
    assert report.provenance_completeness == 1.0
    assert report.identity_preservation == 1.0
    assert report.update_recall == 1.0


def test_empty_state_scores_are_neutral():
    store = InMemoryStore()
    consolidator = RecurrenceConsolidator()
    report = evaluate(
        store=store, predicted=[], consolidator=consolidator,
        semantic_nodes=[], existing_durable=[],
    )
    assert report.provenance_completeness == 1.0
    assert report.identity_preservation == 1.0
    assert report.minimal_change == 1.0
