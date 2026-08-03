#!/usr/bin/env python3
"""Run one case through the whole harness — same pipeline for every domain.

    ingest → semantic extraction → durable → entity resolution → canonical view
    → site data package → quality report → register in the Explorer's case list

    # baseline (no key, crude but real):
    python explorer/pipeline/run_case.py --case explorer/cases/pride-and-prejudice.json
    # a real case (your key), first 20 units:
    OPENAI_API_KEY=... python explorer/pipeline/run_case.py \
        --case explorer/cases/hong-lou-meng.json --extractor llm --provider openai --limit 20

One manifest per case; no per-title code. The same Explorer UI reads every case
from site/data/cases.json.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def run(script: str, *a) -> None:
    cmd = [sys.executable, str(HERE / script), *map(str, a)]
    print("▶ " + " ".join(cmd[2:]))
    if subprocess.run(cmd).returncode != 0:
        raise SystemExit(f"{script} failed")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True, help="path to a case manifest JSON")
    ap.add_argument("--extractor", choices=["rule", "llm"], default="rule")
    ap.add_argument("--provider", choices=["anthropic", "openai"], default="openai")
    ap.add_argument("--model", default=None)
    ap.add_argument("--consolidator", choices=["recurrence", "llm"], default="recurrence")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--data-dir", default=str(REPO / "explorer/data"))
    ap.add_argument("--site-dir", default=str(REPO / "site/data"))
    args = ap.parse_args()

    m = json.loads(Path(args.case).read_text(encoding="utf-8"))
    cid, title = m["case_id"], m["title"]
    data, site = Path(args.data_dir), Path(args.site_dir)
    knowledge = data / f"{cid}.knowledge.json"
    canonical = data / f"{cid}.canonical.json"
    casedir = site / cid

    print(f"=== case: {cid} ({title}) · {m.get('language')} · {m.get('source_type')} ===\n")

    ek = ["--manifest", args.case, "--extractor", args.extractor, "--out", str(knowledge)]
    if args.extractor == "llm":
        ek += ["--provider", args.provider, "--consolidator", args.consolidator]
    if args.model:
        ek += ["--model", args.model]
    if args.limit:
        ek += ["--limit", str(args.limit)]
    run("export_knowledge.py", *ek)
    run("canonicalize.py", "--in", knowledge, "--out", canonical)
    run("build_site_data.py", "--in", canonical, "--case-id", cid, "--title", title, "--out", casedir)
    run("quality_report.py", "--in", knowledge, "--out", casedir / "quality.json")

    # register the case for the Explorer's source selector
    cases_path = site / "cases.json"
    cases = json.loads(cases_path.read_text(encoding="utf-8")) if cases_path.exists() else []
    cases = [c for c in cases if c.get("case_id") != cid]
    cases.append({"case_id": cid, "title": title, "language": m.get("language", "en"),
                  "source_type": m.get("source_type", "book"), "dir": cid, "public": m.get("public", True)})
    cases.sort(key=lambda c: c["case_id"])
    cases_path.write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✓ case '{cid}' complete → site/data/{cid}/ (+ quality.json), registered in cases.json")


if __name__ == "__main__":
    main()
