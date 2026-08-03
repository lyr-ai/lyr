#!/usr/bin/env python3
"""Canonicalization Layer — Explorer-side presentation view over core output.

Reads the raw ``knowledge.json`` (LYR core output — never modified) and produces
a canonical *view* in which aliases of one entity are shown as one canonical
entity, preserving every original node id, version chain, evidence link, chapter
span, and merge provenance.

Grouping source (`--groups`):
  * **resolver** (default) — the generic ``lyr.semantic.resolution`` resolver.
    No per-book data. This is the runtime path.
  * **adapter** — a hand alias map (`--adapter`). Kept only for evaluation /
    comparison; it is no longer the runtime path.

    python explorer/pipeline/canonicalize.py \
        --in explorer/data/knowledge.full.json \
        --out explorer/data/knowledge.canonical.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from lyr.semantic.resolution import resolve  # noqa: E402


def _norm(s: str) -> str:
    return re.sub(r"[.,]", "", " ".join(str(s).split())).strip().casefold()


def _build_entities(groups: list[tuple[str, list[dict]]], src_chapter, via: str):
    """groups: list of (canonical_label, [raw entity node dicts])."""
    canon_entities, label_to_canon = [], {}
    merged = 0

    def chapters_for(evidence):
        return sorted({src_chapter[e] for e in evidence if src_chapter.get(e) is not None})

    for canon_label, nodes in groups:
        labels = [n["label"] for n in nodes]
        evidence = sorted({x for n in nodes for x in n["evidence"]})
        chapters = sorted({c for n in nodes for c in n.get("chapters", [])})
        timeline = []
        for n in nodes:
            for h in n.get("history", []):
                timeline.append({"alias": n["label"], "version": h["version"], "label": h["label"],
                                 "chapters": h.get("chapters", []), "evidence": h["evidence"]})
        # presentation timeline: chapter → version (Explorer-side; core history untouched)
        timeline.sort(key=lambda s: (s["chapters"][0] if s["chapters"] else 0, s["version"]))
        primary = max((n for n in nodes if _norm(n["label"]) == _norm(canon_label)),
                      default=max(nodes, key=lambda n: len(n["evidence"])),
                      key=lambda n: len(n["evidence"]))
        primary_versions = max((n["version"] for n in nodes), default=1)
        if len(nodes) > 1:
            merged += 1
        canon_entities.append({
            "canonical_label": canon_label,
            "entity_type": primary.get("attributes", {}).get("entity_type", "entity"),
            "aliases": sorted(set(labels)),
            "source_node_ids": [n["id"] for n in nodes],
            "evidence": evidence,
            "chapters": chapters,
            "primary_versions": primary_versions,          # headline number (main chain)
            "updates_across_aliases": len(timeline),        # secondary (sum across chains)
            "timeline": timeline,
            "merge": {"merged": len(nodes) > 1, "from": {n["label"]: n["id"] for n in nodes}, "via": via},
        })
        for lb in labels:
            label_to_canon[_norm(lb)] = canon_label
    canon_entities.sort(key=lambda x: -len(x["evidence"]))
    return canon_entities, label_to_canon, merged


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="explorer/data/knowledge.full.json")
    ap.add_argument("--out", default="explorer/data/knowledge.canonical.json")
    ap.add_argument("--groups", choices=["resolver", "adapter"], default="resolver")
    ap.add_argument("--adapter", default="explorer/adapters/pride-and-prejudice.aliases.json")
    args = ap.parse_args()

    k = json.loads(Path(args.inp).read_text(encoding="utf-8"))
    entities = k.get("entities", [])
    by_id = {e["id"]: e for e in entities}
    src_chapter = {s["id"]: s.get("chapter") for s in k.get("sources", [])}
    warnings: list[str] = []

    if args.groups == "resolver":
        r = resolve(entities, k.get("relationships", []))
        groups = [(g.canonical_label, [by_id[i] for i in g.member_ids if i in by_id]) for g in r.groups]
        via = "resolver:lyr.semantic.resolution"
        unsure = [(d.a, d.b) for d in r.decisions if d.decision == "UNSURE"]
        warnings += r.warnings
        source_note = f"generic resolver — {sum(1 for g in r.groups if len(g.member_ids) > 1)} merged, {len(unsure)} UNSURE candidates surfaced"
    else:
        adapter = json.loads(Path(args.adapter).read_text(encoding="utf-8"))
        alias_to_canon = {}
        for canon, aliases in adapter.get("canonical", {}).items():
            alias_to_canon[_norm(canon)] = canon
            for a in aliases:
                alias_to_canon[_norm(a)] = canon
        grouped: dict[str, list[dict]] = {}
        for e in entities:
            grouped.setdefault(alias_to_canon.get(_norm(e["label"]), e["label"]), []).append(e)
        groups = list(grouped.items())
        via = "adapter:" + adapter.get("book", "unknown")
        source_note = "hand adapter (EVAL ONLY — not the runtime path)"

    canon_entities, label_to_canon, merged = _build_entities(groups, src_chapter, via)

    rels = []
    for rel in k.get("relationships", []):
        a = dict(rel["attributes"])
        a["subject_canonical"] = label_to_canon.get(_norm(a.get("subject", "")), a.get("subject"))
        a["object_canonical"] = label_to_canon.get(_norm(a.get("object", "")), a.get("object"))
        rels.append({**rel, "attributes": a})

    meta = dict(k.get("meta", {}))
    meta["canonicalization"] = {"source": args.groups, "note": source_note,
                                "raw_entities": len(entities), "canonical_entities": len(canon_entities),
                                "merged_groups": merged, "warnings": warnings,
                                "detail": "Presentation-only. LYR core nodes/identities unchanged; provenance preserved per entity."}
    meta["themes"] = "not_yet_derived"
    out = {"meta": meta, "formation": k.get("formation", []), "entities": canon_entities,
           "events": k.get("events", []), "relationships": rels, "sources": k.get("sources", [])}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"groups: {args.groups}  |  raw entities {len(entities)} → canonical {len(canon_entities)}  ({merged} merged)")
    for e in canon_entities:
        if e["merge"]["merged"]:
            print(f"  {e['canonical_label']:26} ← {[a for a in e['aliases'] if a != e['canonical_label']]}")
    if warnings:
        print("warnings:", *warnings, sep="\n  ")
    print(f"✓ wrote {args.out}")


if __name__ == "__main__":
    main()
