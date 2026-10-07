from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Sales(Base):
    __tablename__ = "sales"
    __table_args__ = (
        Index("idx_sales_date", "sales_date"),
        Index("idx_sales_item", "item_name"),
        Index("idx_sales_time", "sell_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sale_id: Mapped[str] = mapped_column(String(128), nullable=True, unique=True)
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    sales_date: Mapped[date] = mapped_column(Date, nullable=False)
    day: Mapped[str] = mapped_column(String(20), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    sell_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    waste_quantity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    waste_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    upload_batch_id: Mapped[int] = mapped_column(ForeignKey("upload_batches.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class UploadBatch(Base):
    __tablename__ = "upload_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    total_records: Mapped[int] = mapped_column(Integer, nullable=False)
    valid_records: Mapped[int] = mapped_column(Integer, nullable=False)
    invalid_records: Mapped[int] = mapped_column(Integer, nullable=False)
    duplicate_records: Mapped[int] = mapped_column(Integer, nullable=False)
    validation_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    mapping: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
