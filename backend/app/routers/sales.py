from sqlalchemy import func, select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.models.sales import Sales
from app.schemas.sales import FilterParams, SalesResponse
from app.utils.helpers import apply_filters

router = APIRouter(prefix="/api/sales", tags=["Sales"])


@router.get("", response_model=dict)
def list_sales(params: FilterParams = Depends(), db: Session = Depends(get_db)) -> dict:
    query = apply_filters(db, params)
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    rows = db.scalars(query.order_by(Sales.sales_date, Sales.id).offset((params.page - 1) * params.page_size).limit(params.page_size)).all()
    return {"items": [SalesResponse.model_validate(row).model_dump(mode="json") for row in rows], "total": total or 0, "page": params.page, "page_size": params.page_size, "total_pages": (total + params.page_size - 1) // params.page_size if total else 0}


@router.delete("/{sale_id}", status_code=204)
def delete_sale(sale_id: str, db: Session = Depends(get_db)) -> None:
    record = db.scalar(__import__("sqlalchemy").select(Sales).where(Sales.sale_id == sale_id))
    if not record:
        raise HTTPException(404, "Sale not found")
    db.delete(record)
    db.commit()
