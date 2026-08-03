#!/usr/bin/env python3
"""Phase 4 — run the GENERIC resolver against the first real corpus + gold fixture.

Success = recover every accepted group, reject every title-conflict pair, using
no book-specific logic. Reads the raw (label-fragmented) knowledge.json; skips
gracefully if it isn't present (it is gitignored / regenerated locally).

    python experiments/entity-resolution/validate_pnp.py [path-to-knowledge.json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from lyr.semantic.resolution import resolve  # noqa: E402

RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "explorer/data/knowledge.full.json"
GOLD = REPO / "experiments/entity-resolution/pnp-gold.json"


def main() -> int:
    if not RAW.exists():
        print(f"skip: {RAW} not found (regenerate with explorer/run.py). Resolver unit tests still run in CI.")
        return 0
    k = json.loads(RAW.read_text(encoding="utf-8"))
    gold = json.loads(GOLD.read_text(encoding="utf-8"))

    result = resolve(k.get("entities", []), k.get("relationships", []))
    # label -> group index
    g_of: dict[str, int] = {}
    for gi, g in enumerate(result.groups):
        for lb in g.member_labels:
            g_of[lb] = gi

    print(f"raw entities: {len(k.get('entities', []))}  →  resolved groups: {len(result.groups)}")
    ok = True

    print("\nPOSITIVES (must all land in ONE group):")
    for grp in gold["positives"]:
        present = [lb for lb in grp if lb in g_of]
        roots = {g_of[lb] for lb in present}
        passed = len(present) >= 2 and len(roots) == 1
        ok &= passed
        canon = result.groups[next(iter(roots))].canonical_label if roots else "—"
        print(f"  [{'✓' if passed else '✗'}] {grp}  → {'one group: ' + repr(canon) if passed else 'SPLIT/absent ' + str(roots)}")

    print("\nNEGATIVES (must be in DIFFERENT groups):")
    for a, b in gold["negatives"]:
        if a in g_of and b in g_of:
            passed = g_of[a] != g_of[b]
            print(f"  [{'✓' if passed else '✗'}] {a} ≠ {b}  → {'separate' if passed else 'WRONGLY MERGED'}")
            ok &= passed
        else:
            print(f"  [–] {a} / {b}  → one absent from this run (cannot test)")

    merged = [g for g in result.groups if len(g.member_ids) > 1]
    print(f"\nmerged groups ({len(merged)}):")
    for g in merged:
        print(f"  {g.canonical_label:26} ← {[l for l in g.member_labels if l != g.canonical_label]}")
    unsure = [d for d in result.decisions if d.decision == "UNSURE"]
    if unsure:
        print(f"\nUNSURE candidates (surfaced, NOT merged) — {len(unsure)}:")
        for d in unsure[:12]:
            print(f"  {d.a}  ?  {d.b}")
    if result.warnings:
        print("\nwarnings:")
        for w in result.warnings:
            print("  " + w)

    print("\n" + ("✓ PASS — generic resolver matches the fixture" if ok else "✗ FAIL — see marks above"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
