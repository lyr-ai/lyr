"""Adversarial gold set for the proposer-behind-verifier measurement.

Three categories per corpus (the whole point — feeding only the 6 easy hand-probe claims would
be too easy):

  SUPPORTED_TRUTH        the corpus states it → expect SUPPORTED
  PLAUSIBLE_UNSUPPORTED  sounds right, corpus does NOT state it → expect UNKNOWN (the real test)
  CONTRADICTED           the corpus states the opposite → expect CONTRADICTED

Corpus roles (frozen): DeepSeek = development · P&P/Elizabeth = second-structure dev sanity
(softer evidence, watch over-abstention) · Kimi = HELD-OUT evaluation. Do not tune the verifier
on Kimi and still call it held-out (see README).

Each record carries everything needed to build a `Claim`, plus its category and expected verdict.
`aliases` use word-boundary matching in the verifier, so precise aliases avoid e.g. `K2` matching
`K2-Thinking`.
"""

from __future__ import annotations

from claim_verifier import Claim

MLA = ("MLA", "Multi-head Latent Attention")
DSA = ("DSA", "DeepSeek Sparse Attention")
CSA = ("CSA", "Compressed Sparse Attention")
HCA = ("HCA", "Heavily Compressed Attention")
EFFICIENCY = ("efficiency", "long-context", "long context", "kv cache", "inference")

# (corpus, category, expected, Claim)
GOLD: list[tuple[str, str, str, Claim]] = [
    # ---------- DeepSeek (development) ----------
    ("deepseek", "SUPPORTED_TRUTH", "SUPPORTED",
     Claim("MLA/DSA/CSA/HCA", "grouping", "attention efficiency", "architecture",
           group_members=(MLA, DSA, CSA, HCA), goal_terms=EFFICIENCY)),
    ("deepseek", "SUPPORTED_TRUTH", "SUPPORTED",
     Claim("V4-Pro", "quantified", "27% FLOPs / 10% KV cache vs V3.2", "vs V3.2",
           value_tokens=("27%", "kv cache"))),
    ("deepseek", "PLAUSIBLE_UNSUPPORTED", "UNKNOWN",
     Claim("DSA", "derives_from", "MLA", "architecture", DSA, MLA)),
    ("deepseek", "PLAUSIBLE_UNSUPPORTED", "UNKNOWN",
     Claim("CSA", "derives_from", "DSA", "architecture", CSA, DSA)),
    ("deepseek", "PLAUSIBLE_UNSUPPORTED", "UNKNOWN",
     Claim("DeepSeek-V4", "derives_from", "DeepSeek-V3", "version",
           ("DeepSeek-V4", "V4-Pro", "V4-Flash"), ("DeepSeek-V3", "DeepSeek-V3-Base"))),
    ("deepseek", "CONTRADICTED", "CONTRADICTED",   # inferential — baseline expected to MISS → UNKNOWN
     Claim("MLA", "introduces", "sparse attention", "architecture",
           MLA, ("sparse attention",))),

    # ---------- P&P / Elizabeth (dev sanity; softer evidence) ----------
    ("pnp", "SUPPORTED_TRUTH", "SUPPORTED",
     Claim("Elizabeth", "refuses", "Darcy", "ch34",
           ("Elizabeth",), ("Darcy", "Mr. Darcy"))),
    ("pnp", "SUPPORTED_TRUTH", "SUPPORTED",
     Claim("Elizabeth", "married", "Darcy", "ch61",
           ("Elizabeth",), ("Darcy", "Mr. Darcy"))),
    ("pnp", "PLAUSIBLE_UNSUPPORTED", "UNKNOWN",   # interpretive inner-state, unstated
     Claim("Elizabeth's prejudice", "resolved_by", "Darcy's letter", "ch36",
           ("prejudice",), ("letter",))),
    ("pnp", "PLAUSIBLE_UNSUPPORTED", "UNKNOWN",   # thematic argument, unstated
     Claim("Austen", "critiques", "the marriage market", "book",
           ("Austen",), ("marriage market",))),
    ("pnp", "CONTRADICTED", "CONTRADICTED",       # corpus says she REFUSES at ch34
     Claim("Elizabeth", "accepts", "Darcy", "ch34",
           ("Elizabeth",), ("Darcy", "Mr. Darcy"))),

    # ---------- Kimi (HELD-OUT) ----------
    ("kimi", "SUPPORTED_TRUTH", "SUPPORTED",
     Claim("MuonClip", "derives_from", "Muon", "optimization", ("MuonClip",), ("Muon",))),
    ("kimi", "PLAUSIBLE_UNSUPPORTED", "UNKNOWN",
     Claim("MLA", "derives_from", "MuonClip", "architecture", MLA, ("MuonClip",))),
    ("kimi", "PLAUSIBLE_UNSUPPORTED", "UNKNOWN",  # causal, unstated
     Claim("INT4 QAT", "introduces", "SOTA on HLE", "K2-Thinking",
           ("INT4",), ("HLE", "Humanity's Last Exam"))),
    ("kimi", "CONTRADICTED", "CONTRADICTED",      # precedence — baseline expected to MISS → UNKNOWN
     Claim("Kimi K2", "introduces", "INT4 quantization", "version",
           ("Kimi K2", "Kimi-K2-Instruct"), ("INT4",))),
]


def by_corpus(corpus: str) -> list[tuple[str, str, Claim]]:
    return [(cat, exp, c) for (co, cat, exp, c) in GOLD if co == corpus]
