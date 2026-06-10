from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from app import deepseek, main
from app.errors import UpstreamUnavailable

client = TestClient(main.app)


def _valid_body() -> dict[str, str]:
    return {
        "systemInstruction": "你是一个虚拟人，请生成日常事件。",
        "personality": "开朗爱冒险",
        "realTime": "2026-06-10T12:00:00+00:00",
    }


def test_complete_contract_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    async def fake_call(
        messages: list[dict[str, str]], *, transport: httpx.BaseTransport | None = None
    ) -> str:
        captured["messages"] = messages
        return "你好，我刚来到这座城市。"

    monkeypatch.setattr(deepseek, "call_deepseek", fake_call)

    resp = client.post("/v1/complete", json=_valid_body())

    # 符合 CompletionResponse schema
    assert resp.status_code == 200
    data = resp.json()
    assert set(data.keys()) == {"text"}
    assert isinstance(data["text"], str) and data["text"]

    # 机械映射断言：system==systemInstruction 原文；性格走数据消息、未并入指令
    msgs = captured["messages"]
    assert msgs[0] == {"role": "system", "content": "你是一个虚拟人，请生成日常事件。"}
    assert "开朗爱冒险" in msgs[1]["content"]
    assert "开朗爱冒险" not in msgs[0]["content"]


def test_complete_upstream_unavailable_returns_502(monkeypatch: pytest.MonkeyPatch) -> None:
    async def boom(
        messages: list[dict[str, str]], *, transport: httpx.BaseTransport | None = None
    ) -> str:
        raise UpstreamUnavailable("down")

    monkeypatch.setattr(deepseek, "call_deepseek", boom)

    resp = client.post("/v1/complete", json=_valid_body())
    assert resp.status_code == 502
    body = resp.json()
    assert set(body.keys()) == {"code", "message"}  # M1：错误体符合契约③ Error
    assert body["code"] == "upstream_unavailable"


def test_complete_invalid_request_returns_400() -> None:
    # C1：缺 personality → 请求校验失败，须 400 invalid_request（非 FastAPI 默认 422 {detail}）
    bad = {"systemInstruction": "你是一个虚拟人", "realTime": "2026-06-10T12:00:00+00:00"}
    resp = client.post("/v1/complete", json=bad)
    assert resp.status_code == 400
    body = resp.json()
    assert set(body.keys()) == {"code", "message"}  # 不是 {detail}
    assert body["code"] == "invalid_request"


def test_complete_unexpected_error_returns_500_without_leak(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # C3：非预期异常 → 500 internal_error，且响应不泄漏 prompt/personality
    secret = "绝密性格标记XYZ"

    async def kaboom(
        messages: list[dict[str, str]], *, transport: httpx.BaseTransport | None = None
    ) -> str:
        raise RuntimeError(f"boom containing {secret}")  # 即便异常夹带秘密……

    monkeypatch.setattr(deepseek, "call_deepseek", kaboom)

    # catch-all（ServerErrorMiddleware）会回 500 并重抛供服务端记日志；
    # 测试关掉 raise_server_exceptions 以观察响应。
    no_raise = TestClient(main.app, raise_server_exceptions=False)
    body_in = dict(_valid_body())
    body_in["personality"] = secret
    resp = no_raise.post("/v1/complete", json=body_in)

    assert resp.status_code == 500
    body = resp.json()
    assert set(body.keys()) == {"code", "message"}
    assert body["code"] == "internal_error"
    assert secret not in resp.text  # 响应体绝不回显 personality
