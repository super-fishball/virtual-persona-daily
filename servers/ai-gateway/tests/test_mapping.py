from datetime import datetime, timezone

from app.mapping import build_messages
from app.models import CompletionRequest


def test_build_messages_mechanical_mapping() -> None:
    req = CompletionRequest(
        systemInstruction="你是一个虚拟人助手",
        personality="开朗爱冒险",
        realTime=datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc),
    )
    messages = build_messages(req)

    # 系统消息 == systemInstruction 原文（性格未并入指令）
    assert messages[0] == {"role": "system", "content": "你是一个虚拟人助手"}
    # 性格作为数据进用户消息
    assert messages[1]["role"] == "user"
    assert "开朗爱冒险" in messages[1]["content"]
    # 指令/数据物理分离：性格不出现在系统指令里
    assert "开朗爱冒险" not in messages[0]["content"]
    # 现实时间进上下文（用户/数据消息）
    assert "2026-06-10" in messages[1]["content"]
