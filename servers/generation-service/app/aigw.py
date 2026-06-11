import logging

import httpx

from app.errors import CODE_GENERATION_BLOCKED, CODE_UPSTREAM_UNAVAILABLE, GenError
from app.prompt import CompletionInputs

logger = logging.getLogger("gen.aigw")


class AigwClient:
    """契约③ 消费方。自身超时 > 30s 且不重试（spec §6.2，G-1 非幂等）。"""

    def __init__(self, base_url: str, timeout: float) -> None:
        self._base = base_url
        # F-3：实例级复用一个 AsyncClient，由 lifespan 在 app 级创建/关闭（app/main.py）。
        self._client = httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def complete(self, inputs: CompletionInputs) -> str:
        payload = {
            "systemInstruction": inputs.system_instruction,
            "personality": inputs.personality,  # 数据槽，分立字段
            "realTime": inputs.real_time,
        }
        try:
            resp = await self._client.post(f"{self._base}/v1/complete", json=payload)
        except httpx.HTTPError as exc:
            # 超时/连接失败 → 502；不重试（一次性请求）
            raise GenError(502, CODE_UPSTREAM_UNAVAILABLE, "ai-gateway unavailable") from exc

        if resp.status_code == 200:
            return str(resp.json()["text"])

        # 错误码映射（spec §6.3）
        if resp.status_code == 422:
            # guardrail 命中：内容问题、不可重试 → 独立 code
            raise GenError(502, CODE_GENERATION_BLOCKED, "generation blocked by guardrail")
        if resp.status_code == 400:
            # gen 自身构造请求 bug → 502 + 内部告警（不静默；不回显 payload/PII）
            logger.error("ai-gateway rejected request as invalid (gen-side defect)")
        raise GenError(502, CODE_UPSTREAM_UNAVAILABLE, "ai-gateway upstream error")
