# Reproduction Experiment 1 — Independent Execution of the Identifiability Note

*Phase 1 of the roadmap (minimal note → **independent reproduction** → paper → scaling).
The test of a methodological note is not whether its authors find it coherent, but whether
a stranger can **execute** it. This records that test, honestly, including where it did not
fully reproduce.*

**Spine under test:** *Identification is not a property of an explanation; it is the output
of an auditable procedure.* If that is true, the procedure must run in hands other than the
authors'.

---

## Design (pre-registered before reading results)

Three independent executors were each given a **self-contained packet** — the note's
definitions (`Θ = H × M`, the compatibility relation `r ⊨_m h`, `C(r)`, constraint
accumulation `Θₙ`, target `Q`, identified set `I_Q`) and the constraint-witness schema —
plus the **inputs only** of the two worked examples (record `r`, `H`, `M`, the targets, and
the available constraints). The committed answers (§3/§4 tables, `C(r)`, `I_Q`) were
**withheld**. Executors were forbidden from reading any repository file, and given no access
to the conversation that produced the note.

Each was asked to (1) enumerate `Θ`, (2) evaluate compatibility for every pair, (3) write
`C(r)`, (4) compute `I_Q` per target, (5) fill the witness schema per constraint, and
crucially (6) **keep a running list of every point where they could not continue without
inventing something not in the packet.**

One refinement over the committed note: the packet offered compatibility three values —
`compatible / incompatible / underspecified` — where §1 offers only two. This was
deliberate: it lets an executor *flag* an undecidable cell instead of silently guessing, so
the experiment can see divergence instead of hiding it.

**Pre-registered outcomes:**
- **PASS** — executors converge on the same `Θ`, `C(r)`, `I_Q`, and their invention lists
  are empty or trivial.
- **PARTIAL** — executors converge on structure and most results, but shared inventions
  localize specific under-specifications in the note.
- **FAIL** — divergent `I_Q` with no traceable cause, or an executor stuck (cannot continue
  at all).

---

## Result: **executability PASS, reproducibility PARTIAL**

No executor got stuck. All three ran the protocol end-to-end and produced output in the
schema. They continued past every difficulty by *logging an invention* — exactly the
protocol's step (6). So the **definitions are executable by strangers**; the divergences are
all in the two **worked examples**, and all three are localized.

### Example A (Diary) — reproduced

| quantity | replica 1 | replica 2 | replica 3 | committed §3 |
|---|---|---|---|---|
| `C(r)` | `{cs, cc, sc}` | `{cs, cc, sc}` | `{cs, cc, sc}` | `{cs, cc, sc}` |
| `I_{Q₁}` before / after `c₁` | `{yes,no}` / `{yes}` | same | same | same |
| `I_{Q₂}` | `{fear,duty,social}` | same | same | same |

*(`cs = (h_change,m_stable)`, `cc = (h_change,m_change)`, `sc = (h_stable,m_change)`.)*

Full convergence, matching the committed answer. The load-bearing detail: **all three
independently re-derived the note's background commitment `A₁` ("stable stylometry ⟹ stable
framing")** as the assumption `c₁` needs — without ever seeing §3. The assumption the note
*logs* is the one strangers *reach for*. That is reproduction working.

### Example B (Agent log) — diverged at one cell

| quantity | replica 1 | replica 2 | replica 3 | committed §4 |
|---|---|---|---|---|
| `(h_notX, m_censored)` | **underspecified** | **compatible** | **branched** (Res A ✗ / Res B ✓) | **compatible ✓** |
| `C(r)` size | 2 (+1 flagged) | 3 | 2 or 3 | 3 |
| `I_Q` after `c₁` | `{yes}` or `{yes,no}` | `{yes,no}` | `{yes}` / `{yes,no}` | `{yes,no}` |
| `I_Q` after `c₂` | `{yes}` | `{yes}` | `{yes}` | `{yes}` |

