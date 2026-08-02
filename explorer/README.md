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

## Embed it in the blog

It is a static, self-contained page with no external requests, so it drops straight
into the M3.1 article as a live demo — readers click through *actual* judgments
instead of looking at screenshots:

```html
<iframe src="explorer/index.html" width="100%" height="720"
        style="border:1px solid #e5e7eb;border-radius:12px"></iframe>

<p><em>Try one real judgment — coffee, family, or the guidance reversal.</em></p>
```

## Notes

- **Read-only** by design — it explains, it never edits (P4).
- **One judgment at a time** (P3) — never a whole-knowledge-base summary.
- It frames each case as *"Why does the system keep / reject this?"* and walks the
  **full LYR stack** — `Source → Semantic → Builder → Verifier → Durable` — so a
  first-time viewer sees it as *explaining how a knowledge formed*, not a pipeline.
- Each case ends with the **research finding** it demonstrates (e.g. coffee → *false
  positive removed*; guidance → *false negative*), which makes it a *research*
  explorer, not a data viewer.
- The 16 substantive judgments (13 KEEP + 3 REJECT) are shown; the builder-`NO_OP`
  units (donuts / rent / version-bumps — empty statement, nothing to display) are
  skipped by `build_data.py`.
