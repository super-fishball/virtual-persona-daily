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
    assert calls["n"] == deepseek.MAX_RETRIES + 1  # F6：自文档化


def test_call_deepseek_5xx_retries_then_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    # F1：上游 5xx 也走重试，耗尽 → UpstreamUnavailable（5xx 分支独立于 except 路径）
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(503, json={"error": "overloaded"})

    transport = httpx.MockTransport(handler)
    with pytest.raises(UpstreamUnavailable):
        asyncio.run(
            deepseek.call_deepseek([{"role": "system", "content": "x"}], transport=transport)
        )
    assert calls["n"] == deepseek.MAX_RETRIES + 1


def test_call_deepseek_malformed_body_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    # F4：上游 2xx 但响应体畸形（缺 choices）→ UpstreamUnavailable（→502），不外泄异常
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "shape"})

    transport = httpx.MockTransport(handler)
    with pytest.raises(UpstreamUnavailable):
        asyncio.run(
            deepseek.call_deepseek([{"role": "system", "content": "x"}], transport=transport)
        )


def test_call_deepseek_uses_base_url_from_env_per_call(monkeypatch: pytest.MonkeyPatch) -> None:
    # F2：DEEPSEEK_BASE_URL 须 per-call 读（可在进程运行后注入/patch）
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://custom.example.test")
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["host"] = request.url.host
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    transport = httpx.MockTransport(handler)
    asyncio.run(deepseek.call_deepseek([{"role": "system", "content": "x"}], transport=transport))
    assert seen["host"] == "custom.example.test"


def test_call_deepseek_missing_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(UpstreamUnavailable):
        asyncio.run(deepseek.call_deepseek([{"role": "system", "content": "x"}]))
