# DeepSeek-V3 Technical Report

## Abstract

We present DeepSeek-V3, a strong Mixture-of-Experts (MoE) language model with
671B total parameters with 37B activated for each token. To achieve efficient
inference and cost-effective training, DeepSeek-V3 adopts Multi-head Latent
Attention (MLA) and DeepSeekMoE architectures, which were thoroughly validated
in DeepSeek-V2. Furthermore, DeepSeek-V3 pioneers an auxiliary-loss-free
strategy for load balancing and sets a multi-token prediction training
objective for stronger performance.

## Models

- **DeepSeek-V3** — the main model: 671B total parameters, 37B activated per token.
- **DeepSeek-V3-Base** — the base model variant.

## Architecture

DeepSeek-V3 adopts **Multi-head Latent Attention (MLA)** for efficient inference
and **DeepSeekMoE** for cost-effective training. Both MLA and DeepSeekMoE were
thoroughly validated in DeepSeek-V2. DeepSeek-V3 pioneers an
**auxiliary-loss-free strategy** for load balancing, minimizing the performance
degradation that arises from encouraging load balancing. It also sets a
**Multi-Token Prediction (MTP)** training objective for stronger performance.
Training uses an **FP8 mixed precision** framework.

## Claims

Comprehensive evaluations reveal that DeepSeek-V3 outperforms other open-source
models and achieves performance comparable to leading closed-source models.
DeepSeek-V3 requires only 2.788M H800 GPU hours for its full training, with
remarkable training stability throughout the process.
