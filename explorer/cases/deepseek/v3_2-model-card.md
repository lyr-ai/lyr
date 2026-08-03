# DeepSeek-V3.2-Exp Model Card

## Model Information

**Model Name:** DeepSeek-V3.2-Exp

**Base Model:** DeepSeek-V3.2-Exp builds upon V3.1-Terminus by introducing
DeepSeek Sparse Attention — a sparse attention mechanism designed to explore and
validate optimizations for training and inference efficiency in long-context
scenarios.

## Architecture Components

- **DeepSeek Sparse Attention (DSA):** achieves fine-grained sparse attention for
  the first time, delivering substantial improvements in long-context training
  and inference efficiency while maintaining virtually identical model output
  quality.
- **MLA module:** referenced in the context of RoPE (Rotary Position Embedding)
  implementation details.
- **Indexer module:** referenced alongside architectural specifications for RoPE
  handling.
- **MoE (Mixture of Experts):** the configuration uses 256 experts.

## Performance Claims

The model demonstrates performance on par with V3.1-Terminus across public
benchmarks. Highlighted capabilities include reasoning (MMLU-Pro: 85.0, AIME
2025: 89.3), code generation (Codeforces: 2121), agentic tool use, and
long-context processing efficiency.

## License

This repository and the model weights are licensed under the MIT License.
