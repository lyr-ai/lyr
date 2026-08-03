# Applications — notebook (not a theory notebook)

The protocol is frozen (see `docs/research-status.md`). This notebook holds **applications** of
it — concrete domains where it might be run. An application is a *use*, never a *reason to
modify*.

**The rule that makes the separation real.** A domain here does not change the protocol. If, and
only if, a real application forces a contradiction the protocol *cannot express*, that is re-open
trigger #3 — and it belongs back in the research process, explicitly, not smuggled in as an
application tweak. Every domain below is a validation surface, never the design center.

## Application lines

- **Agent root-cause analysis** — `applications/agent-root-cause/`. Closest to the data already at
  hand (bugs, telemetry, git history, incidents, agent logs), cleanest real evidence, on the
  long-term path (auditable memory, long-running agents, security). Internal / closest-to-home.
  Seeded: case 001.
- **Community knowledge (pet health)** — `applications/community-knowledge/` (**Proposal**).
  Public, reproducible, longitudinal, multi-channel, with eventual real confirmations. Aimed at
  the first *public* demonstration. Ethically-obtained data only (public → consented → personal);
  no Facebook API / scraping.

**Open decision (pending):** which is the *active* line. The single-active-line discipline
("pick one; wait, don't do") was set for agent root-cause; community knowledge is a strong but
newer proposal and cannot produce cases until real (public or consented) data is in hand. Both
inherit the same discipline — fixed protocol, preserved failures, reopening metric, failure-mode
coverage. The remaining candidate domains below stay parked.

## Candidate domains

- **Clinical notes** — did the patient's condition change, or did the documentation practice?
  (`M` = the charting process; `F` = clinical phrasing.)
- **Root-cause analysis** — did component `X` cause the outage? (Example B's structure at scale;
  logs as an adversarial-leaning `M`.)
- **Autobiographical journals** — Example A's structure: attitude vs. framing over a life.
- **Agent trajectories** — did the agent's stated reason cause its action? (`M` = the self-log,
  with censoring; `F` = "because".)
- **Scientific interpretation** — does the measured signal identify the claimed effect, or the
  instrument? (`M` = the apparatus.)
- **Historical sources** — did the event occur, or did the chronicler's framing shift? (`M` = the
  source's production and transmission.)

## The same five questions for every application

1. What is the target `Q` (the world-level claim being made)?
2. What is `H` (world hypotheses) and `M` (measurement processes)?
3. Where is `F` — which natural-language phrases are multi-valued?
4. What witnesses are available, and what do they cost in background commitments?
5. What is `I_Q`, and which *missing* constraint would identify it?

If those five run cleanly, the domain is an application. If question 3 or 5 has no expressible
answer in the protocol, stop — that is trigger #3, not an application.
