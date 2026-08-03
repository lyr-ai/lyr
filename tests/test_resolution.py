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


# --- cross-domain (git / incident) — Phase 5 behaviour, generic names ---

def test_identifier_tokenization_exact_match():
    lg, _ = _group_of([_E("1", "Payments Service", "service"), _E("2", "payments-service", "service")])
    assert lg["Payments Service"] == lg["payments-service"]


def test_file_extension_is_prefix_link():
    lg, _ = _group_of([_E("1", "README", "file"), _E("2", "README.md", "file")])
    assert lg["README"] == lg["README.md"]


def test_component_substring_is_unsure_not_merged():
    lg, r = _group_of([_E("1", "api-gateway", "service"), _E("2", "gateway", "service")])
    assert lg["api-gateway"] != lg["gateway"]
    assert any(d.decision == "UNSURE" for d in r.decisions)


def test_cjk_name_expansion_links_given_to_full():
    # space-less script: a >=2-char given name is a suffix of surname+given
    lg, _ = _group_of([_E("1", "玉明"), _E("2", "李玉明")])
    assert lg["玉明"] == lg["李玉明"]


def test_cjk_two_char_surname_ok():
    lg, _ = _group_of([_E("1", "玉明"), _E("2", "歐陽玉明")])
    assert lg["玉明"] == lg["歐陽玉明"]


def test_cjk_ambiguous_bare_form_never_merges_two_people():
    # a bare given-name fitting TWO surnames must stay UNSURE (红楼梦: 甄寶玉/賈寶玉)
    lg, r = _group_of([_E("1", "玉明"), _E("2", "李玉明"), _E("3", "王玉明")])
    assert lg["李玉明"] != lg["王玉明"]
    assert any(d.decision == "UNSURE" and d.reason == "ambiguous CJK short form" for d in r.decisions)


def test_cjk_type_conflict_not_merged():
    # 寶玉 (person) is a suffix of 通靈寶玉 (concept) — different type, no merge
    lg, _ = _group_of([_E("1", "寶玉", "person"), _E("2", "通靈寶玉", "concept")])
    assert lg["寶玉"] != lg["通靈寶玉"]


# --- fix D: versioned-entity identity (digit-bearing added token = sibling) ---

def test_version_suffix_not_auto_merged():
    # DeepSeek-V3 ⊂ DeepSeek-V3.2 is a sibling RELEASE, not a name expansion.
    lg, r = _group_of([_E("1", "DeepSeek-V3", "model"), _E("2", "DeepSeek-V3.2", "model")])
    assert lg["DeepSeek-V3"] != lg["DeepSeek-V3.2"]
    assert any(d.decision == "UNSURE" and d.reason == "version discriminator" for d in r.decisions)


def test_version_chain_stays_distinct():
    # the witnessed cross-version false merge must not recur: distinct version
    # NUMBERS land in distinct groups. (Within-version word qualifiers like
    # -Base / -Exp / -Speciale still merge — the documented residual, digit-only.)
    labels = ["DeepSeek-V3", "DeepSeek-V3-Base", "DeepSeek-V3.1-Terminus",
              "DeepSeek-V3.2-Exp", "DeepSeek-V3.2", "DeepSeek-V3.2-Speciale"]
    lg, _ = _group_of([_E(str(i), l, "model") for i, l in enumerate(labels)])
    # the three version points V3, V3.1, V3.2 are pairwise distinct (was 1 group)
    assert lg["DeepSeek-V3"] != lg["DeepSeek-V3.1-Terminus"]
    assert lg["DeepSeek-V3.1-Terminus"] != lg["DeepSeek-V3.2"]
    assert lg["DeepSeek-V3"] != lg["DeepSeek-V3.2"]
    assert len({lg[l] for l in labels}) >= 3  # was 1 before fix D


def test_numeric_dotted_version_not_merged():
    lg, _ = _group_of([_E("1", "Model 2", "system"), _E("2", "Model 2.1", "system")])
    assert lg["Model 2"] != lg["Model 2.1"]


def test_same_normalized_version_still_links():
    # punctuation/spacing only — same tokens, same entity: MUST still LINK
    lg, _ = _group_of([_E("1", "DeepSeek-V3.2", "model"), _E("2", "DeepSeek V3.2", "model")])
    assert lg["DeepSeek-V3.2"] == lg["DeepSeek V3.2"]


def test_file_extension_added_token_has_no_digit_still_links():
    # README ⊂ README.md — added token "md" has no digit → remains a LINK
    lg, _ = _group_of([_E("1", "README", "file"), _E("2", "README.md", "file")])
    assert lg["README"] == lg["README.md"]


def test_person_version_like_suffix_unaffected():
    # a person is never demoted by the digit rule (guarded on non-person)
    lg, _ = _group_of([_E("1", "Henry", "person"), _E("2", "Henry 3rd", "person")])
    assert lg["Henry"] == lg["Henry 3rd"]


def test_word_qualifier_variant_is_known_residual_still_links():
    # DOCUMENTED residual: V4-Pro ⊂ V4-Pro-Max adds "max" (no digit), so digit-only
    # fix D does NOT demote it — it still LINKs. Recorded, not silently accepted:
    # see docs/design/witness-versioned-entity-false-merge.md (deferred to a future
    # metadata-aware variant signal, NOT a pro/max/flash wordlist). If a later fix
    # changes this, this test should be updated intentionally.
    lg, _ = _group_of([_E("1", "V4-Pro", "model"), _E("2", "V4-Pro-Max", "model")])
    assert lg["V4-Pro"] == lg["V4-Pro-Max"]


def test_bare_form_links_person_but_not_component():
    # identical structural shape (X ⊆ "<w> X"), opposite decision by entity type
    lg_p, _ = _group_of([_E("1", "Vale", "person"), _E("2", "George Vale", "person")])
    assert lg_p["Vale"] == lg_p["George Vale"]
    lg_s, _ = _group_of([_E("3", "cache", "service"), _E("4", "redis-cache", "service")])
    assert lg_s["cache"] != lg_s["redis-cache"]
