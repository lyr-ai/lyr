"""M3.1-C — the durability verifier and its commit gate.

Covers the invocation rules (design §8) and the two-axis Verdict, especially the
frozen boundary that a verifier ERROR is NOT a semantic UNSURE.
"""

from __future__ import annotations

import json

import pytest

from lyr.durable import (
    JudgmentBuilder,
    LLMDurabilityVerifier,
    ThresholdDurabilityVerifier,
    Verdict,
)
from lyr.durable.base import ADD, NO_OP
from lyr.durable.judgment import ERROR, REJECT, SUCCESS, ModelProposal
from lyr.llm.fake import FakeClient
from lyr.models import Node
from lyr.store import InMemoryStore


def _sem(label: str) -> Node:
    return Node(layer="semantic", kind="event", label=label, identity=f"idn_{label}", evidence=[f"src_{label}"])


def _add(statement: str, evidence=(0,)) -> str:
    return json.dumps({"operation": "ADD", "statement": statement, "kind": "lesson",
                       "evidence": list(evidence), "target": None, "merge": []})


def _verdict(decision: str, **extra) -> str:
    return json.dumps({"verdict": decision, "confidence": 0.9, "reason": "test", **extra})


# ── verifier component in isolation --------------------------------------
def test_llm_verifier_keep_and_reject_parse():
    prop = ModelProposal(operation=ADD, statement="x", kind="lesson")
    keep = LLMDurabilityVerifier(FakeClient(_verdict("KEEP"))).verify(prop, [])
    assert keep.decision == "KEEP" and keep.status == SUCCESS
    rej = LLMDurabilityVerifier(FakeClient(_verdict("REJECT"))).verify(prop, [])
    assert rej.decision == REJECT and rej.status == SUCCESS


def test_llm_verifier_malformed_output_is_error_not_unsure():
    prop = ModelProposal(operation=ADD, statement="x", kind="lesson")
    v = LLMDurabilityVerifier(FakeClient("not json")).verify(prop, [])
    assert v.status == ERROR
    assert "malformed" in (v.error_reason or "")


def test_llm_verifier_illegal_verdict_is_error():
    prop = ModelProposal(operation=ADD, statement="x", kind="lesson")
    v = LLMDurabilityVerifier(FakeClient(_verdict("MAYBE"))).verify(prop, [])
    assert v.status == ERROR


def test_llm_verifier_client_exception_is_error():
    def boom(_p):
        raise TimeoutError("api timeout")
    prop = ModelProposal(operation=ADD, statement="x", kind="lesson")
    v = LLMDurabilityVerifier(FakeClient(boom)).verify(prop, [])
    assert v.status == ERROR
    assert "TimeoutError" in (v.error_reason or "")


# ── invocation rules via the builder gate --------------------------------
def _build(store, builder_resp, verifier):
    return JudgmentBuilder(store, FakeClient([builder_resp]), verifier=verifier)


def test_keep_commits_and_records_verdict():
    store = InMemoryStore()
    s0 = _sem("a"); store.add_node(s0)
    v = LLMDurabilityVerifier(FakeClient(_verdict("KEEP")))
    r = JudgmentBuilder(store, FakeClient([_add("Durable thing.")]), verifier=v).update([s0], [])
    assert r.updated_durable is not None
    assert r.engine_action.operation == ADD
    assert r.judgment_record.verification.decision == "KEEP"


def test_reject_vetoes_commit_as_noop():
    store = InMemoryStore()
    s0 = _sem("a"); store.add_node(s0)
    v = LLMDurabilityVerifier(FakeClient(_verdict("REJECT")))
    r = JudgmentBuilder(store, FakeClient([_add("Trivial coffee habit.")]), verifier=v).update([s0], [])
    assert r.updated_durable is None
    assert r.engine_action.operation == NO_OP
    assert "verifier REJECT" in (r.engine_action.rejection_reason or "")
    assert list(store.nodes(layer="durable")) == []       # nothing committed
    assert r.judgment_record.verification.decision == REJECT   # but recorded


def test_unsure_commits_flagged():
    store = InMemoryStore()
    s0 = _sem("a"); store.add_node(s0)
    v = LLMDurabilityVerifier(FakeClient(_verdict("UNSURE")))
    r = JudgmentBuilder(store, FakeClient([_add("Borderline thing.")]), verifier=v).update([s0], [])
    assert r.updated_durable is not None                   # retained
    assert r.updated_durable.attributes["verification"] == "unsure"
    assert r.engine_action.operation == ADD


def test_error_vetoes_commit_and_is_not_unsure():
    store = InMemoryStore()
    s0 = _sem("a"); store.add_node(s0)
    v = LLMDurabilityVerifier(FakeClient("garbage"))       # → status=ERROR
    r = JudgmentBuilder(store, FakeClient([_add("Something.")]), verifier=v).update([s0], [])
    assert r.updated_durable is None                        # NOT committed
    assert r.engine_action.operation == REJECT              # error → REJECT, not NO_OP
    assert "verifier ERROR" in (r.engine_action.rejection_reason or "")
    assert r.judgment_record.verification.status == ERROR


def test_verifier_not_called_on_builder_noop():
    store = InMemoryStore()
    s0 = _sem("a"); store.add_node(s0)
    # verifier would raise if called — proves it is skipped for NO_OP
    boom = LLMDurabilityVerifier(FakeClient(lambda _p: (_ for _ in ()).throw(AssertionError("called"))))
    resp = json.dumps({"operation": "NO_OP", "evidence": []})
    r = JudgmentBuilder(store, FakeClient([resp]), verifier=boom).update([s0], [])
    assert r.engine_action.operation == NO_OP
    assert r.judgment_record.verification is None           # never ran


def test_verifier_not_called_on_builder_reject():
    store = InMemoryStore()
    s0 = _sem("a"); store.add_node(s0)
    boom = LLMDurabilityVerifier(FakeClient(lambda _p: (_ for _ in ()).throw(AssertionError("called"))))
    bad = json.dumps({"operation": "ADD", "statement": "x", "evidence": [9]})  # out-of-range → builder REJECT
    r = JudgmentBuilder(store, FakeClient([bad]), verifier=boom).update([s0], [])
    assert r.engine_action.operation == REJECT
    assert r.judgment_record.verification is None


def test_no_verifier_is_unchanged_behavior():
    store = InMemoryStore()
    s0 = _sem("a"); store.add_node(s0)
    r = JudgmentBuilder(store, FakeClient([_add("Thing.")])).update([s0], [])  # no verifier
    assert r.updated_durable is not None
    assert r.judgment_record.verification is None


def test_threshold_control_rejects_low_confidence():
    store = InMemoryStore()
    s0 = _sem("a"); store.add_node(s0)
    resp = json.dumps({"operation": "ADD", "statement": "x", "kind": "lesson",
                       "evidence": [0], "confidence": 0.1})
    r = JudgmentBuilder(store, FakeClient([resp]),
                        verifier=ThresholdDurabilityVerifier(threshold=0.5)).update([s0], [])
    assert r.engine_action.operation == NO_OP              # low conf → control REJECT
    assert r.judgment_record.verification.decision == REJECT


def test_verdict_serializes_in_record():
    store = InMemoryStore()
    s0 = _sem("a"); store.add_node(s0)
    v = LLMDurabilityVerifier(FakeClient(_verdict("KEEP")))
    r = JudgmentBuilder(store, FakeClient([_add("Thing.")]), verifier=v).update([s0], [])
    d = r.judgment_record.to_dict()
    assert d["verification"]["decision"] == "KEEP"
    assert d["verification"]["status"] == SUCCESS
