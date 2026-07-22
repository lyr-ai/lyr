"""LLM client abstraction — one method, many providers."""

from .base import LLMClient
from .fake import FakeClient

__all__ = ["LLMClient", "FakeClient"]
