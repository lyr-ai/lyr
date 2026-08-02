# LYR Experiments

**Not benchmarks.** These are research experiments that watch how an LLM *reasons*
about durable-knowledge formation, before any of that reasoning is committed to
the engine.

The loop we are in:

```
Theory  →  Experiment  →  Theory
```

Each experiment feeds a set of **semantic records** into a **durability-judgment
prompt** and records the model's full reasoning:

```
semantic records  →  durability-judgment prompt  →  LLM  →  transcript
```

We are looking at *how the model thinks*: how it groups evidence into independent
observations, when it decides something is durable, when it refuses, how it scopes
a claim under contradiction. The answer matters less than the reasoning.

## Layout

```
experiments/
  harness.py                       # renders the prompt over an experiment, optionally calls the LLM
  prompts/
    durability_judgment_v1.md      # reasoning-INSPECTION prompt (step-by-step, for reading how a
                                   #   model thinks). NOT the builder contract — the canonical
                                   #   builder prompt is lyr/durable/prompts/durable_builder_v1.md
  experiment-001-memoir/
    semantic_nodes.json            # hand-authored clean semantic records (the input)
    input.md                       # the raw passages the records were drawn from (provenance)
    hypothesis.md                  # what we expect, and what to watch for
    runs/                          # captured transcripts (gitignored)
```

## Running

```bash
# Dry-run: render the prompt, call nothing. Paste it into claude.ai to watch reasoning.
.venv/bin/python experiments/harness.py experiment-001-memoir --dry-run

# Live: set a key and it calls the model, saving prompt + completion to runs/.
export ANTHROPIC_API_KEY=...            # and: pip install -e '.[anthropic]'
.venv/bin/python experiments/harness.py experiment-001-memoir --model claude-opus-4-8
```

## Why hand-authored semantic nodes?

To isolate the variable under study. Full `Input → Semantic → Durable` runs mix in
semantic-extraction quality; experiment-001 feeds clean records so what we observe
is *durable judgment alone*. Later experiments can drive the full pipeline from raw
input and compare.

## Relation to the design

These experiments probe the reasoning that
[`docs/design/M3.1-A-judgment-contract.md`](../docs/design/M3.1-A-judgment-contract.md)
will eventually record as `JudgmentRecord`s, and that
[`M3.1-llm-guided-durable-consolidation.md`](../docs/design/M3.1-llm-guided-durable-consolidation.md)
splits into Proposer / Verifier / Challenger / Reviser. Here they are still fused
into one observational prompt on purpose — watch the whole thought first, split it
into roles later.
