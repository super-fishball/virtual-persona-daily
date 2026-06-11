from datetime import datetime, timedelta, timezone

from app.schemas import EventPayload

CN_TZ = timezone(timedelta(hours=8))          # A1 固定 UTC+8（spec §9·⑤）
STATUS_TAG = "初来乍到"                          # A1 无状态机，固定常量
_DEFAULT = timedelta(minutes=60)


def assemble_birth_event(content: str, now: datetime) -> EventPayload:
    start = now
    # 午夜边界优先（spec §9·⑤）：不跨午夜优先于 15min 下限，罕见场景允许 <15min。
    # 上界取当日「真正末刻」23:59:59.999999（不抹秒）——抹秒会得到早于 start 的上界、
    # 令 start 落在 [23:59:00, 24:00) 时 end<start（F-1 负时长 bug）。min 两侧均 ≥ start，
    # 故 end 必 ≥ start（A1 时长固定 60min，恒在 [15min,4h] 内，无需再钳上下限）。
    end_of_day = start.replace(hour=23, minute=59, second=59, microsecond=999999)
    end = min(start + _DEFAULT, end_of_day)
    return EventPayload(
        start=start.isoformat(),
        end=end.isoformat(),
        placeRef="home",  # G-2：诞生事件落 home
        content=content,
        statusTag=STATUS_TAG,
    )
