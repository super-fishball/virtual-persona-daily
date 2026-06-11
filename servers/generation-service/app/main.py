import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.aigw import AigwClient
from app.amap import AmapClient
from app.config import get_settings
from app.errors import register_exception_handlers
from app.schemas import GenerateRequest, GenerateResponse
from app.service import generate_birth

# spec §7.2/§7.3：httpx 默认在 INFO 记完整请求 URL——逆地理 URL 含精确坐标(PII)，
# 各高德请求 URL 含 key(凭证)。gen 收口"精确坐标/凭证不入日志" → 抑制 httpx 请求日志
# （保留 WARNING+ 仍可见真实故障）。test_precise_location_not_logged 守门。
logging.getLogger("httpx").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # F-3：app 级创建/关闭下游 client，httpx 连接池跨请求复用（不再每次调用新建）。
    settings = get_settings()
    amap = AmapClient(settings.amap_key, settings.amap_base_url, settings.amap_timeout_seconds)
    aigw = AigwClient(settings.aigw_base_url, settings.aigw_timeout_seconds)
    app.state.amap = amap
    app.state.aigw = aigw
    try:
        yield
    finally:
        await amap.aclose()
        await aigw.aclose()


app = FastAPI(title="generation-service", lifespan=lifespan)
register_exception_handlers(app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest, request: Request) -> GenerateResponse:
    return await generate_birth(req, request.app.state.amap, request.app.state.aigw)
