#!/usr/bin/env python3
"""Phase 5 — cross-domain smoke test (git / incident), self-contained.

Runs the SAME generic resolver on a tiny synthetic git/incident fixture, with no
resolver changes per domain. Answers: does it recover clear identifier aliases,
stay conservative on ambiguous shorthand, and avoid book-oriented assumptions
dominating outside books?

    python experiments/entity-resolution/validate_git.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from lyr.semantic.resolution import resolve  # noqa: E402

FX = REPO / "experiments/entity-resolution/git-gold.json"


def main() -> int:
    fx = json.loads(FX.read_text())
    r = resolve(fx["entities"], fx.get("relationships", []))
    lg = {}
    for gi, g in enumerate(r.groups):
        for lb in g.member_labels:
            lg[lb] = gi

    ok = True
    print("expect SAME (clear aliases recovered):")
    for a, b in fx["expect_same"]:
        p = a in lg and b in lg and lg[a] == lg[b]
        ok &= p
        print(f"  [{'✓' if p else '✗'}] {a} == {b}")
    print("expect DIFFERENT (conservative / no false merge):")
    for a, b in fx["expect_different"]:
        p = lg.get(a) != lg.get(b)
        ok &= p
        print(f"  [{'✓' if p else '✗'}] {a} != {b}")

    merged = [(g.canonical_label, g.member_labels) for g in r.groups if len(g.member_ids) > 1]
    print(f"\nmerged: {merged}")
    print("UNSURE candidates:", [(d.a, d.b) for d in r.decisions if d.decision == "UNSURE"])
    print("\n" + ("✓ PASS — generic across a second domain (no per-domain code)" if ok else "✗ FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
