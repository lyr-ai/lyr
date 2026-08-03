# EXPERIMENT — M3.2-A Phase 1 (Evidence-Connectivity Baseline)

*Genericity passed. Provenance connectivity, on its own, is not the organizing signal —
and the very thing that made M3.1 formation work is what makes it fail here.*

## Setup

One function, `form_navigation(nodes: list[Node]) -> NavigationGraph`, run over the four
M3.1 domains — memoir, meeting, financial, git — reconstructed from real data (semantic
nodes from the fixtures; the 13 committed durable memories from the M3.1-C.1 verified
run). **No domain argument** is passed; the function cannot be told which domain it is
looking at.

## Result 1 — Genericity: **PASS**

- one code path, **no `domain` argument, no domain-specific branch**;
- identical output schema across all four domains;
- every `group → durable → semantic → source` path resolves (provenance intact);
- reproducible (order-independent); singletons reported honestly.

*Implementation genericity is confirmed.* This is all Phase 1 claims — not that the
navigation is useful.

## Result 2 — Organization: a blend of pre-registered **B and C**

| domain | durables | groups | compression | outcome |
|---|---|---|---|---|
| memoir | 3 | 3 | 1.0 | **B** — all singletons |
| meeting | 4 | 3 | 1.33 | **C** — a standup glued billing-sunset + CI-flakiness |
| financial | 3 | 2 | 1.5 | **C** — a 10-Q glued the acquisition + the dividend |
| git | 3 | 3 | 1.0 | **B** — all singletons |

The diagnostic number tells the whole story:

```
shared_semantic connections (all domains):  0
shared_source   connections (all domains):  2   ← both spurious
```

- **Zero `shared_semantic` links.** M3.1-B.2 decomposition *deliberately* gave each
  durable memory a disjoint set of semantic evidence (that is how it solved F7). So at
  the semantic level, provenance provides **no** topic links at all.
- **The only links are `shared_source`, and both are document artifacts, not topic
  coherence:** the financial 10-Q-2025Q2 filing mentions the acquisition *and* the
  dividend; the standup-04-12 note mentions the billing decision *and* CI flakiness.
  Grouping by shared source merges **topically unrelated** durables that merely
  co-occur in one document — structurally connected, navigationally misleading.

## Diagnosis

Provenance connectivity is simultaneously **too sparse** (decomposition disjoints
semantic evidence → no semantic links) and **too coarse** (source overlap = "same
document," not "same topic"). As an organizing signal it is **insufficient and partly
misleading.** Recorded as-is — the algorithm was *not* tuned to look like a knowledge
map.

The elegant part: **the very mechanism that made *formation* succeed makes
provenance-based *organization* fail.** Decomposition separates topics by design;
organization needs to *re-relate* them. Formation and Organization are genuinely
different problems that need different signals — exactly the M3 → M3.2 boundary.

## Implication / next step

Generic organization needs a **semantic (aboutness)** signal over the durable
*statements themselves* — not their provenance structure. The next experiment is a
**generic semantic organizer** (e.g. embeddings or an LLM over durable statements),
which must still obey the same falsifier: **one code path, no domain-specific
branch.** Provenance stays as the *explainable spine* (`group → durable → semantic →
source`), but it is not the clustering signal.

Only after a *semantic* organizer clears both this falsifier **and** Phase 2
(organizational adequacy on a richer corpus) should M3.2-B (`render(NavigationGraph)`)
begin.

## Caveat

13 durables total is small. But the load-bearing finding — **0 `shared_semantic` links
by construction** — is a structural consequence of decomposition, not a small-sample
artifact: more data would add more disjoint-evidence durables, not more semantic
overlap.
