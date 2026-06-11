import httpx

from app.errors import CODE_UPSTREAM_UNAVAILABLE, GenError
from app.schemas import Coordinate, PlacePayload

# 固定休闲集（spec §9·④）：按序取首条命中。F3：用 keywords 检索而非类目码——
# 高德类目码（尤其书店）易错，keywords 自描述、稳健；label 同时作对外 type。
_POI_KEYWORDS: list[str] = ["咖啡馆", "公园", "书店"]
_POI_RADIUS = 5000


def _as_str(value: object) -> str:
    # 高德空字段可能返回 [] 而非缺失；统一成字符串。
    return value if isinstance(value, str) and value else ""


class AmapClient:
    def __init__(self, key: str, base_url: str, timeout: float) -> None:
        self._key = key
        self._base = base_url
        self._timeout = timeout

    async def _get(self, path: str, params: dict[str, str]) -> dict:
        params = {**params, "key": self._key}
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.get(f"{self._base}{path}", params=params)
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise GenError(502, CODE_UPSTREAM_UNAVAILABLE, "amap unavailable") from exc
        if str(data.get("status")) != "1":
            raise GenError(502, CODE_UPSTREAM_UNAVAILABLE, "amap returned non-success")
        return data

    async def regeo_city(self, location: Coordinate) -> tuple[str, str]:
        # ② 逆地理；location 仅此处使用，调用后即丢弃（不落库/不入日志）。
        data = await self._get(
            "/v3/geocode/regeo", {"location": f"{location.lng},{location.lat}"}
        )
        comp = data["regeocode"]["addressComponent"]
        city = _as_str(comp.get("city")) or _as_str(comp.get("province"))
        adcode = _as_str(comp.get("adcode"))
        if not city or len(adcode) != 6:
            raise GenError(502, CODE_UPSTREAM_UNAVAILABLE, "amap regeo incomplete")
        # F1：regeo adcode 是**区级**（如黄浦 310101），取代表点会落到区中心
        # → 既非"城市代表点"又泄露区级位置(PII)。派生**市级** adcode = 前4位+"00"。
        city_adcode = adcode[:4] + "00"
        return city, city_adcode

    async def representative_point(self, city_adcode: str) -> Coordinate:
        # ③ 城市代表点 = 市级行政区划中心（不依赖用户精确位置；F1：用市级 adcode）。
        data = await self._get(
            "/v3/config/district", {"keywords": city_adcode, "subdistrict": "0"}
        )
        districts = data.get("districts") or []
        if not districts or not _as_str(districts[0].get("center")):
            raise GenError(502, CODE_UPSTREAM_UNAVAILABLE, "amap district incomplete")
        lng_s, lat_s = districts[0]["center"].split(",")
        return Coordinate(lng=float(lng_s), lat=float(lat_s))

    async def poi_place(self, around: Coordinate) -> PlacePayload:
        # ③ POI 围绕城市代表点（绝不用精确坐标，spec §7.2/§9·④）；按 keywords 集取首条命中。
        for keyword in _POI_KEYWORDS:
            data = await self._get(
                "/v3/place/around",
                {
                    "location": f"{around.lng},{around.lat}",
                    "keywords": keyword,
                    "radius": str(_POI_RADIUS),
                    "offset": "1",
                    "page": "1",
                },
            )
            pois = data.get("pois") or []
            if pois and _as_str(pois[0].get("location")):
                lng_s, lat_s = pois[0]["location"].split(",")
                return PlacePayload(
                    type=keyword, coordinate=Coordinate(lng=float(lng_s), lat=float(lat_s))
                )
        raise GenError(502, CODE_UPSTREAM_UNAVAILABLE, "amap poi not found")
