# Prototype 3 — Elizabeth → State (representation probe)

**Status:** research probe, by hand from the extracted P&P package (`elizabeth-bennet.json`, 98
chapter-stamped timeline steps, 128 evidence passages). Tests the sharp question, **not** "does
Elizabeth have an arc": *for a fixed target claim, when is a change in its committed value licensed
by evidence?* Target as stated: **Elizabeth's assessment of Darcy.**

## The first move the protocol forces: split the target by scope

"Elizabeth's assessment of Darcy" is not one claim. The evidence separates into two scopes that must
**not** be conflated:

- **Claim A — behavioral disposition:** *Elizabeth's disposition toward marrying Darcy.* Scope =
  public acts.
- **Claim B — inner assessment:** *Elizabeth's private judgment of Darcy's character.* Scope =
  interior state.

Conflating A and B into one "prejudice → love" arc is the fabrication the stateful-claims gap warned
about. Kept separate, they get very different statuses.

## Claim A — behavioral disposition (committable)

    value          anchor   evidence                          status of the transition
    refuses        ch34     "Elizabeth refuses Mr. Darcy"(3ev) —
    → engaged      ch59     "Elizabeth ... engaged to Darcy"(3) SUPPORTED (event, same scope, direct)
    → married      ch61     "Elizabeth is married to Darcy"(1)  SUPPORTED (event, same scope, direct)

Every value is a **public act**, directly narrated, same scope throughout. The transitions are
committable: `SUPPORTED`. This is a real, honest state history — and notably it is built from
*events*, not from interpretive labels.

## Claim B — inner assessment (mostly abstain)

    value              anchor   evidence                                    transition status
    negative           ch18/34  "discontent"(2) / "dislike of Darcy"(2)     — (extractor-interpreted)
    → destabilized     ch36     "changing perception of Wickham & Darcy"(3) SUPPORTED* (letter, ch35–36
                                 after "Darcy delivers letter" + "Elizabeth  narrated reassessment)
                                 reads Darcy's letter")
    → warming          ch44     "Elizabeth's evolving feelings ..."(1)      UNKNOWN (1 ev; interpreter
                                                                            label "evolving", direction
                                                                            asserted not shown)
    → positive/love    (—)      no inner-state passage; inferred from        ABSTAINED (inferred from
                                 engagement (Claim A)                        behavior, not stated)

Applying the five transition questions:

1. **Which value changed?** negative → destabilized → (warming?) → (positive?).
2. **Same scope before/after?** Yes *within* Claim B — but the terminal "positive" is only reachable
   by importing Claim A (behavior), a **scope violation** → refuse.
3. **Inner state / expression / behavior?** ch18–34 "dislike" and ch44 "evolving feelings" are the
   **extractor's interpretive labels**, not quoted inner statements. Only ch35–36 (the letter and her
   reading it) is a **directly narrated** reassessment.
4. **Directly supported or interpreter-inferred?** Only the ch36 pivot is directly supported. The
   endpoints (settled "dislike", terminal "love") are interpreter-inferred.
5. **Can it stop at `unknown`?** It must: the terminal inner value is `ABSTAINED`; ch44 "warming" is
   `UNKNOWN` (single weak, direction-asserting label).

So Claim B is **largely `UNKNOWN`/`ABSTAINED`, with exactly one `SUPPORTED` transition** (the letter
pivot). That is the honest answer — and it refines the stateful-claims doc precisely: the
*behavioral* arc IS in the data (Claim A, supported); the *inner-understanding* arc is mostly **not**
(Claim B, abstained), except where the text itself narrates the reassessment.

## What this proves about the abstention discipline

Prototype 1's discipline holds in a third, unrelated domain, and it is what keeps "Elizabeth's arc"
honest: separate scoped claims, commit a value-change only when it is same-scope **and**
directly-supported, abstain otherwise. The tempting single "prejudice → love" narrative is refused
not by taste but by the scope + status rules.

## Representation requirements — the same primitive, now time-indexed

Identical four constituents; identical `target · relation · value · scope · evidence · status`. State
adds only that the *position index* is **time/chapter** (Concept's was **version**), and that a
**transition** is itself a status-bearing assertion (`SUPPORTED / UNKNOWN / ABSTAINED / CONTRADICTED`)
answering "is this value-change licensed?"

## Falsifiability verdict

A State object forms **honestly only when split by scope**: the behavioral disposition commits a real
value history; the inner assessment mostly abstains. Zero fabrication survived. The protocol produced
a result that is *less* satisfying as a story and *more* defensible as knowledge — which is the point.
