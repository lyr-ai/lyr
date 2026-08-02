#!/usr/bin/env python3
"""Build the Judgment Explorer's data bundle (M5.0).

Reads the preserved full-lifecycle JudgmentRecords in ``explorer/records/`` (real
records from the M3.1-C.1 verified run), resolves each record's cited evidence back to
its **semantic label and its original Source passage** (from the experiment
fixtures), attaches a human-readable title and the research finding it demonstrates,
and writes a single self-contained ``explorer/data.js`` (``window.LYR_RECORDS``) that
``index.html`` loads with no build step and no network.

    python explorer/build_data.py
"""
from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
EXPERIMENTS = REPO / "experiments"

DOMAIN_TITLES = {
    "experiment-001-memoir": "Memoir",
    "experiment-002-meeting": "Meeting notes",
    "experiment-003-financial-report": "Financial report",
    "experiment-004-git-history": "Git history",
}

# Human titles, matched by a distinctive word-boundary keyword in the builder
# statement (these are the fixed demo cases).
TITLES = [
    (r"\bfamily\b",           "Family over career"),
    (r"\b(letters|sister)\b", "Weekly letters to her sister"),
    (r"\bcoffee\b",           "Coffee ritual"),
    (r"\bfinancial\b",        "Lifelong financial-risk pattern"),
    (r"\bbilling\b",          "Sunset the billing API"),
    (r"\b(postgres|dynamodb)\b", "Postgres → DynamoDB reversal"),
    (r"\bflaky\b",            "Payments CI flakiness"),
    (r"\bsre\b",              "Second SRE hire"),
    (r"\bnorthwind\b",        "Northwind acquisition"),
    (r"\bdividend\b",         "12-year dividend streak"),
    (r"\bguidance\b",         "Guidance reversal"),
    (r"\bcloud\b",            "One-quarter cloud growth"),
    (r"\bimpairment\b",       "Goodwill impairment"),
    (r"\bgrpc\b",             "REST → gRPC migration"),
    (r"\bauth\b",             "Auth-fragility pattern"),
    (r"\bredis\b",            "Redis stale-read lesson"),
]

# The research finding a rejection demonstrates (KEEP is always a correct retention).
REJECT_FINDINGS = [
    (r"\bguidance\b", "False negative — a durable trend the verifier over-pruned"),
    (r"\bcoffee\b",   "False positive removed — trivia correctly rejected"),
    (r"\bcloud\b",    "False positive removed — a single-quarter metric, not durable"),
]


def _curate(statement: str, verdict: str) -> tuple[str, str]:
    s = (statement or "").lower()
    title = next((t for pat, t in TITLES if re.search(pat, s)), (statement[:40] or "(untitled)"))
    if verdict == "KEEP":
        finding = "Correct durable retained"
    elif verdict == "REJECT":
        finding = next((f for pat, f in REJECT_FINDINGS if re.search(pat, s)), "Rejected by the verifier")
    elif verdict == "UNSURE":
        finding = "Retained but flagged uncertain"
    else:
        finding = "Builder proposed nothing durable"
    return title, finding


def _source_passages(domain: str) -> dict:
    """Parse a fixture's input.md into {source_key: passage}. Best-effort per format."""
    f = EXPERIMENTS / domain / "input.md"
    if not f.exists():
        return {}
    text = f.read_text()
    out = {}
    # `**key.** passage …` up to the next bold marker (memoir / meeting / financial)
    for m in re.finditer(r"\*\*([\w\-./]+?)\.\*\*\s*(.*?)(?=\n\*\*|\n##|\Z)", text, re.DOTALL):
        out[m.group(1).strip()] = " ".join(m.group(2).split())
    # git commit log: `<hash>  <subject>`  (fixture keys are "commit-<hash>")
    if "git" in domain:
        for m in re.finditer(r"^([0-9a-f]{6}|merge\d+)\s{2,}(.+)$", text, re.M):
            out["commit-" + m.group(1)] = m.group(2).strip()
    return out


