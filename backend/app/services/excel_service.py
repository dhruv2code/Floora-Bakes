import json
from io import BytesIO

import pandas as pd
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sales import Sales, UploadBatch
from app.schemas.upload import ImportResponse, UploadPreview
from app.utils.validators import detect_columns, validate_frame


class ExcelService:
    @staticmethod
    def read_file(file: UploadFile) -> pd.DataFrame:
        if file.content_type and file.content_type not in {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"}:
            raise ValueError("Only Excel files (.xlsx or .xls) are supported.")
        if file.filename and not file.filename.lower().endswith((".xlsx", ".xls")):
            raise ValueError("Only Excel files (.xlsx or .xls) are supported.")
        if file.size and file.size > 10 * 1024 * 1024:
            raise ValueError("Excel files must be smaller than 10 MB.")
        return pd.read_excel(BytesIO(file.file.read()))

    @staticmethod
    def preview(file: UploadFile) -> UploadPreview:
        frame = ExcelService.read_file(file)
        mapping, columns = detect_columns(frame)
        return UploadPreview(filename=file.filename or "upload.xlsx", total_rows=len(frame), detected_columns=columns, mapping=mapping)

    @staticmethod
    def import_file(db: Session, file: UploadFile, mapping: dict[str, str | None]) -> ImportResponse:
        frame = ExcelService.read_file(file)
        valid, errors, duplicates = validate_frame(frame, mapping)
        batch = UploadBatch(
            filename=file.filename or "upload.xlsx",
            total_records=len(frame),
            valid_records=len(valid),
            invalid_records=len(errors),
            duplicate_records=duplicates,
            validation_message=f"Imported {len(valid)} valid records.",
            mapping=json.dumps(mapping),
        )
        db.add(batch)
        db.flush()
        if valid:
            db.bulk_save_objects([Sales(**record, upload_batch_id=batch.id) for record in valid])
        db.commit()
        return ImportResponse(
            batch_id=batch.id,
            imported_records=len(valid),
            invalid_records=len(errors),
            duplicate_records=duplicates,
            message=f"Imported {len(valid)} valid records from {len(frame)} rows.",
        )

    @staticmethod
    def get_batches(db: Session) -> list[UploadBatch]:
        return list(db.scalars(select(UploadBatch).order_by(UploadBatch.uploaded_at.desc())))
