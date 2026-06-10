from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models import CompletionRequest, CompletionResponse


def test_request_accepts_valid_payload() -> None:
    req = CompletionRequest(
        systemInstruction="你是一个虚拟人",
        personality="开朗爱冒险",
        realTime=datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc),
    )
    assert req.systemInstruction == "你是一个虚拟人"


def test_request_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError):
        CompletionRequest(
            systemInstruction="x",
            personality="y",
            realTime=datetime(2026, 6, 10, tzinfo=timezone.utc),
            extra="nope",  # type: ignore[call-arg]
        )


def test_request_rejects_empty_system_instruction() -> None:
    with pytest.raises(ValidationError):
        CompletionRequest(
            systemInstruction="",
            personality="y",
            realTime=datetime(2026, 6, 10, tzinfo=timezone.utc),
        )


def test_response_shape() -> None:
    assert CompletionResponse(text="hi").model_dump() == {"text": "hi"}
