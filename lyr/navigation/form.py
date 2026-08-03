"""form_navigation — the Evidence-Connectivity Baseline (M3.2-A).

One generic function: durable memories → a NavigationGraph, built **only** from
structural facts that exist in every domain (evidence ancestry + generic node kinds).

    durable nodes
      → resolve evidence ancestry (durable → semantic → source)
      → connect durables sharing semantic or source ancestry
      → connected components
      → NavigationGraph

It is a *baseline*, honestly named: it presupposes nothing about producing *useful*
topics — whether provenance connectivity is even sufficient for organization is the
experiment (M3.2-A §7). It contains **no domain argument and no domain-specific
branch** — it receives ``list[Node]`` and cannot be told which domain it is looking at,
so it cannot special-case one. That is the falsifier.

Deterministic → reproducible and unit-testable offline.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Iterable

from ..durable.base import is_active
from ..models import Node
from .graph import SHARED_SEMANTIC, SHARED_SOURCE, NavConnection, NavGroup, NavigationGraph


def form_navigation(nodes: Iterable[Node]) -> NavigationGraph:
    nodes = list(nodes)
    durables = [n for n in nodes if n.layer == "durable" and is_active(n)]
    semantic = {n.id: n for n in nodes if n.layer == "semantic"}

    # Evidence ancestry: durable → semantic ids, and → source ids (one hop down).
    sem_ev = {d.id: set(d.evidence) for d in durables}
    src_ev: dict[str, set] = {}
    for d in durables:
        srcs: set = set()
        for sid in d.evidence:
            s = semantic.get(sid)
            if s is not None:
                srcs.update(s.evidence)
        src_ev[d.id] = srcs

    # Connections — semantic overlap preferred; else source overlap. Reason recorded.
    ordered = sorted(durables, key=lambda n: n.id)
    connections: list[NavConnection] = []
    for a, b in combinations(ordered, 2):
        shared_sem = sem_ev[a.id] & sem_ev[b.id]
        if shared_sem:
            connections.append(NavConnection(a.id, b.id, SHARED_SEMANTIC, tuple(sorted(shared_sem))))
            continue
        shared_src = src_ev[a.id] & src_ev[b.id]
        if shared_src:
            connections.append(NavConnection(a.id, b.id, SHARED_SOURCE, tuple(sorted(shared_src))))

    # Connected components (union-find) — the baseline's groups.
    parent = {d.id: d.id for d in durables}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for c in connections:
        parent[find(c.frm)] = find(c.to)

    comps: dict[str, list[str]] = {}
    for d in durables:
        comps.setdefault(find(d.id), []).append(d.id)

    dmap = {d.id: d for d in durables}
    degree: Counter = Counter()
    for c in connections:
        degree[c.frm] += 1
        degree[c.to] += 1

    groups: list[NavGroup] = []
    for i, members in enumerate(sorted((sorted(m) for m in comps.values()))):
        # Representative = most-connected member; label from its statement (no model).
        rep = max(members, key=lambda m: (degree[m], -len(dmap[m].label), m))
        groups.append(NavGroup(id=f"grp_{i:02d}", label=dmap[rep].label, members=members))

    durable_dicts = [
        {"id": d.id, "kind": d.kind, "statement": d.label,
         "semantic_evidence": sorted(sem_ev[d.id]), "source_origins": sorted(src_ev[d.id])}
        for d in ordered
    ]

    entry_points = {
        "entity": sorted({n.label for n in semantic.values() if n.kind == "entity"}),
        "event": sorted({n.label for n in semantic.values() if n.kind == "event"}),
        "durable_kind": dict(sorted(Counter(d.kind for d in durables).items())),
    }

    return NavigationGraph(
        durables=durable_dicts,
        groups=groups,
        connections=sorted(connections, key=lambda c: (c.frm, c.to)),
        entry_points=entry_points,
    )
