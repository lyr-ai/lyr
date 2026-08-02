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
from collections import Counter
from datetime import datetime, timezone
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


# ── score-verifier (M3.1-C.1) --------------------------------------------
#
# Frozen BEFORE the live run so the scoring rules cannot be tuned to the output.
# Runs a durability verifier over the FIXED benchmark proposals (not a fresh
# builder run — that would fold builder/decomposer noise into the verifier's
# score) and compares each verdict to the human label.
#
#   scored cases      = benchmark cases whose builder op was a write (ADD/UPDATE/
#                       MERGE) — the ones a verifier actually judges.
#   NO_OP cases        = builder true-negatives (rent, version bumps): reported as
#                       context, NOT part of the verifier metric.
#   false positive     = verdict KEEP on a label 'no'
#   false negative     = verdict REJECT on a label 'yes'
#   strict score       = confirmed yes/no labels only
#   provisional score  = strict + unconfirmed 'no' (e.g. cloud-growth)
#   borderline/debatable and execution-ERROR cases: reported separately, never
#                       folded into FP/FN.
def _semantic_map(domain: str) -> dict:
    sys.path.insert(0, str(EXPERIMENTS))
    from harness import load_records, to_semantic_nodes  # type: ignore
    return {n.id: n for n in to_semantic_nodes(load_records(EXPERIMENTS / domain))}


def _proposal_from_record(rec: dict):
    from lyr.durable.judgment import ModelProposal
    mi = rec["model_intent"]
    return ModelProposal(
        operation=mi["operation"], statement=mi["statement"], kind=mi["kind"],
        evidence=tuple(mi.get("evidence", [])), confidence=mi.get("confidence"),
        rationale=mi.get("rationale", ""), counter_evidence=mi.get("counter_evidence", ""),
    )


def _build_scoring_verifier(args) -> tuple[object, str, str]:
    from lyr.durable import LLMDurabilityVerifier, ThresholdDurabilityVerifier
    from lyr.durable.verifier import VERIFIER_PROMPT_VERSION
    if args.control:
        return ThresholdDurabilityVerifier(args.threshold), f"control:threshold-{args.threshold}", "n/a"
    if args.provider == "openai":
        from lyr.llm import OpenAIClient
        client = OpenAIClient(model=args.model)
    else:
        from lyr.llm import AnthropicClient
        client = AnthropicClient(model=args.model)
    return LLMDurabilityVerifier(client), f"{args.provider}:{args.model}", VERIFIER_PROMPT_VERSION


def cmd_score_verifier(args: argparse.Namespace) -> None:
    from lyr.durable.judgment import ERROR, SUCCESS

    bench = BENCHMARK / args.benchmark
    doc = json.loads((bench / "labels.json").read_text())
    verifier, vname, pver = _build_scoring_verifier(args)
    sem_maps: dict[str, dict] = {}

    rows: list[dict] = []
    for case in doc["cases"]:
        jid, domain = case["judgment_id"], case["domain"]
        rec = json.loads((bench / "records" / f"{domain}__{jid}.json").read_text())
        row = {
            "domain": domain, "statement": case["statement"],
            "label": case["deserves_persistence"], "confirmed": case.get("confirmed", True),
            "builder_op": rec["model_intent"]["operation"],
        }
        if rec["model_intent"]["operation"] == "NO_OP":
            row.update(scored=False, note="builder-rejected (not verifier-scored)")
            rows.append(row)
            continue
        sem_maps.setdefault(domain, _semantic_map(domain))
        proposal = _proposal_from_record(rec)
        evidence = [sem_maps[domain][i] for i in proposal.evidence if i in sem_maps[domain]]
        v = verifier.verify(proposal, evidence)
        row.update(scored=True, status=v.status,
                   verdict=(v.decision if v.status == SUCCESS else None),
                   error_reason=v.error_reason)
        rows.append(row)

    judged = [r for r in rows if r["scored"]]
    ok = [r for r in judged if r["status"] == SUCCESS]
    errors = [r for r in judged if r["status"] == ERROR]
    counts = Counter(r["verdict"] for r in ok)

    def fp(rs): return [r for r in rs if r["label"] == "no" and r["verdict"] == "KEEP"]
    def fn(rs): return [r for r in rs if r["label"] == "yes" and r["verdict"] == "REJECT"]
    strict = [r for r in ok if r["label"] in ("yes", "no") and r["confirmed"]]
    prov = [r for r in ok if r["label"] in ("yes", "no")]
    borderline = [r for r in judged if r["label"] == "borderline" or not r["confirmed"]]
    noop = [r for r in rows if not r["scored"]]

    report = {
        "benchmark": args.benchmark,
        "verifier": vname,
        "verifier_prompt_version": pver,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "verdict_counts": {k: counts.get(k, 0) for k in ("KEEP", "REJECT", "UNSURE")},
        "execution_errors": len(errors),
        "strict": {"n": len(strict), "false_positives": len(fp(strict)), "false_negatives": len(fn(strict))},
        "provisional": {"n": len(prov), "false_positives": len(fp(prov)), "false_negatives": len(fn(prov))},
        "borderline_excluded": [r["statement"] for r in borderline],
        "builder_true_negatives_not_scored": [r["statement"] or "(NO_OP)" for r in noop],
        "detail": rows,
    }
    scores = bench / "scores"
    scores.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe = vname.replace(":", "_").replace("/", "_")
    (scores / f"{stamp}__{safe}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))

    print(f"=== durability verifier score — {vname} on {args.benchmark} ===")
    print(f"verdicts: KEEP={report['verdict_counts']['KEEP']} "
          f"REJECT={report['verdict_counts']['REJECT']} UNSURE={report['verdict_counts']['UNSURE']} "
          f"| execution errors: {len(errors)}")
    for name in ("strict", "provisional"):
        s = report[name]
        print(f"{name:11}: n={s['n']}  false_positives={s['false_positives']}  false_negatives={s['false_negatives']}")
    print(f"borderline/debatable (excluded): {len(borderline)}  |  builder true-negatives: {len(noop)}")
    print("\nfalse positives (KEEP on a 'no'):")
    for r in fp(prov):
        conf = "" if r["confirmed"] else "  [provisional]"
        print(f"  KEEP  {r['statement'][:60]}{conf}")
    for r in fn(strict):
        print(f"  FN REJECT  {r['statement'][:60]}")
    if errors:
        print("execution errors:")
        for r in errors:
            print(f"  {r['statement'][:50]} — {r['error_reason']}")
    print(f"\nwrote {(scores / f'{stamp}__{safe}.json').relative_to(EXPERIMENTS.parent)}")


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

    v = sub.add_parser("score-verifier", help="score a durability verifier against a benchmark (M3.1-C.1)")
    v.add_argument("--benchmark", default="durability-v1")
    v.add_argument("--provider", choices=["openai", "anthropic"], default="openai")
    v.add_argument("--model", default="gpt-4o")
    v.add_argument("--control", action="store_true", help="use the deterministic threshold control (offline)")
    v.add_argument("--threshold", type=float, default=0.5, help="control threshold on builder confidence")
    v.set_defaults(func=cmd_score_verifier)

    s = sub.add_parser("summarize", help="tally failures + check builder-config uniformity")
    s.set_defaults(func=cmd_summarize)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
