"""Structured-claim verifier — SUPPORTED / CONTRADICTED / UNKNOWN, from evidence only.

Extends `grounding.py` from a relation-status checker to a verifier over a structured
`Claim(subject, predicate, object, scope)`. Three verdicts:

  SUPPORTED     a passage names both endpoints (or the value) with a cue matching the
                predicate's polarity.
  CONTRADICTED  a passage names both endpoints with the predicate's ANTONYM cue — the corpus
                asserts the opposite. (Generic antonym families; no corpus-specific words.)
  UNKNOWN       neither — checked and refused (abstained). Absence of support is NOT
                contradiction: an unstated derivation is UNKNOWN, never CONTRADICTED.

Deliberately a **deterministic baseline** (the control the LLM verifier is measured against).
Its known limit is *inferential* contradiction ("MLA is sparse" contradicted only by implication
from "DSA is sparse for the first time") — that needs the LLM verifier; the baseline returns
UNKNOWN there (safe: never accepted as SUPPORTED). See README for the honest bound.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from grounding import (CONTRADICTED, DERIVATION_CUES, NOT_EVALUATED, SUPPORTED,
                       UNKNOWN, Passage, _mentions)

# Generic predicate polarity families. Each maps a normalized predicate to the cue phrases
# that SUPPORT it and the antonym phrases that CONTRADICT it. These are ordinary-English
# relation polarities — not tied to any corpus.
PREDICATE_POLARITY: dict[str, dict[str, tuple[str, ...]]] = {
    "derives_from": {"support": DERIVATION_CUES, "contra": ()},  # absence ≠ contradiction
    "accepts":      {"support": ("accepts", "accepted", "agrees to", "consents to", "consented"),
                     "contra": ("refuses", "refused", "rejects", "rejected", "declines", "declined")},
    "refuses":      {"support": ("refuses", "refused", "rejects", "rejected", "declines", "declined"),
                     "contra": ("accepts", "accepted", "agrees to", "consents to")},
    "introduces":   {"support": ("introduces", "introduced", "for the first time", "adds ", "proposes"),
                     "contra": ("absent from", "not present in", "removed", "no longer")},
    "married":      {"support": ("married", "marriage", "wed", "wedding", "wife", "husband"),
                     "contra": ()},
    "engaged":      {"support": ("engaged", "engagement", "betrothed"),
                     "contra": ("refuses", "refused", "rejects", "rejected")},
}


@dataclass
class Claim:
    subject: str
    predicate: str          # normalized: derives_from / accepts / refuses / introduces / grouping / quantified
    object: str
    scope: str = ""
    subject_aliases: tuple[str, ...] = ()
    object_aliases: tuple[str, ...] = ()
    value_tokens: tuple[str, ...] = ()   # for "quantified"
    group_members: tuple[tuple[str, ...], ...] = ()  # for "grouping"
    goal_terms: tuple[str, ...] = ()                 # for "grouping"

    def _subj(self) -> tuple[str, ...]:
        return self.subject_aliases or (self.subject,)

    def _obj(self) -> tuple[str, ...]:
        return self.object_aliases or (self.object,)


@dataclass
class Verdict:
    claim: Claim
    status: str = NOT_EVALUATED
    evidence: list[str] = field(default_factory=list)
    reason: str = ""


def _relational(claim: Claim, passages: list[Passage]) -> Verdict:
    pol = PREDICATE_POLARITY.get(claim.predicate, {"support": (), "contra": ()})
    for p in passages:
        t = p.text.lower()
        if _mentions(t, claim._subj()) and _mentions(t, claim._obj()):
            contra = next((c for c in pol["contra"] if c in t), None)
            if contra:
                return Verdict(claim, CONTRADICTED, [p.id],
                               f"passage {p.id} asserts the antonym '{contra.strip()}'")
            sup = next((c for c in pol["support"] if c in t), None)
            if sup:
                return Verdict(claim, SUPPORTED, [p.id],
                               f"passage {p.id} states '{sup.strip()}'")
    return Verdict(claim, UNKNOWN, [], "no passage links these endpoints with a matching cue")


def verify(claim: Claim, passages: list[Passage]) -> Verdict:
    if claim.predicate == "grouping":
        ev, grounded = [], 0
        for m in claim.group_members:
            for p in passages:
                t = p.text.lower()
                if _mentions(t, m) and any(g in t for g in claim.goal_terms):
                    grounded += 1
                    ev.append(p.id)
                    break
        if grounded >= 2:
            return Verdict(claim, SUPPORTED, ev, f"{grounded} members cited with the shared goal")
        return Verdict(claim, UNKNOWN, ev, f"only {grounded} member(s) grounded to the goal")
    if claim.predicate == "quantified":
        for p in passages:
            t = p.text.lower()
            if all(k.lower() in t for k in claim.value_tokens):
                return Verdict(claim, SUPPORTED, [p.id], f"passage {p.id} states the value")
        return Verdict(claim, UNKNOWN, [], "no passage states this value")
    return _relational(claim, passages)
