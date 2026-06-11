from dataclasses import dataclass

from app.schemas import PlacePayload


@dataclass(frozen=True)
class CompletionInputs:
    system_instruction: str
    personality: str
    real_time: str


# 静态任务模板（spec §6.1）：只含任务 + city/place 系统事实；不含用户性格、不含 realTime。
_TEMPLATE = (
    "你是一个虚拟人物日常事件生成器。请基于人物性格，生成 ta 刚来到城市「{city}」的"
    "“诞生”事件的内容文本（中文，1-2 句，仅内容、不要解释、不要时间/地点字段）。"
    "城市内已知一个休闲地点类型：{place_type}。"
)


def build_completion_inputs(
    personality: str, city: str, place: PlacePayload, real_time: str
) -> CompletionInputs:
    # personality 绝不 format 进 system_instruction（断言由测试守住）。
    system_instruction = _TEMPLATE.format(city=city, place_type=place.type)
    assert personality not in system_instruction  # 防御性自检：性格不得入指令
    return CompletionInputs(
        system_instruction=system_instruction, personality=personality, real_time=real_time
    )
