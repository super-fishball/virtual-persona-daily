from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.errors import GuardrailBlocked, UpstreamUnavailable
from app.models import CompletionRequest, CompletionResponse
from app.service import complete

app = FastAPI(title="ai-gateway")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/complete", response_model=CompletionResponse)
async def complete_endpoint(req: CompletionRequest) -> CompletionResponse:
    return await complete(req)


# C1：请求校验失败 → 400 invalid_request（与 guardrail 的 422 分离；
# 覆盖 FastAPI 默认 422 {detail}，统一为契约③ Error{code,message}）。
@app.exception_handler(RequestValidationError)
async def _validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"code": "invalid_request", "message": "request does not match schema"},
    )


@app.exception_handler(GuardrailBlocked)
async def _guardrail_handler(request: Request, exc: GuardrailBlocked) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"code": "guardrail_blocked", "message": "output blocked by guardrail"},
    )


@app.exception_handler(UpstreamUnavailable)
async def _upstream_handler(request: Request, exc: UpstreamUnavailable) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={"code": "upstream_unavailable", "message": "upstream LLM unavailable"},
    )


# C3：兜底——任何非预期异常 → 500 internal_error，body 绝不回显 prompt/personality
# （message 为固定常量，不含 exc 细节，杜绝 body 经响应/日志泄漏）。
@app.exception_handler(Exception)
async def _internal_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"code": "internal_error", "message": "internal error"},
    )
