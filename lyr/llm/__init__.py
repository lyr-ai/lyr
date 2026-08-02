"""LLM client abstraction — one method, many providers.

Every provider implements the same ``LLMClient`` contract (``complete(prompt) ->
str``). ``AnthropicClient`` and ``OpenAIClient`` import their SDKs lazily (inside
``__init__``), so importing the class here never requires the optional package —
only *constructing* one does.
"""

from .anthropic import AnthropicClient
from .base import LLMClient
from .fake import FakeClient
from .openai import OpenAIClient

__all__ = ["LLMClient", "FakeClient", "AnthropicClient", "OpenAIClient"]
