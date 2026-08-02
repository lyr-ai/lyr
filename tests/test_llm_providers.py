"""Provider clients conform to the one-method LLMClient seam.

These assert the wiring only — importing a provider class never requires its SDK
(the SDK import is lazy, inside ``__init__``); only *constructing* one does. No
network, no keys.
"""

from __future__ import annotations

import importlib.util

import pytest

from lyr.llm import AnthropicClient, FakeClient, LLMClient, OpenAIClient


@pytest.mark.parametrize("client_cls", [OpenAIClient, AnthropicClient, FakeClient])
def test_provider_is_shaped_like_llmclient(client_cls):
    # structural conformance to the protocol: a callable complete()
    assert callable(getattr(client_cls, "complete", None))


@pytest.mark.parametrize(
    "client_cls, pkg, extra",
    [(OpenAIClient, "openai", "openai"), (AnthropicClient, "anthropic", "anthropic")],
)
def test_missing_sdk_raises_helpful_error(client_cls, pkg, extra):
    if importlib.util.find_spec(pkg) is not None:
        pytest.skip(f"{pkg} is installed; the missing-SDK path can't be exercised here")
    with pytest.raises(ImportError, match=rf"pip install 'lyr\[{extra}\]'"):
        client_cls()


def test_fake_client_still_satisfies_the_seam():
    c: LLMClient = FakeClient("hello")
    assert c.complete("anything") == "hello"
