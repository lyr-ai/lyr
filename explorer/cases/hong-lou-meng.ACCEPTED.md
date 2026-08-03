# 红楼梦 — Cross-language case passed at current scope

**Status:** ACCEPTED · frozen at current scope · 2026-08-03

This case validated that the two backend fixes for cross-language identity
fragmentation reached the product path (Explorer), not just the test suite:

- **Fix C** — extractor source-fidelity contract (`lyr/semantic/llm.py`): the
  extractor writes each mention in the exact script/language of the cited
  passage; canonicalization is downstream. Eliminated 简/繁/English variants of
  the same source form.
- **Fix A** — guarded CJK name-expansion in the generic resolver
  (`lyr/semantic/resolution.py`, pass 1b): `寶玉 ⊂ 賈寶玉` linked the way
  `Elizabeth ⊂ Elizabeth Bennet` already was for English; ambiguous bare forms
  stay UNSURE, type/mutual-exclusion conflicts hard-reject.

## Acceptance checks (20-chapter scope, deployed package)

| # | Check | Result |
|---|-------|--------|
| 1 | `賈寶玉` is a single canonical person | PASS — one entry, ch5–20, 15 rel, 58 evidence passages |
| 2 | aliases preserved + evidence aggregated | PASS — aliases `['寶玉','賈寶玉']`; 58 passages / 15 rel / 14 events |
| 3 | timeline + evidence clickable | PASS — 29 steps, each with ≥1 source passage, 0 empty |
| 4 | no new false merge | PASS — 4 merges all containment name-expansions; 賈政≠賈珍 stay distinct; 0 guard_warnings, 0 unsure |
| 5 | quality report ↔ UI numbers agree | PASS — 33 people = people.json; 49 raw → 45 canonical / 4 merges consistent |

Backing numbers: `site/data/hong-lou-meng/quality.json` (49→45, 4 merges,
0 unsure, 19 rejects, dup 1.09, coverage 76.4%).

## Explicitly OUT of scope for this freeze (do not reopen for polish)

- 鳳姐 / 王熙鳳 — a true semantic alias (no shared substring). Needs the gated
  **v0.2 proposer**, which stays gated until a second independent witness.
- Script normalization (fix B) — no residual 简/繁 pair remained after C;
  building it now would be ahead of evidence.
- Themes — `not_yet_derived`; a stated capability gap, not a bug.
- Full-book (120-回) run — the acceptance is about *correctness of the fix*, not
  page completeness. Scale behaviour is answered post-hoc by `scale_report.py`.
- Any 红楼梦-specific UI. The Explorer stays generic; the next witness
  (DeepSeek/Kimi) tests whether the generic model survives a non-person domain.

**Next:** DeepSeek / Kimi official corpus — model/version/component/concept
identity, the second independent cross-domain witness.
