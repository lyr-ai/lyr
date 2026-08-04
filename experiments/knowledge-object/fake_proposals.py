"""A canned FakeClient for the --fake harness self-test.

NOT a model measurement — it returns fixed proposals so Part B's metrics can be exercised without
a paid call. Each corpus's canned set deliberately mixes a real supported relation, a plausible
fabrication (unsupported), and (for P&P) a contradicted one, so the verifier's commit/withhold
split is visible. Real numbers require `--client openai/anthropic` with a key.
"""

from __future__ import annotations

import json

from lyr.llm.fake import FakeClient

_CANNED = {
    "deepseek": [
        {"subject": "MLA", "predicate": "evolved into", "object": "DSA",
         "scope": "architecture", "rationale": "they appear in successive versions"},
        {"subject": "CSA", "predicate": "replaced", "object": "DSA",
         "scope": "architecture", "rationale": "V4 supersedes V3.2"},
    ],
    "kimi": [
        {"subject": "MuonClip", "predicate": "improves upon", "object": "Muon",
         "scope": "optimization", "rationale": "stated in the abstract"},
        {"subject": "MLA", "predicate": "evolved into", "object": "MuonClip",
         "scope": "architecture", "rationale": "both are Kimi components"},
    ],
    "pnp": [
        {"subject": "Elizabeth", "predicate": "refuses", "object": "Mr. Darcy",
         "scope": "ch34", "rationale": "the first proposal is rejected"},
        {"subject": "Elizabeth", "predicate": "accepts", "object": "Mr. Darcy",
         "scope": "ch34", "rationale": "she ends up with him"},
        {"subject": "Elizabeth", "predicate": "married", "object": "Mr. Darcy",
         "scope": "ch61", "rationale": "they marry"},
    ],
}


def make_fake_client() -> FakeClient:
    def respond(prompt: str) -> str:
        for corpus, canned in _CANNED.items():
            if f"[{corpus}/" in prompt:
                return json.dumps(canned)
        return "[]"
    return FakeClient(respond)
