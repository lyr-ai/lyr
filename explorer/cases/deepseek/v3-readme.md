# DeepSeek-V3 README

## Overview

DeepSeek-V3 is a Mixture-of-Experts (MoE) language model featuring 671B total
parameters with 37B activated per token. The model leverages Multi-head Latent
Attention (MLA) and DeepSeekMoE architectures, trained on 14.8 trillion tokens
with remarkable training stability and no rollbacks required.

## Key Architecture Innovations

The model pioneers an auxiliary-loss-free load balancing strategy and introduces
Multi-Token Prediction (MTP) objectives for enhanced performance. Training
employed an FP8 mixed precision framework validated at extreme scale, achieving
full computation-communication overlap in cross-node MoE training.

## Model Availability

Two variants are available on Hugging Face:

- **DeepSeek-V3-Base** — 671B parameters, 128K context.
- **DeepSeek-V3** — 671B parameters (includes 14B MTP module weights), 128K context.

## Performance Highlights

DeepSeek-V3 demonstrates competitive results against closed-source models:

- Math: MATH-500 (90.2%), AIME 2024 (39.2%)
- Code: HumanEval-Mul (82.6%), Codeforces (51.6 percentile)
- General: MMLU (88.5%), MMLU-Redux (89.1%)
- Long Context: NIAH evaluation validates the 128K context window
- Open-ended: Arena-Hard (85.5), AlpacaEval 2.0 (70.0)

## Deployment

Recommended inference frameworks include DeepSeek-Infer Demo (FP8/BF16), SGLang,
LMDeploy, TensorRT-LLM, vLLM, and LightLLM, with support for AMD GPU and Huawei
Ascend NPU.

## Licensing

The code is released under the MIT License; the model is released under a Model
Agreement supporting commercial use. Access is available via chat.deepseek.com
and the OpenAI-compatible API at platform.deepseek.com.
