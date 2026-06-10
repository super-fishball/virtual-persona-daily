from app import deepseek
from app.mapping import build_messages
from app.models import CompletionRequest, CompletionResponse


async def complete(req: CompletionRequest) -> CompletionResponse:
    messages = build_messages(req)
    text = await deepseek.call_deepseek(messages)
    return CompletionResponse(text=text)
