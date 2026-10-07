from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.sales import FilterParams
from app.services.report_service import create_report

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/export")
def export_sales(
    format: str = "xlsx",
    filters: FilterParams = Depends(),
    db: Session = Depends(get_db),
) -> Response:
    normalized_format = format.lower()
    buffer, filename = create_report(db, normalized_format, filters)
    media_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if normalized_format == "xlsx"
        else "text/csv"
    )
    return Response(
        content=buffer.getvalue(),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
