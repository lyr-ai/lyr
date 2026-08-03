# Case 001 — GitHub Pages deploy failure

*Bootstrap case. A **real** incident from this repository's own history, run through the frozen
protocol. It is here to seed the template and to demonstrate one core move — naming a generic
error message a **measurement artifact** rather than reading it as the cause.*

**Provenance note (honest, up front):** the incident is real (it occurred while setting up the
LYR GitHub Pages site and was fixed by adding `enablement: true` to the `configure-pages` step,
after which the site went live). The failing run's exact log text was read in-session but not
re-captured into the repo, so the record below is at **summary granularity**. Where that weakens
a witness, it is flagged. This under-provenance is itself recorded, per the discipline.

---

## Incident

The first GitHub Actions run of the Pages deployment workflow (`site/` → GitHub Pages) failed at
the `actions/configure-pages` step and halted; the site did not publish.

## Evidence (`r`)

- `r₁`: the `configure-pages` step failed with a **generic** message of the form *"Get Pages
  site failed…"* and the run stopped. (Summary granularity — see provenance note.)
- `r₂`: the repository **Settings → Pages** view at the time (screenshots shared in-session),
  showing the Pages source not yet established via Actions.

## Formalization (`F`)

The phrase in `r₁`, *"Get Pages site failed,"* is multi-valued:

- `f_absent`: *there is no Pages site to get* (Pages never enabled).
- `f_fetch`: *a Pages site exists but the step could not fetch/configure it* (permissions,
  transient outage, or workflow error).

`F(d) = {f_absent, f_fetch}`.

## H (candidate causes)

- `h_notenabled`: Pages was never enabled for the repo (no site source set).
- `h_workflow`: the workflow YAML is misconfigured (e.g. missing enablement).
- `h_perms`: the workflow token lacks Pages write permission.
- `h_transient`: a transient GitHub-side outage.

## M (measurement — how the failure became this record)

- `m_specific`: the `configure-pages` action reports the *true underlying cause* in its message.
- `m_generic`: the action emits the same *"Get Pages site failed"* for several distinct causes —
  a **lossy** measurement that under-determines the cause.

Observation: the message did not vary with the candidate cause; it is generic across
`h_notenabled / h_perms / h_transient`. So **`m_generic` is the operative measurement**. This is
the crux of the case: `r₁` is a *measurement artifact*, not a reading of the cause.

## Constraints

- `c₁` (settings witness). Restriction `S₁`: worlds where Pages was not enabled.
  Excludes `h_workflow`, `h_perms` as *primary* (there was no site to configure or authorize
  against). Witness: `r₂`, the Settings → Pages view. Type: **empirical, under `A_settings`**
  (the settings view at inspection reflects the state at failure time).
- `c₂` (intervention witness). Restriction `S₂`: worlds where the missing enablement was the
  blocking cause → `h_notenabled`. Witness: adding `with: enablement: true` to the
  `configure-pages` step — *changing nothing else* — made the next run succeed and the site went
  live (`https://lyr-ai.github.io/lyr/`). Type: **empirical, under `A_intervention`** (the fix's
  success is attributable to that single change; no confounding change in the same window) **and
  `A_nontransient`** (success was not merely a transient outage clearing on its own).

## Witnesses

| constraint | witness | type |
|---|---|---|
| `c₁` | Settings → Pages view (`r₂`) | empirical, under `A_settings` |
| `c₂` | single-change fix → successful deploy | empirical, under `A_intervention`, `A_nontransient` |

## I_Q — target `Q` = "what caused the deploy failure?"

| stage | `I_Q` |
|---|---|
| on `r` alone (F-robust) | `{h_notenabled, h_workflow, h_perms, h_transient}` — **not identified**; `m_generic` distinguishes none |
| after `c₁` | narrows toward `h_notenabled`; `h_perms` not yet excluded from co-occurring |
| after `c₂` | **`{h_notenabled}`** — F-robustly identified, under `{A_settings, A_intervention, A_nontransient}` |

Under `f_absent` the identification is direct; under `f_fetch`, `c₂`'s single-change success still
pins the *blocking* cause to the missing enablement. So `Q` is `F`-robustly identified.

## Final diagnosis

The deployment failed because **GitHub Pages had not been enabled for the repository** — there was
no site for `configure-pages` to configure. The generic *"Get Pages site failed"* message was a
**measurement artifact** that did not itself reveal this. Held under `A_settings`,
`A_intervention`, `A_nontransient`.

## Unidentified

- Whether `h_perms` would have independently blocked a later step (never reached; untested).
  *Closing witness:* a run with Pages enabled but token permission removed.
- Whether `h_transient` contributed at all (excluded only *weakly*, by the fix's immediate
  success). *Closing witness:* GitHub status history for that window.
- The exact raw log text (this case is at summary provenance). *Closing witness:* re-capturing
  the failed run's log into the repo.

---

**What this case shows about the protocol (one line).** The value was not a cleverer guess — the
fix was already known. It was forcing the generic error message to be *named* a measurement
artifact (`m_generic`) instead of read as the cause, and requiring the diagnosis to be *tagged*
with the intervention assumption (`A_intervention`) that actually carried it — so the record of
"why it broke" states what it rests on, and what it still doesn't know.
