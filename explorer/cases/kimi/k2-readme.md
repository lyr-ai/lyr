# Kimi K2 README — Open Agentic Intelligence

## Overview

Kimi K2 is a state-of-the-art Mixture-of-Experts (MoE) language model with 32 billion activated
parameters and 1 trillion total parameters. The architecture employs the Muon optimizer at
unprecedented scale together with novel optimization techniques for training stability.

## Specifications

| Component | Details |
|-----------|---------|
| Total parameters | 1 Trillion |
| Activated parameters | 32 Billion |
| Architecture | Mixture-of-Experts (MoE) |
| Layers | 61 (including 1 dense layer) |
| Experts | 384 total; 8 selected per token |
| Context length | 128K tokens |
| Vocabulary | 160K tokens |
| Attention | MLA (Multi-head Latent Attention) |

## Model variants

- **Kimi-K2-Base** — foundation model for researchers requiring full control for fine-tuning and
  custom solutions.
- **Kimi-K2-Instruct** — post-trained variant optimized for drop-in, general-purpose chat and
  agentic experiences.

## Capabilities

Kimi K2 performs strongly in coding (53.7 on LiveCodeBench), tool use (70.6 on Tau2 retail tasks),
mathematics (69.6 on AIME 2024), and general knowledge (89.5 MMLU), with strong agentic capabilities
including autonomous problem-solving and reasoning.

## Access and license

Models are available via Hugging Face in block-fp8 format and through the Moonshot AI API with
OpenAI/Anthropic-compatible endpoints. Recommended inference engines: vLLM, SGLang, KTransformers,
TensorRT-LLM. Code and weights are released under a Modified MIT License.
