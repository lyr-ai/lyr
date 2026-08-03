# DeepSeek-V4 Technical Report

## Title

DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence

## Abstract

We present a preview version of the DeepSeek-V4 series, including two strong
Mixture-of-Experts (MoE) language models — DeepSeek-V4-Pro with 1.6T parameters
(49B activated) and DeepSeek-V4-Flash with 284B parameters (13B activated) —
both supporting a context length of one million tokens. The DeepSeek-V4 series
incorporates several key upgrades in architecture and optimization: (1) a hybrid
attention architecture that combines Compressed Sparse Attention (CSA) and
Heavily Compressed Attention (HCA) to improve long-context efficiency;
(2) Manifold-Constrained Hyper-Connections (mHC) that enhance conventional
residual connections; and (3) the Muon optimizer for faster convergence and
greater training stability.

## Model Variants

- **DeepSeek-V4-Pro** — 1.6T parameters, 49B activated.
- **DeepSeek-V4-Flash** — 284B parameters, 13B activated.
- **DeepSeek-V4-Pro-Max** — the maximum reasoning effort mode of DeepSeek-V4-Pro.

## Architecture Components

- Compressed Sparse Attention (CSA)
- Heavily Compressed Attention (HCA)
- Manifold-Constrained Hyper-Connections (mHC)
- Mixture-of-Experts (MoE) design
- Muon optimizer
- One-million-token context length support

## Capability Claims

DeepSeek-V4-Pro-Max, the maximum reasoning effort mode of DeepSeek-V4-Pro,
redefines the state-of-the-art for open models. DeepSeek-V4-Pro requires only 27%
of single-token inference FLOPs and 10% of KV cache compared with DeepSeek-V3.2.
The models routinely support one-million-token contexts, thereby making
long-horizon tasks and further test-time scaling more feasible.
