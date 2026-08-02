"""OpenAI (ChatGPT) provider. Optional dep — ``pip install 'lyr[openai]'``.

A thin wrapper around ``openai.OpenAI().chat.completions.create`` so the rest of
LYR only ever sees the one-method ``LLMClient`` contract — the exact same seam
``AnthropicClient`` implements. Swap one for the other anywhere a client is taken
(``LLMExtractor``, ``JudgmentBuilder``, the experiment harness).
"""

from __future__ import annotations


class OpenAIClient:
    """Maps a prompt to a completion via the OpenAI Chat Completions API.

    Defaults to ``gpt-4o``; pass any chat model to ``model=`` (e.g.
    ``"gpt-4o-mini"`` for a cheaper, faster option on large corpora).

    Like ``AnthropicClient``, no sampling parameters are sent — ``temperature`` /
    ``top_p`` are omitted so the request stays portable across model families
    (several newer OpenAI models reject a non-default ``temperature``). LYR steers
    generation through the prompt instead.
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: str | None = None,
        *,
        max_tokens: int | None = 4096,
    ) -> None:
        try:
            import openai  # type: ignore[import-not-found]
        except ImportError as e:
            raise ImportError(
                "openai package is not installed. Install with: pip install 'lyr[openai]'"
            ) from e
        self._client = openai.OpenAI(api_key=api_key) if api_key else openai.OpenAI()
        self.model = model
        self.max_tokens = max_tokens

    def complete(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        try:
            msg = self._client.chat.completions.create(
                model=self.model, messages=messages, **self._token_kwarg()
            )
        except Exception as e:  # noqa: BLE001 — provider-specific error surface
            # Newer models rename ``max_tokens`` to ``max_completion_tokens``.
            if self.max_tokens is not None and "max_completion_tokens" in str(e):
                msg = self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_completion_tokens=self.max_tokens,
                )
            else:
                raise
        return msg.choices[0].message.content or ""

    def _token_kwarg(self) -> dict[str, int]:
        return {"max_tokens": self.max_tokens} if self.max_tokens is not None else {}
