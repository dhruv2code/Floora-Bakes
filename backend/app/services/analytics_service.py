from datetime import date, time
from typing import Any

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.sales import Sales
from app.schemas.sales import FilterParams
from app.utils.helpers import apply_filters

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _query_sales(db: Session, filters: FilterParams | None = None) -> list[Sales]:
    query = apply_filters(db, filters) if filters else select(Sales)
    return list(db.scalars(query.order_by(Sales.sales_date, Sales.id)))


def _frame(records: list[Sales]) -> pd.DataFrame:
    return pd.DataFrame([{
        "sale_id": record.sale_id,
        "item_name": record.item_name,
        "sales_date": record.sales_date,
        "day": record.day,
        "price": record.price,
        "sell_time": record.sell_time,
        "waste_quantity": record.waste_quantity,
        "waste_amount": record.waste_amount,
    } for record in records])


def _safe_group(df: pd.DataFrame, column: str) -> pd.DataFrame:
    return df.groupby(column, dropna=False).agg(revenue=("price", "sum"), transactions=("sale_id", "count"))


def calculate_analytics(db: Session, filters: FilterParams | None = None) -> dict[str, Any]:
    records = _query_sales(db, filters)
    df = _frame(records)
    if df.empty:
        return empty_analytics()

    total_sales = float(df["price"].sum())
    total_transactions = int(len(df))
    average_sale = total_sales / total_transactions
    item_group = _safe_group(df, "item_name").sort_values(["revenue", "transactions"], ascending=False)
    day_group = _safe_group(df, "day").reindex(WEEKDAYS, fill_value=0)
    day_group["revenue"] = day_group["revenue"].astype(float)
    day_group["transactions"] = day_group["transactions"].astype(int)
    day_group["average"] = day_group["revenue"] / day_group["transactions"].replace(0, 1)

    by_hour = df.copy()
    by_hour["hour"] = by_hour["sell_time"].apply(lambda value: value.hour if pd.notna(value) else None)
    hour_group = by_hour.groupby("hour", dropna=False).agg(revenue=("price", "sum"), transactions=("sale_id", "count"))
    hour_group = hour_group.reindex(range(24), fill_value=0)
    hour_group["revenue"] = hour_group["revenue"].astype(float)
    hour_group["transactions"] = hour_group["transactions"].astype(int)

    item_group["share"] = item_group["revenue"] / total_sales * 100
    item_group["average_price"] = item_group["revenue"] / item_group["transactions"]
    top_revenue = item_group.index[0]
    top_quantity = df.groupby("item_name")["sale_id"].count().sort_values(ascending=False).index[0]
    best_day = day_group["revenue"].idxmax()
    peak_hour = hour_group["revenue"].idxmax()
    peak_hour_data = hour_group.loc[peak_hour]
    peak_start = peak_hour
    peak_end = (peak_hour + 1) % 24

    sales_trend = build_trend(df, "sales_date", "D")
    daily_sales = [{"label": row["label"], "revenue": round(float(row["revenue"]), 2), "transactions": int(row["transactions"])} for row in sales_trend]
    weekly_sales = build_trend(df, "sales_date", "W")
    day_analysis = []
    for day in WEEKDAYS:
        row = day_group.loc[day]
        day_analysis.append({
            "day": day,
            "revenue": round(float(row["revenue"]), 2),
            "transactions": int(row["transactions"]),
            "average_sale": round(float(row["average"]), 2),
        })

    time_analysis = []
    for hour, row in hour_group.iterrows():
        if hour is None:
            continue
        time_analysis.append({
            "hour": hour,
            "label": f"{hour:02d}:00",
            "revenue": round(float(row["revenue"]), 2),
            "transactions": int(row["transactions"]),
        })

    period_analysis = build_period_analysis(df)
    return {
        "kpis": {
            "total_sales": round(total_sales, 2),
            "total_transactions": total_transactions,
            "average_sale": round(average_sale, 2),
            "best_seller_by_revenue": str(top_revenue),
            "best_seller_by_quantity": str(top_quantity),
            "best_day": str(best_day),
            "peak_time": f"{peak_hour:02d}:00",
            "peak_time_start": f"{peak_start:02d}:00",
            "peak_time_end": f"{peak_end:02d}:00",
        },
        "sales_trend": sales_trend,
        "daily_sales": daily_sales,
        "weekly_sales": weekly_sales,
        "top_items": item_group.head(10).reset_index().to_dict(orient="records"),
        "sales_share": item_group.reset_index().to_dict(orient="records"),
        "time_analysis": time_analysis,
        "period_analysis": period_analysis,
        "day_analysis": day_analysis,
    }


