from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CompletionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    systemInstruction: str = Field(min_length=1)
    personality: str = Field(max_length=4000)
    realTime: datetime


class CompletionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str


class Error(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
