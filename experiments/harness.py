#!/usr/bin/env python3
"""Experiment harness: watch an LLM reason about durable-knowledge formation.

    semantic records  ->  durability-judgment prompt  ->  LLM  ->  transcript

This is a *research* harness — not part of the engine, not a benchmark. It exists
to observe how a model groups evidence and decides what becomes durable, before
that reasoning is committed to code (see docs/design/M3.1-A-judgment-contract.md).

Usage:
    python experiments/harness.py experiment-001-memoir --dry-run     # render only
    python experiments/harness.py experiment-001-memoir               # live if ANTHROPIC_API_KEY set
    python experiments/harness.py experiment-001-memoir --model claude-opus-4-8
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_PROMPT = HERE / "prompts" / "durability_judgment_v1.md"


def load_records(exp_dir: Path) -> list[dict]:
    f = exp_dir / "semantic_nodes.json"
    if not f.exists():
        raise SystemExit(f"no semantic_nodes.json in {exp_dir}")
    return json.loads(f.read_text())


def load_durable(exp_dir: Path) -> list[dict]:
    f = exp_dir / "existing_durable.json"
    return json.loads(f.read_text()) if f.exists() else []


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
    # Sentinel tokens (not str.format) so the literal JSON braces in the prompt
    # template survive untouched.
    return template.replace("<<EXISTING_DURABLE>>", render_durable(durable)).replace(
        "<<SEMANTIC_RECORDS>>", render_records(records)
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("experiment", help="experiment dir name under experiments/")
    ap.add_argument("--prompt", default=str(DEFAULT_PROMPT), help="prompt template file")
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--dry-run", action="store_true", help="render the prompt, call nothing")
    args = ap.parse_args()

    exp_dir = HERE / args.experiment
    if not exp_dir.is_dir():
        raise SystemExit(f"no experiment dir: {exp_dir}")

    records = load_records(exp_dir)
    durable = load_durable(exp_dir)
    prompt_path = Path(args.prompt)
    prompt = build_prompt(prompt_path.read_text(), records, durable)

    live = not args.dry_run and bool(os.environ.get("ANTHROPIC_API_KEY"))
    completion: str | None = None
    if live:
        try:
            from lyr.llm.anthropic import AnthropicClient
        except ImportError as e:
            raise SystemExit(f"live mode needs the anthropic extra (pip install -e '.[anthropic]'): {e}")
        completion = AnthropicClient(model=args.model, max_tokens=args.max_tokens).complete(prompt)

    runs = exp_dir / "runs"
    runs.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    tag = args.model if live else "DRYRUN"
    out = runs / f"{stamp}__{prompt_path.stem}__{tag}.md"

    body = [
        f"# Run {stamp}",
        "",
        f"- experiment: `{args.experiment}`",
        f"- prompt: `{prompt_path.stem}`",
        f"- model: {args.model if live else '(dry-run — no model call)'}",
        f"- records: {len(records)}   existing durable: {len(durable)}",
        "",
        "---",
        "",
        "## Prompt",
        "",
        prompt,
    ]
    if completion is not None:
        body += ["", "---", "", "## Completion", "", completion]
    out.write_text("\n".join(body))

    print(f"wrote {out.relative_to(HERE.parent)}")
    if not live:
        reason = "--dry-run" if args.dry_run else "no ANTHROPIC_API_KEY"
        print(f"({reason}) — rendered prompt only. Paste it into claude.ai to watch the")
        print("reasoning, or set ANTHROPIC_API_KEY and re-run for a captured completion.")


if __name__ == "__main__":
    main()
