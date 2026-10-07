from datetime import date, datetime, time
from typing import Any

import pandas as pd

COLUMN_ALIASES = {
    "sale_id": {"sale id", "sale_id", "invoice id", "invoice_id", "transaction id", "transaction_id"},
    "item_name": {"item name", "item_name", "product", "product_name", "item", "description"},
    "sales_date": {"sales date", "sales_date", "date", "sale date", "sale_date", "transaction date"},
    "day": {"day", "weekday", "sales day"},
    "price": {"price", "sales", "amount", "sale amount", "total", "net sales"},
    "sell_time": {"sell time", "sell_time", "time", "sales time", "sale time"},
    "waste_quantity": {"waste", "wasted quantity", "waste quantity", "spoilage", "damaged quantity"},
    "waste_amount": {"waste amount", "wasted amount", "spoilage amount", "damage amount"},
}


def normalize_column_name(value: object) -> str:
    return " ".join(str(value).strip().lower().split())


def detect_columns(frame: pd.DataFrame) -> tuple[dict[str, str | None], list[str]]:
    normalized = {normalize_column_name(column): column for column in frame.columns}
    mapping: dict[str, str | None] = {}
    for field, aliases in COLUMN_ALIASES.items():
        mapping[field] = next((normalized[alias] for alias in aliases if alias in normalized), None)
    return mapping, list(frame.columns)


def parse_date(value: Any) -> date | None:
    if pd.isna(value):
        return None
    try:
        return pd.to_datetime(value, errors="raise").date()
    except (TypeError, ValueError, OverflowError):
        return None


def parse_time(value: Any) -> time | None:
    if pd.isna(value):
        return None
    try:
        return pd.to_datetime(value, errors="raise").time()
    except (TypeError, ValueError, OverflowError):
        return None


def parse_price(value: Any) -> float | None:
    if pd.isna(value):
        return None
    try:
        parsed = float(value)
        return parsed if parsed >= 0 else None
    except (TypeError, ValueError, OverflowError):
        return None


def validate_frame(frame: pd.DataFrame, mapping: dict[str, str | None]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    required = ("item_name", "sales_date", "price")
    missing_columns = [field for field in required if not mapping.get(field)]
    errors: list[dict[str, Any]] = []
    valid: list[dict[str, Any]] = []
    duplicate_ids = set()
    seen_sale_ids: set[str] = set()

    for index, row in frame.iterrows():
        row_errors: list[str] = []
        row_number = int(index) + 2
        item = row[mapping["item_name"]] if mapping.get("item_name") else None
        sale_date = parse_date(row[mapping["sales_date"]]) if mapping.get("sales_date") else None
        price = parse_price(row[mapping["price"]]) if mapping.get("price") else None
        sale_id = row[mapping["sale_id"]] if mapping.get("sale_id") else None
        if pd.isna(sale_id):
            sale_id = None
        else:
            sale_id = str(sale_id).strip()

        if missing_columns:
            row_errors.extend(f"Missing required column: {field}" for field in missing_columns)
        if pd.isna(item) or not str(item).strip():
            row_errors.append("Missing item name")
        if sale_date is None:
            row_errors.append("Invalid or missing sales date")
        if price is None:
            row_errors.append("Invalid or missing price")
        if sale_id and sale_id in seen_sale_ids:
            duplicate_ids.add(sale_id)
            row_errors.append("Duplicate Sale ID")
        elif sale_id:
            seen_sale_ids.add(sale_id)

        sell_time = None
        if mapping.get("sell_time"):
            sell_time = parse_time(row[mapping["sell_time"]])
            if row[mapping["sell_time"]] is not None and not pd.isna(row[mapping["sell_time"]]) and sell_time is None:
                row_errors.append("Invalid sell time")

        if row_errors:
            errors.append({"row": row_number, "errors": row_errors})
            continue

        day = sale_date.strftime("%A")
        if mapping.get("day"):
            raw_day = row[mapping["day"]]
            if not pd.isna(raw_day) and str(raw_day).strip():
                day = str(raw_day).strip().capitalize()

        record = {
            "sale_id": sale_id,
            "item_name": str(item).strip(),
            "sales_date": sale_date,
            "day": day,
            "price": price,
            "sell_time": sell_time,
            "waste_quantity": None,
            "waste_amount": None,
        }
        if mapping.get("waste_quantity"):
            waste_quantity = parse_price(row[mapping["waste_quantity"]])
            record["waste_quantity"] = waste_quantity
        if mapping.get("waste_amount"):
            waste_amount = parse_price(row[mapping["waste_amount"]])
            record["waste_amount"] = waste_amount
        valid.append(record)

    return valid, errors, len(duplicate_ids)
