"""KPI calculations. Pure pandas, no UI code, so they are easy to test and reuse."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class Data:
    orders: pd.DataFrame
    customers: pd.DataFrame
    tickets: pd.DataFrame


def load(folder: str | Path) -> Data:
    folder = Path(folder)
    return Data(
        orders=pd.read_csv(folder / "orders.csv", parse_dates=["order_date"]),
        customers=pd.read_csv(folder / "customers.csv", parse_dates=["signup_date"]),
        tickets=pd.read_csv(folder / "tickets.csv", parse_dates=["opened_at"]),
    )


def filter_orders(orders: pd.DataFrame, start=None, end=None, regions=None, channels=None) -> pd.DataFrame:
    mask = pd.Series(True, index=orders.index)
    if start is not None:
        mask &= orders["order_date"] >= pd.Timestamp(start)
    if end is not None:
        mask &= orders["order_date"] <= pd.Timestamp(end)
    if regions:
        mask &= orders["region"].isin(regions)
    if channels:
        mask &= orders["channel"].isin(channels)
    return orders[mask]


def completed(orders: pd.DataFrame) -> pd.DataFrame:
    """Revenue KPIs only count delivered orders (returns and cancellations excluded)."""
    return orders[orders["status"] == "Delivered"]


def headline(orders: pd.DataFrame, tickets: pd.DataFrame) -> dict:
    done = completed(orders)
    revenue = float(done["revenue"].sum())
    profit = revenue - float(done["cost"].sum())
    n_orders = done["order_id"].nunique()
    on_time = (done["delivery_days"] <= done["promised_days"]).mean() if len(done) else 0.0
    return {
        "revenue": round(revenue, 2),
        "orders": int(n_orders),
        "avg_order_value": round(revenue / n_orders, 2) if n_orders else 0.0,
        "gross_margin_pct": round(profit / revenue * 100, 1) if revenue else 0.0,
        "active_customers": int(done["customer_id"].nunique()),
        "return_rate_pct": round(float((orders["status"] == "Returned").mean()) * 100, 1) if len(orders) else 0.0,
        "on_time_delivery_pct": round(float(on_time) * 100, 1),
        "avg_resolution_hours": round(float(tickets["resolution_hours"].mean()), 1) if len(tickets) else 0.0,
        "csat_pct": round(float((tickets["csat"] >= 4).mean()) * 100, 1) if len(tickets) else 0.0,
    }


def monthly(orders: pd.DataFrame) -> pd.DataFrame:
    done = completed(orders)
    out = (done.groupby(done["order_date"].dt.to_period("M"))
           .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"), customers=("customer_id", "nunique"))
           .reset_index())
    out["month"] = out["order_date"].dt.to_timestamp()
    out["mom_growth_pct"] = (out["revenue"].pct_change() * 100).round(1)
    return out.drop(columns="order_date")[["month", "revenue", "orders", "customers", "mom_growth_pct"]]


def by(orders: pd.DataFrame, column: str, top: int | None = None) -> pd.DataFrame:
    done = completed(orders)
    out = (done.groupby(column).agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
           .sort_values("revenue", ascending=False).reset_index())
    out["share_pct"] = (out["revenue"] / out["revenue"].sum() * 100).round(1)
    return out.head(top) if top else out


def repeat_customer_rate(orders: pd.DataFrame) -> float:
    """% of customers with more than one delivered order."""
    counts = completed(orders).groupby("customer_id")["order_id"].nunique()
    return round(float((counts > 1).mean()) * 100, 1) if len(counts) else 0.0


def tickets_by_topic(tickets: pd.DataFrame) -> pd.DataFrame:
    return (tickets.groupby("topic")
            .agg(tickets=("ticket_id", "count"), avg_hours=("resolution_hours", "mean"),
                 csat_pct=("csat", lambda s: (s >= 4).mean() * 100))
            .round(1).sort_values("tickets", ascending=False).reset_index())
