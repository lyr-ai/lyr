"""Evidence-grounded status verifier — the anti-fabrication core of a Knowledge Object.

The Knowledge-Object Exploration (docs/design/review-semantic-to-knowledge-transition.md)
found that four independent corpora reduce to one primitive: a **scoped, evidenced,
status-bearing claim** over semantic objects. The fabrication risk lives entirely in the
*status*: a system that confidently asserts an unsupported relation (DeepSeek's
`MLA → DSA → CSA → HCA` "lineage") is manufacturing narrative, not knowledge.

This module is the smallest thing that decides status **from the evidence**, not from a
model's prior. It is a deterministic **baseline verifier** — the same role
`RecurrenceConsolidator` plays for the durable layer and the rule extractor plays for the
semantic layer: crude, transparent, offline, and a control the eventual LLM verifier is
measured against. It does NOT propose knowledge objects; it grades proposed claims/relations.

A relation is `SUPPORTED` only if a single passage mentions **both** endpoints together with a
**derivation cue**; otherwise `UNKNOWN` (abstained — checked and refused, not merely unseen).
That one rule is what makes DeepSeek's lineage abstain (no passage links MLA and DSA) while
Kimi's `MuonClip improves upon Muon` commits (one passage states it).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

SUPPORTED = "SUPPORTED"
CONTRADICTED = "CONTRADICTED"
UNKNOWN = "UNKNOWN"          # checked, evidence absent → abstain
NOT_EVALUATED = "NOT_EVALUATED"  # never checked

# Multi-word on purpose: a bare "improve" false-positives on "combines CSA and HCA to
# improve long-context efficiency" (which is NOT a derivation between CSA and HCA). Requiring
# a derivation *phrase* is the minimal guard against cue-matching fabrication.
DERIVATION_CUES = (
    "improves upon", "improved upon", "builds upon", "built upon", "based upon",
    "based on", "derived from", "successor to", "successor of", "evolution of",
    "an evolution", "evolved from", "replaces", "supersedes", "extends",
)


@dataclass
class Passage:
    id: str
    text: str
    anchor: str = ""  # version / chapter, if known


@dataclass
class Claim:
    target: str
    relation: str          # e.g. "member_of", "derivation", "quantified"
    value: str
    scope: str
    status: str = NOT_EVALUATED
    evidence: list[str] = field(default_factory=list)
    reason: str = ""


def _mentions(text_low: str, aliases: tuple[str, ...]) -> bool:
    """Word-boundary alias match. `\\bmuon\\b` matches a standalone 'Muon' but NOT the 'muon'
    inside 'MuonClip', so the two are never conflated."""
    return any(re.search(r"\b" + re.escape(a.lower()) + r"\b", text_low) for a in aliases)


def ground_derivation(a_aliases: tuple[str, ...], b_aliases: tuple[str, ...],
                      passages: list[Passage]) -> Claim:
    """Does the corpus state that A derives from / improves upon B? SUPPORTED only if one
    passage names BOTH and carries a derivation phrase; else UNKNOWN (abstained)."""
    for p in passages:
        t = p.text.lower()
        if _mentions(t, a_aliases) and _mentions(t, b_aliases):
            cue = next((c for c in DERIVATION_CUES if c in t), None)
            if cue:
                return Claim(a_aliases[0], "derivation", f"derives from/({cue}) {b_aliases[0]}",
                             "architecture", SUPPORTED, [p.id],
                             f"passage {p.id} links both endpoints with '{cue}'")
    return Claim(a_aliases[0], "derivation", f"derives from {b_aliases[0]}", "architecture",
                 UNKNOWN, [], "no passage links these two endpoints with a derivation cue")


def ground_grouping(members: list[tuple[str, ...]], goal_terms: tuple[str, ...],
                    passages: list[Passage]) -> Claim:
    """Are the members one group by a shared goal? SUPPORTED if >=2 members each appear in a
    passage that also states the shared goal."""
    ev, grounded = [], 0
    for m in members:
        for p in passages:
            t = p.text.lower()
            if _mentions(t, m) and any(g in t for g in goal_terms):
                grounded += 1
                ev.append(p.id)
                break
    if grounded >= 2:
        return Claim("group", "member_of", "shared goal", "grouping", SUPPORTED, ev,
                     f"{grounded} members each cited alongside the shared goal")
    return Claim("group", "member_of", "shared goal", "grouping", UNKNOWN, ev,
                 f"only {grounded} member(s) grounded to the shared goal")


def ground_value(key_tokens: tuple[str, ...], passages: list[Passage],
                 *, target: str = "", scope: str = "") -> Claim:
    """A specific value claim (e.g. a quantified comparison). SUPPORTED if one passage
    contains all key tokens."""
    for p in passages:
        t = p.text.lower()
        if all(k.lower() in t for k in key_tokens):
            return Claim(target, "quantified", " ".join(key_tokens), scope, SUPPORTED, [p.id],
                         f"passage {p.id} states the value")
    return Claim(target, "quantified", " ".join(key_tokens), scope, UNKNOWN, [],
                 "no passage states this value")
