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
    # 23:30 + 60min = 次日00:30 → 钳到当日真正末刻 23:59:59.999999（不跨午夜）
    ev = assemble_birth_event(content="x", now=_at(23, 30))
    start = datetime.fromisoformat(ev.start)
    end = datetime.fromisoformat(ev.end)
    assert end == datetime(2026, 6, 10, 23, 59, 59, 999999, tzinfo=CN_TZ)
    assert end.day == 10                          # 不跨午夜
    assert end > start                            # 非零正时长（F-1：上界不抹秒）


def test_midnight_priority_allows_sub_15min() -> None:
    # 23:50 → 「不跨午夜」优先于 15min 下限；end 钳到当日末刻、可 <15min（spec §9·⑤ 午夜优先级）
    ev = assemble_birth_event(content="x", now=_at(23, 50))
    start = datetime.fromisoformat(ev.start)
    end = datetime.fromisoformat(ev.end)
    assert end == datetime(2026, 6, 10, 23, 59, 59, 999999, tzinfo=CN_TZ)
    assert end >= start
    assert (end - start) < timedelta(minutes=15)


def test_end_not_before_start_in_final_minute_with_seconds() -> None:
    # F-1：now 落当天最后一分钟、带秒（如 23:59:30）。抹秒得到的 23:59:00 会早于 start
    # → 必须保证 end >= start、时长非负（spec §9·⑤ 允许罕见 <15min，但不得 end<start）。
    now = datetime(2026, 6, 10, 23, 59, 30, tzinfo=CN_TZ)
    ev = assemble_birth_event(content="x", now=now)
    start = datetime.fromisoformat(ev.start)
    end = datetime.fromisoformat(ev.end)
    assert end >= start
    assert (end - start) >= timedelta(0)
    assert end.day == 10                          # 仍不跨午夜


def test_end_not_before_start_at_2359_exact() -> None:
    # F-1 边界：start 恰为 23:59:00 整 → end 不得早于 start（旧实现给 end==start，已非负即可）。
    now = datetime(2026, 6, 10, 23, 59, 0, tzinfo=CN_TZ)
    ev = assemble_birth_event(content="x", now=now)
    start = datetime.fromisoformat(ev.start)
    end = datetime.fromisoformat(ev.end)
    assert end >= start
