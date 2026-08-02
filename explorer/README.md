# LYR Judgment Explorer (M5.0)

A read-only view of **one durable judgment's full lifecycle** — the reasoning LYR
preserves that most systems throw away:

```
Evidence → Builder proposal → Verifier verdict → Engine action → Durable memory
```

It answers, for any one `JudgmentRecord`, without reading code: *what evidence
existed, what the Builder proposed, why the Verifier kept or rejected it, and what
changed in durable memory.*

Design: [`docs/design/M5.0-judgment-explorer.md`](../docs/design/M5.0-judgment-explorer.md).

## Run it

It is a **single self-contained page** — no build, no server, no network. Just open
it:

```bash
open explorer/index.html        # macOS  (or double-click the file)
```

The data is real: `explorer/records/` holds actual full-lifecycle `JudgmentRecord`s
from the M3.1-C.1 verified run (`gpt-4o`), and `explorer/data.js` is generated from
them. Click any judgment in the sidebar — e.g. **coffee** (`ADD → REJECT → NO_OP`) or
**family** (`ADD → KEEP → durable v1`).

## Regenerate the data

After adding/replacing records under `explorer/records/`:

```bash
python explorer/build_data.py   # records/ + fixtures → data.js (resolves evidence labels)
```

## Layout

```
explorer/
  index.html       self-contained viewer (loads data.js; theme-aware; read-only)
  data.js          generated: window.LYR_RECORDS = [ …enriched records… ]
  build_data.py    records/ + experiment fixtures → data.js
  records/         real JudgmentRecords (committed demo evidence)
```

## Notes

- **Read-only** by design — it explains, it never edits (P4).
- **One judgment at a time** (P3) — it never summarizes the whole knowledge base.
- Because it is self-contained and static, it embeds directly in the M3.1 article /
  a blog: readers click through *actual* experimental judgments, not screenshots.
- Provenance currently shows `durable → semantic` (the cited evidence); the further
  `semantic → source` hop is noted per record and is a future extension.
