#!/usr/bin/env python3
"""Per-case quality report — tells you WHERE a case fails, generically.

Reads a raw ``knowledge.json`` (entities/events/relationships/sources), runs the
generic resolver, and reports the numbers that separate an extractor failure from
a resolver failure from a representation gap from a UI problem:

    entities · canonical entities · merges / unsure / rejects · duplicate ratio ·
    events · relationships · evidence coverage · orphan entities · source types ·
    known capability gaps

    python explorer/pipeline/quality_report.py --in explorer/data/knowledge.full.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from lyr.semantic.resolution import resolve  # noqa: E402


def build_report(k: dict) -> dict:
    entities = k.get("entities", [])
    events = k.get("events", [])
    rels = k.get("relationships", [])
    sources = k.get("sources", [])

    r = resolve(entities, rels)
    dcount = {"LINK": 0, "UNSURE": 0, "REJECT": 0}
    for d in r.decisions:
        dcount[d.decision] = dcount.get(d.decision, 0) + 1
    canonical = len(r.groups)

    # evidence coverage: source records cited by at least one node
    src_ids = {s["id"] for s in sources}
    cited = set()
    for n in entities + events + rels:
        cited.update(x for x in n.get("evidence", []) if x in src_ids)
    coverage = round(100 * len(cited) / len(src_ids), 1) if src_ids else 0.0

    # orphan entities: appear in no relationship (and are the sole member of their group)
    in_rel = set()
    for rel in rels:
        a = rel.get("attributes", {})
        in_rel.add(a.get("subject")); in_rel.add(a.get("object"))
    in_rel_norm = {str(x).strip().casefold() for x in in_rel if x}
    orphans = [e["label"] for e in entities if e["label"].strip().casefold() not in in_rel_norm]

    src_types = sorted({s.get("kind", "?") for s in sources}) or ["?"]

    return {
        "entities_extracted": len(entities),
        "canonical_entities": canonical,
        "resolver": {"merges": sum(1 for g in r.groups if len(g.member_ids) > 1),
                     "link_pairs": dcount["LINK"], "unsure": dcount["UNSURE"], "rejects": dcount["REJECT"],
                     "guard_warnings": len(r.warnings)},
        "duplicate_ratio": round(len(entities) / canonical, 2) if canonical else None,
        "events": len(events),
        "relationships": len(rels),
        "sources": len(sources),
        "evidence_coverage_pct": coverage,
        "orphan_entities": {"count": len(orphans), "sample": orphans[:10]},
        "source_types": src_types,
        "claims_themes": k.get("meta", {}).get("themes", "not_derived"),
        "known_capability_gaps": [
            "stateful semantic claims — entity version chain is evidence accumulation, not interpretation change (docs/design/capability-gap-stateful-claims.md)",
            "themes / durable ideas — not_yet_derived (docs/design/canonicalization-and-identity.md)",
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="explorer/data/knowledge.full.json")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    k = json.loads(Path(args.inp).read_text(encoding="utf-8"))
    rep = build_report(k)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    res = rep["resolver"]
    print(f"entities {rep['entities_extracted']} → canonical {rep['canonical_entities']} "
          f"(dup ratio {rep['duplicate_ratio']}) | merges {res['merges']} · unsure {res['unsure']} · rejects {res['rejects']}")
    print(f"events {rep['events']} · relationships {rep['relationships']} · sources {rep['sources']} "
          f"· evidence coverage {rep['evidence_coverage_pct']}%")
    print(f"orphan entities: {rep['orphan_entities']['count']}  {rep['orphan_entities']['sample'][:6]}")
    print(f"source types: {rep['source_types']} · themes: {rep['claims_themes']}")
    if args.out:
        print(f"✓ wrote {args.out}")


if __name__ == "__main__":
    main()
