# Kimi corpus — provenance

First-party (Moonshot AI) only. Assembled as the **fourth-world falsification** of the scoped-claim
primitive from the Knowledge-Object Exploration — a corpus NOT used to discover the primitive.

| corpus file | official source | version |
|-------------|-----------------|---------|
| `k2-technical-report.md`     | arXiv:2507.20534 — *Kimi K2: Open Agentic Intelligence* | K2 |
| `k2-readme.md`               | github.com/MoonshotAI/Kimi-K2 — README                 | K2 |
| `k2-thinking-model-card.md`  | huggingface.co/moonshotai/Kimi-K2-Thinking             | K2-Thinking |

Lineage context (from official sources): Kimi K1.5 → **Kimi K2** (1T MoE, 32B active) →
Kimi-K2.5 / **Kimi-K2-Thinking** (Nov 2025).

## Fidelity note (honest)

Rendered from the official sources via a fetch step, not byte-exact scrapes. Extraction preserved
**entity names, version strings, component names, and claim wording verbatim** (`MuonClip`, `Muon`,
`Multi-head Latent Attention (MLA)`, `MoE`, `SwiGLU`, "improves upon Muon with a novel QK-clip
technique", "native INT4 quantization via QAT … absent from previous Kimi versions"). Surrounding
prose is condensed. Replace any file with the raw official document at the same path for a byte-exact
corpus.

## Why this corpus (falsification, not confirmation)

Kimi was chosen to try to **break** the scoped-claim primitive, not confirm it. It offers three
tests the first three probes could not:

1. A **SUPPORTED derivation** relation — `MuonClip improves upon Muon` is *explicitly stated*, the
   mirror image of DeepSeek's *unstated* MLA→DSA→CSA lineage (which had to be `ABSTAINED`). Same
   relation type, opposite evidence → does the `status` enum actually commit when warranted?
2. A **version-scoped departure** — K2-Thinking's INT4 QAT "absent from previous Kimi versions".
3. A **cross-corpus identity** question — `MLA` appears in *both* DeepSeek and Kimi. Does the
   within-corpus primitive say anything about that? (Prediction: no — a boundary, not a break.)
