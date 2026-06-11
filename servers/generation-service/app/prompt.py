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
    # personality 绝不 format 进 system_instruction（模板只填 city/place_type）。
    system_instruction = _TEMPLATE.format(city=city, place_type=place.type)
    # 防御性自检：性格不得出现在指令构造中（spec §6.1）。用显式 if/raise 而非 assert——
    # assert 在 python -O 下被剥离，安全不变量不可依赖会被优化掉的语句（F-8）。
    # 消息不回显 personality（防泄漏）；命中=代码 bug，经 catch-all 映 502 + 落日志。
    if personality in system_instruction:
        raise RuntimeError("personality must not appear in systemInstruction")
    return CompletionInputs(
        system_instruction=system_instruction, personality=personality, real_time=real_time
    )
