import pytest
from pydantic import ValidationError

from app.schemas import (
    Coordinate,
    EventPayload,
    GenerateRequest,
    GenerateResponse,
    PlacePayload,
)


def test_request_parses_valid() -> None:
    req = GenerateRequest(personality="温柔的人", location={"lng": 121.47, "lat": 31.23})
    assert req.location.lng == 121.47


def test_request_rejects_extra_field() -> None:
    with pytest.raises(ValidationError):
        GenerateRequest(personality="x", location={"lng": 1, "lat": 1}, evil="y")


def test_request_rejects_out_of_range_coord() -> None:
    with pytest.raises(ValidationError):
        GenerateRequest(personality="x", location={"lng": 999, "lat": 1})


def test_personality_length_bounds() -> None:
    with pytest.raises(ValidationError):
        GenerateRequest(personality="", location={"lng": 1, "lat": 1})
    with pytest.raises(ValidationError):
        GenerateRequest(personality="a" * 501, location={"lng": 1, "lat": 1})


def test_response_serializes() -> None:
    resp = GenerateResponse(
        city="上海市",
        home=Coordinate(lng=121.47, lat=31.23),
        place=PlacePayload(type="咖啡馆", coordinate=Coordinate(lng=121.5, lat=31.2)),
        birthEvent=EventPayload(
            start="2026-06-10T10:00:00+08:00",
            end="2026-06-10T11:00:00+08:00",
            placeRef="home",
            content="刚来到这座城市",
            statusTag="初来乍到",
        ),
    )
    assert resp.model_dump(by_alias=True)["birthEvent"]["placeRef"] == "home"
