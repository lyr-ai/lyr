# Prototype 2 — P&P → Theme (representation probe)

**Status:** research probe, by hand from the real corpus (`pride-and-prejudice.raw.txt` + the
extracted P&P package). Uses the Prototype-1-revised protocol: every assertion carries a **committed
status** (`SUPPORTED / CONTRADICTED / UNKNOWN / NOT_EVALUATED`); safe claims are separated from
interpretive ones; abstentions are first-class.

Theme is the hallucination-prone candidate — an LLM will emit "Pride / Class / Marriage" whether or
not an object formed. So the probe is run as **three gates**, and a theme may pass one and fail the
next.

## Gate 1 — instance coverage (which extracted objects actually instantiate the theme?)

Grounded in the extracted graph (events/relationships with evidence), not in memory of the novel:

- **Marriage — SUPPORTED.** 29 distinct extracted instances, e.g. Collins proposes to Elizabeth
  (ch19, 6 ev) → Elizabeth rejects (ch19) → Charlotte accepts Collins (ch22, 4 ev) → Charlotte's
  wedding (ch26) → Darcy proposes (ch34, 3 ev) → Lydia elopes with Wickham (ch46, 3 ev). Real
  instances, each evidence-cited.
- **Class / money — INSUFFICIENT (does not form).** Only ~6 weak, ambiguous hits, most of them the
  generic word "connection" (ch21, ch25, ch30, ch43) plus "Collins is heir to the estate" (ch13).
  The extractor did **not** surface class/economic pressure as instances. Gate 1 **fails** → the
  Class theme must **abstain**, not be asserted.

**First result already:** the two behave differently. A representation that lets "Marriage" form and
forces "Class" to abstain is doing its job; one that emits both equally is hallucinating.

## Gate 2 — unifying claim (on what basis are the instances ONE theme?)

For Marriage, two different claims hide under one word, and they do not share a status:

- **`marriage-formation events recur and are central`** — **SUPPORTED.** The instances are all
  proposal / acceptance / rejection / wedding / elopement events; grouping them by that event-type is
  evidence-backed.
- **`the novel critiques the marriage market as social/economic coercion`** — **ABSTAINED
  (interpreter-inferred).** That is the literary reading. The *events* support "marriage recurs and
  drives the plot"; they do **not**, by themselves, support the thematic *argument*. Committing it
  would be exactly the Prototype-1 error (asserting an organizing narrative beyond the evidence),
  here in thematic clothing.

So a Theme object has (at least) **two claim layers**: an *instance-grouping* claim (safe) and a
*thematic-interpretation* claim (must be earned separately or abstained). This is the Theme-domain
form of Prototype 1's "grouping vs lineage."

## Gate 3 — inter-theme relations

- **`Marriage co-occurs with Class/money`** — **SUPPORTED (weakly).** Collins proposes *because* he
  is the entail heir (ch13 + ch19); Charlotte accepts for security (ch22). Co-occurrence is
  evidenced.
- **`Class causes the marriage pressure`** — **UNKNOWN.** A causal claim; no passage asserts the
  causation, and Gate 1 already showed Class barely extracts. Abstain.

## The honest result shape

    Theme candidate: Marriage
      instance coverage:            SUPPORTED   (29 instances, cited)
      instance-grouping claim:      SUPPORTED
      thematic-interpretation claim: ABSTAINED  (interpreter-inferred)
      causal relation to Class:     UNKNOWN
      global importance:            NOT_ESTABLISHED

    Theme candidate: Class
      instance coverage:            INSUFFICIENT → object does not form (abstain)

This is precisely the differentiated, partly-abstaining output the protocol demanded — a theme that
"looks true" at Gate 1 can still be exposed as interpretive packaging at Gate 2/3.

## Representation requirements — same four, plus one

Prototype 2 needs the identical four constituents Prototype 1 forced (members · grouping claim ·
typed relations *with status* · explicit abstentions), and every assertion still carries
`target · relation · value · scope · evidence · status`. The one addition Theme makes explicit:

- **a claim can have layers of increasing interpretive commitment** (instance-grouping →
  thematic-argument), and each layer gets its **own** status. The safe layer may be `SUPPORTED` while
  the interpretive layer is `ABSTAINED` on the same object.

## Falsifiability verdict

The hallucination-prone candidate was **contained** by the protocol: Marriage forms at the instance
layer and correctly abstains at the interpretive layer; Class correctly fails to form. No fabricated
theme survived. The status discipline from Prototype 1 held in a completely different domain.

## Carried forward (candidate, not conclusion)

Concept (P1) and Theme (P2) reduced to the **same shape**: members + a grouping claim + typed
relations, where the *safe* assertion (co-membership) is separated from the *unsafe* one (lineage /
thematic-argument), which must carry an `ABSTAINED` status. Same lower unit: **a scoped, evidenced,
status-bearing claim.** Two of three worlds agree; Prototype 3 (Elizabeth → State) is the deciding
leg.