def build_trend(df: pd.DataFrame, column: str, frequency: str) -> list[dict[str, Any]]:
    trend_frame = df.copy()
    trend_frame[column] = pd.to_datetime(trend_frame[column])
    grouped = trend_frame.groupby(pd.Grouper(freq=frequency, key=column)).agg(
        revenue=("price", "sum"),
        transactions=("sale_id", "count"),
    )
    return [
        {"label": str(index.strftime("%b %d, %Y")), "revenue": round(float(row.revenue), 2), "transactions": int(row.transactions)}
        for index, row in grouped.iterrows()
    ]


def build_period_analysis(df: pd.DataFrame) -> list[dict[str, Any]]:
    period_frames = {
        "Morning": df[df["sell_time"].apply(lambda value: value is not None and 8 <= value.hour < 12)],
        "Afternoon": df[df["sell_time"].apply(lambda value: value is not None and 12 <= value.hour < 16)],
        "Evening": df[df["sell_time"].apply(lambda value: value is not None and 16 <= value.hour < 20)],
        "Night": df[df["sell_time"].apply(lambda value: value is not None and value.hour >= 20)],
    }
    total = float(df["price"].sum())
    result = []
    for name, subset in period_frames.items():
        revenue = float(subset["price"].sum()) if not subset.empty else 0
        result.append({"period": name, "revenue": round(revenue, 2), "share": round(revenue / total * 100, 1) if total else 0, "transactions": int(len(subset))})
    return result


def calculate_waste_analytics(db: Session, filters: FilterParams | None = None) -> dict[str, Any]:
    records = _query_sales(db, filters)
    df = _frame(records)
    waste_columns = [column for column in ("waste_quantity", "waste_amount") if df[column].notna().any()]
    if not waste_columns:
        return {"available": False, "total_waste_quantity": 0, "total_waste_amount": 0, "waste_percentage": 0, "top_wasted_items": [], "trend": [], "by_day": [], "by_item": [], "message": "Waste analysis requires waste/spoilage data. Upload additional columns to analyze waste."}
    quantity = df["waste_quantity"].fillna(0).sum()
    amount = df["waste_amount"].fillna(0).sum()
    total_sales = float(df["price"].sum())
    waste_percentage = amount / total_sales * 100 if total_sales else 0
    by_item = df.groupby("item_name").agg(quantity=("waste_quantity", "sum"), amount=("waste_amount", "sum"), transactions=("sale_id", "count")).sort_values("amount", ascending=False)
    by_day = df.groupby("day").agg(quantity=("waste_quantity", "sum"), amount=("waste_amount", "sum"))
    trend = build_trend(df, "sales_date", "M")
    return {
        "available": True,
        "total_waste_quantity": round(float(quantity), 2),
        "total_waste_amount": round(float(amount), 2),
        "waste_percentage": round(float(waste_percentage), 2),
        "top_wasted_items": by_item.head(10).reset_index().to_dict(orient="records"),
        "trend": trend,
        "by_day": by_day.reset_index().to_dict(orient="records"),
        "by_item": by_item.reset_index().to_dict(orient="records"),
    }


def empty_analytics() -> dict[str, Any]:
    return {
        "kpis": {"total_sales": 0, "total_transactions": 0, "average_sale": 0, "best_seller_by_revenue": None, "best_seller_by_quantity": None, "best_day": None, "peak_time": None, "peak_time_start": None, "peak_time_end": None},
        "sales_trend": [], "daily_sales": [], "weekly_sales": [], "top_items": [], "sales_share": [], "time_analysis": [], "period_analysis": [], "day_analysis": [],
    }
