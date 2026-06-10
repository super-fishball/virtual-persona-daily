import asyncio

import httpx
import pytest

from app import deepseek
from app.errors import UpstreamUnavailable


def test_call_deepseek_returns_content(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": "你好"}}]})

    transport = httpx.MockTransport(handler)
    text = asyncio.run(
        deepseek.call_deepseek([{"role": "system", "content": "x"}], transport=transport)
    )
    assert text == "你好"


def test_call_deepseek_retries_then_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        raise httpx.ReadTimeout("timeout", request=request)

    transport = httpx.MockTransport(handler)
    with pytest.raises(UpstreamUnavailable):
        asyncio.run(
            deepseek.call_deepseek([{"role": "system", "content": "x"}], transport=transport)
        )
    assert calls["n"] == 2  # MAX_RETRIES + 1


def test_call_deepseek_missing_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(UpstreamUnavailable):
        asyncio.run(deepseek.call_deepseek([{"role": "system", "content": "x"}]))
