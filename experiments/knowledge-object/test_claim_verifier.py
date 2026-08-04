"""Unit tests for the structured-claim verifier — synthetic passages only."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from claim_verifier import Claim, verify  # noqa: E402
from grounding import CONTRADICTED, SUPPORTED, UNKNOWN, Passage  # noqa: E402


def P(i, t):
    return Passage(str(i), t)


def test_antonym_yields_contradicted():
    ps = [P(1, "Elizabeth refuses Mr. Darcy at the parsonage.")]
    v = verify(Claim("Elizabeth", "accepts", "Darcy", "", ("Elizabeth",), ("Darcy", "Mr. Darcy")), ps)
    assert v.status == CONTRADICTED


def test_matching_predicate_yields_supported():
    ps = [P(1, "Elizabeth refuses Mr. Darcy at the parsonage.")]
    v = verify(Claim("Elizabeth", "refuses", "Darcy", "", ("Elizabeth",), ("Darcy", "Mr. Darcy")), ps)
    assert v.status == SUPPORTED


def test_unsupported_derivation_is_unknown_not_contradicted():
    # absence of a stated derivation is UNKNOWN, never CONTRADICTED
    ps = [P(1, "DSA is a sparse attention mechanism."), P(2, "MLA is a latent attention mechanism.")]
    v = verify(Claim("DSA", "derives_from", "MLA", "", ("DSA",), ("MLA",)), ps)
    assert v.status == UNKNOWN


def test_unknown_predicate_family_abstains_even_if_both_present():
    ps = [P(1, "Prejudice and the letter both appear in this passage.")]
    v = verify(Claim("prejudice", "resolved_by", "letter", "", ("prejudice",), ("letter",)), ps)
    assert v.status == UNKNOWN  # 'resolved_by' has no polarity → abstain


def test_grouping_and_quantified():
    ps = [P(1, "MLA improves inference efficiency."), P(2, "DSA improves long-context efficiency."),
          P(3, "requires only 27% of FLOPs and 10% of KV cache.")]
    g = verify(Claim("g", "grouping", "", "", group_members=(("MLA",), ("DSA",)),
                     goal_terms=("efficiency",)), ps)
    q = verify(Claim("m", "quantified", "", "", value_tokens=("27%", "kv cache")), ps)
    assert g.status == SUPPORTED and q.status == SUPPORTED


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
