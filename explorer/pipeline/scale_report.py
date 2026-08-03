#!/usr/bin/env python3
"""Scale-run report — does identity failure grow linearly or explode with length?

Post-hoc (no extra API cost): given a knowledge.json, replays the generic resolver
at chapter checkpoints and reports how fragmentation grows. For the full 120-回 run
this answers the only question the scale test exists for — is the resolver's failure
bounded, linear, or super-linear as the corpus grows.

    python explorer/pipeline/scale_report.py --in explorer/data/hong-lou-meng.knowledge.json --step 20
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from lyr.semantic.resolution import resolve  # noqa: E402


def _minch(node) -> int:
    chs = node.get("chapters") or []
    return min(chs) if chs else 10**9


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--step", type=int, default=20)
    args = ap.parse_args()
    k = json.loads(Path(args.inp).read_text(encoding="utf-8"))
    ents, rels = k.get("entities", []), k.get("relationships", [])
    maxch = max((c for e in ents for c in e.get("chapters", [])), default=0)
    checkpoints = list(range(args.step, maxch + 1, args.step))
    if not checkpoints or checkpoints[-1] != maxch:
        checkpoints.append(maxch)

    print(f"{'thru ch':>8}{'raw':>7}{'canon':>7}{'dup':>7}{'unsure':>8}{'orphans':>9}")
    print("-" * 46)
    rows = []
    for C in checkpoints:
        e_c = [e for e in ents if _minch(e) <= C]
        r_c = [r for r in rels if _minch(r) <= C]
        res = resolve(e_c, r_c)
        canon = len(res.groups)
        raw = len(e_c)
        dup = round(raw / canon, 3) if canon else 0
        unsure = sum(1 for d in res.decisions if d.decision == "UNSURE")
        in_rel = set()
        for r in r_c:
            a = r.get("attributes", {})
            in_rel.add(str(a.get("subject", "")).strip().casefold())
            in_rel.add(str(a.get("object", "")).strip().casefold())
        orphans = sum(1 for e in e_c if e["label"].strip().casefold() not in in_rel)
        rows.append((C, raw, canon, dup))
        print(f"{C:>8}{raw:>7}{canon:>7}{dup:>7}{unsure:>8}{orphans:>9}")

    # growth verdict: compare raw-entity increment per checkpoint (linear vs accelerating)
    if len(rows) >= 3:
        incs = [rows[i][1] - rows[i - 1][1] for i in range(1, len(rows))]
        trend = "accelerating (super-linear — fragmentation explodes)" if incs[-1] > 1.5 * incs[0] \
            else "decelerating (saturating)" if incs[-1] < 0.66 * incs[0] \
            else "roughly linear"
        print(f"\nraw-entity growth per {args.step} ch: {incs}  →  {trend}")
        print("dup ratio trend:", [r[3] for r in rows],
              "— flat ≈ resolver never catches up (fragmentation ∝ raw entities)")
    else:
        print("\n(need ≥3 checkpoints for a growth verdict — run the full book)")


if __name__ == "__main__":
    main()
