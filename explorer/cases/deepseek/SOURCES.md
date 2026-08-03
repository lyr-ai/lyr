# DeepSeek corpus — provenance

All first-party (official DeepSeek). No news, blogs, or third-party commentary,
so any identity failure localizes to the LYR backend, not to source disagreement.

| corpus file | official source | version |
|-------------|-----------------|---------|
| `v3-technical-report.md` | arXiv:2412.19437 — *DeepSeek-V3 Technical Report* | V3 |
| `v3-readme.md`           | github.com/deepseek-ai/DeepSeek-V3 — README      | V3 |
| `v3_2-model-card.md`     | huggingface.co/deepseek-ai/DeepSeek-V3.2-Exp     | V3.2 |
| `v3_2-release.md`        | api-docs.deepseek.com/news/news251201 — V3.2 release notes | V3.2 |
| `v4-technical-report.md` | arXiv:2606.19348 — *DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence* | V4 |

## Fidelity note (honest)

These `.md` files were rendered from the official sources via a fetch step, not
pasted as byte-exact scrapes. Extraction preserved **entity names, version
strings, component names, and claim wording verbatim** (e.g. `DeepSeek-V4-Pro`,
`Multi-head Latent Attention (MLA)`, `DeepSeek Sparse Attention`, "requires only
27% of single-token inference FLOPs and 10% of KV cache compared with
DeepSeek-V3.2") — which is exactly what the identity/claim resolver is tested on.
Surrounding prose is condensed. For a byte-exact corpus, replace any file with
the raw official document at the same path and re-run; the manifest is unchanged.

## Identity questions this corpus poses

- **Version identity:** DeepSeek, DeepSeek-V2, V3, V3-Base, V3.1-Terminus,
  V3.2-Exp, V3.2, V3.2-Speciale, V4-Pro, V4-Flash, V4-Pro-Max — one persistent
  entity across versions, or distinct? (Note: the v0 resolver drops non-alpha
  tokens, so `V3`/`V4` may not discriminate — a predicted false-merge to verify.)
- **Component identity:** `MLA` ↔ `Multi-head Latent Attention`; `MoE` ↔
  `DeepSeekMoE`; and the attention lineage `DeepSeek Sparse Attention (DSA)` →
  `Compressed Sparse Attention (CSA)` → `Heavily Compressed Attention (HCA)` —
  same evolving component or distinct ones?
- **Claim tracing:** does "V4-Pro requires only 27% of FLOPs / 10% of KV cache
  vs V3.2" trace to its source doc, and does it correctly reference two versions?
- **Model shape:** does the People-centered Explorer bend to
  Models / Components / Claims, or break?
