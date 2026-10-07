from typing import Any

from sqlalchemy.orm import Session

from app.schemas.sales import FilterParams
from app.services.analytics_service import calculate_analytics, calculate_waste_analytics


def generate_insights(db: Session, filters: FilterParams | None = None) -> list[str]:
    analytics = calculate_analytics(db, filters)
    kpis = analytics["kpis"]
    items = analytics["top_items"]
    days = analytics["day_analysis"]
    periods = analytics["period_analysis"]
    insights: list[str] = []
    if not items:
        return ["No sales data is available yet. Upload an Excel file to generate business insights."]

    top_item = items[0]
    share = float(top_item.get("share", 0))
    insights.append(f"{top_item['item_name']} generates the highest revenue and contributes {share:.1f}% of total sales.")

    if len(days) >= 2:
        best = max(days, key=lambda row: float(row["revenue"]))
        lowest = min(days, key=lambda row: float(row["revenue"]))
        average = sum(float(row["revenue"]) for row in days) / len(days)
        if best["revenue"] > average:
            insights.append(f"{best['day']} generates {((best['revenue'] - average) / average * 100):.1f}% more revenue than the average weekday.")
        if lowest["revenue"] > 0:
            insights.append(f"{lowest['day']} is the lowest-performing weekday; consider a targeted promotion or production adjustment.")

    peak = periods[0] if periods else None
    if peak and peak["revenue"] > 0:
        insights.append(f"The strongest sales period is {peak['period'].lower()}, contributing {peak['share']:.1f}% of revenue.")

    quantity_item = next((row for row in items if float(row["transactions"]) > 0), None)
    if quantity_item:
        revenue_item = next((row for row in items if row["item_name"] == quantity_item["item_name"]), None)
        if revenue_item and float(revenue_item["revenue"]) < float(kpis["total_sales"]) * 0.25:
            insights.append(f"{quantity_item['item_name']} has strong transaction volume but a lower revenue contribution; review its pricing and mix.")

    waste = calculate_waste_analytics(db, filters)
    if not waste["available"]:
        insights.append("Waste analysis is unavailable because the uploaded dataset does not contain waste or spoilage data.")
    return insights[:5]


def generate_recommendations(db: Session, filters: FilterParams | None = None) -> list[str]:
    analytics = calculate_analytics(db, filters)
    items = analytics["top_items"]
    days = analytics["day_analysis"]
    periods = analytics["period_analysis"]
    recommendations: list[str] = []
    if not items:
        return []
    top = items[0]
    best_day = max(days, key=lambda row: float(row["revenue"])) if days else None
    lowest_day = min(days, key=lambda row: float(row["revenue"])) if days else None
    peak_period = max(periods, key=lambda row: float(row["revenue"])) if periods else None
    recommendations.append(f"Increase production of {top['item_name']} before {best_day['day'] if best_day else 'the strongest sales day'}, as it is your highest-selling product.")
    if lowest_day and lowest_day["revenue"] < best_day["revenue"] if best_day else False:
        recommendations.append(f"Consider a weekday promotion on {lowest_day['day']} because it has the lowest sales revenue.")
    if peak_period:
        recommendations.append(f"Stock additional inventory for the {peak_period['period'].lower()} period to align with the strongest sales window.")
    low_item = items[-1]
    if float(low_item["revenue"]) < float(analytics["kpis"]["total_sales"]) * 0.1:
        recommendations.append(f"Review low-performing inventory for {low_item['item_name']} and adjust production before the next cycle.")
    return recommendations[:5]
