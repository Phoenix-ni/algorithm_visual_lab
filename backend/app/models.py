from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TestCase(BaseModel):
    name: str
    value: str
    expected: str | None = None


class AlgorithmInfo(BaseModel):
    id: str
    type: str
    title: str
    difficulty: str
    input_label: str
    input_hint: str
    summary: str
    time_complexity: str
    space_complexity: str
    test_cases: list[TestCase]


class RunRequest(BaseModel):
    input: str = Field(min_length=1)


class Step(BaseModel):
    index: int
    phase: str
    status: str
    message: str
    state: dict[str, Any]
    explain: str


class RunResponse(BaseModel):
    algorithm_id: str
    input: str
    result: dict[str, Any]
    steps: list[Step]
    metrics: dict[str, Any]


class CustomDataCreate(BaseModel):
    algorithm_id: str
    name: str = Field(min_length=1, max_length=50)
    input: str = Field(min_length=1)


class CustomData(CustomDataCreate):
    id: int
    created_at: datetime


class ExportLogRequest(BaseModel):
    algorithm_id: str
    input: str
    result: dict[str, Any] = Field(default_factory=dict)
    steps: list[Step]
    metrics: dict[str, Any] = Field(default_factory=dict)


class ExportLogResponse(BaseModel):
    filename: str
    content: str


class SortCompareRequest(BaseModel):
    input: str = Field(min_length=1)


class CnnRequest(BaseModel):
    sample: str = "digit_3"


class CnnCanvasRequest(BaseModel):
    image: list[list[float]]
