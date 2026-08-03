# Application Data Strategy — Community Knowledge (Pet Health)

**Status:** Proposal — **deferred** (committed but not started; queued behind the active
agent-root-cause line, and awaiting real public/consented pet-health data)
**Project:** LYR Applications
**Purpose:** Define a sustainable, ethical, and reproducible data strategy for LYR applications
using real community knowledge.

> **Inherits the application-line discipline** (see `../agent-root-cause/README.md` and
> `../../research-status.md`): real evidence only; the protocol is **fixed**; failure cases are
> preserved, not patched (a protocol that cannot express a real case triggers **Research
> Reopening #3**, never an ad-hoc modification); provenance and uncertainty stay explicit. Cases
> use the shared fixed template. No data is collected by committing this note — it is a plan.

---

## Motivation

The goal of the Applications line is **not** to validate the theory by creating synthetic
examples. It is to expose the protocol to **real-world evidence** and let reality — not the
authors — determine whether the protocol remains sufficient.

Pet-health communities are an attractive first domain because they naturally contain uncertain
diagnoses, multiple competing hypotheses, evolving evidence, multiple measurement channels, and
eventual confirmations (or unresolved outcomes). This closely matches the assumptions of the
LYR identification protocol.

## Why not the Facebook Group API?

**The Facebook Groups API is not a viable data source.** Meta has removed public support for
accessing group posts/comments through the Graph API. Even if scraping were technically possible,
it introduces terms-of-service concerns, privacy and consent problems, poor reproducibility, and
risk to an open-source research project.

> **LYR Applications will not depend on Facebook Group API access or unauthorized scraping.**

## Design principle

The application line follows the same discipline as the research line:

> Use **real** evidence rather than generated examples.
> Use **ethically obtained** data rather than merely technically obtainable data.

---

## Data source hierarchy

**Tier 1 (preferred) — public communities.** Reddit, public discussion forums, open veterinary
communities, public support forums. Publicly accessible, reproducible, referenceable, lower
privacy risk, better for open demonstrations. *This becomes the primary reproducible dataset.*

**Tier 2 — consented Facebook cases.** Not scraping groups — collecting *individual* cases with
permission:

```
case owner → permission → original post → replies → veterinary updates → final diagnosis
           → anonymized LYR case
```

Real longitudinal history, rich evidence, multiple viewpoints, ethical provenance, high-quality
witness chains.

**Tier 3 — personal cases.** Personal pet history, friends, family. Useful during development;
**not** primary evaluation datasets.

## Unit of analysis

LYR does **not** analyze individual posts. The unit is a **complete longitudinal case**:

```
initial report → community discussion → additional evidence → veterinary examinations
              → testing → treatment → outcome
```

This lets identification evolve over time.

## Measurement channels

Each information source is a different **measurement process**. Rather than collapsing them, LYR
models each as its own channel:

```
owner observations → community replies → general vet → specialist → MRI/imaging → pathology → outcome
```

## Protocol output (per case)

Uses the shared fixed template (`Incident/Evidence/F/H/M/Constraints/Witnesses/I_Q/Diagnosis/
Unidentified`), with one forward-looking field natural to longitudinal cases — **the next
informative observation** (which missing witness would most shrink `I_Q`; this is the
"Unidentified → closing witness" field, stated prospectively):

```
world hypotheses → measurement assumptions → witnesses → constraints → identified set I_Q
                → remaining uncertainty → next informative observation
```

The goal is **not** to predict. It is to make identification transparent.

## First demonstration

The first public application should answer:

> **What diagnosis is currently _identified_?**

not

> What diagnosis is most _likely_?

Output: competing hypotheses · supporting evidence · measurement assumptions · remaining
uncertainty · the next observation that would most reduce uncertainty.

---

## Ethical principles

- **No unauthorized scraping.** No collection that violates platform policies.
- **Consent when required.** Private community cases require explicit permission.
- **Preserve provenance.** Each observation records source, timestamp, channel, evidence type.
- **Preserve uncertainty.** LYR never reports certainty unsupported by the available evidence.

## Success criteria

Not prediction accuracy alone. Success means:

- real-world cases can be represented **without modifying the protocol**;
- evidence provenance stays explicit;
- measurement assumptions stay visible;
- competing hypotheses stay auditable;
- new evidence progressively shrinks the identified set;
- any protocol failure triggers **Research Reopening #3** rather than an ad-hoc modification.

(Consistent with the shared metric: the number that matters is *research reopenings*, not cases
completed.)

## Long-term vision & future work

The same protocol should apply across community-knowledge domains — pet health, parenting,
gardening, automotive repair, programming forums, rare-disease communities. *The protocol stays
identical; only the evidence changes.* After the pet-health application stabilizes, apply the
same methodology to further domains to test whether the protocol generalizes **without
theoretical modification**.

---

> **Design principle.** Community knowledge is valuable not because it contains many answers, but
> because it records **how uncertainty evolves as evidence accumulates.** LYR's role is to make
> that evolution explicit, auditable, and reproducible.
