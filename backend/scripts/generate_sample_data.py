from datetime import date, time, timedelta
from pathlib import Path

import pandas as pd

PRODUCTS = {
    "Chocolate Cake": (450, 590),
    "Red Velvet Cake": (350, 480),
    "Croissant": (120, 180),
    "Blueberry Muffin": (180, 260),
    "Chocolate Brownie": (220, 310),
    "Cinnamon Roll": (160, 230),
    "Cheesecake Slice": (280, 390),
    "Garlic Bread": (140, 210),
    "Cupcake": (110, 170),
    "Chocolate Chip Cookie": (85, 130),
}
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TIMES = [time(8, 30), time(9, 30), time(10, 45), time(12, 15), time(14, 30), time(17, 30), time(19, 15)]


def generate_rows(count: int = 500) -> pd.DataFrame:
    rows = []
    start = date(2026, 1, 1)
    for index in range(count):
        product = list(PRODUCTS)[index % len(PRODUCTS)]
        unit_price = PRODUCTS[product][0] + (index % 7) * 10
        sale_date = start + timedelta(days=index % 180)
        rows.append({
            "Sale ID": f"FB-{index + 1:04d}",
            "Item Name": product,
            "Sales Date": sale_date,
            "Day": DAYS[sale_date.weekday()],
            "Price": round(unit_price + (index % 5) * 3, 2),
            "Sell Time": TIMES[(index * 3) % len(TIMES)],
        })
    return pd.DataFrame(rows)


def main() -> None:
    output = Path(__file__).resolve().parents[1] / "sample_sales.xlsx"
    generate_rows().to_excel(output, index=False)
    print(f"Created {output} with {len(generate_rows())} records.")


if __name__ == "__main__":
    main()
