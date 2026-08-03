# Applying the Auditable Identification Protocol to Agent Root-Cause Analysis

The paper's protocol is frozen (see `../../research-status.md`). This line does **not** modify it.
It runs the protocol on real incidents to answer a different question:

> Does the protocol make real root-cause work **better**? — not "is the theory good?"

## Why this domain (chosen over clinical / journals / historical / scientific)

- **Closest to the data already at hand** — bugs, telemetry, git history, incidents, agent logs.
  No new data collection.
- **Cleanest real evidence** — the same incident, "guess the root cause" vs. run the protocol;
  the difference is inspectable, case by case.
- **On the long-term path** — auditable memory, long-running agents, security. The protocol
  becomes the theoretical basis of that work, not a separate project.
- **Generates the next paper by itself** — ten working cases turn "here is a theory" into
  "applying auditable identification to agent root-cause analysis." Theory becomes tool.

## Goal: 10 real cases. Not a second paper (yet).

Each case is ~2 pages on one fixed template. At case 10, the world — not the desk — will have
shown where the protocol is strong, where it is painful, and where it needs automation.

## Fixed template (every case)

```
Incident            — what happened, one paragraph
Evidence  (r)       — the actual record(s), with provenance
Formalization (F)   — which phrases are multi-valued; the admissible readings
H                   — world hypotheses (candidate causes)
M                   — measurement processes (how the incident became the record)
Constraints         — each cᵢ that shrinks Θ
Witnesses           — the artifact/observation behind each constraint (or "assumption")
I_Q                 — the identified set for the target, at each stage
Final diagnosis     — the world claim, under its named assumptions
Unidentified        — what stayed open, and which missing witness would close it
```

## Rules (the discipline, applied here)

- **Real incidents only.** Real evidence, real witnesses. A fabricated case validates nothing.
- **The protocol is fixed.** A case is a *use*, not a patch. If a real incident forces a
  contradiction the protocol *cannot express*, that is re-open trigger #3 — record it loudly and
  send it back to the research process; never fix it silently inside a case.
- **Honest provenance.** Where the raw witness is weaker than ideal (summary-level, a missing
  log), say so in the case. That is the protocol's own witness discipline turned on itself.

## Cases

- `case-001-pages-deploy-failure.md` — bootstrap case, sourced from **this repo's own history**
  (a real GitHub Pages deploy failure). It seeds the format and demonstrates the
  measurement-artifact move; the richer cases will come from live agent / telemetry incidents.
