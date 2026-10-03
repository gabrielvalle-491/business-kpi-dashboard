"""Generate 12 months of realistic data for a small e-commerce / distribution business.

    python -m dashboard.generate_data data/
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd

PRODUCTS = {
    "Office": [("Paper A4 box", 18.0), ("Toner cartridge", 64.0), ("Ergonomic chair", 210.0)],
    "Tech": [("Wireless mouse", 22.0), ("27in monitor", 245.0), ("USB-C dock", 120.0)],
    "Cleaning": [("Disinfectant 5L", 15.0), ("Paper towels x12", 21.0)],
}
REGIONS = ["Cuyo", "Buenos Aires", "Córdoba", "Patagonia", "NOA"]
CHANNELS = ["Website", "Marketplace", "Sales rep"]


def generate(out_dir: Path, seed: int = 11, start: str = "2025-10-01", months: int = 12) -> dict[str, Path]:
    rng = np.random.default_rng(seed)
    first = pd.Timestamp(start)
    last = first + pd.offsets.MonthBegin(months) - pd.offsets.Day(1)
    days = pd.date_range(first, last, freq="D")  # whole months only
    catalog = [(cat, name, price) for cat, items in PRODUCTS.items() for name, price in items]

    n_customers = 4000
    customers = pd.DataFrame({
        "customer_id": [f"C{i:05d}" for i in range(1, n_customers + 1)],
        "region": rng.choice(REGIONS, n_customers, p=[0.3, 0.3, 0.2, 0.1, 0.1]),
        "segment": rng.choice(["SMB", "Enterprise", "Consumer"], n_customers, p=[0.5, 0.15, 0.35]),
        "signup_date": rng.choice(days[: len(days) // 2], n_customers),
    })
    # A few loyal customers buy often, most buy once (long-tail, like real stores).
    weights = 1 / np.arange(1, n_customers + 1) ** 0.9
    weights /= weights.sum()

    orders = []
    order_id = 10000
    for i, day in enumerate(days):
        growth = 1 + i / len(days) * 0.6  # business grows ~60% over the year
        seasonality = 1 + 0.25 * math.sin(2 * math.pi * (day.dayofyear / 365) - 1.2)
        weekday = 0.6 if day.dayofweek >= 5 else 1.0
        for _ in range(rng.poisson(14 * growth * seasonality * weekday)):
            order_id += 1
            category, product, price = catalog[rng.integers(len(catalog))]
            customer = customers.iloc[rng.choice(n_customers, p=weights)]
            qty = int(rng.integers(1, 8))
            unit_price = round(price * rng.uniform(0.92, 1.08), 2)
            promised = int(rng.choice([2, 3, 5]))
            delivery = max(1, int(rng.normal(promised - 0.3, 1.2)))
            orders.append({
                "order_id": order_id, "order_date": day, "customer_id": customer.customer_id,
                "region": customer.region, "segment": customer.segment, "channel": rng.choice(CHANNELS, p=[0.5, 0.3, 0.2]),
                "category": category, "product": product, "quantity": qty, "unit_price": unit_price,
                "revenue": round(qty * unit_price, 2), "cost": round(qty * price * rng.uniform(0.55, 0.7), 2),
                "status": rng.choice(["Delivered", "Returned", "Cancelled"], p=[0.93, 0.04, 0.03]),
                "promised_days": promised, "delivery_days": delivery,
            })
    orders = pd.DataFrame(orders)

    tickets = pd.DataFrame({
        "ticket_id": range(1, 1501),
        "opened_at": rng.choice(days, 1500),
        "channel": rng.choice(["Email", "WhatsApp", "Phone"], 1500, p=[0.4, 0.45, 0.15]),
        "topic": rng.choice(["Delivery", "Invoice", "Product", "Return"], 1500, p=[0.4, 0.2, 0.25, 0.15]),
        "resolution_hours": np.round(rng.gamma(2.0, 6.0, 1500), 1),
        "csat": rng.choice([1, 2, 3, 4, 5], 1500, p=[0.04, 0.06, 0.15, 0.35, 0.40]),
    }).sort_values("opened_at")

    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {"orders": out_dir / "orders.csv", "customers": out_dir / "customers.csv", "tickets": out_dir / "tickets.csv"}
    orders.to_csv(paths["orders"], index=False)
    customers.to_csv(paths["customers"], index=False)
    tickets.to_csv(paths["tickets"], index=False)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", type=Path, nargs="?", default=Path("data"))
    args = parser.parse_args()
    for name, path in generate(args.out_dir).items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
