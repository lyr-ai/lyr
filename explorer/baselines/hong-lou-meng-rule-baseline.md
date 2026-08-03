# 红楼梦 (紅樓夢) — rule-based baseline

Zero-cost baseline before any LLM spend, to measure the LLM run against. Source: Project
Gutenberg #24264 (traditional Chinese, 120 回, public domain). Run: first 20 回, `--extractor rule`.

## Findings

| check | result |
|---|---|
| `第X回` segmentation | **works** — 123 segments (第一回…第一二零回); ~3 extra from the TOC (over-count, minor) |
| encoding | traditional Chinese reads correctly |
| provenance | intact (100% evidence coverage) |
| **rule extractor entities** | **0** — `RuleBasedExtractor` matches `[A-Z]` proper-noun runs; Chinese has no capitals. Only paragraph-events. For zh, the LLM does 100% of extraction. |
| **ingestion granularity** | **coarse** — 45 records for 20 回 (median 1,699, max 8,796 chars). This text has no blank-line paragraphs and `TextIngestor` splits on blank lines → ~1 giant record per chapter. |

`quality.json` (rule baseline): `entities 0 · events 43 · relationships 0 · sources 45 · coverage 100% · merges 0`.

## What this witnesses (recorded, not patched)

1. **Rule extraction is not language-generic** — capitalization-dependent, 0 for zh. Expected; the
   LLM path is the real one for Chinese.
2. **Ingestion assumes blank-line paragraphs** — a *generic* gap (any single-newline text hits it:
   transcripts, some docs), not Chinese-specific. With whole-chapter records the LLM run would give
   coarse provenance (a "passage" = a whole chapter) and sparser extraction. **Recommended fix before
   the LLM run:** a language-independent normalization — when a block has no blank-line paragraphs,
   split on newlines / sentence punctuation (`。．！？`) into passage-sized records.
3. **Identity stress test deferred** — 王熙鳳/鳳姐, 寶玉/寶二爺 need entities to test; 0 at rule level.
   The resolver's Chinese behaviour (its rules are space-token + English-honorific shaped) becomes a
   witness only after the LLM extractor produces entities.

## Fine ingestion (done — generic, lossless)

Added a generic `PassageIngestor` (harness-level, injected via `LYR(ingestor=...)`, gated by manifest
`"ingest": "fine"`; **no language/case logic**). Sentence-aware packing into passage-sized records
(target 800 / max 1500 chars), never cutting a sentence, contiguous slices carrying `char_start` /
`char_end` / `passage_index`.

Verified free on 红楼梦 first 20 回:

| | coarse (blank-line) | fine (passage) |
|---|---|---|
| source records | 45 (whole chapters, max 8,796 chars) | **167** (median 841, max 911) |
| lossless (whitespace-normalized) | — | **✓ PASS** |
| empty passages | — | 0 |
| over max(1500) | — | 0 |
| rule entities | 0 | 0 (unchanged — extractor, not ingestion) |

The two baselines are kept separate on purpose (`…-rule-coarse` / `…-rule-fine`) so the diffs are
**attributed**: coarse→fine isolates the *ingestion* effect; rule-fine→LLM-fine isolates the
*extractor* effect (ingestion held constant).

## Next

LLM run on the same 20 回 (fine ingestion) → attributed diff report vs `hong-lou-meng-rule-fine`.
Per discipline: do **not** add a Chinese-nickname dictionary or 红楼梦 special-case; if identity
fails on zh, that is a witness for the v0.2 generic proposer (mention → candidate → contextual
evidence → conflict guards → LINK/CREATE/UNSURE), re-tested on a second non-English/non-person
domain before being called a generic improvement.
