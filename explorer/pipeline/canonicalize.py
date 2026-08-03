#!/usr/bin/env python3
"""Canonicalization Layer — an Explorer-side, adapter-driven presentation pass.

It reads the raw ``knowledge.json`` (LYR core output — never modified) plus a
per-book alias adapter, and writes a canonical *view* in which obvious aliases of
one person are shown as one canonical entity. **LYR core identity semantics are
untouched**: every original node id, label, version chain, evidence link, and
chapter span is preserved inside the canonical entity, alongside merge
provenance. Swap the adapter to canonicalize a different source; this code does
not change (generic representation, domain-specific validation).

Safety: a merge is only accepted if it passes both guards, even when the adapter
lists it —
  1. no title conflict  (Mr./Sir/Colonel vs Mrs./Miss/Lady → refused),
  2. evidence link       (full-name expansion, or a shared significant token).
Anything that fails a guard stays split, and is reported. Duplication is safer
than a wrong merge.

    python explorer/pipeline/canonicalize.py \
        --in explorer/data/knowledge.full.json \
        --adapter explorer/adapters/pride-and-prejudice.aliases.json \
        --out explorer/data/knowledge.canonical.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MALE = {"mr", "sir", "colonel", "col", "lord", "master", "mister"}
FEMALE = {"mrs", "miss", "lady", "madam", "madame"}
TITLES = MALE | FEMALE


def _norm(s: str) -> str:
    return re.sub(r"[.,]", "", " ".join(str(s).split())).strip().casefold()


def _tokens(label: str) -> list[str]:
    return [re.sub(r"[.,]", "", t).casefold() for t in str(label).split()]


def _titles(label: str) -> set[str]:
    return {t for t in _tokens(label) if t in TITLES}


def _significant(label: str) -> set[str]:
    return {t for t in _tokens(label) if t not in TITLES and len(t) >= 3 and t.isalpha()}


def title_conflict(a: str, b: str) -> bool:
    ta, tb = _titles(a), _titles(b)
    return bool((ta & MALE and tb & FEMALE) or (ta & FEMALE and tb & MALE))


def evidence_linked(a: str, b: str) -> bool:
    """Full-name expansion (token subset) or a shared significant token."""
    sa, sb = _significant(a), _significant(b)
    if not sa or not sb:
        return False
    return sa <= sb or sb <= sa or bool(sa & sb)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="explorer/data/knowledge.full.json")
    ap.add_argument("--adapter", default="explorer/adapters/pride-and-prejudice.aliases.json")
    ap.add_argument("--out", default="explorer/data/knowledge.canonical.json")
    args = ap.parse_args()

    k = json.loads(Path(args.inp).read_text(encoding="utf-8"))
    adapter = json.loads(Path(args.adapter).read_text(encoding="utf-8"))

    # alias(normalized) -> canonical_label, from the adapter
    alias_to_canon: dict[str, str] = {}
    for canon, aliases in adapter.get("canonical", {}).items():
        alias_to_canon[_norm(canon)] = canon
        for a in aliases:
            alias_to_canon[_norm(a)] = canon

    entities = k.get("entities", [])
    warnings: list[str] = []

    # 1. assign each entity node to a canonical group (or itself), applying guards
    groups: dict[str, list[dict]] = {}
    for e in entities:
        canon = alias_to_canon.get(_norm(e["label"]))
        if canon and _norm(e["label"]) != _norm(canon):
            if title_conflict(e["label"], canon):
                warnings.append(f"REFUSED (title conflict): '{e['label']}' ✗→ '{canon}' — kept separate")
                canon = e["label"]
            elif not evidence_linked(e["label"], canon):
                warnings.append(f"REFUSED (no evidence link): '{e['label']}' ✗→ '{canon}' — kept separate")
                canon = e["label"]
        groups.setdefault(canon or e["label"], []).append(e)

    # report adapter aliases that never appeared in the data (misses, not errors)
    present = {_norm(e["label"]) for e in entities}
    for canon, aliases in adapter.get("canonical", {}).items():
        for a in [canon, *aliases]:
            if _norm(a) not in present:
                warnings.append(f"note: adapter alias '{a}' (→ {canon}) not found in this export")

    # 2. build canonical entities, preserving all provenance
    canon_entities = []
    label_to_canon: dict[str, str] = {}
    merged_count = 0
    for canon_label, nodes in groups.items():
        labels = [n["label"] for n in nodes]
        evidence = sorted({x for n in nodes for x in n["evidence"]})
        chapters = sorted({c for n in nodes for c in n.get("chapters", [])})
        timeline = []
        for n in nodes:
            for h in n.get("history", []):
                timeline.append(
                    {
                        "alias": n["label"],
                        "version": h["version"],
                        "label": h["label"],
                        "chapters": h.get("chapters", []),
                        "evidence": h["evidence"],
                    }
                )
        timeline.sort(key=lambda s: (s["chapters"][0] if s["chapters"] else 0, s["version"]))
        # attributes: prefer the node whose label == canonical, else the most-evidenced
        primary = max(
            (n for n in nodes if _norm(n["label"]) == _norm(canon_label)),
            default=max(nodes, key=lambda n: len(n["evidence"])),
            key=lambda n: len(n["evidence"]),
        )
        if len(nodes) > 1:
            merged_count += 1
        canon_entities.append(
            {
                "canonical_label": canon_label,
                "entity_type": primary.get("attributes", {}).get("entity_type", "person"),
                "aliases": sorted(set(labels)),
                "source_node_ids": [n["id"] for n in nodes],
                "evidence": evidence,
                "chapters": chapters,
                "n_updates": len(timeline),
                "timeline": timeline,
                "merge": {
                    "merged": len(nodes) > 1,
                    "from": {n["label"]: n["id"] for n in nodes},
                    "via": "adapter:" + adapter.get("book", "unknown"),
                },
            }
        )
        for lb in labels:
            label_to_canon[_norm(lb)] = canon_label
    canon_entities.sort(key=lambda x: -len(x["evidence"]))

    # 3. rewrite relationship endpoints to canonical labels (keep originals)
    rels = []
    for r in k.get("relationships", []):
        a = dict(r["attributes"])
        a["subject_canonical"] = label_to_canon.get(_norm(a.get("subject", "")), a.get("subject"))
        a["object_canonical"] = label_to_canon.get(_norm(a.get("object", "")), a.get("object"))
        rels.append({**r, "attributes": a})

    # 4. assemble the canonical view (Ideas intentionally omitted for v0.1)
    meta = dict(k.get("meta", {}))
    meta["canonicalization"] = {
        "adapter": Path(args.adapter).name,
        "raw_entities": len(entities),
        "canonical_entities": len(canon_entities),
        "merged_groups": merged_count,
        "warnings": warnings,
        "note": "Presentation-only. LYR core nodes/identities unchanged; provenance preserved per entity.",
    }
    meta["themes"] = "not_yet_derived"   # Ideas dropped from v0.1 (no real durable themes yet)
    out = {
        "meta": meta,
        "formation": k.get("formation", []),
        "entities": canon_entities,
        "events": k.get("events", []),
        "relationships": rels,
        "sources": k.get("sources", []),
    }
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # 5. console report
    print(f"raw entities: {len(entities)}  →  canonical: {len(canon_entities)}  "
          f"({merged_count} groups merged)")
    print("\nmerged groups:")
    for e in canon_entities:
        if e["merge"]["merged"]:
            print(f"  {e['canonical_label']:26} ← {', '.join(a for a in e['aliases'] if a != e['canonical_label'])}"
                  f"   [{e['n_updates']} updates · ch{e['chapters'][0]}–{e['chapters'][-1]} · ev={len(e['evidence'])}]")
    if warnings:
        print("\nwarnings / notes:")
        for w in warnings:
            print("  " + w)
    print(f"\n✓ wrote {args.out}")


if __name__ == "__main__":
    main()
