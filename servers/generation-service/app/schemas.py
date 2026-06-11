from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")  # 对齐契约 additionalProperties:false


class Coordinate(_Strict):
    lng: float = Field(ge=-180, le=180)
    lat: float = Field(ge=-90, le=90)


class GenerateRequest(_Strict):
    personality: str = Field(min_length=1, max_length=500)
    location: Coordinate  # PII/瞬态：仅逆地理用，用后即丢（spec §7.2）


class PlacePayload(_Strict):
    type: str
    coordinate: Coordinate


class EventPayload(_Strict):
    start: str
    end: str
    placeRef: Literal["home", "place"]
    content: str
    statusTag: str


class GenerateResponse(_Strict):
    city: str
    home: Coordinate
    place: PlacePayload
    birthEvent: EventPayload
