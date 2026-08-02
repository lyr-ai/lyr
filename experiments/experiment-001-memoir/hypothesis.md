# Experiment 001 — Memoir: hypothesis & what to watch

**Question:** given clean semantic records from a memoir, how does the model group
evidence and decide what is durable? Does it get the hard cases right *for the
right reasons*?

The fixture is engineered so several hard cases collide in one batch. What we
*expect* a good reasoner to do (not a rubric — a lens for reading the transcript):

| Records | Case | Hoped-for behavior |
|---|---|---|
| 0, 1, 2 | independent events → one durable pattern | ADD a scoped pattern: *consistently prioritized family over career advancement*, citing 3 **independent** decisions across decades |
| 0 & 3 | duplicate description of the **same** 1998 event | grouped as **one** piece of evidence — record 3 must **not** add support beyond record 0 |
| 4 | significant one-off (emigration) | may be durable **without recurrence** — an irreversible, identity-shaping event |
| 5, 6 | trivial recurring noise (morning coffee) | **NO_OP** — recurs but not durable; ideally 5 & 6 also seen as the same ritual |
| 7, 8 | contradiction / scope over time (cash-hoarder in 30s vs. risk-taker at 63) | **not** a flat "always risk-averse"; qualify by life phase, or preserve two scoped claims |
| 9 | thirty years of weekly letters | plausibly durable (a sustained devotion) — watch whether it's read as pattern vs. one long fact |

**What to watch for beyond correctness:**

- Does it *conflate repetition of a description with accumulation of evidence*?
  (records 0/3, 5/6) — the core independence test.
- Does it invent support the passages don't contain?
- Does it reach for a grand synthesis, or does it scope claims honestly?
- How does it phrase the coffee refusal — dismissive, or reasoned?
- Where does its confidence sit, and does the stated confidence track the evidence?

**Findings go below** (fill in after runs; keep the transcript filename).

## Runs & observations

### 2026-07-27 — role-play smoke test

- `run_type: non_blind_prompt_smoke_test`
- `evaluation_status: excluded_from_benchmark`
- reasoner: the assistant role-playing the model (authored the fixture) — **not
  evidence**, only a check that the one-step builder prompt yields a sensible,
  auditable, parseable judgment before spending live tokens.
- transcript: `runs/…__judgment__CANNED.json` (gitignored)

**Result:** ADD, kind=pattern, "Across her adult life she repeatedly subordinated
career advancement to family obligations", evidence = records [0,1,2]; committed
durable v1 with a `judgment_id` back-reference. Evidence grouping correctly folded
0&3 (same 1998 promotion) and 5&6 (same coffee ritual); counter_evidence scoped the
claim to ~1998–2012 and flagged the 7/8 risk reversal as a separate topic.

**Structural findings (the only thing this run is allowed to inform):**

- ✅ evidence references present and resolvable; operation unambiguous; output
  parsed; committed node fully traceable to source. No builder change warranted.
- ⚠️ **One-op-per-call vs. multi-topic batch (contract question, not a bug).** The
  memoir holds ≥2 durable candidates (career-vs-family pattern *and* the 30-years
  of weekly letters, record 9). A single `update()` emits exactly one operation, so
  the letters candidate is silently absent from the output — not even a NO_OP with a
  reason. The record accounts for the decision it *made* but not for un-promoted
  candidates. This is expected if candidate-retrieval is meant to hand the builder
  one topic at a time; it is a real gap if a batch can be multi-topic. **Deferred to
  the live four-domain runs to decide** whether the prompt contract needs revision
  before M3.1-C (per direction). Builder left unchanged.
