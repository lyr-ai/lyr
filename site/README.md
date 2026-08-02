# LYR site — landing page + Judgment Explorer (M5.0)

LYR's public site, deployed to **GitHub Pages** (separate audience from the code repo):

- **`index.html`** — landing page: the 30-second value proposition + two CTAs
  (*Open the Judgment Explorer* / *Read the research*).
- **`explorer.html`** — the **Judgment Explorer**: a read-only walk through one durable
  judgment's full lifecycle — *Source → Semantic → Builder → Verifier → Durable* —
  framed as *"Why does the system keep / reject this?"*, ending with the research
  finding each case demonstrates.

Design: [`docs/design/M5.0-judgment-explorer.md`](../docs/design/M5.0-judgment-explorer.md).

## Live

Deployed by [`.github/workflows/pages.yml`](../.github/workflows/pages.yml) on every
push that touches `site/`. One-time repo setup: **Settings → Pages → Source: “GitHub
Actions.”** Then:

- Landing: `https://lyr-ai.github.io/lyr/`
- Explorer: `https://lyr-ai.github.io/lyr/explorer.html`
- Deep links: `.../explorer.html#coffee-ritual`, `#family-over-career`,
  `#guidance-reversal`, `#payments-ci-flakiness`

## Run locally

Fully self-contained — no build, no server, no network:

```bash
open site/index.html
```

## Regenerate the data

```bash
python site/build_data.py   # records/ + experiment fixtures → data.js
```

It reads the real full-lifecycle `JudgmentRecord`s in `site/records/` (from the
M3.1-C.1 verified run), resolves each cited evidence id back to its **semantic label
and original Source passage** (parsed from the experiment `input.md` files), attaches
a human title + the research finding, and writes `site/data.js`
(`window.LYR_RECORDS`). 16 substantive judgments are shown (13 KEEP + 3 REJECT); the
builder-`NO_OP` units (empty statement) are skipped.

## Embed in the blog

```html
<iframe src="https://lyr-ai.github.io/lyr/explorer.html#coffee-ritual"
        width="100%" height="720" style="border:1px solid #e5e7eb;border-radius:12px"></iframe>
```

## Layout

```
site/
  index.html       landing page
  explorer.html    the Judgment Explorer (loads data.js; theme-aware; read-only)
  data.js          generated: window.LYR_RECORDS = [ …enriched records… ]
  build_data.py    records/ + experiment fixtures → data.js
  records/         real JudgmentRecords (committed demo evidence)
  .nojekyll        serve files as-is on Pages
```
