"""Anthropic provider. Optional dep — ``pip install 'lyr[anthropic]'``.

This is the default LLM backend for the semantic layer. A thin wrapper around
``anthropic.Anthropic.messages.create`` so the rest of LYR only ever sees the
one-method ``LLMClient`` contract.
"""

from __future__ import annotations


class AnthropicClient:
    """Maps a prompt to a completion via the Claude Messages API.

    Defaults to Claude Opus 4.8. Extraction runs well on cheaper tiers too —
    pass ``model="claude-haiku-4-5"`` for a lower-cost, latency-friendly option
    when you're processing large corpora.

    Note: no sampling parameters are sent. ``temperature`` / ``top_p`` are
    rejected (HTTP 400) on Opus 4.8/4.7 and Sonnet 5, so LYR steers extraction
    through the prompt instead and keeps the request portable across models.
    """

    def __init__(
        self,
        model: str = "claude-opus-4-8",
        api_key: str | None = None,
        *,
        max_tokens: int = 4096,
    ) -> None:
        try:
            import anthropic  # type: ignore[import-not-found]
        except ImportError as e:
            raise ImportError(
                "anthropic package is not installed. "
                "Install with: pip install 'lyr[anthropic]'"
            ) from e
        self._client = (
            anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        )
        self.model = model
        self.max_tokens = max_tokens

    def complete(self, prompt: str) -> str:
        msg = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        # The API returns a list of content blocks; concatenate the text ones.
        parts: list[str] = []
        for block in msg.content:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        return "".join(parts)
