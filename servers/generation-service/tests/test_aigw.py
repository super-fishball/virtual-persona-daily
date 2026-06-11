import httpx
import pytest
import respx

from app.aigw import AigwClient
from app.errors import (
    CODE_GENERATION_BLOCKED,
    CODE_UPSTREAM_UNAVAILABLE,
    GenError,
)
from app.prompt import CompletionInputs

BASE = "http://gw:8001"
INPUTS = CompletionInputs(
    system_instruction="sys", personality="p", real_time="2026-06-10T10:00:00+08:00"
)


def _client() -> AigwClient:
    return AigwClient(base_url=BASE, timeout=35.0)


@pytest.mark.asyncio
@respx.mock
async def test_success_returns_text() -> None:
    respx.post(f"{BASE}/v1/complete").mock(
        return_value=httpx.Response(200, json={"text": "刚来到这座城市"})
    )
    assert await _client().complete(INPUTS) == "刚来到这座城市"


@pytest.mark.asyncio
@respx.mock
async def test_422_guardrail_maps_502_generation_blocked() -> None:
    respx.post(f"{BASE}/v1/complete").mock(
        return_value=httpx.Response(422, json={"code": "guardrail_blocked", "message": "x"})
    )
    with pytest.raises(GenError) as ei:
        await _client().complete(INPUTS)
    assert ei.value.status_code == 502
    assert ei.value.code == CODE_GENERATION_BLOCKED  # 独立 code（spec §6.3/§9·①）


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize("upstream_status", [400, 500, 502])
async def test_other_codes_map_502_upstream_unavailable(upstream_status: int) -> None:
    respx.post(f"{BASE}/v1/complete").mock(
        return_value=httpx.Response(upstream_status, json={"code": "x", "message": "y"})
    )
    with pytest.raises(GenError) as ei:
        await _client().complete(INPUTS)
    assert ei.value.status_code == 502
    assert ei.value.code == CODE_UPSTREAM_UNAVAILABLE


@pytest.mark.asyncio
@respx.mock
async def test_timeout_maps_502_no_retry() -> None:
    # 超时 → 502；且不重试（spec §6.2，G-1 非幂等）→ 只发一次请求
    route = respx.post(f"{BASE}/v1/complete").mock(side_effect=httpx.ReadTimeout("t"))
    with pytest.raises(GenError) as ei:
        await _client().complete(INPUTS)
    assert ei.value.status_code == 502
    assert ei.value.code == CODE_UPSTREAM_UNAVAILABLE
    assert route.call_count == 1  # 不重试
