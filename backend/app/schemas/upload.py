from datetime import datetime
from typing import Any

from pydantic import BaseModel


class UploadPreview(BaseModel):
    filename: str
    total_rows: int
    detected_columns: list[str]
    mapping: dict[str, str | None]
    validation_message: str | None = None


class UploadBatchResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime
    total_records: int
    valid_records: int
    invalid_records: int
    duplicate_records: int
    validation_message: str | None
    mapping: str


class ImportResponse(BaseModel):
    batch_id: int
    imported_records: int
    invalid_records: int
    duplicate_records: int
    message: str
