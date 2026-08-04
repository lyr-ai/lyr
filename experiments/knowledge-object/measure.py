#!/usr/bin/env python3
"""Measure the baseline verifier against the four hand-probes' ground truth.

The discriminating test: the SAME verifier must **abstain** DeepSeek's unstated attention
lineage (Prototype 1) yet **support** Kimi's stated `MuonClip improves upon Muon`
(Prototype 4). If one rule does both, the status enum commits/abstains by evidence — the
zero-fabrication property the exploration set out to check a system could have.

    python experiments/knowledge-object/measure.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

from grounding import (SUPPORTED, UNKNOWN, Passage, ground_derivation,  # noqa: E402
                       ground_grouping, ground_value)


def load_passages(case_dir: Path, prefix: str) -> list[Passage]:
    """Every blank-line-separated block of every .md doc is a passage."""
    out: list[Passage] = []
    for md in sorted(case_dir.glob("*.md")):
        if md.name in ("SOURCES.md", "CORPUS.md"):
            continue
        blocks = [b.strip() for b in md.read_text(encoding="utf-8").split("\n\n") if b.strip()]
        for i, b in enumerate(blocks):
            out.append(Passage(id=f"{prefix}/{md.stem}#p{i}", text=b))
    return out


MLA = ("MLA", "Multi-head Latent Attention")
DSA = ("DSA", "DeepSeek Sparse Attention")
CSA = ("CSA", "Compressed Sparse Attention")
HCA = ("HCA", "Heavily Compressed Attention")
MUON = ("Muon",)
MUONCLIP = ("MuonClip",)


def main() -> None:
    ds = load_passages(REPO / "explorer/cases/deepseek", "deepseek")
    km = load_passages(REPO / "explorer/cases/kimi", "kimi")

    # (name, computed Claim, expected status)  — expected = hand-probe ground truth
    cases = [
        # DeepSeek Concept (Prototype 1): group forms; lineage abstains; quantified holds
        ("DeepSeek grouping (MLA/DSA/CSA/HCA by efficiency)",
         ground_grouping([MLA, DSA, CSA, HCA],
                         ("efficiency", "long-context", "long context", "kv cache", "inference"),
                         ds), SUPPORTED),
        ("DeepSeek derivation MLA→DSA (must abstain)", ground_derivation(DSA, MLA, ds), UNKNOWN),
        ("DeepSeek derivation DSA→CSA (must abstain)", ground_derivation(CSA, DSA, ds), UNKNOWN),
        ("DeepSeek derivation CSA→HCA (must abstain)", ground_derivation(HCA, CSA, ds), UNKNOWN),
        ("DeepSeek quantified (27% / KV cache)",
         ground_value(("27%", "kv cache"), ds, target="V4-Pro", scope="vs V3.2"), SUPPORTED),
        # Kimi (Prototype 4): the stated derivation must COMMIT — the positive control
        ("Kimi derivation MuonClip→Muon (must support)",
         ground_derivation(MUONCLIP, MUON, km), SUPPORTED),
    ]

    print(f"loaded {len(ds)} DeepSeek + {len(km)} Kimi passages\n")
    print(f"{'expected':>9}  {'got':>9}  ok  case")
    print("-" * 78)
    ok = 0
    fabrications = 0
    over_abstentions = 0
    for name, claim, expected in cases:
        good = claim.status == expected
        ok += good
        if not good and expected == UNKNOWN and claim.status == SUPPORTED:
            fabrications += 1
        if not good and expected == SUPPORTED and claim.status == UNKNOWN:
            over_abstentions += 1
        print(f"{expected:>9}  {claim.status:>9}  {'✓' if good else '✗'}   {name}")
        print(f"{'':>22}      └ {claim.reason}  {claim.evidence}")

    print("-" * 78)
    print(f"score: {ok}/{len(cases)} match the hand-probe ground truth")
    print(f"fabrications (abstain expected, SUPPORTED got): {fabrications}")
    print(f"over-abstentions (SUPPORTED expected, abstain got): {over_abstentions}")
    verdict = ("PASS — the verifier commits and abstains by evidence, on both corpora"
               if ok == len(cases) else "FAIL — see mismatches above")
    print(f"\n{verdict}")
    sys.exit(0 if ok == len(cases) else 1)


if __name__ == "__main__":
    main()
