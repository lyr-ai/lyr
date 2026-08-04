# Case Protocol v1

**Status:** the experiment design for all future case work. Every case is a **research instrument**,
not a demo. This protocol is the only sanctioned path from a case to a backend change, and it
operationalizes the Research v1 freeze: a capability reaching **Count ≥ 2** *is* reopen-trigger #2.

## The reframe

Old question — *what does the backend still lack?* → grows the backend reactively, case by case.

New question — **what long-term knowledge would a real 5-year domain expert hold that LYR does not?**

A senior teammate's knowledge is **not** a paper summary, a runbook, or a character wiki. It is a
durable, structured mental model with explicit unknowns and confidence — which is exactly the
scoped-claim substrate (`review-semantic-to-knowledge-transition.md`), now used as the **expected
target** we diff against rather than as a thing to build.

## The six steps (every case runs all six)

**Step 0 — Expected Teammate.** Before running anything, for one probe question, write what a
5-year expert *knows*. Use the generic expert-memory dimensions (specialize per domain):

    what it is (current identity) · why it exists · when introduced · how it changed (history)
    · what it relates to · current state / owner / known failure modes (ops)
    · what is UNKNOWN · confidence

Examples: DeepSeek "Explain MLA" → the seven-line model, not a paper summary. Ops "why no data for
Germany?" → current state · dependency · history · failure modes · owner · confidence, not a runbook.
红楼梦 "宝玉是谁?" → current identity · family · relationships · evidence · history · unknown, not a wiki.

**Step 1 — Expected Knowledge.** Enumerate the expected **Knowledge Units** (not a schema):

    Objects   (e.g. MLA, DSA, CSA)
    Claims    (current claim · historical claim)
    Unknowns  (what the expert explicitly does not assert)

**Step 2 — Run LYR.** Produce the **Current** knowledge for the same probe, unmodified.

**Step 3 — Diff & classify.** Expected vs Current, tag every gap with exactly one class:

    MISSING       expected, absent in Current
    WRONG         present but the current state is incorrect
    FABRICATED    Current asserts what should be UNKNOWN
    UNREPRESENTED the model cannot even express the expected unit

**Step 4 — Attribute (ask WHY — do NOT fix).** For each gap, name the single responsible
**capability** (Parser · Semantic · Identity · Claim · State · Theme · Current-State · …). Record it
and **increment its frequency.** No code is written in Step 4.

**Step 5 — Next case.** Repeat. A capability is touched **only** when its frequency reaches **≥ 2**
across independent cases. Count 1 → *wait*, do not fix.

## The Capability Board

The board is the only driver of backend work. Fix rows with **Count ≥ 2**; leave Count ≤ 1 to
accumulate. (Provisional retro-seed from work already done — to be re-derived by running the cases
formally through Steps 0–4; not authoritative yet.)

| Capability     | P&P | 红楼梦 | DeepSeek | Kimi | Company | Count |
|----------------|-----|------|----------|------|---------|-------|
| Parser         | ✓   | ✓    | ✓        |      |         | 0 (all pass) |
| Identity       | ✓   | ✓    | ✓        |      |         | 3 → fixed (resolver: CJK, version, type-gating) |
| Claim / open-relation grounding | | | ✓ |      |         | 1 (Part B) → wait |
| State          | ✓   |      |          |      |         | 1 → wait |
| Theme          | ✓   |      |          |      |         | 1 → wait |
| Current-State  |     |      |          |      | ?       | 0 |
| Cross-corpus identity |   |      | ✓        | ✓    |         | 2 → candidate (deferred) |

Read it as: Identity earned its fixes (appeared 3×); Claim/State/Theme are each at Count 1 and must
**wait** for a second independent sighting before any backend work; cross-corpus identity is at 2 but
deferred by the freeze until a *product* surfaces it.

## Per-case output artifact

Each case ends by emitting, automatically:

    Expected · Current · Gap(+class) · Capability · Frequency · Decision(fix / wait)

That artifact — not a "bug" — is the case's product. The Explorer becomes the instrument that
generates it.

## Discipline guards

- **Never fix on first sighting.** Count 1 is data, not a mandate.
- **Never add a capability speculatively** — only ones a real diff surfaces.
- **Step 4 forbids code.** Attribution and fixing are separated on purpose (proposes vs. commits, the
  LYR discipline, applied to our own process).
- **The board is the only bridge** from case to backend. No out-of-band fixes.
- **Consistent with the freeze:** Count ≥ 2 is a formalized reopen-trigger; it does not override the
  product-trigger requirement, it sharpens it.

## Next action

Run **P&P · 红楼梦 · DeepSeek** through Steps 0–4 once each, re-deriving the board from real diffs
(replacing the provisional retro-seed). Backend grows only where the board then shows Count ≥ 2 —
slowly, stably, and always knowing *why*.
