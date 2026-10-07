from datetime import date, time
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SaleCreate(BaseModel):
    sale_id: str | None = None
    item_name: str
    sales_date: date
    day: str
    price: float = Field(ge=0)
    sell_time: time | None = None
    waste_quantity: float | None = Field(default=None, ge=0)
    waste_amount: float | None = Field(default=None, ge=0)


class SalesResponse(SaleCreate):
    id: int
    created_at: str | None = None
    updated_at: str | None = None


class FilterParams(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    item: str | None = None
    day: str | None = None
    time_period: Literal["all", "morning", "afternoon", "evening", "night"] = "all"
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    search: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @field_validator("day")
    @classmethod
    def validate_day(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.capitalize()
