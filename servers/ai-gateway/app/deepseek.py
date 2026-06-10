import asyncio
import os

import httpx

from app.errors import UpstreamUnavailable

_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
_MODEL = "deepseek-chat"
_TIMEOUT = httpx.Timeout(15.0, connect=5.0)  # C4：最坏 ≈2×15+0.5≈30s，已写进契约③
MAX_RETRIES = 1  # 总尝试 = 2；G-1 非幂等，刻意取小
BACKOFF_SECONDS = 0.5


async def call_deepseek(
    messages: list[dict[str, str]],
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        # 不泄露细节；仅作不可用透传。
        raise UpstreamUnavailable("missing DEEPSEEK_API_KEY")

    payload = {"model": _MODEL, "messages": messages}
    headers = {"Authorization": f"Bearer {api_key}"}
    last_error = "upstream failed"

    for attempt in range(MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(
                base_url=_BASE_URL, timeout=_TIMEOUT, transport=transport
            ) as client:
                resp = await client.post("/chat/completions", json=payload, headers=headers)
            if resp.status_code >= 500:
                last_error = f"upstream {resp.status_code}"  # 可重试
            elif resp.status_code >= 400:
                raise UpstreamUnavailable(f"upstream {resp.status_code}")  # 不重试
            else:
                data = resp.json()
                return str(data["choices"][0]["message"]["content"])
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            last_error = type(exc).__name__  # 不记录 body/prompt
        if attempt < MAX_RETRIES:
            await asyncio.sleep(BACKOFF_SECONDS)

    raise UpstreamUnavailable(last_error)
