"""Durability verification (M3.1-C) — should a proposed durable memory persist?

Implements the task frozen in M3.1-C0. A ``DurabilityVerifier`` looks at **one**
proposed durable memory and its cited evidence and answers exactly one question —
*should this become long-term knowledge?* — returning a ``Verdict``. It is:

- a **gate, not an editor** — it never rewrites the statement or changes the
  operation; the builder maps its verdict to commit-or-``NO_OP`` (C0 §1);
- **stateless** — it sees only this proposal + its evidence, no history (C0 §5);
- fed only the **Builder's judgment context** — the cited semantic nodes, never
  candidate durables or source records (C0 §2).

A verifier that *fails to run* returns ``status=ERROR`` — never a semantic UNSURE.
"Broken verifier" must not masquerade as "maybe keep it."

Design: docs/design/M3.1-C-durability-verifier.md.
"""

from __future__ import annotations

import json
import re
from importlib.resources import files
from typing import Any, Iterable, Protocol

from ..llm.base import LLMClient
from ..models import Node
from .judgment import (
    ERROR,
    KEEP,
    REJECT,
    SUCCESS,
    UNSURE,
    VERDICT_DECISIONS,
    ModelProposal,
    Verdict,
)

VERIFIER_PROMPT_VERSION = "durability_verifier_v1"
VERIFIER_PROMPT = (
    files("lyr.durable").joinpath("prompts").joinpath(f"{VERIFIER_PROMPT_VERSION}.md")
).read_text(encoding="utf-8")


class DurabilityVerifier(Protocol):
    def verify(self, proposal: ModelProposal, evidence: list[Node]) -> Verdict:
        """Judge whether ``proposal`` deserves long-term persistence."""
        ...


class LLMDurabilityVerifier:
    """Ask a model the one durability question. ERROR-safe by construction."""

    def __init__(self, client: LLMClient, *, prompt: str = VERIFIER_PROMPT) -> None:
        self._client = client
        self._prompt = prompt

    def verify(self, proposal: ModelProposal, evidence: list[Node]) -> Verdict:
        cfg = self._config()
        rendered = (
            self._prompt.replace("<<STATEMENT>>", proposal.statement)
            .replace("<<KIND>>", proposal.kind)
            .replace("<<EVIDENCE>>", _render_evidence(evidence))
        )
        try:
            raw = self._client.complete(rendered)
        except Exception as e:  # noqa: BLE001 — any client/transport failure is an ERROR
            return Verdict(decision=UNSURE, status=ERROR,
                           error_reason=f"{type(e).__name__}: {e}", model_config=cfg)

        parsed = _parse_object(raw)
        if not isinstance(parsed, dict) or parsed.get("verdict") not in VERDICT_DECISIONS:
            return Verdict(decision=UNSURE, status=ERROR, raw_completion=raw,
                           parsed_payload=parsed, error_reason="malformed verifier output",
                           model_config=cfg)

        return Verdict(
            decision=parsed["verdict"],
            status=SUCCESS,
            rationale=_clean_str(parsed.get("reason")),
            confidence=_clean_confidence(parsed.get("confidence")),
            raw_completion=raw,
            parsed_payload=parsed,
            model_config=cfg,
        )

    def _config(self) -> dict[str, Any]:
        cfg: dict[str, Any] = {"prompt_version": VERIFIER_PROMPT_VERSION,
                               "provider": type(self._client).__name__}
        model = getattr(self._client, "model", None)
        if model:
            cfg["model"] = model
        return cfg


class ThresholdDurabilityVerifier:
    """A deterministic control — KEEP iff the builder's confidence ≥ threshold.

    Not a real durability policy (builder confidence is not durability): a runnable,
    offline baseline the LLM verifier must beat — the same role RecurrenceConsolidator
    plays for the durable layer.
    """

    def __init__(self, threshold: float = 0.5) -> None:
        self.threshold = threshold

    def verify(self, proposal: ModelProposal, evidence: list[Node]) -> Verdict:
        conf = proposal.confidence
        decision = KEEP if (conf is None or conf >= self.threshold) else REJECT
        return Verdict(decision=decision, status=SUCCESS, confidence=conf,
                       rationale=f"threshold={self.threshold} (control)")


# ── helpers ---------------------------------------------------------------
def _render_evidence(nodes: Iterable[Node]) -> str:
    nodes = list(nodes)
    if not nodes:
        return "(none)"
    return "\n".join(f"- ({n.kind}) {n.label}" for n in nodes)


def _parse_object(text: str) -> dict[str, Any] | None:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        data = json.loads(text[start : end + 1])
    except (json.JSONDecodeError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _clean_str(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _clean_confidence(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None
