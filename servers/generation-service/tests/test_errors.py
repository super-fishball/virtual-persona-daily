from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.errors import GenError, register_exception_handlers


def _client() -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    def boom() -> None:
        raise GenError(status_code=502, code="upstream_unavailable", message="x")

    @app.post("/echo")
    def echo(body: dict) -> dict:  # 触发 422→需被改写成 400
        return body

    @app.get("/unexpected")
    def unexpected() -> None:
        raise KeyError("text")  # 非 GenError 的意外异常（如响应缺字段）

    return TestClient(app, raise_server_exceptions=False)


def test_generror_maps_to_error_body() -> None:
    resp = _client().get("/boom")
    assert resp.status_code == 502
    assert resp.json() == {"code": "upstream_unavailable", "message": "x"}


def test_request_validation_becomes_400_invalid_request() -> None:
    # FastAPI 默认 422；契约② 要求请求结构非法 = 400 invalid_request（spec §6.3）
    resp = _client().post(
        "/echo", content=b"not-json", headers={"content-type": "application/json"}
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "invalid_request"


def test_unexpected_exception_becomes_502(caplog) -> None:
    # F2：catch-all → 502 upstream_unavailable + Error{}；gen 永不吐契约②外响应
    with caplog.at_level("ERROR"):
        resp = _client().get("/unexpected")
    assert resp.status_code == 502
    assert resp.json() == {"code": "upstream_unavailable", "message": "internal error"}
    assert caplog.records  # 内部异常须落日志（不静默）
