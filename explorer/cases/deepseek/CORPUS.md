# DeepSeek case — official corpus contract

This case is the **second independent identity witness** (after 红楼梦). It moves
the identity question off *people* and onto:

    model / version / component / concept identity

The question the resolver must survive here is different from a novel's:

- Is `DeepSeek V4` vs `V4-Pro` the **same entity at two versions**, or **two
  distinct entities**? (LYR must not silently merge or silently split.)
- Are `repo`, `model artifact`, `API product`, and the *named model* one thing
  or several?
- Do abbreviations vs full names (`MoE` / `Mixture-of-Experts`,
  `MLA` / `Multi-head Latent Attention`) need normalization?
- Can one technical component be unified across report + README + changelog?
- Does a benchmark claim trace back precisely to its source doc?
- Does the People-centered Explorer model bend naturally to
  Models / Components / Claims — or does it break?

## Official-only (source-reliability is held constant)

Use **only first-party documents** so any failure localizes to the LYR backend,
not to source disagreement. Drop these as `.md` files in this directory:

| file | what it is |
|------|-----------|
| `technical-report.md` | the official technical report (arXiv/PDF → text) |
| `model-card.md`       | the official model card (HuggingFace / repo) |
| `readme.md`           | the official repository README |
| `changelog.md`        | release notes / changelog |
| `announcement.md`     | official announcement / blog (first-party only) |

Do **not** add news, third-party blogs, or Reddit yet — that introduces a
source-reliability variable and makes a backend failure impossible to isolate.

Headings inside each doc are preserved as sections (`MarkdownParser`), so keep
the documents' own `#`/`##` structure intact when you paste them in.

## Run (once the docs are here)

    OPENAI_API_KEY=... python explorer/pipeline/run_case.py \
        --case explorer/cases/deepseek.json --extractor llm --provider openai

Then read `site/data/deepseek/quality.json` and compare its resolver block
(merges / unsure / rejects / guard_warnings) against 红楼梦's — that comparison
is what decides whether the v0.2 proposer has earned a second witness.
