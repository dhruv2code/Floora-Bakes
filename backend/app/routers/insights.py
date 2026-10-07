from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.sales import FilterParams
from app.services.insight_service import generate_insights, generate_recommendations

router = APIRouter(prefix="/api", tags=["Insights"])


@router.get("/dashboard")
def dashboard(filters: FilterParams = Depends(), db: Session = Depends(get_db)) -> dict:
    from app.services.analytics_service import calculate_analytics
    return calculate_analytics(db, filters)


@router.get("/insights")
def insights(filters: FilterParams = Depends(), db: Session = Depends(get_db)) -> dict:
    return {"items": generate_insights(db, filters)}


@router.get("/recommendations")
def recommendations(filters: FilterParams = Depends(), db: Session = Depends(get_db)) -> dict:
    return {"items": generate_recommendations(db, filters)}
