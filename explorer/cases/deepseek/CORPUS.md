# DeepSeek case — official evolution corpus

This case is the **second independent identity witness** (after 红楼梦). It moves
the identity question off *people* and onto:

    model / version / component / claim identity — across a version chain

It is an **evolution corpus** (V3 → V3.2 → V4), not a single-model snapshot. The
product question it probes is not "what is V4" but **how knowledge changes across
versions** — and, honestly, where LYR's current backend cannot yet represent that
change (see the capability-gap note below).

## Corpus (official first-party only)

Five real DeepSeek documents spanning the chain. Provenance + fidelity note:
[`SOURCES.md`](SOURCES.md).

| file | version | doc |
|------|---------|-----|
| `v3-technical-report.md` | V3   | technical report (arXiv:2412.19437) |
| `v3-readme.md`           | V3   | repository README |
| `v3_2-model-card.md`     | V3.2 | model card (V3.2-Exp) |
| `v3_2-release.md`        | V3.2 | release notes |
| `v4-technical-report.md` | V4   | technical report (arXiv:2606.19348) |

No news / blogs / third-party commentary — that would add a source-reliability
variable and make a backend failure impossible to isolate. Headings are
preserved as sections (`MarkdownParser`), lossless.

## What it tests

See [`SOURCES.md`](SOURCES.md) for the concrete identity questions (version
identity, component identity, claim tracing, whether the People-centered Explorer
bends to Models/Components/Claims).

## Honest boundary (recorded, not hidden)

This corpus tests identity **across** a version chain — LYR can resolve whether
`V3` and `V4` are related-but-distinct entities. It does **not** yet model a V4
claim *revising* a V3 claim: that is the recorded `stateful semantic claims`
capability gap (`docs/design/capability-gap-stateful-claims.md`). This corpus is
expected to **expose** that gap sharply; that exposure is the witness, reported
as-is, not smoothed over.

## Run

    OPENAI_API_KEY=... python explorer/pipeline/run_case.py \
        --case explorer/cases/deepseek.json --extractor llm --provider openai

Then read `site/data/deepseek/quality.json` and compare its resolver block
(merges / unsure / rejects / guard_warnings) against 红楼梦's — that comparison
decides whether the gated v0.2 proposer has earned a second independent witness.
