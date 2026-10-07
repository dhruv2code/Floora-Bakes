from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.sales import Sales
from app.schemas.sales import FilterParams


def apply_filters(db: Session, params: FilterParams):
    query = select(Sales)
    if params.start_date:
        query = query.where(Sales.sales_date >= params.start_date)
    if params.end_date:
        query = query.where(Sales.sales_date <= params.end_date)
    if params.item:
        query = query.where(Sales.item_name.ilike(f"%{params.item}%"))
    if params.day:
        query = query.where(Sales.day.ilike(f"%{params.day}%"))
    if params.time_period != "all":
        boundaries = {"morning": (8, 12), "afternoon": (12, 16), "evening": (16, 20), "night": (20, 24)}
        start_hour, end_hour = boundaries[params.time_period]
        query = query.where(Sales.sell_time.is_not(None)).where(
            or_(Sales.sell_time.hour >= start_hour, Sales.sell_time.hour < end_hour)
            if params.time_period != "night" else Sales.sell_time.hour >= start_hour
        )
    if params.min_price is not None:
        query = query.where(Sales.price >= params.min_price)
    if params.max_price is not None:
        query = query.where(Sales.price <= params.max_price)
    if params.search:
        query = query.where(or_(Sales.item_name.ilike(f"%{params.search}%"), Sales.sale_id.ilike(f"%{params.search}%")))
    return query
