from datetime import date, time

from app.models.sales import Sales, UploadBatch
from app.services.analytics_service import calculate_analytics, calculate_waste_analytics
from app.utils.validators import parse_date, parse_price, validate_frame


def test_validation_rejects_invalid_rows():
    import pandas as pd

    frame = pd.DataFrame([
        {"Item Name": "Cake", "Sales Date": "2026-04-01", "Price": "120", "Sell Time": "17:30"},
        {"Item Name": "", "Sales Date": "invalid", "Price": "-5", "Sell Time": "bad"},
    ])
    mapping = {
        "item_name": "Item Name",
        "sales_date": "Sales Date",
        "price": "Price",
        "sell_time": "Sell Time",
    }
    valid, errors, duplicates = validate_frame(frame, mapping)
    assert len(valid) == 1
    assert len(errors) == 1
    assert errors[0]["errors"] == [
        "Missing item name",
        "Invalid or missing sales date",
        "Invalid or missing price",
        "Invalid sell time",
    ]
    assert duplicates == 0


def test_parse_helpers():
    assert parse_date("2026-04-01") == date(2026, 4, 1)
    assert parse_price("-1") is None
    assert parse_price("25.50") == 25.5


def test_analytics_calculations(database):
    batch = UploadBatch(
        filename="analytics.xlsx",
        total_records=3,
        valid_records=3,
        invalid_records=0,
        duplicate_records=0,
        mapping="{}",
    )
    database.add(batch)
    database.flush()
    database.add_all([
        Sales(sale_id="S1", item_name="Cake", sales_date=date(2026, 4, 1), day="Wednesday", price=120, sell_time=time(17, 30), upload_batch_id=batch.id),
        Sales(sale_id="S2", item_name="Cake", sales_date=date(2026, 4, 2), day="Thursday", price=80, sell_time=time(10, 0), upload_batch_id=batch.id),
        Sales(sale_id="S3", item_name="Cookie", sales_date=date(2026, 4, 3), day="Friday", price=20, sell_time=time(17, 0), upload_batch_id=batch.id),
    ])
    database.commit()
    analytics = calculate_analytics(database)
    assert analytics["kpis"]["total_sales"] == 220
    assert analytics["kpis"]["total_transactions"] == 3
    assert analytics["kpis"]["best_seller_by_revenue"] == "Cake"
    assert analytics["kpis"]["peak_time"] == "17:00"


def test_waste_data_is_not_fabricated(database):
    batch = UploadBatch(
        filename="waste.xlsx",
        total_records=1,
        valid_records=1,
        invalid_records=0,
        duplicate_records=0,
        mapping="{}",
    )
    database.add(batch)
    database.flush()
    database.add(Sales(sale_id="S1", item_name="Cake", sales_date=date(2026, 4, 1), day="Wednesday", price=120, upload_batch_id=batch.id))
    database.commit()
    result = calculate_waste_analytics(database)
    assert result["available"] is False
    assert "waste/spoilage data" in result["message"]
