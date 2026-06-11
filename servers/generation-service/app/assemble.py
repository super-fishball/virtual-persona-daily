from datetime import datetime, timedelta, timezone

from app.schemas import EventPayload

CN_TZ = timezone(timedelta(hours=8))          # A1 固定 UTC+8（spec §9·⑤）
STATUS_TAG = "初来乍到"                          # A1 无状态机，固定常量
_DEFAULT = timedelta(minutes=60)
_MIN = timedelta(minutes=15)
_MAX = timedelta(hours=4)


def assemble_birth_event(content: str, now: datetime) -> EventPayload:
    start = now
    end = start + _DEFAULT
    # 钳制下/上限
    if end - start < _MIN:
        end = start + _MIN
    if end - start > _MAX:
        end = start + _MAX
    # 午夜边界优先（spec §9·⑤）：≤当日23:59 优先于 15min 下限，罕见场景允许 <15min
    end_of_day = start.replace(hour=23, minute=59, second=0, microsecond=0)
    if end > end_of_day:
        end = end_of_day
    return EventPayload(
        start=start.isoformat(),
        end=end.isoformat(),
        placeRef="home",  # G-2：诞生事件落 home
        content=content,
        statusTag=STATUS_TAG,
    )
