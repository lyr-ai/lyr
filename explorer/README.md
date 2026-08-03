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

**Easiest — one interactive command (recommended):**

```bash
python explorer/run.py
```

It lets you **pick a provider — OpenAI (ChatGPT) or Anthropic (Claude)** — downloads the source if
needed, **asks for that provider's API key** (hidden input, and offers to save it to a gitignored
`explorer/.env` so you only enter it once), asks how many chapters (default 10), and runs the
demo-quality LLM extraction. No flags to remember. Requires the provider's package
(`pip install openai` or `pip install anthropic`).

> **OpenAI note:** the *API* needs its own credit at
> [platform.openai.com/billing](https://platform.openai.com/settings/organization/billing) — a
> ChatGPT Plus/Pro subscription does **not** include API access; they are billed separately.

**Manual, if you prefer flags:**

```bash
# baseline — no API key, real-but-crude:
python explorer/pipeline/export_knowledge.py --limit 6 --out explorer/data/knowledge.sample.json

# demo quality — OpenAI (ChatGPT), key via env / .env / --api-key:
python explorer/pipeline/export_knowledge.py --extractor llm --provider openai --consolidator llm \
    --model gpt-4o-mini --limit 10 --out explorer/data/knowledge.full.json

# demo quality — Anthropic (Claude):
python explorer/pipeline/export_knowledge.py --extractor llm --provider anthropic --consolidator llm \
    --model claude-haiku-4-5 --limit 10 --out explorer/data/knowledge.full.json
```

The key is resolved in order: `--api-key` → `ANTHROPIC_API_KEY` env → `explorer/.env` → (in
`run.py`) an interactive hidden prompt. It is never committed and never passed on the command line by
`run.py`.

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

## Canonicalization (Explorer presentation — core untouched)

The raw `knowledge.json` keys entities by exact label, so a character appears under aliases
("Elizabeth" vs "Elizabeth Bennet"; three Wickham nodes). The **Canonicalization Layer**
(`pipeline/canonicalize.py`) writes `knowledge.canonical.json` for the explorer. Its grouping now
comes from the **generic resolver** (`lyr/semantic/resolution.py`, `--groups resolver`, default) —
no per-book data, verified cross-domain (see `../experiments/entity-resolution/`). The hand
**alias adapter** (`adapters/*.aliases.json`) is demoted to **evaluation data only** (`--groups
adapter`), no longer the runtime path. **LYR core nodes and identities are never modified** — every original id, label,
version chain, evidence link, and chapter span is preserved inside each canonical entity, with merge
provenance. Full rationale + the identity roadmap:
[`../docs/design/canonicalization-and-identity.md`](../docs/design/canonicalization-and-identity.md).

Every merge is guarded even though the adapter is curated: **no title conflict** (Mr./Sir vs
Mrs./Miss/Lady refused — keeps *Miss Darcy* ≠ *Mr. Darcy*), **evidence link** required (full-name
expansion or shared token), ambiguous stays split. On Pride and Prejudice: **32 raw → 24 canonical,
7 merges, 0 false merges.** `run.py` runs this automatically after extraction.

```bash
python explorer/pipeline/canonicalize.py \
    --in explorer/data/knowledge.full.json \
    --adapter explorer/adapters/pride-and-prejudice.aliases.json \
    --out explorer/data/knowledge.canonical.json
```

Canonical entity shape: `{ canonical_label, entity_type, aliases[], source_node_ids[], evidence[],
chapters[], n_updates, timeline[{alias,version,label,chapters,evidence}], merge{from,via} }`.
Relationships gain `subject_canonical` / `object_canonical`. **Ideas/themes are omitted in v0.1**
(`meta.themes = "not_yet_derived"`) — no real durable themes yet, and we don't fake them.

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
