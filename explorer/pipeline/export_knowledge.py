#!/usr/bin/env python3
"""Week 1 — export a real ``knowledge.json`` from the LYR pipeline.

Runs the **actual** LYR engine (ingest → semantic → durable → provenance) over a
long-form source, chapter by chapter, and writes the knowledge space the
explorer renders. Every number in the output is a real pipeline output — this
script never hand-authors knowledge.

Two extractors:
  --extractor rule   (default)  RuleBasedExtractor — no API key; entities + events
                                only (crude, but real). A baseline / plumbing proof.
  --extractor llm    LLMExtractor — needs an API key; adds relationships and
                                higher-quality events/ideas. The demo-quality path.

    # baseline, no key:
    python explorer/pipeline/export_knowledge.py --limit 6 --out explorer/data/knowledge.sample.json
    # demo quality (your key):
    ANTHROPIC_API_KEY=... python explorer/pipeline/export_knowledge.py \
        --extractor llm --provider anthropic --out explorer/data/knowledge.full.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

from chapters import split_chapters  # noqa: E402
from lyr import LYR  # noqa: E402
from lyr.semantic import RuleBasedExtractor  # noqa: E402

KINDS = ("entity", "event", "relationship")


def _client(provider: str):
    if provider == "anthropic":
        from lyr.llm.anthropic import AnthropicClient
        return AnthropicClient()
    if provider == "openai":
        from lyr.llm.openai import OpenAIClient
        return OpenAIClient()
    raise SystemExit(f"unknown provider {provider!r}")


def _tally(nodes) -> dict[str, int]:
    c = {k: 0 for k in KINDS}
    for n in nodes:
        if n.kind in c:
            c[n.kind] += 1
    return c


def _chapter_of(origin: str) -> int | None:
    # origin is "pnp-chNN"
    tail = origin.rsplit("ch", 1)[-1]
    return int(tail) if tail.isdigit() else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=str(REPO / "explorer/data/pride-and-prejudice.raw.txt"))
    ap.add_argument("--out", default=str(REPO / "explorer/data/knowledge.sample.json"))
    ap.add_argument("--extractor", choices=["rule", "llm"], default="rule")
    ap.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    ap.add_argument("--limit", type=int, default=0, help="max chapters (0 = all)")
    args = ap.parse_args()

    raw = Path(args.source).read_text(encoding="utf-8", errors="replace")
    chapters = split_chapters(raw)
    if args.limit:
        chapters = chapters[: args.limit]
    if not chapters:
        raise SystemExit("no chapters parsed — check --source")

    extractor = (
        RuleBasedExtractor()
        if args.extractor == "rule"
        else __import__("lyr.semantic", fromlist=["LLMExtractor"]).LLMExtractor(_client(args.provider))
    )
    lyr = LYR(extractor=extractor)

    # ── run the real pipeline, chapter by chapter, snapshotting growth ──
    formation = []
    prev = {k: 0 for k in KINDS}
    for ch in chapters:
        lyr.ingest(ch.text, origin=f"pnp-ch{ch.number:02d}", kind="book", chapter=ch.number)
        cur = _tally(lyr.semantic_nodes())
        formation.append(
            {
                "chapter": ch.number,
                "roman": ch.roman,
                "entities": cur["entity"],
                "events": cur["event"],
                "relationships": cur["relationship"],
                "new_entities": cur["entity"] - prev["entity"],
                "new_events": cur["event"] - prev["event"],
                "new_relationships": cur["relationship"] - prev["relationship"],
            }
        )
        prev = cur
        print(f"  ch{ch.number:>2} ({ch.roman:<6}) entities={cur['entity']:>4} "
              f"events={cur['event']:>4} relationships={cur['relationship']:>4}")

    print("consolidating durable knowledge…")
    lyr.build_durable()
    ideas = list(lyr.durable_memories())

    # ── assemble the export ──
    src_chapter: dict[str, int | None] = {}
    sources = []
    for r in lyr.store.sources():
        ch = _chapter_of(r.origin)
        src_chapter[r.id] = ch
        sources.append({"id": r.id, "chapter": ch, "position": r.position, "content": r.content})
    sources.sort(key=lambda s: (s["chapter"] or 0, s["position"]))

    def _chapters_for(evidence: list[str]) -> list[int]:
        return sorted({src_chapter[e] for e in evidence if src_chapter.get(e) is not None})

    def _history(identity: str) -> list[dict]:
        out = []
        for v in lyr.store.versions(identity):
            out.append(
                {
                    "version": v.version,
                    "label": v.label,
                    "evidence": list(v.evidence),
                    "chapters": _chapters_for(list(v.evidence)),
                }
            )
        return out

    buckets: dict[str, list] = {k: [] for k in KINDS}
    for n in lyr.semantic_nodes():
        if n.kind not in buckets:
            continue
        buckets[n.kind].append(
            {
                "id": n.id,
                "identity": n.identity,
                "kind": n.kind,
                "label": n.label,
                "attributes": n.attributes,
                "evidence": list(n.evidence),
                "chapters": _chapters_for(list(n.evidence)),
                "version": n.version,
                "history": _history(n.identity),
            }
        )
    for k in KINDS:
        buckets[k].sort(key=lambda x: (x["chapters"][0] if x["chapters"] else 0, -len(x["evidence"])))

    idea_list = [
        {
            "id": n.id,
            "identity": n.identity,
            "kind": n.kind,
            "label": n.label,
            "evidence": list(n.evidence),   # semantic node ids
            "version": n.version,
        }
        for n in ideas
    ]

    counts = _tally(lyr.semantic_nodes())
    knowledge = {
        "meta": {
            "demo_source": "Pride and Prejudice",
            "source_title": "Pride and Prejudice",
            "source_author": "Jane Austen",
            "public_domain": True,
            "extractor": args.extractor if args.extractor == "rule" else f"llm:{args.provider}",
            "real_run": True,
            "chapters_processed": len(chapters),
            "totals": {
                "entities": counts["entity"],
                "events": counts["event"],
                "relationships": counts["relationship"],
                "ideas": len(idea_list),
                "sources": len(sources),
            },
            "note": (
                "Rule-based baseline: real but crude — entities + one event per paragraph, "
                "no relationships. Run --extractor llm for demo-quality relationships and ideas."
                if args.extractor == "rule"
                else "LLM extraction over the real text."
            ),
        },
        "formation": formation,
        "entities": buckets["entity"],
        "events": buckets["event"],
        "relationships": buckets["relationship"],
        "ideas": idea_list,
        "sources": sources,
    }

    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(knowledge, ensure_ascii=False, indent=2), encoding="utf-8")

    t = knowledge["meta"]["totals"]
    print(f"\n✓ wrote {out_path}")
    print(f"  {len(chapters)} chapters · {t['entities']} entities · {t['events']} events · "
          f"{t['relationships']} relationships · {t['ideas']} ideas · {t['sources']} source records")


if __name__ == "__main__":
    main()
