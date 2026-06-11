import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("gen.errors")

# 契约② 对外 code 常量（spec §6.3）
CODE_PERSONALITY_REJECTED = "personality_rejected"
CODE_INVALID_REQUEST = "invalid_request"
CODE_GENERATION_BLOCKED = "generation_blocked"  # 422 guardrail → 502，独立 code
CODE_UPSTREAM_UNAVAILABLE = "upstream_unavailable"


class GenError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


def _body(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(GenError)
    async def _gen(_: Request, exc: GenError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=_body(exc.code, exc.message))

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, __: RequestValidationError) -> JSONResponse:
        # 契约② 请求结构非法 = 400 invalid_request（不回显细节，避免泄露入参/PII）
        return JSONResponse(
            status_code=400,
            content=_body(CODE_INVALID_REQUEST, "request does not match schema"),
        )

    @app.exception_handler(Exception)
    async def _unexpected(_: Request, exc: Exception) -> JSONResponse:
        # F2：catch-all——任何未预期异常（如 ai-gateway 200 缺 text、Settings 缺 key）
        # 一律映 502 upstream_unavailable + Error{}，gen 永不吐契约②（400/502）外响应。
        # 契约② 无 500：A1 内部错先映 502+log（不静默、不回显 prompt/PII）；
        # 「契约② 是否加 500」记后续刀候选，本刀不改契约。
        logger.error("unexpected internal error: %s", type(exc).__name__)
        return JSONResponse(
            status_code=502,
            content=_body(CODE_UPSTREAM_UNAVAILABLE, "internal error"),
        )
