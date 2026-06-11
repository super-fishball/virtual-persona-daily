import logging

from fastapi import Depends, FastAPI

from app.config import Settings, get_settings
from app.errors import register_exception_handlers
from app.schemas import GenerateRequest, GenerateResponse
from app.service import generate_birth

# spec §7.2/§7.3：httpx 默认在 INFO 记完整请求 URL——逆地理 URL 含精确坐标(PII)，
# 各高德请求 URL 含 key(凭证)。gen 收口"精确坐标/凭证不入日志" → 抑制 httpx 请求日志
# （保留 WARNING+ 仍可见真实故障）。test_precise_location_not_logged 守门。
logging.getLogger("httpx").setLevel(logging.WARNING)

app = FastAPI(title="generation-service")
register_exception_handlers(app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse, response_model_by_alias=True)
async def generate(
    req: GenerateRequest, settings: Settings = Depends(get_settings)
) -> GenerateResponse:
    return await generate_birth(req, settings)
