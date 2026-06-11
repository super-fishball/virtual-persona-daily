from app.config import Settings


def test_settings_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("AMAP_KEY", "k-123")
    monkeypatch.setenv("AIGW_BASE_URL", "http://gw:8001")
    s = Settings()
    assert s.amap_key == "k-123"
    assert s.aigw_base_url == "http://gw:8001"
    assert s.aigw_timeout_seconds > 30  # spec §6.2：自身超时 > 30s
    assert s.amap_timeout_seconds == 5.0


def test_settings_defaults(monkeypatch) -> None:
    monkeypatch.setenv("AMAP_KEY", "k")
    s = Settings()
    assert s.amap_base_url == "https://restapi.amap.com"
    assert s.aigw_base_url == "http://localhost:8001"
