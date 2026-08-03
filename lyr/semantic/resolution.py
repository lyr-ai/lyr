"""Generic entity resolution — do these mentions refer to the same entity?

A real corpus (a full novel) exposed a defect: keying identity on the extracted
label fragments one entity into many (a given name vs a full name; a bare
surname vs "Mr. <surname>" vs "<given> <surname>"). That is a **semantic-identity**
problem, not a presentation one, so it is solved here with **domain-independent**
signals — no per-book names anywhere.

Design principle (LYR's own): *the resolver proposes; the engine commits.* This
module only proposes ``LINK`` / ``UNSURE`` decisions with the evidence behind
them; it never rewrites a stored node's identity. Grouping is the transitive
closure of accepted ``LINK`` pairs.

Conservatism: for a demo (and for trust), a **false split is tolerable; a false
merge is not.** So a pair is linked only on a high-confidence *name-expansion*
signal; a shared surname alone yields ``UNSURE`` (a candidate to review), never a
merge; and any title/gender conflict or an explicit "these two are related as
distinct entities" signal is a hard reject.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

LINK = "LINK"
UNSURE = "UNSURE"
REJECT = "REJECT"

# Honorifics carry gender; a male-vs-female pairing is never the same person.
_MALE = {"mr", "sir", "colonel", "col", "lord", "master", "mister"}
_FEMALE = {"mrs", "miss", "lady", "madam", "madame"}
_TITLES = _MALE | _FEMALE


def _tokens(label: str) -> list[str]:
    return [re.sub(r"[.,]", "", t).casefold() for t in str(label).split() if t.strip()]


def _sig(label: str) -> set[str]:
    """Significant tokens: not a title, length >= 3, alphabetic (drops 'de', 'of')."""
    return {t for t in _tokens(label) if t not in _TITLES and len(t) >= 3 and t.isalpha()}


def _titles(label: str) -> set[str]:
    return {t for t in _tokens(label) if t in _TITLES}


def _titleless(label: str) -> bool:
    return not _titles(label)


def title_conflict(a: str, b: str) -> bool:
    ta, tb = _titles(a), _titles(b)
    return bool((ta & _MALE and tb & _FEMALE) or (ta & _FEMALE and tb & _MALE))


def _prefix_of(a: str, b: str) -> bool:
    """Token sequence of a is a contiguous prefix of b's (same title kept)."""
    ta, tb = _tokens(a), _tokens(b)
    return len(ta) < len(tb) and tb[: len(ta)] == ta


def name_expands(a: str, b: str) -> bool:
    """High-confidence same-name signal: one label is a name-expansion of the other.

    Either a contiguous token-prefix ("Lady <given>" ⊂ "Lady <given> <surname>"),
    or a *titleless* short form whose significant tokens are a subset ("<given>" ⊂
    "<given> <surname>"; a bare "<surname>" ⊂ "<given> <surname>"). The titleless
    requirement is what stops "Mrs. <surname>" ⊂ "<given> <surname>" (a titled
    surname is a specific adult, not a given-name expansion).
    """
    if _prefix_of(a, b) or _prefix_of(b, a):
        return True
    sa, sb = _sig(a), _sig(b)
    if not sa or not sb:
        return False
    # subset-or-equal: a bare "<surname>" expands a titled form with the same
    # surname ("Mr. <surname>", equal significant tokens).
    if _titleless(a) and sa <= sb:
        return True
    if _titleless(b) and sb <= sa:
        return True
    return False


def _shared_surname(a: str, b: str) -> bool:
    return bool(_sig(a) & _sig(b))


@dataclass
class Mention:
    id: str
    label: str
    entity_type: str = "entity"
    evidence: tuple = ()
    chapters: tuple = ()


@dataclass
class Decision:
    a: str
    b: str
    decision: str  # LINK / UNSURE / REJECT
    reason: str


@dataclass
class Group:
    canonical_label: str
    member_ids: list[str]
    member_labels: list[str]


@dataclass
class ResolutionResult:
    groups: list[Group] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class _UF:
    def __init__(self, ids: list[str]) -> None:
        self.p = {i: i for i in ids}

    def find(self, x: str) -> str:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: str, b: str) -> None:
        self.p[self.find(a)] = self.find(b)


