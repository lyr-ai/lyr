# LYR Explorer — Living Knowledge Formation (v0.1)

The first interactive demonstration of LYR: **knowledge forming, stabilizing, and evolving** over a
real long-form source. Design: [`../docs/design/lyr-explorer-v0.1.md`](../docs/design/lyr-explorer-v0.1.md).
Demo source: **Pride and Prejudice** (public domain). The product is a *Living Knowledge Explorer* —
never a "Book Explorer."

## The one rule

**Every number and object the explorer shows is a real output of the real LYR pipeline over the real
text.** Nothing is hand-authored. If the pipeline doesn't produce something, the explorer doesn't
show it. That is the whole point of the demo — and the reason Week 1 (this directory) comes first.

## Status: Week 1 — backend export ✓ (runs, real output)

`pipeline/export_knowledge.py` runs the actual LYR engine (ingest → semantic → durable →
provenance) chapter by chapter and writes `knowledge.json`. It ran end-to-end and produced real
output; the frontend (Weeks 2–5) will render only what this file contains.

### Two extractors — the honest gap

| extractor | key needed | what it produces | role |
|---|---|---|---|
| `rule` (default) | no | entities + one event per paragraph; **no relationships**; crude | baseline / plumbing proof, runs anywhere |
| `llm` | yes | entities, **relationships**, better events, better durable ideas | **the demo-quality path** |

The rule-based baseline is **real but crude** — enough to prove the pipeline and shape `knowledge.json`,
not enough to make someone say *"I've never seen knowledge represented like this."* That reaction needs
the LLM run. Running it (with your key) is the next real decision, because its output determines which
of the design's rich views (relationships, unresolved conflicts) are honestly buildable.

## Run it

```bash
# 1. fetch the public-domain source (not committed)
bash explorer/pipeline/fetch_source.sh

# 2a. baseline — no API key, real-but-crude:
python explorer/pipeline/export_knowledge.py --limit 6 \
    --out explorer/data/knowledge.sample.json

# 2b. demo quality — your key, full book:
ANTHROPIC_API_KEY=... python explorer/pipeline/export_knowledge.py \
    --extractor llm --provider anthropic \
    --out explorer/data/knowledge.full.json
```

### Real baseline numbers (rule-based, first 6 chapters)

```
116 entities · 189 events · 0 relationships · 50 durable ideas · 207 source records
formation grows per chapter: entities 27 → 37 → 66 → 77 → 96 → 116
45 entities already carry a multi-version history (real evolution; e.g. "Bingley" is v6 across ch1–6)
```

These are the actual "knowledge growing" numbers — the §7 formation panel is driven by the
`formation` array, not by illustrative figures.

## `knowledge.json` schema (the frontend contract)

```jsonc
{
  "meta":   { "demo_source", "source_author", "extractor", "real_run", "chapters_processed", "totals", "note" },
  "formation": [ { "chapter", "roman", "entities", "events", "relationships",
                   "new_entities", "new_events", "new_relationships" } ],   // per-chapter growth
  "entities":      [ { "id", "identity", "kind", "label", "attributes", "evidence":[srcId],
                       "chapters":[n], "version", "history":[ {version,label,evidence,chapters} ] } ],
  "events":        [ /* same node shape */ ],
  "relationships": [ /* same shape; attributes = {subject,predicate,object} (llm only) */ ],
  "ideas":         [ { "id","identity","kind","label","evidence":[semanticId],"version" } ],  // durable
  "sources":       [ { "id", "chapter", "position", "content" } ]   // for evidence highlighting
}
```

- `history` is the **timeline** — the Node version chain (same `identity`, v1→v2→v3), which is how LYR
  represents an object evolving as chapters accumulate. This is real, not synthesized.
- `evidence` on any object → `sources[].id`, so every object links back to the exact passages.
- **Not produced by the current pipeline:** "unresolved conflicts" (§7/§12). Left out rather than
  faked; it is a future extraction step, not a hidden field.

## Layout

```
explorer/
  pipeline/
    chapters.py            split the Gutenberg text into 61 chapters
    export_knowledge.py    run the real LYR pipeline -> knowledge.json
    fetch_source.sh        download the public-domain source
  data/
    knowledge.sample.json  committed real sample (rule-based, 6 chapters)
    *.raw.txt              gitignored (regenerable)
    knowledge.full.json    gitignored (regenerable, large)
  README.md
```

Next: Week 2 — the React explorer (People · Relationships · Timeline) over this file. It should be
built against a **`knowledge.full.json` from the LLM run**, so it renders demo-quality knowledge, not
the rule-based baseline.
