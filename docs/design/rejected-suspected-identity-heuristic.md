# Rejected: a downstream heuristic "suspected fragmented identity" display

**Status:** rejected experiment, recorded so it is not retried. A heuristic UI panel that guesses
which fragmented entities are "probably the same" **cannot be built reliably downstream.**

## Attempt

Viewing 红楼梦, Jia Baoyu appears as 4 entries (贾宝玉 / 寶玉 / 賈寶玉 / Jia Baoyu). Goal: surface a
*"possible same identity — no merge committed"* panel from a **generic** signal (not hard-coded
names), so the demo is honest rather than looking broken. Two candidate signals were implemented and
tested on real data.

## Observed false positives

- **Graph-neighbour overlap** (same-type entities not directly related that share ≥2 relationship
  neighbours): catastrophic on the dense English graph — grouped **all 12 P&P main characters into
  one "identity"** (Elizabeth, Darcy, Jane, Bingley, Collins, Wickham, both Bennets…). Everyone in a
  dense graph shares neighbours.
- **Label similarity** (substring / longest-common-substring): over-merged on Latin —
  `Jia Zhen ⊂ Jia Zheng` (賈珍 ≠ 賈政), `Jia Baoyu ~ Jia Rong ~ Jia Zheng`, `Grand View Garden ~
  Rongguo Mansion` (shared "an").

## Why downstream context is unavailable

On 红楼梦 the graph is **fractally fragmented**: the extractor emitted the same entities *and their
relationships and neighbours* in inconsistent scripts/languages per chapter, so the Baoyu variants
share **0** relationship neighbours and **0** evidence passages. There is no shared context to group
by — the fragmentation is graph-wide, upstream of any dedup.

## Located failure boundary

The only signal that was clean was **CJK name-expansion** (雨村 ⊂ 賈雨村, 黛玉 ⊂ 林黛玉, 寶玉 ⊂ 賈寶玉).
But that is not "suspected fragmentation guessing" — it is **name-expansion the resolver already does
for English and fails at for CJK** (it tokenises 賈雨村 as one token). I.e. the reliably-solvable part
belongs to the resolver, deterministically; the unreliable part (context/label heuristics) belongs
nowhere.

## Rejected approach

A downstream heuristic "suspected identity" panel. It over-flags (worse UX than honest splits) and
would launder a guess as system output. **Do not retry** — unless a *formal* proposer emits
evidence-linked `UNSURE` candidates (the gated v0.2), a heuristic panel is off the table.

## Next admissible experiments (deterministic first)

The failure decomposed fragmentation into four causes, three with cheaper/deterministic fixes:

1. **Extractor-created inconsistency** (简/繁/English for the same source form) → **fix C**: an
   extractor source-fidelity contract (use the name exactly as written; canonicalize downstream).
2. **CJK name-expansion blind spot** (space-less tokenisation) → **fix A**: guarded CJK
   name-expansion in the resolver (LINK/UNSURE/REJECT with type + mutual-exclusion guards).
3. **Script-equivalent forms** (寶玉 ↔ 宝玉) → **fix B**: a script-normalisation *comparison form*
   (raw preserved), tested for zero regression on P&P/Git.
4. **True semantic aliases** (鳳姐 / 王熙鳳) → only this needs the graph-aware / LLM **v0.2 proposer**,
   which stays gated until a second non-English/non-person witness.

Order: record this → C → re-run+diff → A → fixtures → B → DeepSeek/Kimi → then decide on v0.2.
