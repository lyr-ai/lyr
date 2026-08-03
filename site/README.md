# LYR site — product site (applications-first)

LYR's public site, deployed to **GitHub Pages**. It is a **product** site, not documentation:
it leads with real applications and shows the protocol working; the research sits behind them.

## Pages

- **`index.html`** — homepage. One line (*AI can generate explanations; LYR tells you whether they
  refer to the world*), then a **real** flagship demo (Case 001: a GitHub Pages deploy failure,
  traditional-AI vs. LYR), the three application cards with honest status badges, and a
  "build with your own evidence" strip.
- **`app-agent-root-cause.html`** — the Agent Root-Cause application (🟢 Live). Case 001 in the
  unified six-part view: Evidence → Hypotheses → Measurement assumptions → Witnesses →
  Identified set → Next observation.
- **`app-pet-health.html`** — the Dog Health / community-knowledge application (🟡 Ready). The same
  view, shown **empty**, awaiting real ethically-obtained cases (no fabricated examples), plus the
  tiered data-ethics table.
- **`research.html`** — for researchers: the paper, the protocol note, the reproduction
  experiment, and the durable-layer Judgment Explorer prototype.
- **`about.html`** — what LYR is, the three lines (Theory frozen / Method / Applications), status,
  and the discipline.
- **`product.css`** — shared styles (theme-aware; self-contained).

**Discipline on this site:** every demo is a **real** case. Domains without real cases show honest
status badges (🟢 Live / 🟡 Ready / ⚪ Planned) — they are never backed by invented examples.

## Durable-layer prototype (earlier line, still live)

- **`explorer.html`** + **`data.js`** + **`records/`** + **`build_data.py`** — the Judgment
  Explorer (model-driven durable memory with provenance, from the M3.1-C.1 run). Linked from
  `research.html`. Regenerate: `python site/build_data.py`.

## Live

Deployed by [`.github/workflows/pages.yml`](../.github/workflows/pages.yml) on every push touching
`site/`. One-time: **Settings → Pages → Source: "GitHub Actions."**

- Home: <https://lyr-ai.github.io/lyr/>
- Agent Root Cause: [app-agent-root-cause.html](https://lyr-ai.github.io/lyr/app-agent-root-cause.html)
- Research: [research.html](https://lyr-ai.github.io/lyr/research.html)

## Run locally

Self-contained — no build, no server, no network:

```bash
open site/index.html
```

## Layout

```
site/
  index.html               product homepage
  app-agent-root-cause.html   Agent Root Cause application (Live; Case 001)
  app-pet-health.html      Dog Health application (Ready; awaiting real cases)
  research.html            paper · protocol · reproduction · explorer
  about.html               what LYR is; the three lines; the discipline
  product.css              shared styles
  explorer.html            durable-layer Judgment Explorer prototype
  data.js / records/ / build_data.py   explorer data
  .nojekyll                serve files as-is on Pages
```
