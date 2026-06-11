import httpx
import pytest
import respx

from app.amap import AmapClient
from app.errors import CODE_UPSTREAM_UNAVAILABLE, GenError
from app.schemas import Coordinate

BASE = "https://restapi.amap.com"


@pytest.mark.asyncio
@respx.mock
async def test_regeo_extracts_city_and_city_level_adcode() -> None:
    # regeo 的 adcode 是**区级**（黄浦 310101）；须派生**市级**（前4位+00 → 310100）
    respx.get(f"{BASE}/v3/geocode/regeo").mock(
        return_value=httpx.Response(200, json={
            "status": "1",
            "regeocode": {"addressComponent": {"city": "上海市", "province": "上海市",
                                               "adcode": "310101", "district": "黄浦区"}},
        })
    )
    client = AmapClient(key="k", base_url=BASE, timeout=5.0)
    city, city_adcode = await client.regeo_city(Coordinate(lng=121.47, lat=31.23))
    assert city == "上海市"
    assert city_adcode == "310100"  # 市级，非区级 310101（F1：不泄露区级位置）


@pytest.mark.asyncio
@respx.mock
async def test_regeo_municipality_fallback() -> None:
    # 直辖市 city 为空 → 回退 province；区级 adcode 110101 → 派生市级 110100（spec §9·④/F1）
    respx.get(f"{BASE}/v3/geocode/regeo").mock(
        return_value=httpx.Response(200, json={
            "status": "1",
            "regeocode": {"addressComponent": {"city": [], "province": "北京市",
                                               "adcode": "110101", "district": "东城区"}},
        })
    )
    client = AmapClient(key="k", base_url=BASE, timeout=5.0)
    city, city_adcode = await client.regeo_city(Coordinate(lng=116.4, lat=39.9))
    assert city == "北京市"
    assert city_adcode == "110100"


@pytest.mark.asyncio
@respx.mock
async def test_representative_point_queries_city_level_adcode() -> None:
    route = respx.get(f"{BASE}/v3/config/district").mock(
        return_value=httpx.Response(200, json={
            "status": "1",
            "districts": [{"center": "121.472644,31.231706", "name": "上海市"}],
        })
    )
    client = AmapClient(key="k", base_url=BASE, timeout=5.0)
    point = await client.representative_point("310100")
    assert point.lng == 121.472644 and point.lat == 31.231706
    # 用市级 adcode 查（F1：取市中心而非区中心）
    assert route.calls.last.request.url.params["keywords"] == "310100"


@pytest.mark.asyncio
@respx.mock
async def test_poi_around_representative_point_first_hit() -> None:
    # 围绕代表点检索；按固定 keywords 集顺序取首条命中（咖啡馆 优先）
    route = respx.get(f"{BASE}/v3/place/around").mock(
        return_value=httpx.Response(200, json={
            "status": "1",
            "pois": [{"name": "某咖啡馆", "location": "121.50,31.20", "type": "餐饮服务;咖啡厅"}],
        })
    )
    client = AmapClient(key="k", base_url=BASE, timeout=5.0)
    repr_point = Coordinate(lng=121.4726, lat=31.2317)
    place = await client.poi_place(repr_point)
    assert place.type == "咖啡馆"
    assert place.coordinate.lng == 121.50
    # F3：用 keywords 检索（绕开类目码不确定性），首个 keyword=咖啡馆
    assert route.calls.last.request.url.params["keywords"] == "咖啡馆"
    # 关键 PII 断言：location 入参 = 代表点，绝非精确坐标（spec §7.2/§9·④）
    assert "121.4726,31.2317" in route.calls.last.request.url.params["location"]


@pytest.mark.asyncio
@respx.mock
async def test_amap_failure_maps_502() -> None:
    respx.get(f"{BASE}/v3/geocode/regeo").mock(return_value=httpx.Response(500))
    client = AmapClient(key="k", base_url=BASE, timeout=5.0)
    with pytest.raises(GenError) as ei:
        await client.regeo_city(Coordinate(lng=1, lat=1))
    assert ei.value.status_code == 502
    assert ei.value.code == CODE_UPSTREAM_UNAVAILABLE