def _entity_type(e) -> str:
    if isinstance(e, dict):
        return e.get("entity_type") or e.get("attributes", {}).get("entity_type") or "entity"
    return getattr(e, "entity_type", "entity")


def _endpoint_pairs(relationships) -> set[frozenset]:
    """Pairs of labels that appear as the two ends of one relationship → distinct."""
    out: set[frozenset] = set()
    for r in relationships or []:
        a = r.get("attributes", r).get("subject") if isinstance(r, dict) else getattr(r, "subject", None)
        b = r.get("attributes", r).get("object") if isinstance(r, dict) else getattr(r, "object", None)
        if a and b:
            na, nb = " ".join(_tokens(a)), " ".join(_tokens(b))
            if na and nb and na != nb:
                out.add(frozenset((na, nb)))
    return out


def resolve(entities, relationships=()) -> ResolutionResult:
    """Group entity mentions that refer to the same entity, generically."""
    ms: list[Mention] = []
    for e in entities:
        if isinstance(e, dict):
            ms.append(Mention(id=e["id"], label=e["label"], entity_type=_entity_type(e),
                              evidence=tuple(e.get("evidence", ())), chapters=tuple(e.get("chapters", ()))))
        else:
            ms.append(Mention(id=e.id, label=e.label, entity_type=_entity_type(e),
                              evidence=tuple(getattr(e, "evidence", ())), chapters=tuple(getattr(e, "chapters", ()))))

    exclusion = _endpoint_pairs(relationships)
    decisions: list[Decision] = []
    reject_pairs: set[frozenset] = set()
    link_pairs: list[tuple[Mention, Mention]] = []

    # pass 1 — decide every pair
    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            a, b = ms[i], ms[j]
            if a.entity_type != b.entity_type:
                continue
            na, nb = " ".join(_tokens(a.label)), " ".join(_tokens(b.label))
            if na == nb:
                continue
            if title_conflict(a.label, b.label):
                decisions.append(Decision(a.label, b.label, REJECT, "title/gender conflict"))
                reject_pairs.add(frozenset((a.label, b.label)))
            elif frozenset((na, nb)) in exclusion:
                decisions.append(Decision(a.label, b.label, REJECT, "related as two distinct entities"))
                reject_pairs.add(frozenset((a.label, b.label)))
            elif name_expands(a.label, b.label):
                decisions.append(Decision(a.label, b.label, LINK, "name expansion"))
                link_pairs.append((a, b))
            elif _shared_surname(a.label, b.label):
                decisions.append(Decision(a.label, b.label, UNSURE, "shared surname — candidate, needs review"))

    # pass 2 — union LINK pairs, but never bridge a rejected pair (guards against
    # a bare form transitively merging a Miss/Mr title-conflict pair)
    uf = _UF([m.id for m in ms])
    comp: dict[str, set[str]] = {m.id: {m.label} for m in ms}
    warnings: list[str] = []
    for a, b in link_pairs:
        ra, rb = uf.find(a.id), uf.find(b.id)
        if ra == rb:
            continue
        if any(frozenset((x, y)) in reject_pairs for x in comp[ra] for y in comp[rb]):
            warnings.append(f"blocked link '{a.label}' ~ '{b.label}' — would merge a rejected pair")
            continue
        merged = comp[ra] | comp[rb]
        uf.union(a.id, b.id)
        comp[uf.find(a.id)] = merged

    by_root: dict[str, list[Mention]] = {}
    for m in ms:
        by_root.setdefault(uf.find(m.id), []).append(m)

    groups: list[Group] = []
    for members in by_root.values():
        canonical = max(members, key=lambda m: (len(_sig(m.label)), len(m.evidence), len(m.label)))
        groups.append(Group(canonical_label=canonical.label,
                            member_ids=[m.id for m in members],
                            member_labels=[m.label for m in members]))
    groups.sort(key=lambda g: -len(g.member_ids))
    return ResolutionResult(groups=groups, decisions=decisions, warnings=warnings)
