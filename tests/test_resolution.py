"""Generic entity-resolution rules — synthetic names only (CI-safe).

The real Pride-and-Prejudice fixture check lives in
experiments/entity-resolution/validate_pnp.py (needs the gitignored export).
These tests use made-up names to prove the domain-independent behaviour.
"""

from __future__ import annotations

from lyr.semantic.resolution import name_expands, resolve, title_conflict


def _E(i, label, t="person"):
    return {"id": i, "label": label, "entity_type": t, "evidence": [i], "chapters": [1]}


def _group_of(entities, rels=()):
    r = resolve(entities, rels)
    lg = {}
    for gi, g in enumerate(r.groups):
        for lb in g.member_labels:
            lg[lb] = gi
    return lg, r


def test_name_expansion_links_given_to_full():
    lg, _ = _group_of([_E("1", "Bob"), _E("2", "Bob Smith")])
    assert lg["Bob"] == lg["Bob Smith"]


def test_bare_surname_bridges_titled_and_named_forms():
    lg, _ = _group_of([_E("1", "Jones"), _E("2", "Mr. Jones"), _E("3", "Al Jones")])
    assert lg["Jones"] == lg["Mr. Jones"] == lg["Al Jones"]


def test_title_prefix_expansion_links():
    lg, _ = _group_of([_E("1", "Lady Anne"), _E("2", "Lady Anne Vale")])
    assert lg["Lady Anne"] == lg["Lady Anne Vale"]


def test_title_gender_conflict_never_merges():
    lg, _ = _group_of([_E("1", "Miss Stone"), _E("2", "Mr. Stone")])
    assert lg["Miss Stone"] != lg["Mr. Stone"]


def test_shared_surname_alone_is_unsure_not_merged():
    lg, r = _group_of([_E("1", "Mr. Reed"), _E("2", "Sara Reed")])
    assert lg["Mr. Reed"] != lg["Sara Reed"]
    assert any(d.decision == "UNSURE" for d in r.decisions)


def test_relationship_endpoints_stay_distinct_even_with_bridging_bare_form():
    # A bare "Vale" name-expands to BOTH "Anna Vale" and "Mrs. Vale", but a
    # mother-of relationship marks them distinct → the guard must not merge them.
    ents = [_E("1", "Anna Vale"), _E("2", "Vale"), _E("3", "Mrs. Vale")]
    rels = [{"attributes": {"subject": "Mrs. Vale", "object": "Anna Vale", "predicate": "mother of"}}]
    lg, _ = _group_of(ents, rels)
    assert lg["Mrs. Vale"] != lg["Anna Vale"]


def test_different_type_never_merges():
    lg, _ = _group_of([_E("1", "Rose"), _E("2", "Rose Manor", t="place")])
    assert lg["Rose"] != lg["Rose Manor"]


def test_helpers():
    assert title_conflict("Miss X", "Mr. X")
    assert not title_conflict("Anne", "Anne Vale")
    assert name_expands("Bob", "Bob Smith")
    assert not name_expands("Mrs. Reed", "Sara Reed")
