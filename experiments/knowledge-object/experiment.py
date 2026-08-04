#!/usr/bin/env python3
"""Proposer-behind-verifier measurement.

    Part A  (deterministic, always runs): the verifier's DEFENSE against the adversarial gold set.
             Measures fabrication-acceptance, contradiction-detection, supported-retention,
             over-abstention — against known labels. No LLM needed.

    Part B  (needs an LLM client): the PROPOSER. The LLM freely proposes relations from evidence
             packets; we compare proposer-only vs proposer+verifier (how much narrative it invents,
             how much the verifier stops, and whether it proposes SUPPORTED claims not in the gold).

Corpus roles (frozen): deepseek = dev · pnp = dev sanity · kimi = HELD-OUT.

    python experiment.py                 # Part A only (deterministic result)
    python experiment.py --fake          # + Part B with a canned FakeClient (harness self-test)
    OPENAI_API_KEY=... python experiment.py --client openai --model gpt-...   # the real paid run
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))

from claim_verifier import Claim, verify  # noqa: E402
from gold import by_corpus  # noqa: E402
from grounding import CONTRADICTED, SUPPORTED, UNKNOWN, Passage  # noqa: E402
from proposer import propose  # noqa: E402

CORPORA = ("deepseek", "pnp", "kimi")


# ---------- passage loading ----------

def _md_passages(case_dir: Path, prefix: str) -> list[Passage]:
    out: list[Passage] = []
    for md in sorted(case_dir.glob("*.md")):
        if md.name in ("SOURCES.md", "CORPUS.md"):
            continue
        for i, b in enumerate(x.strip() for x in md.read_text(encoding="utf-8").split("\n\n")):
            if b:
                out.append(Passage(f"{prefix}/{md.stem}#p{i}", b))
    return out


def _pnp_passages() -> list[Passage]:
    """Elizabeth's extracted timeline observations, chapter-anchored (the semantic-evidence layer)."""
    p = json.loads((REPO / "site/data/pride-and-prejudice/people/elizabeth-bennet.json")
                   .read_text(encoding="utf-8"))
    out = []
    for i, s in enumerate(p.get("timeline", [])):
        txt = (s.get("text", "") or "")
        if txt:
            out.append(Passage(f"pnp/eliz#c{s.get('chapter')}_{i}", txt, anchor=f"ch{s.get('chapter')}"))
    return out


def load_passages(corpus: str) -> list[Passage]:
    if corpus == "deepseek":
        return _md_passages(REPO / "explorer/cases/deepseek", "deepseek")
    if corpus == "kimi":
        return _md_passages(REPO / "explorer/cases/kimi", "kimi")
    if corpus == "pnp":
        return _pnp_passages()
    raise ValueError(corpus)


# ---------- Part A: verifier defense on the adversarial gold set ----------

def part_a(log: dict) -> bool:
    print("=== Part A — verifier defense against the adversarial gold set ===\n")
    passages = {c: load_passages(c) for c in CORPORA}
    totals = {"fab_accept_den": 0, "fab_accept_num": 0, "sup_den": 0, "sup_keep": 0,
              "sup_overabstain": 0, "contra_den": 0, "contra_hit": 0, "contra_as_sup": 0}
    for corpus in CORPORA:
        print(f"-- {corpus} --")
        for cat, expected, claim in by_corpus(corpus):
            v = verify(claim, passages[corpus])
            ok = v.status == expected
            # metrics
            if expected in (UNKNOWN, CONTRADICTED):
                totals["fab_accept_den"] += 1
                if v.status == SUPPORTED:
                    totals["fab_accept_num"] += 1
            if expected == SUPPORTED:
                totals["sup_den"] += 1
                totals["sup_keep"] += v.status == SUPPORTED
                totals["sup_overabstain"] += v.status == UNKNOWN
            if expected == CONTRADICTED:
                totals["contra_den"] += 1
                totals["contra_hit"] += v.status == CONTRADICTED
                totals["contra_as_sup"] += v.status == SUPPORTED
            flag = "✓" if ok else ("‼FAB" if (expected != SUPPORTED and v.status == SUPPORTED) else "·miss")
            print(f"   [{cat:21}] want {expected:11} got {v.status:11} {flag}  {claim.subject} "
                  f"--{claim.predicate}--> {claim.object}")
            log["gold"].append({"corpus": corpus, "category": cat, "expected": expected,
                                "status": v.status, "subject": claim.subject,
                                "predicate": claim.predicate, "object": claim.object,
                                "evidence": v.evidence, "reason": v.reason})
        print()

    fa = totals["fab_accept_num"]
    ret = totals["sup_keep"] / totals["sup_den"] if totals["sup_den"] else 0
    print("── metrics ──")
    print(f"  fabrication acceptance (unsupported/contradicted accepted as SUPPORTED): "
          f"{fa}/{totals['fab_accept_den']}   [GATE: must be 0]")
    print(f"  supported retention:   {totals['sup_keep']}/{totals['sup_den']} ({ret:.0%})   "
          f"[must not win by abstaining all]")
    print(f"  over-abstention:       {totals['sup_overabstain']}/{totals['sup_den']}")
    print(f"  contradiction detected:{totals['contra_hit']}/{totals['contra_den']}   "
          f"(contradicted-as-SUPPORTED: {totals['contra_as_sup']})")
    log["metrics_part_a"] = {**totals, "fabrication_acceptance": fa, "supported_retention": ret}
    gate = fa == 0 and totals["contra_as_sup"] == 0 and ret >= 0.5
    print(f"\n  Part-A gate (fabrication acceptance 0, retention ≥ 50%): {'PASS' if gate else 'FAIL'}")
    return gate