def _fixture_index(domain: str):
    """id -> {kind, label, source_key, passage} for a domain's semantic fixtures."""
    sys.path.insert(0, str(EXPERIMENTS))
    from harness import load_records, to_semantic_nodes  # type: ignore
    raw = load_records(EXPERIMENTS / domain)
    nodes = to_semantic_nodes(raw)
    passages = _source_passages(domain)
    idx = {}
    for rec, node in zip(raw, nodes):
        key = rec.get("source", "")
        idx[node.id] = {"kind": node.kind, "label": node.label,
                        "source_key": key, "passage": passages.get(key)}
    return idx


def _enrich(rec: dict, idx: dict, domain: str) -> dict:
    mi, ea = rec["model_intent"], rec["final_engine_action"]
    ver = rec.get("verification")
    if not ver:
        decision = "NONE"
    elif ver.get("status") == "ERROR":
        decision = "ERROR"
    else:
        decision = ver.get("decision") or "NONE"

    def ev(sid):
        return idx.get(sid, {"kind": "?", "label": sid, "source_key": "", "passage": None})

    evidence = [ev(s) for s in mi.get("evidence", [])]
    # dedupe source passages (several records can share one observation)
    sources, seen = [], set()
    for e in evidence:
        k = e["source_key"] or e["label"]
        if k not in seen:
            seen.add(k)
            sources.append({"key": e["source_key"], "passage": e["passage"], "label": e["label"]})
    title, finding = _curate(mi["statement"], decision)

    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return {
        "id": rec["judgment_id"], "domain": domain, "domain_title": DOMAIN_TITLES.get(domain, domain),
        "title": title, "slug": slug, "finding": finding, "verdict": decision,
        "sources": sources,
        "evidence": [{"kind": e["kind"], "label": e["label"]} for e in evidence],
        "evidence_groups": [
            {"same_observation": g.get("same_observation", False), "note": g.get("note", ""),
             "members": [ev(s)["label"] for s in g.get("semantic_ids", [])]}
            for g in rec.get("evidence_groups", [])
        ],
        "builder": {"operation": mi["operation"], "kind": mi["kind"], "statement": mi["statement"],
                    "rationale": mi.get("rationale", ""), "counter_evidence": mi.get("counter_evidence", ""),
                    "confidence": mi.get("confidence")},
        "verifier": None if not ver else {"decision": ver.get("decision"), "status": ver.get("status"),
                    "rationale": ver.get("rationale", ""), "confidence": ver.get("confidence"),
                    "error_reason": ver.get("error_reason")},
        "engine": {"operation": ea["operation"], "identity": ea.get("identity"),
                   "version": ea.get("version"), "rejection_reason": ea.get("rejection_reason")},
        "committed": ea.get("node_id") is not None,
        "model": rec.get("model_config", {}).get("model", "?"),
    }


def main() -> None:
    records, idxs = [], {}
    for path in sorted(glob.glob(str(HERE / "records" / "*.json"))):
        rec = json.loads(Path(path).read_text())
        # Skip builder-NO_OP units (empty statement/evidence — nothing to show).
        if rec["model_intent"]["operation"] == "NO_OP" or not rec["model_intent"].get("evidence"):
            continue
        domain = Path(path).stem.split("__", 1)[0]
        idxs.setdefault(domain, _fixture_index(domain))
        records.append(_enrich(rec, idxs[domain], domain))

    # reading order: kept first, then rejects, then builder-NO_OPs
    order = {"KEEP": 0, "UNSURE": 1, "REJECT": 2, "ERROR": 2, "NONE": 3}
    records.sort(key=lambda r: (order.get(r["verdict"], 3), r["domain"]))

    out = HERE / "data.js"
    out.write_text("// Generated by build_data.py — real JudgmentRecords from the M3.1-C.1 verified run.\n"
                   "window.LYR_RECORDS = " + json.dumps(records, indent=2, ensure_ascii=False) + ";\n")
    print(f"wrote {out.relative_to(REPO)} — {len(records)} judgments")


if __name__ == "__main__":
    main()
