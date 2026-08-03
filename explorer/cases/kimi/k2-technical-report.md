# Kimi K2 Technical Report — Open Agentic Intelligence

## Abstract

We introduce Kimi K2, a Mixture-of-Experts (MoE) large language model with 32 billion activated
parameters and 1 trillion total parameters. We propose the MuonClip optimizer, which improves upon
Muon with a novel QK-clip technique to address training instability while enjoying the advanced token
efficiency of Muon. Based on MuonClip, K2 was pre-trained on 15.5 trillion tokens with zero loss
spike. During post-training, K2 undergoes a multi-stage post-training process, highlighted by a
large-scale agentic data synthesis pipeline and a joint reinforcement learning (RL) stage, where the
model improves its capabilities through interactions with real and synthetic environments.

Kimi K2 achieves state-of-the-art performance among open-source non-thinking models, with strengths
in agentic capabilities. Notably, K2 obtains 66.1 on Tau2-Bench, 76.5 on ACEBench (En), 65.8 on
SWE-Bench Verified, and 47.3 on SWE-Bench Multilingual — surpassing most open and closed-sourced
baselines in non-thinking settings. It also exhibits strong capabilities in coding, mathematics, and
reasoning tasks, with 53.7 on LiveCodeBench v6, 49.5 on AIME 2025, 75.1 on GPQA-Diamond, and 27.1 on
OJBench, all without extended thinking.

## Model variants

- **Kimi K2** — the primary model.
- **Kimi-K2-Base** — the base checkpoint.
- **Kimi-K2-Instruct** — the post-trained checkpoint.

## Architecture and optimization

- **Mixture-of-Experts (MoE):** 32B activated of 1T total parameters.
- **MuonClip optimizer:** improves upon Muon with a novel QK-clip technique to address training
  instability, while keeping the token efficiency of Muon. Enabled pre-training on 15.5T tokens with
  zero loss spike.
- **Multi-stage post-training:** a large-scale agentic data synthesis pipeline and a joint
  reinforcement learning (RL) stage.

## Departures from prior work

The MuonClip optimizer is a departure from standard Muon: it introduces a novel QK-clip technique to
address training instability while maintaining Muon's token-efficiency advantages.
