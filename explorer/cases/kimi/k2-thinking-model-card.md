# Kimi-K2-Thinking Model Card

## Model identity

Kimi K2 Thinking is the latest, most capable version of the open-source thinking model, built upon
Kimi K2 — an evolution in the product line.

## Architecture components

- **MoE (Mixture-of-Experts):** 384 total experts with 8 selected per token; 1T total, 32B activated.
- **MLA (Multi-head Latent Attention):** the attention mechanism.
- **SwiGLU:** activation function.
- 61 total layers (including 1 dense layer); 256K context window.

## Capability claims

Kimi K2 Thinking sets a new state-of-the-art on Humanity's Last Exam (HLE), BrowseComp, and other
benchmarks. It demonstrates stable tool-use across 200–300 sequential tool calls, a significant
improvement in multi-step reasoning stability.

## Departures from prior versions

The model introduces native INT4 quantization via Quantization-Aware Training (QAT), achieving
roughly 2x generation-speed improvement without performance degradation — a technical advancement
absent from previous Kimi versions.
