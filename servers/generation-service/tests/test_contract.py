from pathlib import Path

import httpx
import pytest
import respx
import yaml
from fastapi.testclient import TestClient
from jsonschema import validate

from app.config import get_settings
from app.main import app

client = TestClient(app)
CONTRACT = Path(__file__).resolve().parents[1] / "contracts" / "api-gen.openapi.yaml"


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _response_schema() -> dict:
    spec = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    components = spec["components"]["schemas"]

    # 内联 $ref 以便 jsonschema 校验（A1 schema 浅，手工解析够用）
    def deref(node):
        if isinstance(node, dict):
            if "$ref" in node:
                return deref(components[node["$ref"].split("/")[-1]])
            return {k: deref(v) for k, v in node.items()}
        if isinstance(node, list):
            return [deref(x) for x in node]
        return node

    return deref(components["GenerateResponse"])


@respx.mock
def test_response_conforms_to_contract(monkeypatch) -> None:
    monkeypatch.setenv("AMAP_KEY", "k")
    amap, gw = "https://restapi.amap.com", "http://localhost:8001"
    respx.get(f"{amap}/v3/geocode/regeo").mock(return_value=httpx.Response(200, json={
        "status": "1", "regeocode": {"addressComponent": {
            "city": "上海市", "province": "上海市", "adcode": "310101", "district": "黄浦区"}}}))
    respx.get(f"{amap}/v3/config/district").mock(return_value=httpx.Response(200, json={
        "status": "1", "districts": [{"center": "121.4726,31.2317", "name": "上海市"}]}))
    respx.get(f"{amap}/v3/place/around").mock(return_value=httpx.Response(200, json={
        "status": "1", "pois": [{"name": "c", "location": "121.50,31.20", "type": "咖啡厅"}]}))
    respx.post(f"{gw}/v1/complete").mock(
        return_value=httpx.Response(200, json={"text": "刚来到这座城市"})
    )

    resp = client.post(
        "/generate",
        json={"personality": "p", "location": {"lng": 121.47, "lat": 31.23}},
    )
    assert resp.status_code == 200
    validate(instance=resp.json(), schema=_response_schema())
