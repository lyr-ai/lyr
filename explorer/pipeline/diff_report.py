#!/usr/bin/env python3
"""Attributed diff across quality reports — isolate ingestion vs extractor effects.

Give it labelled quality.json files; it prints a side-by-side table so each change
is attributable to one variable at a time:

    coarse → fine   : the INGESTION effect (extractor held constant)
    rule-fine → llm-fine : the EXTRACTOR effect (ingestion held constant)

    python explorer/pipeline/diff_report.py \
        coarse=explorer/baselines/hong-lou-meng-rule-coarse.quality.json \
        fine=explorer/baselines/hong-lou-meng-rule-fine.quality.json \
        llm=site/data/hong-lou-meng/quality.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROWS = [
    ("sources", lambda q: q["sources"]),
    ("entities_extracted", lambda q: q["entities_extracted"]),
    ("canonical_entities", lambda q: q["canonical_entities"]),
    ("duplicate_ratio", lambda q: q["duplicate_ratio"]),
    ("merges", lambda q: q["resolver"]["merges"]),
    ("unsure", lambda q: q["resolver"]["unsure"]),
    ("rejects", lambda q: q["resolver"]["rejects"]),
    ("relationships", lambda q: q["relationships"]),
    ("events", lambda q: q["events"]),
    ("evidence_coverage_%", lambda q: q["evidence_coverage_pct"]),
    ("orphan_entities", lambda q: q["orphan_entities"]["count"]),
]


def main() -> None:
    cols = []  # (label, quality dict)
    for arg in sys.argv[1:]:
        if "=" not in arg:
            continue
        label, path = arg.split("=", 1)
        p = Path(path)
        if not p.exists():
            print(f"(skip {label}: {path} not found)")
            continue
        cols.append((label, json.loads(p.read_text(encoding="utf-8"))))
    if not cols:
        raise SystemExit("give labelled quality.json paths, e.g. coarse=... fine=... llm=...")

    w = 20
    header = "metric".ljust(24) + "".join(l.rjust(w) for l, _ in cols)
    print(header)
    print("-" * len(header))
    for name, fn in ROWS:
        line = name.ljust(24)
        for _, q in cols:
            try:
                line += str(fn(q)).rjust(w)
            except Exception:
                line += "—".rjust(w)
        print(line)

    labels = [l for l, _ in cols]
    print("\nattribution:")
    if "coarse" in labels and "fine" in labels:
        print("  coarse → fine        = INGESTION effect (extractor constant)")
    if "fine" in labels and "llm" in labels:
        print("  fine  → llm          = EXTRACTOR effect (ingestion constant)")
    print("\nwatch (per the plan): raw-entity explosion · duplicate ratio · merges vs unsure ·"
          " orphan entities · evidence coverage. A big raw-entity jump with a low merge ratio and"
          " many unsure aliases = the resolver's generic limit (e.g. zh aliases) — a witness, not a fix.")


if __name__ == "__main__":
    main()
