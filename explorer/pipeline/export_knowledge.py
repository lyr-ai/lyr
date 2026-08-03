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
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

from chapters import split_chapters  # noqa: E402
from segments import Segment  # noqa: E402
from parsers import get_parser  # noqa: E402
from lyr import LYR  # noqa: E402
from lyr.semantic import RuleBasedExtractor  # noqa: E402

KINDS = ("entity", "event", "relationship")


def _load_env(path: Path) -> None:
    """Populate os.environ from a simple KEY=VALUE .env file (no dependency)."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _resolve_key(explicit: str | None, provider: str) -> str | None:
    if explicit:
        return explicit
    env_name = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
    return os.environ.get(env_name)


def _client(provider: str, api_key: str | None, model: str | None):
    if provider == "anthropic":
        try:
            from lyr.llm.anthropic import AnthropicClient
        except Exception as e:  # noqa: BLE001
            raise SystemExit(str(e))
        kwargs = {"api_key": api_key}
        if model:
            kwargs["model"] = model
        return AnthropicClient(**kwargs)
    if provider == "openai":
        try:
            from lyr.llm.openai import OpenAIClient
        except Exception as e:  # noqa: BLE001
            raise SystemExit(str(e))
        kwargs = {"api_key": api_key}
        if model:
            kwargs["model"] = model
        return OpenAIClient(**kwargs)
    raise SystemExit(f"unknown provider {provider!r}")


def _tally(nodes) -> dict[str, int]:
    c = {k: 0 for k in KINDS}
    for n in nodes:
        if n.kind in c:
            c[n.kind] += 1
    return c


def _chapter_of(origin: str) -> int | None:
    # origin ends in the segment number, e.g. "pnp-ch03", "hlm-seg012", "case-doc02"
    m = re.search(r"(\d+)$", origin)
    return int(m.group(1)) if m else None


def _read(path: str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = REPO / p
    # A partial corpus is a valid state — a case may list five official docs but
    # only some have been dropped in yet. Skip a missing source (empty text →
    # the parser emits no section for it) instead of crashing the whole run.
    if not p.exists():
        print(f"  · skip missing source: {p}")
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


def _segments_from_manifest(m: dict) -> list[Segment]:
    # Document Parser Layer: the manifest's `parser` chooses how structure is read;
    # every parser returns the same Section shape (see parsers.py).
    parser = get_parser(m)
    docs = [(s.get("title", Path(s["path"]).name), _read(s["path"])) for s in m["sources"]]
    return parser.parse(docs, m.get("case_id", "case"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=str(REPO / "explorer/data/pride-and-prejudice.raw.txt"))
    ap.add_argument("--manifest", default=None, help="case manifest JSON (generic multi-source path)")
    ap.add_argument("--out", default=str(REPO / "explorer/data/knowledge.sample.json"))
    ap.add_argument("--extractor", choices=["rule", "llm"], default="rule")
    ap.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    ap.add_argument("--limit", type=int, default=0, help="max chapters (0 = all)")
    ap.add_argument("--api-key", default=None, help="LLM API key (else env / explorer/.env)")
    ap.add_argument("--model", default=None, help="model override, e.g. claude-haiku-4-5")
    ap.add_argument("--consolidator", choices=["recurrence", "llm"], default="recurrence",
                    help="durable-idea consolidation; 'llm' needs a key and gives quality ideas")
    args = ap.parse_args()

    _load_env(REPO / "explorer" / ".env")

    source_type = "book"
    ingest_policy = "paragraph"
    if args.manifest:
        manifest = json.loads(_read(args.manifest))
        source_type = manifest.get("source_type", "book")
        ingest_policy = manifest.get("ingest", "paragraph")
        segs = _segments_from_manifest(manifest)
    else:
        segs = [Segment(c.number, f"pnp-ch{c.number:02d}", f"Chapter {c.roman}", c.text)
                for c in split_chapters(Path(args.source).read_text(encoding="utf-8", errors="replace"))]
    if args.limit:
        segs = segs[: args.limit]
    if not segs:
        raise SystemExit("no segments parsed — check --source / --manifest")

    if args.extractor == "llm":
        api_key = _resolve_key(args.api_key, args.provider)
        if not api_key:
            env_name = "OPENAI_API_KEY" if args.provider == "openai" else "ANTHROPIC_API_KEY"
            raise SystemExit(
                f"No API key found. Pass --api-key, set {env_name}, add it to "
                "explorer/.env, or use the friendly runner:  python explorer/run.py"
            )
        client = _client(args.provider, api_key, args.model)
        from lyr.semantic import LLMExtractor
        extractor = LLMExtractor(client)
        consolidator = None
        if args.consolidator == "llm":
            from lyr.durable import LLMConsolidator
            consolidator = LLMConsolidator(client)
    else:
        extractor = RuleBasedExtractor()
        consolidator = None

    lyr_kwargs = {"extractor": extractor}
    if consolidator:
        lyr_kwargs["consolidator"] = consolidator
    if ingest_policy == "fine":
        from passage_ingestor import PassageIngestor
        lyr_kwargs["ingestor"] = PassageIngestor()
    lyr = LYR(**lyr_kwargs)

    # ── run the real pipeline, chapter by chapter, snapshotting growth ──
    formation = []
    prev = {k: 0 for k in KINDS}
    for seg in segs:
        lyr.ingest(seg.text, origin=seg.origin, kind=source_type, chapter=seg.number)
        cur = _tally(lyr.semantic_nodes())
        formation.append(
            {
                "chapter": seg.number,
                "roman": seg.title,
                "entities": cur["entity"],
                "events": cur["event"],
                "relationships": cur["relationship"],
                "new_entities": cur["entity"] - prev["entity"],
                "new_events": cur["event"] - prev["event"],
                "new_relationships": cur["relationship"] - prev["relationship"],
            }
        )
        prev = cur
        print(f"  seg{seg.number:>3} ({seg.title[:16]:<16}) entities={cur['entity']:>4} "
              f"events={cur['event']:>4} rel={cur['relationship']:>4}")

    print("consolidating durable knowledge…")
    lyr.build_durable()
    ideas = list(lyr.durable_memories())

    # ── assemble the export ──
    src_chapter: dict[str, int | None] = {}
    sources = []
    for r in lyr.store.sources():
        ch = _chapter_of(r.origin)
        src_chapter[r.id] = ch
        rec = {"id": r.id, "chapter": ch, "position": r.position, "content": r.content}
        for mk in ("passage_index", "char_start", "char_end"):
            if mk in r.metadata:
                rec[mk] = r.metadata[mk]
        sources.append(rec)
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
            "chapters_processed": len(segs),
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
    print(f"  {len(segs)} segments · {t['entities']} entities · {t['events']} events · "
          f"{t['relationships']} relationships · {t['ideas']} ideas · {t['sources']} source records")


if __name__ == "__main__":
    main()
