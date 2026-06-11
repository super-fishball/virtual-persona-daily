from datetime import datetime

from app.aigw import AigwClient
from app.amap import AmapClient
from app.assemble import CN_TZ, assemble_birth_event
from app.config import Settings
from app.prompt import build_completion_inputs
from app.review import review_personality
from app.schemas import GenerateRequest, GenerateResponse


async def generate_birth(req: GenerateRequest, settings: Settings) -> GenerateResponse:
    # ① 录入审核第二道（命中即 400）
    review_personality(req.personality)

    amap = AmapClient(settings.amap_key, settings.amap_base_url, settings.amap_timeout_seconds)
    # ② 逆地理取城市；精确坐标 req.location 仅此处用，之后不再传递、不入日志
    city, adcode = await amap.regeo_city(req.location)
    # ③ home = 城市代表点；place = 围绕代表点的 POI（不用精确坐标）
    home = await amap.representative_point(adcode)
    place = await amap.poi_place(home)

    # ⑥ start 在前：realTime/start 同一锚点（设定城市时区，A1 固定 UTC+8）
    now = datetime.now(tz=CN_TZ)
    # ④ 性格当数据构建 prompt（realTime 走专属字段）
    inputs = build_completion_inputs(
        personality=req.personality, city=city, place=place, real_time=now.isoformat()
    )
    # ⑤ 经 ai-gateway 调 LLM（仅产 content）
    aigw = AigwClient(settings.aigw_base_url, settings.aigw_timeout_seconds)
    content = await aigw.complete(inputs)
    # ⑥ 机械组装
    birth_event = assemble_birth_event(content=content, now=now)
    return GenerateResponse(city=city, home=home, place=place, birthEvent=birth_event)
