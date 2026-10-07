import json

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.sales import Sales, UploadBatch
from app.schemas.upload import ImportResponse, UploadBatchResponse, UploadPreview
from app.services.excel_service import ExcelService

router = APIRouter(prefix="/api/upload", tags=["Upload"])


@router.post("", response_model=ImportResponse, status_code=status.HTTP_201_CREATED)
async def import_upload(
    file: UploadFile,
    mapping: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> ImportResponse:
    try:
        parsed_mapping = json.loads(mapping) if mapping else {}
        if not parsed_mapping:
            raise ValueError("Column mapping is required.")
        return ExcelService.import_file(db, file, parsed_mapping)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.post("/preview", response_model=UploadPreview)
async def preview_upload(file: UploadFile) -> UploadPreview:
    try:
        return ExcelService.preview(file)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("/history", response_model=list[UploadBatchResponse])
def upload_history(db: Session = Depends(get_db)) -> list[UploadBatchResponse]:
    return [
        UploadBatchResponse.model_validate(batch, from_attributes=True)
        for batch in ExcelService.get_batches(db)
    ]


@router.delete("/batches/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_upload_batch(batch_id: int, db: Session = Depends(get_db)) -> None:
    batch = db.scalar(select(UploadBatch).where(UploadBatch.id == batch_id))
    if not batch:
        raise HTTPException(status_code=404, detail="Upload batch not found.")

    db.execute(delete(Sales).where(Sales.upload_batch_id == batch_id))
    db.delete(batch)
    db.commit()
