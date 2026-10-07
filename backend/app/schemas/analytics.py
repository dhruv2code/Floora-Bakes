from datetime import date
from typing import Any

from pydantic import BaseModel


class KPIData(BaseModel):
    total_sales: float
    total_transactions: int
    average_sale: float
    best_seller_by_revenue: str | None
    best_seller_by_quantity: str | None
    best_day: str | None
    peak_time: str | None
    peak_time_start: str | None
    peak_time_end: str | None


class TrendPoint(BaseModel):
    label: str
    revenue: float
    transactions: int


class AnalyticsOverview(BaseModel):
    kpis: KPIData
    sales_trend: list[TrendPoint]
    daily_sales: list[TrendPoint]
    weekly_sales: list[TrendPoint]
    top_items: list[dict[str, Any]]
    sales_share: list[dict[str, Any]]
    time_analysis: list[dict[str, Any]]
    period_analysis: list[dict[str, Any]]
    day_analysis: list[dict[str, Any]]


class WasteAnalytics(BaseModel):
    available: bool
    total_waste_quantity: float
    total_waste_amount: float
    waste_percentage: float
    top_wasted_items: list[dict[str, Any]]
    trend: list[TrendPoint]
    by_day: list[dict[str, Any]]
    by_item: list[dict[str, Any]]
    message: str | None = None
