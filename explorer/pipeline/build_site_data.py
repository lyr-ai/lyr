#!/usr/bin/env python3
"""Build the Explorer's publishable data package from the canonical knowledge.

Splits knowledge.canonical.json into a small, versioned package the static page
loads on demand (the homepage never downloads the whole book):

    site/data/pride-and-prejudice/
      manifest.json          data version, provenance, counts, honest framing
      people.json            list-page rows (slug, label, aliases, coverage)
      people/<slug>.json     a person's Story Timeline (observations) + inline evidence

The Timeline is built from REAL, chapter-stamped relationships and events involving
the person — never from the (evidence-only) version chain. Each step is an
observation with its source passages, not a psychological conclusion.

    python explorer/pipeline/build_site_data.py \
        --in explorer/data/knowledge.canonical.json \
        --out site/data/pride-and-prejudice
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def _norm(s: str) -> str:
    return re.sub(r"[.,]", "", " ".join(str(s).split())).strip().casefold()


def _slug(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.casefold()).strip("-")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=str(REPO / "explorer/data/knowledge.canonical.json"))
    ap.add_argument("--case-id", default="pride-and-prejudice")
    ap.add_argument("--title", default="Pride and Prejudice")
    ap.add_argument("--entity-types", default="all", help="'all' or a specific type e.g. 'person'")
    ap.add_argument("--out", default="", help="default site/data/<case-id>")
    ap.add_argument("--commit", default="", help="optional generation commit sha")
    args = ap.parse_args()

    k = json.loads(Path(args.inp).read_text(encoding="utf-8"))
    out = Path(args.out) if args.out else (REPO / "site/data" / args.case_id)
    (out / "people").mkdir(parents=True, exist_ok=True)

    src = {s["id"]: s for s in k.get("sources", [])}
    entities = [e for e in k["entities"]
                if args.entity_types == "all" or e.get("entity_type") == args.entity_types]
    canon_by_norm = {}
    for e in k["entities"]:
        for a in e["aliases"]:
            canon_by_norm[_norm(a)] = e["canonical_label"]
        canon_by_norm[_norm(e["canonical_label"])] = e["canonical_label"]

    def passages(ev_ids, limit=6):
        out_p = []
        for sid in ev_ids[:limit]:
            s = src.get(sid)
            if s:
                out_p.append({"id": sid, "chapter": s.get("chapter"), "text": s.get("content", "")})
        return out_p

    rels = k.get("relationships", [])
    events = k.get("events", [])

    people_rows = []
    for e in entities:
        canon = e["canonical_label"]
        ev = set(e["evidence"])
        steps = []

        # relationships involving this person (subject or object, canonicalized)
        for r in rels:
            a = r["attributes"]
            subj, obj = a.get("subject_canonical"), a.get("object_canonical")
            if _norm(subj) == _norm(canon) or _norm(obj) == _norm(canon):
                other = obj if _norm(subj) == _norm(canon) else subj
                text = r.get("label") or f"{a.get('subject','')} {a.get('predicate','')} {a.get('object','')}".strip()
                chs = r.get("chapters", [])
                steps.append({
                    "chapter": chs[0] if chs else None,
                    "kind": "relationship",
                    "text": text,
                    "other": other,
                    "evidence_count": len(r.get("evidence", [])),
                    "passages": passages(r.get("evidence", [])),
                })

        # events that actually NAME this person (participant or in the label) —
        # shared-evidence alone was too noisy (incidental co-occurrence).
        names = [canon] + e["aliases"]
        for ev_node in events:
            parts = ev_node.get("attributes", {}).get("participants", []) or []
            named = any(canon_by_norm.get(_norm(p)) == canon or _norm(p) == _norm(canon) for p in parts)
            label_hit = any(_norm(n) in _norm(ev_node.get("label", "")) for n in names)
            if named or label_hit:
                chs = ev_node.get("chapters", [])
                steps.append({
                    "chapter": chs[0] if chs else None,
                    "kind": "event",
                    "text": ev_node.get("label", ""),
                    "other": None,
                    "evidence_count": len(ev_node.get("evidence", [])),
                    "passages": passages(ev_node.get("evidence", [])),
                })

        steps.sort(key=lambda s: (s["chapter"] if s["chapter"] is not None else 9999, s["kind"]))
        chapters = e.get("chapters", [])
        n_rel = sum(1 for s in steps if s["kind"] == "relationship")
        n_ev = sum(1 for s in steps if s["kind"] == "event")

        person = {
            "slug": _slug(canon),
            "canonical_label": canon,
            "aliases": e["aliases"],
            "entity_type": e["entity_type"],
            "summary": {
                "chapter_min": chapters[0] if chapters else None,
                "chapter_max": chapters[-1] if chapters else None,
                "evidence_passages": len(e["evidence"]),
                "relationships": n_rel,
                "events": n_ev,
                "note": "Version count reflects evidence accumulation, not interpretation change.",
                "primary_versions": e.get("primary_versions"),
            },
            "timeline": steps,
        }
        (out / "people" / f"{person['slug']}.json").write_text(
            json.dumps(person, ensure_ascii=False, indent=2), encoding="utf-8")

        if steps:  # only list people who actually have a timeline
            people_rows.append({
                "slug": person["slug"],
                "label": canon,
                "aliases": e["aliases"],
                "evidence_passages": len(e["evidence"]),
                "chapter_min": chapters[0] if chapters else None,
                "chapter_max": chapters[-1] if chapters else None,
                "relationships": n_rel,
                "events": n_ev,
            })

    people_rows.sort(key=lambda r: -r["evidence_passages"])
    (out / "people.json").write_text(json.dumps(people_rows, ensure_ascii=False, indent=2), encoding="utf-8")

    meta = k.get("meta", {})
    manifest = {
        "product": "LYR — Living Knowledge Explorer",
        "framing": "A traceable knowledge space formed from the text.",
        "case_id": args.case_id,
        "demo_source": args.title,
        "public_domain": True,
        "extractor": meta.get("extractor"),
        "identity_resolution": "generic entity resolution v0 — production path for Explorer v0.1; persistent, evolving identity formation remains future work",
        "canonicalization": meta.get("canonicalization", {}).get("source"),
        "people": len(people_rows),
        "chapters": (meta.get("chapters_processed") or meta.get("totals", {}).get("chapters")),
        "themes": {"status": "not_yet_derived"},
        "known_gap": "Version chain is evidence accumulation, not interpretation change — see docs/design/capability-gap-stateful-claims.md",
        "generation_commit": args.commit or None,
        "data_version": "0.1",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✓ wrote {out}/  — {len(people_rows)} entities with timelines")
    for r in people_rows[:6]:
        print(f"    {r['label']:24} ch{r['chapter_min']}–{r['chapter_max']}  "
              f"{r['relationships']} rel · {r['events']} ev · {r['evidence_passages']} passages")


if __name__ == "__main__":
    main()
