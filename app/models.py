from typing import Any, Optional

from pydantic import BaseModel, Field


class Extractor(BaseModel):

    name: str

    json_path: str


class TestRequest(BaseModel):

    method: str

    url: str

    headers: dict[str, str] = Field(
        default_factory=dict
    )

    params: dict[str, Any] = Field(
        default_factory=dict
    )

    body: Optional[Any] = None


class TestCase(BaseModel):

    name: str

    category: str

    description: str

    request: TestRequest

    expected_status_codes: list[int] = Field(
        default_factory=list
    )

    extractors: list[Extractor] = Field(
        default_factory=list
    )


class TestPlan(BaseModel):

    endpoint: str

    method: str

    tests: list[TestCase] = Field(
        default_factory=list
    )


class APIRequest(BaseModel):

    name: str

    method: str

    url: str

    headers: dict[str, str] = Field(
        default_factory=dict
    )

    params: dict[str, Any] = Field(
        default_factory=dict
    )

    body: Optional[Any] = None