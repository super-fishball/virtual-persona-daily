from app.models import CompletionRequest

# 固定数据槽模板：性格作为数据、现实时间作为上下文，均不并入系统指令。
_DATA_TEMPLATE = "[现实时间] {real_time}\n[性格] {personality}"


def build_messages(req: CompletionRequest) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": req.systemInstruction},
        {
            "role": "user",
            "content": _DATA_TEMPLATE.format(
                real_time=req.realTime.isoformat(),
                personality=req.personality,
            ),
        },
    ]
