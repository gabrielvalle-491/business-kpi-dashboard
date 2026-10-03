import subprocess
import sys
from pathlib import Path

import pandas as pd

from dashboard import kpis
from dashboard.__main__ import main as cli_main

ROOT = Path(__file__).resolve().parents[1]


def make_orders(rows):
    columns = ["order_id", "order_date", "customer_id", "region", "channel", "category",
               "revenue", "cost", "status", "promised_days", "delivery_days"]
    df = pd.DataFrame(rows, columns=columns)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


EMPTY_TICKETS = pd.DataFrame({"ticket_id": pd.Series(dtype=int), "topic": pd.Series(dtype=str),
                              "resolution_hours": pd.Series(dtype=float), "csat": pd.Series(dtype=int)})


def test_empty_data_returns_zeros_and_empty_tables():
    orders = make_orders([])
    k = kpis.headline(orders, EMPTY_TICKETS)
    assert set(k.values()) == {0}
    assert kpis.monthly(orders).empty
    assert kpis.by(orders, "region").empty
    assert kpis.repeat_customer_rate(orders) == 0.0
    assert kpis.tickets_by_topic(EMPTY_TICKETS).empty


def test_no_delivered_orders_avoids_division_by_zero():
    orders = make_orders([
        (1, "2026-03-01", "A", "Cuyo", "Website", "Tech", 100.0, 60.0, "Returned", 3, 2),
        (2, "2026-03-02", "B", "NOA", "Website", "Tech", 50.0, 30.0, "Cancelled", 3, 2),
    ])
    k = kpis.headline(orders, EMPTY_TICKETS)
    assert k["revenue"] == 0.0 and k["orders"] == 0
    assert k["avg_order_value"] == 0.0 and k["gross_margin_pct"] == 0.0
    assert k["on_time_delivery_pct"] == 0.0
    assert k["return_rate_pct"] == 50.0  # computed over all orders, not only delivered ones


def test_single_month_has_no_growth_value():
    orders = make_orders([
        (1, "2026-05-02", "A", "Cuyo", "Website", "Tech", 100.0, 60.0, "Delivered", 3, 2),
        (2, "2026-05-28", "A", "Cuyo", "Website", "Tech", 40.0, 20.0, "Delivered", 3, 5),
    ])
    m = kpis.monthly(orders)
    assert len(m) == 1
    assert m["revenue"].iloc[0] == 140.0 and m["customers"].iloc[0] == 1
    assert pd.isna(m["mom_growth_pct"].iloc[0])


def test_filters_are_inclusive_and_combinable():
    orders = make_orders([
        (1, "2026-01-01", "A", "Cuyo", "Website", "Tech", 1.0, 0.0, "Delivered", 3, 2),
        (2, "2026-01-31", "B", "Cuyo", "Marketplace", "Tech", 1.0, 0.0, "Delivered", 3, 2),
        (3, "2026-02-01", "C", "NOA", "Website", "Tech", 1.0, 0.0, "Delivered", 3, 2),
    ])
    january = kpis.filter_orders(orders, start="2026-01-01", end="2026-01-31")
    assert list(january["order_id"]) == [1, 2]
    combined = kpis.filter_orders(orders, regions=["Cuyo"], channels=["Website"])
    assert list(combined["order_id"]) == [1]
    assert len(kpis.filter_orders(orders, regions=[], channels=None)) == 3  # empty selection = no filter


def test_cli_help_and_missing_data_exit_codes(tmp_path, capsys):
    result = subprocess.run([sys.executable, "-m", "dashboard", "--help"], cwd=ROOT,
                            capture_output=True, text=True)
    assert result.returncode == 0
    assert "usage: python -m dashboard" in result.stdout
    assert cli_main(["summary", str(tmp_path)]) == 1
    assert "error: file not found" in capsys.readouterr().err

