from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    # 高德 key 收口于 gen（spec §7.3）：经环境注入，禁止硬编码。
    amap_key: str
    amap_base_url: str = "https://restapi.amap.com"
    amap_timeout_seconds: float = 5.0

    # ai-gateway 唯一 LLM 入口（契约③）。自身超时 > 30s 且不重试（spec §6.2）。
    aigw_base_url: str = "http://localhost:8001"
    aigw_timeout_seconds: float = 35.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
