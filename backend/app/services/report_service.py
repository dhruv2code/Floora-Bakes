from io import BytesIO

import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sales import Sales
from app.schemas.sales import FilterParams
from app.services.analytics_service import calculate_analytics
from app.utils.helpers import apply_filters


def create_report(db: Session, report_format: str, filters: FilterParams) -> tuple[BytesIO, str]:
    analytics = calculate_analytics(db, filters)
    query = apply_filters(db, filters).order_by(Sales.sales_date, Sales.id)
    sales = list(db.scalars(query))
    rows = [
        {
            "Sale ID": record.sale_id,
            "Item": record.item_name,
            "Date": record.sales_date.isoformat(),
            "Day": record.day,
            "Price": record.price,
            "Sell Time": record.sell_time.strftime("%H:%M") if record.sell_time else "",
        }
        for record in sales
    ]
    columns = [
        ("Sale ID", "Sale ID"),
        ("Item", "Item"),
        ("Date", "Date"),
        ("Day", "Day"),
        ("Price", "Price"),
        ("Sell Time", "Sell Time"),
    ]
    if report_format == "csv":
        buffer = BytesIO()
        frame = pd.DataFrame(rows, columns=[column for column, _ in columns])
        frame.to_csv(buffer, index=False)
        buffer.seek(0)
        return buffer, "sales-report.csv"

    if report_format == "xlsx":
        buffer = BytesIO()
        summary = pd.DataFrame(
            [
                {
                    "Metric": "Total Sales",
                    "Value": analytics["kpis"]["total_sales"],
                },
                {
                    "Metric": "Transactions",
                    "Value": analytics["kpis"]["total_transactions"],
                },
                {
                    "Metric": "Average Sale",
                    "Value": analytics["kpis"]["average_sale"],
                },
                {
                    "Metric": "Best Selling Item",
                    "Value": analytics["kpis"]["best_seller_by_revenue"],
                },
                {
                    "Metric": "Best Day",
                    "Value": analytics["kpis"]["best_day"],
                },
            ]
        )
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            summary.to_excel(writer, sheet_name="Summary", index=False)
            pd.DataFrame(rows, columns=[column for column, _ in columns]).to_excel(writer, sheet_name="Sales", index=False)
            pd.DataFrame(analytics["top_items"], columns=["Item", "Revenue", "Transactions", "Average Price", "Share"]).to_excel(writer, sheet_name="Top Products", index=False)
            pd.DataFrame(analytics["day_analysis"], columns=["Day", "Revenue", "Transactions", "Average Sale"]).to_excel(writer, sheet_name="Daily Analysis", index=False)
            pd.DataFrame(analytics["time_analysis"], columns=["Hour", "Label", "Revenue", "Transactions"]).to_excel(writer, sheet_name="Time Analysis", index=False)
        buffer.seek(0)
        return buffer, "floora-sales-report.xlsx"

    raise HTTPException(status_code=400, detail="Unsupported report format. Use xlsx or csv.")
