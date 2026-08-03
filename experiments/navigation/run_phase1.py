#!/usr/bin/env python3
"""M3.2-A Phase 1 — genericity sanity check for form_navigation.

Runs the SAME form_navigation(nodes) over the four M3.1 domains (memoir, meeting,
financial, git), reconstructing each domain's nodes from real data:
  - semantic nodes  ← the experiment fixtures
  - durable nodes   ← the committed (engine ADD) JudgmentRecords in site/records/

It passes NO domain argument to form_navigation. Success = one code path, identical
output schema, provenance intact, honest singletons — implementation genericity only.
It does NOT claim the navigation is useful (that is Phase 2). Prints per-domain metrics
+ the pre-registered outcome (A/B/C), and writes each graph to graphs/.

    python experiments/navigation/run_phase1.py
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "experiments"))

from harness import load_records, to_semantic_nodes  # noqa: E402
from lyr.ids import content_id  # noqa: E402
from lyr.models import Node  # noqa: E402
from lyr.navigation import form_navigation  # noqa: E402

DOMAINS = ["experiment-001-memoir", "experiment-002-meeting",
           "experiment-003-financial-report", "experiment-004-git-history"]


def _durable_nodes(domain: str) -> list[Node]:
    """Committed durable memories (engine ADD) reconstructed from site/records/."""
    out = []
    for f in sorted(glob.glob(str(REPO / "site" / "records" / f"{domain}__*.json"))):
        rec = json.loads(Path(f).read_text())
        ea, mi = rec["final_engine_action"], rec["model_intent"]
        if ea["operation"] != "ADD":
            continue  # only committed durables live in the durable layer
        out.append(Node(layer="durable", kind=mi["kind"], label=mi["statement"],
                        identity=ea["identity"], evidence=list(mi["evidence"])))
    return out


def _source_key_map(domain: str) -> dict:
    """src content-id → human source key, for readable connection support."""
    raw = load_records(REPO / "experiments" / domain)
    return {content_id("src", r.get("source", "")): r.get("source", "") for r in raw}


def _outcome(g) -> str:
    if g.n_durables == 0:
        return "—"
    if g.compression == 1.0:
        return "B (all singletons — provenance connectivity insufficient)"
    if g.largest_group >= max(2, 0.6 * g.n_durables):
        return "C (giant component — source overlap too coarse)"
    return "A (some coherent grouping)"


def main() -> None:
    (HERE / "graphs").mkdir(exist_ok=True)
    schemas = set()
    print("=== M3.2-A Phase 1 — genericity sanity check (form_navigation, no domain arg) ===\n")
    for domain in DOMAINS:
        semantic = to_semantic_nodes(load_records(REPO / "experiments" / domain))
        durables = _durable_nodes(domain)
        graph = form_navigation(semantic + durables)   # ← identical call, every domain
        keymap = _source_key_map(domain)

        d = graph.to_dict()
        schemas.add(tuple(sorted(d.keys())))
        (HERE / "graphs" / f"{domain}.json").write_text(json.dumps(d, indent=2, ensure_ascii=False))

        name = domain.split("-", 2)[-1]
        print(f"[{name}]  durables={graph.n_durables}  groups={graph.n_groups}  "
              f"compression={graph.compression}  singletons={graph.singletons}  "
              f"largest={graph.largest_group}")
        print(f"    outcome: {_outcome(graph)}")
        for g in graph.groups:
            tag = "singleton" if len(g.members) == 1 else f"{len(g.members)} members"
            print(f"      · [{tag}] {g.label[:64]}")
        for c in graph.connections:
            sup = ", ".join(keymap.get(s, s) for s in c.support)
            print(f"        ↔ {c.relation}: {sup}")
        print()

    print("=== genericity check ===")
    print(f"one code path, no domain argument: form_navigation(nodes)  ✓")
    print(f"identical output schema across all {len(DOMAINS)} domains: "
          f"{'✓' if len(schemas) == 1 else '✗ ' + str(schemas)}")
    print(f"graphs written to {(HERE / 'graphs').relative_to(REPO)}/")


if __name__ == "__main__":
    main()
