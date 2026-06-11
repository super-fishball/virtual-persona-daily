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


@pytest.mark.asyncio
@respx.mock
async def test_400_maps_502_and_alert_is_not_silent(caplog) -> None:
    # F-5：契约③ 400 = gen 自造请求 bug → 对外 502 upstream_unavailable + 内部告警**不可静默**
    # （spec §6.3/§9·①）。守住"告警真被记"，否则 gen 侧 bug 会无声无息。
    respx.post(f"{BASE}/v1/complete").mock(
        return_value=httpx.Response(400, json={"code": "invalid_request", "message": "x"})
    )
    with caplog.at_level("ERROR", logger="gen.aigw"):
        with pytest.raises(GenError) as ei:
            await _client().complete(INPUTS)
    assert ei.value.status_code == 502
    assert ei.value.code == CODE_UPSTREAM_UNAVAILABLE
    alerts = [r for r in caplog.records if r.name == "gen.aigw" and r.levelname == "ERROR"]
    assert alerts, "aigw-400（gen 自造请求 bug）必须落 error 告警，不可静默"
    # 告警文案不得回显 payload/personality/PII
    assert "p" not in alerts[0].getMessage().split()  # INPUTS.personality="p" 不入告警


@pytest.mark.asyncio
@respx.mock
async def test_transport_error_does_not_leak_personality_in_exception_chain() -> None:
    # F-5：aigw 传输错误用 `from exc` **保留**诊断链（与 amap `from None` 不对称——
    # aigw URL 为内网 {base}/v1/complete、无 key/坐标；personality 在 POST body、不进 httpx
    # 异常 repr）。回归守门（与 amap 错误路径不泄漏平价）：链上不得出现用户 personality。
    sensitive = "UNIQUE_PII_PERSONALITY_TOKEN_xyz"
    inputs = CompletionInputs(
        system_instruction="sys", personality=sensitive, real_time="2026-06-10T10:00:00+08:00"
    )
    respx.post(f"{BASE}/v1/complete").mock(side_effect=httpx.ConnectError("connection refused"))
    with pytest.raises(GenError) as ei:
        await _client().complete(inputs)
    err = ei.value
    assert err.__cause__ is not None  # 有意保留链（诊断），不同于 amap 的断链
    carried = f"{err} || cause={err.__cause__!r} || ctx={err.__context__!r}"
    assert sensitive not in carried
