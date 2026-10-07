from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.analytics import AnalyticsOverview, WasteAnalytics
from app.schemas.sales import FilterParams
from app.services.analytics_service import calculate_analytics, calculate_waste_analytics

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def overview(filters: FilterParams = Depends(), db: Session = Depends(get_db)) -> AnalyticsOverview:
    return AnalyticsOverview.model_validate(calculate_analytics(db, filters))


@router.get("/items")
def items(filters: FilterParams = Depends(), db: Session = Depends(get_db)) -> dict:
    return calculate_analytics(db, filters)["top_items"]


@router.get("/days")
def days(filters: FilterParams = Depends(), db: Session = Depends(get_db)) -> dict:
    return calculate_analytics(db, filters)["day_analysis"]


@router.get("/time")
def time_analysis(filters: FilterParams = Depends(), db: Session = Depends(get_db)) -> dict:
    return calculate_analytics(db, filters)["time_analysis"]


@router.get("/share")
def share(filters: FilterParams = Depends(), db: Session = Depends(get_db)) -> dict:
    return calculate_analytics(db, filters)["sales_share"]


@router.get("/waste", response_model=WasteAnalytics)
def waste(filters: FilterParams = Depends(), db: Session = Depends(get_db)) -> WasteAnalytics:
    return WasteAnalytics.model_validate(calculate_waste_analytics(db, filters))
