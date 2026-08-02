#!/usr/bin/env python3
"""M3.1-E evaluation kit — preserve JudgmentRecords, review them, summarize.

This tool does **not** touch the Builder or the prompt (the M3.1-E frozen-builder
rule). It only collects the evidence the experiment produces and helps classify
it:

    review    <experiment>   preserve a run's JudgmentRecord as committed evidence
                             and write a blank review skeleton to fill in by hand
    summarize                tally failures (F1-F8) across all reviews, and verify
                             every preserved record shares one prompt/provider/model
                             (a mid-experiment change would destroy comparability)

Records and reviews live under experiments/evaluation/ and ARE committed — unlike
the scratch runs/ transcripts — because M3.1-E requires every JudgmentRecord to be
preserved as experimental evidence.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
RECORDS = HERE / "records"
REVIEWS = HERE / "reviews"
BENCHMARK = HERE / "benchmark"

# The evaluation vocabulary (design §7, §8) — kept here so a review is self-describing.
DIMENSIONS = [
    "groundedness",
    "durability",
    "scope",
    "evidence_independence",
    "candidate_coverage",
    "operation_correctness",
    "audit_quality",
]
FAILURES = {
    "F1": "Unsupported Abstraction — claim exceeds available evidence",
    "F2": "Over-Generalization — statement broader than justified",
    "F3": "Under-Abstraction — repeats observations, no durable knowledge",
    "F4": "Incorrect Durability Judgment — kept transient / dropped durable",
    "F5": "Evidence Independence Failure — same event counted as many",
    "F6": "Incorrect Operation — wrong ADD/UPDATE/MERGE/NO_OP",
    "F7": "Candidate Coverage Failure — one judgment can't represent the input",
    "F8": "Audit Failure — record doesn't explain the decision",
}


# ── review ---------------------------------------------------------------
def _newest_record(experiment: str) -> Path | None:
    runs = EXPERIMENTS / experiment / "runs"
    hits = sorted(glob.glob(str(runs / "*judgment*.json")))
    return Path(hits[-1]) if hits else None


def _semantic_labels(experiment: str) -> dict[str, str]:
    """Map semantic node id -> label for the fixture (for human-readable review)."""
    sys.path.insert(0, str(EXPERIMENTS))
    try:
        from harness import load_records, to_semantic_nodes  # type: ignore
    except Exception:
        return {}
    exp_dir = EXPERIMENTS / experiment
    if not (exp_dir / "semantic_nodes.json").exists():
        return {}
    nodes = to_semantic_nodes(load_records(exp_dir))
    return {n.id: n.label for n in nodes}


def cmd_review(args: argparse.Namespace) -> None:
    record_path = Path(args.record) if args.record else _newest_record(args.experiment)
    if record_path is None or not record_path.exists():
        raise SystemExit(
            f"no JudgmentRecord found for {args.experiment}. Run the builder first:\n"
            f"  python experiments/harness.py {args.experiment} --builder --model claude-opus-4-8"
        )
    record = json.loads(record_path.read_text())

    # Guard: never preserve a canned/offline run as experimental evidence. If the
    # newest run in runs/ is a FakeClient record, the live model call almost
    # certainly failed (e.g. an API/billing error) and this is a stale leftover.
    provider = record.get("model_config", {}).get("provider")
    if provider == "FakeClient" and not args.allow_canned:
        raise SystemExit(
            f"refusing to preserve a canned (FakeClient) record as evidence:\n"
            f"  {record_path}\n"
            "The newest run in this experiment's runs/ is a --canned/offline run, so a\n"
            "live model call likely failed. Fix the live run and re-collect, or pass\n"
            "--allow-canned only if you are deliberately testing the kit."
        )

    jid = record["judgment_id"]
    labels = _semantic_labels(args.experiment)

    RECORDS.mkdir(exist_ok=True)
    REVIEWS.mkdir(exist_ok=True)
    stem = f"{args.experiment}__{jid}"

    # Preserve the record verbatim as committed evidence.
    (RECORDS / f"{stem}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False))

    review_path = REVIEWS / f"{stem}.json"
    if review_path.exists() and not args.force:
        raise SystemExit(f"review already exists: {review_path} (use --force to overwrite)")

    intent = record["model_intent"]
    action = record["final_engine_action"]
    review = {
        "experiment": args.experiment,
        "judgment_id": jid,
        "judgment_fingerprint": record.get("judgment_fingerprint"),
        "prompt_version": record.get("model_config", {}).get("prompt_version"),
        "model": record.get("model_config", {}).get("model"),
        # ↓ human-readable context (do not edit — regenerated from the record)
        "_context": {
            "model_operation": intent["operation"],
            "engine_operation": action["operation"],
            "statement": intent["statement"],
            "kind": intent["kind"],
            "confidence": intent["confidence"],
            "counter_evidence": intent.get("counter_evidence", ""),
            "evidence": [labels.get(e, e) for e in intent["evidence"]],
            "evidence_groups": [
                {"same_observation": g["same_observation"],
                 "records": [labels.get(sid, sid) for sid in g.get("semantic_ids", [])],
                 "note": g.get("note", "")}
                for g in record.get("evidence_groups", [])
            ],
        },
        # ↓ fill these in by hand (design §7 / §8)
        "dimensions": {d: {"rating": "", "note": ""} for d in DIMENSIONS},
        "failures": [],  # any of F1..F8
        "reviewer": "",
        "verdict": "",
    }
    review_path.write_text(json.dumps(review, indent=2, ensure_ascii=False))
    print(f"preserved record → {(RECORDS / f'{stem}.json').relative_to(EXPERIMENTS.parent)}")
    print(f"review skeleton  → {review_path.relative_to(EXPERIMENTS.parent)}")
    print("Fill in dimensions (rating: ok|weak|fail) and failures (F1..F8), then run: "
          "evaluate.py summarize")


# ── preserve (decomposed run → durability benchmark) ---------------------
def _newest_decomposed_run(experiment: str) -> list[str]:
    """Unit record files of the newest decomposed run (…__unitNN.json), in order."""
    files = glob.glob(str(EXPERIMENTS / experiment / "runs" / "*__unit*.json"))
    by_stamp: dict[str, list[str]] = {}
    for f in files:
        stamp = os.path.basename(f).split("__", 1)[0]
        by_stamp.setdefault(stamp, []).append(f)
    if not by_stamp:
        return []
    return sorted(by_stamp[max(by_stamp)])


def cmd_preserve(args: argparse.Namespace) -> None:
    """Preserve a decomposed run's records as durability-benchmark cases.

    Each proposed durable memory (one JudgmentRecord per topic unit) becomes a
    benchmark case with a durability label a Verifier can later be scored against.
    """
    unit_files = _newest_decomposed_run(args.experiment)
    if not unit_files:
        raise SystemExit(
            f"no decomposed run (…__unitNN.json) in {args.experiment}/runs.\n"
            f"  python experiments/harness.py {args.experiment} --builder "
            f"--provider openai --model gpt-4o --decompose llm"
        )

    bench = BENCHMARK / args.benchmark
    recdir = bench / "records"
    recdir.mkdir(parents=True, exist_ok=True)
    labels_path = bench / "labels.json"
    doc = json.loads(labels_path.read_text()) if labels_path.exists() else {"benchmark": args.benchmark, "cases": []}
    cases = doc["cases"]
    seen = {c["judgment_id"] for c in cases}

    preserved = 0
    for f in unit_files:
        rec = json.loads(Path(f).read_text())
        if rec.get("model_config", {}).get("provider") == "FakeClient" and not args.allow_canned:
            raise SystemExit(f"refusing to preserve a canned (FakeClient) record: {f}")
        jid = rec["judgment_id"]
        (recdir / f"{args.experiment}__{jid}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
        preserved += 1
        if jid not in seen:
            intent = rec["model_intent"]
            cases.append({
                "judgment_id": jid,
                "domain": args.experiment,
                "operation": rec["final_engine_action"]["operation"],
                "statement": intent["statement"],
                "kind": intent["kind"],
                "deserves_persistence": "",   # yes | no | borderline  (fill in)
                "note": "",
            })
            seen.add(jid)
    labels_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False))
    print(f"{args.experiment}: preserved {preserved} record(s) → {recdir.relative_to(EXPERIMENTS.parent)}")


# ── summarize ------------------------------------------------------------
def cmd_summarize(args: argparse.Namespace) -> None:
    reviews = [json.loads(Path(p).read_text()) for p in sorted(glob.glob(str(REVIEWS / "*.json")))]
    records = [json.loads(Path(p).read_text()) for p in sorted(glob.glob(str(RECORDS / "*.json")))]

    if not reviews:
        print("no reviews yet. Collect runs, then: evaluate.py review <experiment>")
        return

    # §4 integrity guard: the frozen-builder rule.
    configs = {
        (r.get("model_config", {}).get("prompt_version"),
         r.get("model_config", {}).get("provider"),
         r.get("model_config", {}).get("model"))
        for r in records
    }
    print(f"=== M3.1-E summary — {len(reviews)} review(s), {len(records)} preserved record(s) ===\n")
    if len(configs) > 1:
        print("⚠️  FROZEN-BUILDER RULE VIOLATED: preserved records span multiple "
              "prompt/provider/model configs — comparability is compromised:")
        for c in sorted(configs):
            print(f"      prompt_version={c[0]} provider={c[1]} model={c[2]}")
        print()
    elif configs:
        c = next(iter(configs))
        print(f"builder config (uniform ✓): prompt_version={c[0]} provider={c[1]} model={c[2]}\n")

    # Per-domain + overall failure tally.
    by_domain: dict[str, list[str]] = {}
    failure_counts: dict[str, int] = {k: 0 for k in FAILURES}
    unreviewed = 0
    for rv in reviews:
        exp = rv.get("experiment", "?")
        fs = rv.get("failures") or []
        by_domain.setdefault(exp, []).extend(fs)
        if not any(d.get("rating") for d in rv.get("dimensions", {}).values()):
            unreviewed += 1
        for f in fs:
            if f in failure_counts:
                failure_counts[f] += 1

    print("failures by domain:")
    for exp in sorted(by_domain):
        fs = by_domain[exp]
        print(f"  {exp}: {', '.join(sorted(fs)) if fs else '(none)'}")
    print("\nfailure totals:")
    for code, n in sorted(failure_counts.items()):
        if n:
            print(f"  {code} ×{n}  — {FAILURES[code]}")
    if not any(failure_counts.values()):
        print("  (none recorded)")
    if unreviewed:
        print(f"\nnote: {unreviewed} review(s) have no dimension ratings filled in yet.")

    # Decision INPUT only — the outcome is a human call over the complete set (§9).
    print("\n--- decision inputs (design §9; the call is human, over the full set) ---")
    print("  Outcome A → proceed to M3.1-C   (failures mostly judgment-quality: F1/F2/F3/F6)")
    print("  Outcome B → M3.1-B.2 first       (F7 dominant: one judgment can't represent input)")
    print("  Outcome C → revisit durability   (F4 dominant across domains: theory inconsistent)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("review", help="preserve a run's record + write a review skeleton")
    r.add_argument("experiment", help="experiment dir name under experiments/")
    r.add_argument("--record", help="specific JudgmentRecord json (default: newest in runs/)")
    r.add_argument("--force", action="store_true", help="overwrite an existing review")
    r.add_argument("--allow-canned", action="store_true",
                   help="permit preserving a FakeClient/offline record (kit testing only)")
    r.set_defaults(func=cmd_review)

    p = sub.add_parser("preserve", help="preserve a decomposed run as durability-benchmark cases")
    p.add_argument("experiment", help="experiment dir name under experiments/")
    p.add_argument("--benchmark", default="durability-v1", help="benchmark name (default: durability-v1)")
    p.add_argument("--allow-canned", action="store_true", help="permit FakeClient records (testing only)")
    p.set_defaults(func=cmd_preserve)

    s = sub.add_parser("summarize", help="tally failures + check builder-config uniformity")
    s.set_defaults(func=cmd_summarize)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
