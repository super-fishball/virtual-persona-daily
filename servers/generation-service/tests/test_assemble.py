from datetime import datetime, timedelta

from app.assemble import CN_TZ, STATUS_TAG, assemble_birth_event


def _at(h: int, m: int) -> datetime:
    return datetime(2026, 6, 10, h, m, tzinfo=CN_TZ)


def test_normal_duration_60min() -> None:
    ev = assemble_birth_event(content="刚来到这座城市", now=_at(10, 0))
    start = datetime.fromisoformat(ev.start)
    end = datetime.fromisoformat(ev.end)
    assert (end - start) == timedelta(minutes=60)
    assert ev.placeRef == "home"          # G-2
    assert ev.statusTag == STATUS_TAG     # 固定常量
    assert ev.content == "刚来到这座城市"
    assert start.utcoffset() == timedelta(hours=8)  # 固定 UTC+8


def test_end_clamped_not_cross_midnight() -> None:
    # 23:30 + 60min = 次日00:30 → 钳到当日 23:59（不跨午夜）
    ev = assemble_birth_event(content="x", now=_at(23, 30))
    end = datetime.fromisoformat(ev.end)
    assert end <= _at(23, 59)
    assert end.day == 10


def test_midnight_priority_allows_sub_15min() -> None:
    # 23:50 → 「≤当日23:59」优先于 15min 下限；end 可 <15min（spec §9·⑤ 午夜优先级）
    ev = assemble_birth_event(content="x", now=_at(23, 50))
    start = datetime.fromisoformat(ev.start)
    end = datetime.fromisoformat(ev.end)
    assert end == _at(23, 59)
    assert (end - start) < timedelta(minutes=15)
