from __future__ import annotations

from pydantic import BaseModel


class UseCaseRead(BaseModel):
    domain: str
    category: str
    title: str
    overview: str
    process_flow: list[str]
    systems_involved: list[str]
    roi_benchmarks: dict[str, int]
    value_props: list[str]
    complexity: str