# ---------- Part B: the LLM proposer ----------

def _norm_predicate(pred: str) -> str:
    p = pred.lower()
    if any(w in p for w in ("improve", "build", "deriv", "evolv", "succeed", "replac", "base on")):
        return "derives_from"
    if "refus" in p or "reject" in p or "declin" in p:
        return "refuses"
    if "accept" in p or "agree" in p:
        return "accepts"
    if "marri" in p or "wed" in p:
        return "married"
    if "introduc" in p or "add" in p or "first" in p:
        return "introduces"
    return p.replace(" ", "_")


def part_b(client, model_id: str, log: dict) -> None:
    print("\n=== Part B — proposer (LLM) vs proposer+verifier ===\n")
    log["model"] = model_id
    for corpus in CORPORA:
        passages = load_passages(corpus)
        proposals = propose(client, passages)
        graded = []
        for pr in proposals:
            claim = Claim(pr.subject, _norm_predicate(pr.predicate), pr.object, pr.scope,
                          (pr.subject,), (pr.object,))
            v = verify(claim, passages)
            graded.append((pr, v.status, v.evidence))
        supported = [g for g in graded if g[1] == SUPPORTED]
        not_supported = [g for g in graded if g[1] != SUPPORTED]
        print(f"-- {corpus} ({'HELD-OUT' if corpus == 'kimi' else 'dev'}) --")
        print(f"   proposer-only:     {len(proposals)} claims proposed")
        print(f"   proposer+verifier: {len(supported)} committed (SUPPORTED), "
              f"{len(not_supported)} withheld (UNKNOWN/CONTRADICTED)")
        print(f"   → verifier withheld {len(not_supported)}/{len(proposals)} of the proposer's claims")
        for pr, st, ev in graded:
            log["proposals"].append({"corpus": corpus, "subject": pr.subject,
                                     "predicate": pr.predicate, "object": pr.object,
                                     "status": st, "evidence": ev, "rationale": pr.rationale})
        print()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fake", action="store_true", help="run Part B with a canned FakeClient (self-test)")
    ap.add_argument("--client", choices=["openai", "anthropic"], help="run Part B with a real LLM")
    ap.add_argument("--model", default=None)
    ap.add_argument("--label", default="run", help="log file label (keep deterministic, no timestamp)")
    args = ap.parse_args()

    log: dict = {"label": args.label, "gold": [], "proposals": [], "model": None}
    gate = part_a(log)

    if args.fake:
        from fake_proposals import make_fake_client
        part_b(make_fake_client(), "fake:canned", log)
    elif args.client:
        if args.client == "openai":
            from lyr.llm.openai import OpenAIClient as C
        else:
            from lyr.llm.anthropic import AnthropicClient as C
        client = C(model=args.model) if args.model else C()
        part_b(client, f"{args.client}:{args.model or 'default'}", log)

    out = HERE / "runs" / f"{args.label}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nlogged → {out.relative_to(REPO)}")
    sys.exit(0 if gate else 1)


if __name__ == "__main__":
    main()
