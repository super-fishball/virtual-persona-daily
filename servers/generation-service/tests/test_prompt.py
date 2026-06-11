from app.prompt import build_completion_inputs
from app.schemas import Coordinate, PlacePayload


def test_system_instruction_excludes_personality() -> None:
    personality = "ABSOLUTELY_UNIQUE_PERSONALITY_TOKEN"
    place = PlacePayload(type="咖啡馆", coordinate=Coordinate(lng=121.5, lat=31.2))
    inputs = build_completion_inputs(
        personality=personality, city="上海市", place=place, real_time="2026-06-10T10:00:00+08:00"
    )
    # 性格当数据：永不进 systemInstruction（spec §6.1/§9·②）
    assert personality not in inputs.system_instruction
    # 性格只走 personality 数据槽
    assert inputs.personality == personality


def test_system_instruction_includes_city_and_place_not_realtime() -> None:
    place = PlacePayload(type="公园", coordinate=Coordinate(lng=1, lat=1))
    inputs = build_completion_inputs(
        personality="p", city="北京市", place=place, real_time="2026-06-10T10:00:00+08:00"
    )
    assert "北京市" in inputs.system_instruction          # city 进指令（系统派生事实）
    assert "公园" in inputs.system_instruction            # place 进指令
    assert "2026-06-10T10:00:00+08:00" not in inputs.system_instruction  # realTime 走专属字段
    assert inputs.real_time == "2026-06-10T10:00:00+08:00"
