import logging

import httpx

from app.errors import CODE_UPSTREAM_UNAVAILABLE, GenError
from app.schemas import Coordinate, PlacePayload

logger = logging.getLogger("gen.amap")

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
        # F-3：实例级复用一个 AsyncClient（连接池跨本实例多次高德调用复用），由 lifespan
        # 在 app 级创建/关闭（app/main.py），不再每次调用新建（省 TCP/TLS 反复握手）。
        self._client = httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _get(self, path: str, params: dict[str, str]) -> dict:
        params = {**params, "key": self._key}
        try:
            resp = await self._client.get(f"{self._base}{path}", params=params)
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            # from None 断异常链：httpx 异常的 str/repr 含完整请求 URL（精确坐标 + 高德 key），
            # 若随 __cause__ 外泄，off-box 错误捕获(Sentry/APM) / 框架默认异常日志会渲染异常链
            # 而泄漏 PII/凭证（spec §7.2/§7.3，B15）。仅记异常类型名（不含 URL/凭证）保留诊断。
            logger.warning("amap upstream error: %s", type(exc).__name__)
            raise GenError(502, CODE_UPSTREAM_UNAVAILABLE, "amap unavailable") from None
        if str(data.get("status")) != "1":
            raise GenError(502, CODE_UPSTREAM_UNAVAILABLE, "amap returned non-success")
        return data

    async def regeo_city(self, location: Coordinate) -> tuple[str, str]:
        # ② 逆地理；location 仅此处使用，调用后即丢弃（不落库/不入日志）。
        data = await self._get(
            "/v3/geocode/regeo", {"location": f"{location.lng},{location.lat}"}
        )
        comp = data["regeocode"]["addressComponent"]
        # city 回退（spec §9·④"直辖市回退"）：直辖市 regeo 的 `city` 常为空 [] → 回退 `province`
        # （province 即直辖市城市名"上海市"）。不回退 district（区名"黄浦区"非城市）。
        # spec 字面写 district/province，此处只取 province 才正确（F-9）。
        city = _as_str(comp.get("city")) or _as_str(comp.get("province"))
        adcode = _as_str(comp.get("adcode"))
        if not city or len(adcode) != 6:
            raise GenError(502, CODE_UPSTREAM_UNAVAILABLE, "amap regeo incomplete")
        # F1/F-2：regeo adcode 是**区级**（如黄浦 310101），取代表点会落到区中心
        # → 既非"城市代表点"又泄露区级位置(PII)。派生**市级** adcode：
        #   直辖市（省码 11/12/31/50 = 京/津/沪/渝）市级码 = 省码+"0000"（如 310000）；
        #   普通地级市 = 前4位+"00"（如杭州上城 330102 → 330100）。
        # 旧实现一律 [:4]+"00" 对直辖市得市辖区伪码 310100，/v3/config/district 可能
        # 无中心点 → 直辖市用户全 502（F-2；高德对该码的真实解析待集成实测）。
        if adcode[:2] in {"11", "12", "31", "50"}:
            city_adcode = adcode[:2] + "0000"
        else:
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