The endpoints agree (`{yes}` after the independent channel). The divergence is at
`(h_notX, m_censored)`: whether a failure "caused by a logged call" is consistent with a
process that "drops failed calls" depends on an undefined predicate — *does the causing call
itself count as "failed," and therefore get censored (contradicting "logged")?* The note's
bare `✓` never resolves it, so executors split.

---

## Three localized fixes (each a missing row in the note's *own* schema)

Every divergence points *inward* — to a premise the note already has machinery for, not to a
hole in the theory.

1. **§3, the `(h_stable,m_stable)` exclusion — missing closure premise.**
   The cell is declared "forbidden ✗" with no background commitment. All three executors
   supplied the same one: *the record is generated only by (attitude × framing), with no
   third driver* (e.g. real family events could raise family content under constant attitude
   and constant framing). Without it, the cell is `underspecified`, not forbidden. **Fix:**
   log the closure premise as an explicit assumption on that cell.

2. **§4, the `(h_notX,m_censored)` cell — a formalization split (`F`), unapplied.**
   "Caused" is multi-valued: `F(d) = {caused-and-failed, caused-without-failing}`. Under
   *caused-and-failed*, the causing call is censored ⟹ not logged ⟹ contradicts `h_notX` ⟹
   cell incompatible. Under *caused-without-failing*, it stays ⟹ compatible. The note's `✓`
   is one reading silently chosen. This is precisely the §6 `F` machinery — the note should
   **apply its own F-robust identified set** here and report the reading its membership
   depends on. (Replicas 1 and 3 effectively demanded this by refusing to collapse the cell.)

3. **§4, `c₂` — missing causation bridge.**
   `S₂ = {h_X}` is asserted directly, but the witness (external audit: "deploy failed @ 3")
   licenses "X *ran and failed*," not "X *caused* the terminal failure." All three executors
   flagged the gap. **Fix:** add `A_cause` (the failed call is the terminal cause) as a named
   background commitment alongside `A_audit`, so the restriction is witnessed, not smuggled.

**Meta-finding.** The two executors who had access to an explicit `underspecified` value used
it exactly where §1's two-valued relation would have forced a silent guess. This suggests the
compatibility relation should route an undecidable cell into `F` (split into readings) rather
than collapse it — i.e. §3/§4's bare `✓`/`✗` cells whose truth is non-obvious should each
carry the formalization that makes them decidable.

---

## What this establishes, precisely

- **The procedure is executable by people who never spoke to its authors.** No executor was
  stuck; all reached a definite `I_Q` for every target. The spine survives its first external
  test: identification came out as *the output of running the procedure*, not as a property
  the executors had to already agree on.
- **The two worked examples are not yet fully self-contained.** Three spots require a premise
  the example text omits. This is a defect in the *examples*, not the *formalism* — every fix
  is an application of machinery the note already defines (§2's commitments column, §6's `F`).
- **The audit caught its own gaps.** The "log every invention" step located 100% of the
  divergences, and each maps to a nameable row. That is the protocol behaving as advertised:
  it does not hide where it leans on an assumption; it surfaces it.

**Honest bar check.** The user's Phase-1 criterion was "record every place they cannot
continue without inventing something." They had to invent at three places. By the strict
reading those are three reproduction misses; by the generous reading two of them (`A₁`, the
`F` split) are the note's own declared machinery being re-derived rather than holes. Recorded
as-is, un-spun.

## Next step (gated on the fixes)

Apply the three fixes to §3/§4, then **re-run the same reproduction test on the patched
note.** Phase 2 (writing the methodological paper) should begin only if the patched examples
reproduce with an *empty* invention list — i.e. a stranger can execute both examples to the
committed `I_Q` without supplying any premise the note did not give them.

## Caveat

The "strangers" here are independent LLM executors given a clean packet and no conversational
context — a strong but not identical proxy for human first-time readers. It removes the
authors' shared context (the thing that makes self-assessment unreliable) but does not remove
model-shared priors. A human execution remains the stronger version of Phase 1 and is not
replaced by this run.
