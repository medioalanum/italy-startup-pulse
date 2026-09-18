from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class AggregateRecord(BaseModel):
    """A validated regional or sector row from a quarterly report."""

    model_config = ConfigDict(extra="forbid")
    quarter: str = Field(pattern=r"^\d{4}-Q[1-4]$")
    dimension: str = Field(pattern=r"^(region|sector)$")
    name: str = Field(min_length=1)
    startup_count: int = Field(ge=0)
    share_national: float | None = Field(default=None, ge=0, le=100)
    source_reference_date: date | None = None
    classification: str | None = None
