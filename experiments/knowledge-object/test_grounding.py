"""Unit tests for the evidence-grounded status verifier — synthetic passages only."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from grounding import (SUPPORTED, UNKNOWN, Passage, ground_derivation,  # noqa: E402
                       ground_grouping, ground_value)


def P(i, t):
    return Passage(id=str(i), text=t)


def test_derivation_supported_when_stated():
    ps = [P(1, "The Foo optimizer improves upon Bar with a new technique.")]
    c = ground_derivation(("Foo",), ("Bar",), ps)
    assert c.status == SUPPORTED and c.evidence == ["1"]


def test_derivation_abstains_when_both_present_but_no_cue():
    # both endpoints, but "combines … to improve" is NOT a derivation between them
    ps = [P(1, "A hybrid that combines Alpha and Beta to improve long-context efficiency.")]
    c = ground_derivation(("Alpha",), ("Beta",), ps)
    assert c.status == UNKNOWN


def test_derivation_abstains_when_only_one_endpoint():
    ps = [P(1, "Gamma builds upon the previous model release.")]  # Delta absent
    c = ground_derivation(("Gamma",), ("Delta",), ps)
    assert c.status == UNKNOWN


def test_word_boundary_does_not_conflate_substring():
    # the critical case: 'Muon' must NOT match inside 'MuonClip'
    ps = [P(1, "MuonClip is a standalone optimizer name here.")]  # no standalone 'Muon'
    c = ground_derivation(("MuonClip",), ("Muon",), ps)
    assert c.status == UNKNOWN  # Muon endpoint not actually present


def test_word_boundary_supports_when_both_really_present():
    ps = [P(1, "The MuonClip optimizer, which improves upon Muon, is stable.")]
    c = ground_derivation(("MuonClip",), ("Muon",), ps)
    assert c.status == SUPPORTED


def test_grouping_supported_with_two_members_and_goal():
    ps = [P(1, "MLA improves inference efficiency."), P(2, "DSA improves long-context efficiency.")]
    c = ground_grouping([("MLA",), ("DSA",)], ("efficiency",), ps)
    assert c.status == SUPPORTED


def test_grouping_abstains_with_one_member():
    ps = [P(1, "MLA improves inference efficiency."), P(2, "DSA is a sparse mechanism.")]
    c = ground_grouping([("MLA",), ("DSA",)], ("efficiency",), ps)
    assert c.status == UNKNOWN  # only MLA co-occurs with the goal term


def test_value_supported_when_all_tokens_present():
    ps = [P(1, "requires only 27% of FLOPs and 10% of KV cache compared with the prior model.")]
    c = ground_value(("27%", "kv cache"), ps)
    assert c.status == SUPPORTED


def test_value_abstains_when_token_missing():
    ps = [P(1, "requires far less compute than the prior model.")]
    c = ground_value(("27%", "kv cache"), ps)
    assert c.status == UNKNOWN


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    ok = 0
    for f in fns:
        try:
            f()
            ok += 1
        except AssertionError as e:
            print("FAIL", f.__name__, e)
    print(f"{ok}/{len(fns)} passed")
