"""M3.2-A — the Evidence-Connectivity Baseline (form_navigation).

Deterministic structural tests. form_navigation takes list[Node] and NOTHING else —
no domain argument — so it cannot special-case a domain.
"""

from __future__ import annotations

from lyr.models import Node
from lyr.navigation import SHARED_SEMANTIC, SHARED_SOURCE, form_navigation


def _sem(label, source_id):
    return Node(layer="semantic", kind="event", label=label, identity=f"idn_{label}",
                evidence=[source_id])


def _dur(label, evidence):
    return Node(layer="durable", kind="lesson", label=label, identity=f"idn_{label}",
                evidence=list(evidence))


def test_no_domain_argument():
    import inspect
    params = list(inspect.signature(form_navigation).parameters)
    assert params == ["nodes"]   # the falsifier: it cannot be told the domain


def test_shared_semantic_groups_two_durables():
    s0, s1 = _sem("a", "src1"), _sem("b", "src2")
    d0 = _dur("D0", [s0.id, s1.id])
    d1 = _dur("D1", [s1.id])           # shares semantic s1 with d0
    g = form_navigation([s0, s1, d0, d1])
    assert g.n_groups == 1
    assert len(g.connections) == 1
    assert g.connections[0].relation == SHARED_SEMANTIC
    assert set(g.groups[0].members) == {d0.id, d1.id}


def test_shared_source_links_when_no_semantic_overlap():
    # two DIFFERENT semantic records from the SAME source
    s0, s1 = _sem("a", "srcX"), _sem("b", "srcX")
    d0 = _dur("D0", [s0.id])
    d1 = _dur("D1", [s1.id])           # disjoint semantic, but same source srcX
    g = form_navigation([s0, s1, d0, d1])
    assert g.n_groups == 1
    assert g.connections[0].relation == SHARED_SOURCE
    assert g.connections[0].support == ("srcX",)


def test_disjoint_evidence_yields_honest_singletons():
    s0, s1 = _sem("a", "src1"), _sem("b", "src2")
    d0, d1 = _dur("D0", [s0.id]), _dur("D1", [s1.id])
    g = form_navigation([s0, s1, d0, d1])
    assert g.n_groups == 2
    assert g.singletons == 2
    assert g.connections == []
    assert g.compression == 1.0        # generic, but no organization value — reported honestly


def test_schema_allows_multi_group_membership():
    # the baseline produces disjoint groups, but the data model must not forbid overlap
    from lyr.navigation import NavGroup
    g = NavGroup(id="grp_x", label="l", members=["a", "b"])
    g.members.append("c")              # members is a plain list — a node can be added to many
    assert g.members == ["a", "b", "c"]


def test_reproducible():
    s0, s1 = _sem("a", "srcX"), _sem("b", "srcX")
    d0, d1 = _dur("D0", [s0.id]), _dur("D1", [s1.id])
    a = form_navigation([s0, s1, d0, d1]).to_dict()
    b = form_navigation([d1, s1, d0, s0]).to_dict()   # different input order
    assert a == b                      # deterministic regardless of order


def test_entry_points_are_generic_facets():
    person = Node(layer="semantic", kind="entity", label="Ye Wenjie", identity="idn_p", evidence=["s"])
    ev = _sem("an event", "src1")
    d = _dur("D", [ev.id])
    g = form_navigation([person, ev, d])
    assert "Ye Wenjie" in g.entry_points["entity"]
    assert "an event" in g.entry_points["event"]
    assert g.entry_points["durable_kind"] == {"lesson": 1}


def test_retired_durable_excluded():
    from lyr.durable.base import RETIRED
    ev = _sem("a", "src1")
    active = _dur("A", [ev.id])
    retired = Node(layer="durable", kind="lesson", label="R", identity="idn_R",
                   evidence=[ev.id], attributes={"status": RETIRED})
    g = form_navigation([ev, active, retired])
    ids = {d["id"] for d in g.durables}
    assert active.id in ids and retired.id not in ids
