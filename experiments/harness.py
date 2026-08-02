#!/usr/bin/env python3
"""Experiment harness: watch — and now *run* — durable-knowledge formation.

Two modes over the same fixtures:

    (prompt)   semantic records -> durability prompt -> LLM -> transcript
    (--builder) semantic records -> JudgmentBuilder.update() -> JudgmentRecord

The prompt mode is for reading how a model reasons; the builder mode drives the
real M3.1-B pipeline end to end and dumps the JudgmentRecord for inspection —
the "Run on real data -> Inspect JudgmentRecord" loop from the M3.1-B design.

Neither mode is a benchmark. See experiments/README.md.

Usage:
    # Prompt only (paste into claude.ai to watch reasoning):
    python experiments/harness.py experiment-001-memoir --dry-run

    # Run the builder live with Claude (needs a key + the anthropic extra):
    export ANTHROPIC_API_KEY=...
    python experiments/harness.py experiment-001-memoir --builder --model claude-opus-4-8

    # ...or with OpenAI / ChatGPT (needs a key + the openai extra):
    export OPENAI_API_KEY=...
    python experiments/harness.py experiment-001-memoir --builder --provider openai --model gpt-4o

    # Run the builder offline against a canned model response (for testing the loop):
    python experiments/harness.py experiment-001-memoir --builder --canned response.json
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_PROMPT = HERE / "prompts" / "durability_judgment_v1.md"


# ── fixture loading -------------------------------------------------------
def load_records(exp_dir: Path) -> list[dict]:
    f = exp_dir / "semantic_nodes.json"
    if not f.exists():
        raise SystemExit(f"no semantic_nodes.json in {exp_dir}")
    return json.loads(f.read_text())


def load_durable(exp_dir: Path) -> list[dict]:
    f = exp_dir / "existing_durable.json"
    return json.loads(f.read_text()) if f.exists() else []


def to_semantic_nodes(records: list[dict]):
    """Turn fixture dicts into real semantic ``Node``s for the builder.

    Identity comes from the label (relationships from their s/p/o), evidence from
    the ``source`` field — a stand-in for the Source Records a full ingest would
    produce, kept stable so provenance references resolve.
    """
    from lyr.ids import content_id, normalize
    from lyr.models import Node

    nodes = []
    for r in records:
        kind = r.get("kind", "entity")
        label = r.get("label", "")
        attrs = dict(r.get("attributes", {}))
        if kind == "relationship" and any(attrs.get(k) for k in ("subject", "predicate", "object")):
            identity = content_id("idn", kind, normalize(str(attrs.get("subject", ""))),
                                  normalize(str(attrs.get("predicate", ""))),
                                  normalize(str(attrs.get("object", ""))))
        else:
            identity = content_id("idn", kind, normalize(label))
        source = r.get("source", "")
        evidence = [content_id("src", source)] if source else []
        nodes.append(Node(layer="semantic", kind=kind, label=label, identity=identity,
                          evidence=evidence, attributes=attrs))
    return nodes


def to_durable_nodes(memories: list[dict]):
    from lyr.models import Node
    out = []
    for m in memories:
        out.append(Node(layer="durable", kind=m.get("kind", "lesson"),
                        label=m.get("statement", m.get("label", "")),
                        identity=m["identity"], evidence=list(m.get("evidence", []))))
    return out


# ── prompt rendering (prompt mode) ---------------------------------------
def render_records(records: list[dict]) -> str:
    lines = []
    for i, r in enumerate(records):
        src = r.get("source", "")
        suffix = f"   (source: {src})" if src else ""
        lines.append(f"[{i}] ({r.get('kind', '?')}) {r.get('label', '')}{suffix}")
    return "\n".join(lines)


def render_durable(memories: list[dict]) -> str:
    if not memories:
        return "(none)"
    return "\n".join(
        f"[{i}] {m.get('statement', m.get('label', ''))}" for i, m in enumerate(memories)
    )


def build_prompt(template: str, records: list[dict], durable: list[dict]) -> str:
    return template.replace("<<EXISTING_DURABLE>>", render_durable(durable)).replace(
        "<<SEMANTIC_RECORDS>>", render_records(records)
    )


# ── modes -----------------------------------------------------------------
def run_prompt_mode(args, exp_dir: Path, records: list[dict], durable: list[dict]) -> None:
    prompt_path = Path(args.prompt)
    prompt = build_prompt(prompt_path.read_text(), records, durable)

    live = not args.dry_run and _has_key(args)
    completion: str | None = None
    if live:
        completion = _make_client(args).complete(prompt)

    runs = _runs_dir(exp_dir)
    stamp = _stamp()
    tag = args.model if live else "DRYRUN"
    out = runs / f"{stamp}__{prompt_path.stem}__{tag}.md"
    body = [
        f"# Run {stamp}", "",
        f"- experiment: `{args.experiment}`",
        f"- prompt: `{prompt_path.stem}`",
        f"- model: {args.model if live else '(dry-run — no model call)'}",
        f"- records: {len(records)}   existing durable: {len(durable)}",
        "", "---", "", "## Prompt", "", prompt,
    ]
    if completion is not None:
        body += ["", "---", "", "## Completion", "", completion]
    out.write_text("\n".join(body))
    print(f"wrote {out.relative_to(HERE.parent)}")
    if not live:
        env = _PROVIDERS[args.provider]["env"]
        reason = "--dry-run" if args.dry_run else f"no {env}"
        print(f"({reason}) — rendered prompt only. Paste it into a chat UI to watch the")
        print(f"reasoning, or set {env} and re-run for a captured completion.")


def run_builder_mode(args, exp_dir: Path, records: list[dict], durable: list[dict]) -> None:
    from lyr.durable import JudgmentBuilder
    from lyr.store import InMemoryStore

    if args.canned:
        from lyr.llm.fake import FakeClient
        client = FakeClient(Path(args.canned).read_text())
        tag = "CANNED"
    elif _has_key(args):
        client = _make_client(args)
        tag = args.model
    else:
        prov = _PROVIDERS[args.provider]
        raise SystemExit(
            f"builder mode needs a model: set {prov['env']} "
            f"(+ pip install -e '.[{prov['extra']}]')\n"
            "or pass --canned <file> with a model response to run the loop offline."
        )

    store = InMemoryStore()
    semantic = to_semantic_nodes(records)
    for n in semantic:
        store.add_node(n)
    candidates = to_durable_nodes(durable)
    for n in candidates:
        store.add_node(n)

    verifier = _make_verifier(args, client)

    if args.decompose:
        _run_decomposed(args, exp_dir, store, client, semantic, candidates, tag, verifier)
        return

    result = JudgmentBuilder(store, client, verifier=verifier).update(semantic, candidates)
    record = result.judgment_record

    runs = _runs_dir(exp_dir)
    stamp = _stamp()
    (runs / f"{stamp}__judgment__{tag}.json").write_text(
        json.dumps(record.to_dict(), indent=2, ensure_ascii=False)
    )

    ea = result.engine_action
    node = result.updated_durable
    print(f"=== {args.experiment} — builder run ({tag}) ===")
    print(f"model op   : {record.model_intent.operation}   -> engine: {ea.operation}")
    print(f"statement  : {record.model_intent.statement or '(none)'}")
    print(f"kind       : {record.model_intent.kind}")
    print(f"evidence   : {len(record.model_intent.evidence)} semantic record(s)")
    print(f"confidence : {record.model_intent.confidence}")
    if record.model_intent.counter_evidence:
        print(f"counter    : {record.model_intent.counter_evidence}")
    if ea.rejection_reason:
        print(f"rejected   : {ea.rejection_reason}")
    if node is not None:
        print(f"committed  : durable {node.identity} v{node.version}  (judgment {record.judgment_id})")
    print(f"wrote {(runs / f'{stamp}__judgment__{tag}.json').relative_to(HERE.parent)}")


# ── providers -------------------------------------------------------------
# One row per LLM provider: which env var holds the key, which pip extra installs
# the SDK, and the default model. Adding a provider is one entry + one client class.
_PROVIDERS = {
    "anthropic": {"env": "ANTHROPIC_API_KEY", "extra": "anthropic", "default_model": "claude-opus-4-8"},
    "openai": {"env": "OPENAI_API_KEY", "extra": "openai", "default_model": "gpt-4o"},
}


def _make_verifier(args, client):
    if not getattr(args, "verify", False):
        return None
    from lyr.durable import LLMDurabilityVerifier
    return LLMDurabilityVerifier(client)


def _has_key(args) -> bool:
    return bool(os.environ.get(_PROVIDERS[args.provider]["env"]))


def _make_client(args):
    prov = _PROVIDERS[args.provider]
    try:
        if args.provider == "openai":
            from lyr.llm.openai import OpenAIClient
            return OpenAIClient(model=args.model, max_tokens=args.max_tokens)
        from lyr.llm.anthropic import AnthropicClient
        return AnthropicClient(model=args.model, max_tokens=args.max_tokens)
    except ImportError as e:
        raise SystemExit(
            f"live mode needs the {args.provider} extra "
            f"(pip install -e '.[{prov['extra']}]'): {e}"
        )


# ── decomposed pipeline (M3.1-B.2) ---------------------------------------
def _run_decomposed(args, exp_dir, store, client, semantic, candidates, tag, verifier=None) -> None:
    from lyr.durable import (
        JudgmentPipeline,
        LLMDecomposer,
        SingletonDecomposer,
        WholeBatchDecomposer,
    )

    decomposer = {
        "whole": WholeBatchDecomposer(),
        "singleton": SingletonDecomposer(),
        "llm": LLMDecomposer(client),
    }[args.decompose]

    results = JudgmentPipeline(store, client, decomposer, verifier=verifier).run(semantic, candidates)

    runs = _runs_dir(exp_dir)
    stamp = _stamp()
    committed = 0
    print(f"=== {args.experiment} — decomposed run ({tag}, decompose={args.decompose}) ===")
    print(f"{len(semantic)} record(s) → {len(results)} judgment unit(s)")
    for i, r in enumerate(results):
        rec = r.judgment_record
        (runs / f"{stamp}__judgment__{tag}__unit{i:02d}.json").write_text(
            json.dumps(rec.to_dict(), indent=2, ensure_ascii=False)
        )
        node = r.updated_durable
        if node:
            committed += 1
        v = rec.verification
        vtag = (f" [verify:{v.decision if v.status == 'SUCCESS' else 'ERROR'}]" if v else "")
        mark = (f"durable {node.identity} v{node.version}" if node else r.engine_action.operation) + vtag
        print(f"  [{i}] {rec.model_intent.operation:5} -> {r.engine_action.operation:6} | "
              f"{rec.model_intent.statement or '(none)'}  ({mark})")
    print(f"committed {committed} durable memory(ies) from one batch; "
          f"wrote {len(results)} record(s) to runs/")


# ── helpers ---------------------------------------------------------------


def _runs_dir(exp_dir: Path) -> Path:
    d = exp_dir / "runs"
    d.mkdir(exist_ok=True)
    return d


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("experiment", help="experiment dir name under experiments/")
    ap.add_argument("--prompt", default=str(DEFAULT_PROMPT), help="prompt template file")
    ap.add_argument("--provider", choices=sorted(_PROVIDERS), default="anthropic",
                    help="LLM provider (default: anthropic)")
    ap.add_argument("--model", default=None,
                    help="model id (default: the provider's default model)")
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--dry-run", action="store_true", help="prompt mode: render, call nothing")
    ap.add_argument("--builder", action="store_true", help="run JudgmentBuilder.update end to end")
    ap.add_argument("--decompose", choices=["whole", "singleton", "llm"],
                    help="builder mode: decompose the batch into topic units first (M3.1-B.2)")
    ap.add_argument("--verify", action="store_true",
                    help="builder mode: gate each proposal with the durability verifier (M3.1-C)")
    ap.add_argument("--canned", help="builder mode: a file with a canned model response (offline)")
    args = ap.parse_args()
    # Resolve the model default from the chosen provider.
    args.model = args.model or _PROVIDERS[args.provider]["default_model"]

    exp_dir = HERE / args.experiment
    if not exp_dir.is_dir():
        raise SystemExit(f"no experiment dir: {exp_dir}")

    records = load_records(exp_dir)
    durable = load_durable(exp_dir)

    if args.builder:
        run_builder_mode(args, exp_dir, records, durable)
    else:
        run_prompt_mode(args, exp_dir, records, durable)


if __name__ == "__main__":
    main()
