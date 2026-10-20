from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

from research_agent.config import settings


class ResearchRequest(BaseModel):
    query: str = Field(min_length=8, max_length=1000, description="Research question or topic")
    depth: Literal["basic", "advanced"] = "advanced"
    max_results: int = Field(default=settings.max_results, ge=1, le=20)


class Source(BaseModel):
    id: str
    title: str
    url: HttpUrl
    content: str
    score: float | None = None


class ResearchResponse(BaseModel):
    run_id: str
    query: str
    report: str
    sources: list[Source]
    created_at: datetime


class HistoryItem(BaseModel):
    run_id: str
    query: str
    created_at: datetime
    source_count: int
