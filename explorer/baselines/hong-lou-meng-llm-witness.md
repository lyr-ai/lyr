# 红楼梦 LLM run — witness #1: the resolver is name-structure-generic, not language-generic

First cross-language case. OpenAI `gpt-4o-mini`, first 20 回, **fine** ingestion. Attributed diff
against the two rule baselines (`diff_report.py`).

## Attributed diff

| metric | coarse | fine | llm | attribution |
|---|---|---|---|---|
| sources | 45 | 167 | 167 | coarse→fine = ingestion (4× finer provenance) |
| entities | 0 | 0 | 50 | fine→llm = extractor |
| relationships | 0 | 0 | 39 | |
| evidence coverage | 100% | 100% | 73.1% | strong (P&P was 23.9%) |
| duplicate ratio | — | — | **1.06** | resolver merged almost nothing |
| merges/unsure/rejects | — | — | 3 / 1 / 14 | the 3 merges are exact-dup, not aliases |

**Ingestion works, extraction works (73% coverage on Classical Chinese). Identity resolution is the
bottleneck.**

## The witness — same entity split three ways

```
Baoyu           寶玉 · 宝玉 · 贾宝玉 · 賈寶玉      (4 nodes)
Wang Xifeng     鳳姐 · 凤姐 · 鳳姐兒            (王熙鳳 not linked)
Jia Zheng       賈政 · 贾政
Jia Yucun       賈雨村 · 贾雨村
Jia Mu          賈母 · 贾母
Qin Zhong       秦鐘 · 秦钟
Xue Baochai     薛寶釵 · 薛宝钗
Ningguo Mansion 宁国府 · Ningguo Mansion · Ning Mansion
```

Three distinct, generic failure modes:

1. **Traditional ↔ simplified** — 寶↔宝, 賈↔贾, 鐘↔钟. `casefold()` normalizes Latin case but not CJK
   variants; the LLM emits both inconsistently.
2. **Chinese aliases, no shared token** — 鳳姐 vs 王熙鳳, 水溶 vs 北靜王水溶. The resolver's
   space-token / English-honorific rules find nothing to work with.
3. **Chinese ↔ English translation** — 宁国府 vs "Ningguo Mansion", 妙玉 vs "Miaoyu".

## Disposition (per discipline)

- **Do NOT** add a 红楼梦 nickname dictionary, a zh special-case, or a core patch.
- Recorded as **witness #1** for the **v0.2 generic proposer**:
  `mention → candidate → contextual evidence (shared relations, co-occurrence) → conflict guards →
  LINK / CREATE / UNSURE`, likely with an LLM proposer whose output is structured + evidence-linked.
- A resolver change is called "generic" only after a **second** non-English / non-person witness
  (DeepSeek V4 / Kimi K3 docs: version vs alias, component vs package path).
- **Open question for the human:** is a traditional↔simplified normalization (a Unicode fold,
  analogous to `casefold`) a *generic normalization* or a *language special-case*? It needs zh
  mapping data. Left undecided rather than sneaked into core.

The 红楼梦 Explorer package is committed **as-is (splits and all)** — an honest demonstration that
the harness runs cross-language and exactly where genericity currently ends.

## Fixed-segmentation re-run (attributed diff)

Re-ran the same 20 回 after the Document-Parser segmentation fix. Attribution is clean:

| metric | broken-seg | fixed-seg | attributed to |
|---|---|---|---|
| sources | 167 | 174 | segmentation (aligned content) |
| entities | 50 | 52 | comparable, no distortion |
| duplicate ratio | 1.06 | **1.06** | **resolver unchanged** |
| merges / orphans | 3 / 28 | 3 / 28 | unchanged |
| coverage | 73.1% | 70.7% | comparable |

- **Segmentation fixed** — source-record chapters now **1–20 continuous** (no 5/17 gap). Provenance
  is passage-precise (174 records with char ranges).
- **Resolver fragmentation unchanged** (dup 1.06; Baoyu still 贾宝玉 / 寶玉 / 賈寶玉 / Jia Baoyu) — the
  fix did not touch the resolver witness, as intended.
- **New witness — extractor coverage:** chapters **9 and 14 produced 0 surviving entities** despite
  8 and 7 source passages (ch14 added nothing at all). An **extractor** degeneracy on some
  chapters, distinct from segmentation and resolver. Recorded, not fixed.

The live package is now the fixed-seg run (trustworthy chapter attribution); the broken-seg baseline
is preserved as `hong-lou-meng-brokenseg-llm-fine.quality.json`.
