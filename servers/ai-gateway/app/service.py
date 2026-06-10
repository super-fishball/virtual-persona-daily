from app import deepseek
from app.errors import GuardrailBlocked
from app.guardrail import scan_output
from app.mapping import build_messages
from app.models import CompletionRequest, CompletionResponse


async def complete(req: CompletionRequest) -> CompletionResponse:
    messages = build_messages(req)
    text = await deepseek.call_deepseek(messages)
    reason = scan_output(text, req.systemInstruction)
    if reason is not None:
        raise GuardrailBlocked(reason)
    return CompletionResponse(text=text)
