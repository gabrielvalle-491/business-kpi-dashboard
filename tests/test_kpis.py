import pandas as pd
import pytest

from dashboard import charts, kpis
from dashboard.build_static import build
from dashboard.generate_data import generate


@pytest.fixture
def tiny_orders():
    return pd.DataFrame({
        "order_id": [1, 2, 3, 4],
        "order_date": pd.to_datetime(["2026-01-05", "2026-01-20", "2026-02-03", "2026-02-10"]),
        "customer_id": ["A", "A", "B", "C"],
        "region": ["Cuyo", "Cuyo", "NOA", "Cuyo"],
        "channel": ["Website", "Website", "Marketplace", "Website"],
        "category": ["Tech", "Office", "Tech", "Tech"],
        "product": ["Mouse", "Paper", "Mouse", "Dock"],
        "revenue": [100.0, 50.0, 200.0, 999.0],
        "cost": [60.0, 30.0, 120.0, 500.0],
        "status": ["Delivered", "Delivered", "Delivered", "Returned"],
        "promised_days": [3, 3, 3, 3],
        "delivery_days": [2, 4, 3, 1],
    })


@pytest.fixture
def tiny_tickets():
    return pd.DataFrame({"ticket_id": [1, 2], "opened_at": pd.to_datetime(["2026-01-01", "2026-01-02"]),
                         "topic": ["Delivery", "Invoice"], "resolution_hours": [4.0, 8.0], "csat": [5, 2]})


def test_headline_excludes_returned_orders(tiny_orders, tiny_tickets):
    k = kpis.headline(tiny_orders, tiny_tickets)
    assert k["revenue"] == 350.0
    assert k["orders"] == 3
    assert k["avg_order_value"] == pytest.approx(116.67)
    assert k["gross_margin_pct"] == 40.0
    assert k["return_rate_pct"] == 25.0
    assert k["on_time_delivery_pct"] == pytest.approx(66.7)
    assert k["avg_resolution_hours"] == 6.0
    assert k["csat_pct"] == 50.0


def test_monthly_growth(tiny_orders):
    m = kpis.monthly(tiny_orders)
    assert list(m["revenue"]) == [150.0, 200.0]
    assert m["mom_growth_pct"].iloc[1] == pytest.approx(33.3)


def test_breakdown_and_repeat_rate(tiny_orders):
    by_cat = kpis.by(tiny_orders, "category")
    assert by_cat.iloc[0]["category"] == "Tech"
    assert by_cat["share_pct"].sum() == pytest.approx(100.0)
    assert kpis.repeat_customer_rate(tiny_orders) == 50.0  # A ordered twice, B once


def test_filters(tiny_orders):
    assert len(kpis.filter_orders(tiny_orders, regions=["NOA"])) == 1
    assert len(kpis.filter_orders(tiny_orders, start="2026-02-01")) == 2


def test_generated_data_and_static_build(tmp_path):
    generate(tmp_path / "data", months=2)
    data = kpis.load(tmp_path / "data")
    assert len(data.orders) > 300
    assert kpis.headline(data.orders, data.tickets)["revenue"] > 0
    for fig in (charts.revenue_trend(data.orders), charts.channel_mix(data.orders),
                charts.delivery_performance(data.orders), charts.support_overview(data.tickets)):
        assert fig.data
    page = build(tmp_path / "data", tmp_path / "index.html").read_text(encoding="utf-8")
    assert "Business KPI Dashboard" in page and "plotly" in page
