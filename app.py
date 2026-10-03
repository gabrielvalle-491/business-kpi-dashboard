"""Interactive dashboard.

    streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from dashboard import charts, kpis
from dashboard.generate_data import generate

DATA_DIR = Path(__file__).parent / "data"

st.set_page_config(page_title="Business KPI Dashboard", page_icon="📊", layout="wide")


@st.cache_data
def load_data():
    if not (DATA_DIR / "orders.csv").exists():
        generate(DATA_DIR)
    return kpis.load(DATA_DIR)


data = load_data()
orders, tickets = data.orders, data.tickets

with st.sidebar:
    st.header("Filters")
    min_d, max_d = orders["order_date"].min().date(), orders["order_date"].max().date()
    start, end = st.date_input("Period", (min_d, max_d), min_value=min_d, max_value=max_d)
    regions = st.multiselect("Region", sorted(orders["region"].unique()))
    channels = st.multiselect("Channel", sorted(orders["channel"].unique()))
    st.caption("Data: synthetic demo dataset (12 months).")

view = kpis.filter_orders(orders, start, end, regions, channels)
view_tickets = tickets[(tickets["opened_at"].dt.date >= start) & (tickets["opened_at"].dt.date <= end)]
k = kpis.headline(view, view_tickets)

st.title("📊 Business KPI Dashboard")
st.caption("Sales, customers and operations at a glance")

c = st.columns(4)
c[0].metric("Revenue", f"${k['revenue']:,.0f}")
c[1].metric("Orders", f"{k['orders']:,}")
c[2].metric("Avg. order value", f"${k['avg_order_value']:,.2f}")
c[3].metric("Gross margin", f"{k['gross_margin_pct']}%")
c = st.columns(4)
c[0].metric("Active customers", f"{k['active_customers']:,}")
c[1].metric("Repeat customers", f"{kpis.repeat_customer_rate(view)}%")
c[2].metric("On-time delivery", f"{k['on_time_delivery_pct']}%")
c[3].metric("CSAT (4-5 stars)", f"{k['csat_pct']}%")

st.plotly_chart(charts.revenue_trend(view), use_container_width=True)
left, right = st.columns(2)
left.plotly_chart(charts.revenue_by(view, "category", "Revenue by category"), use_container_width=True)
right.plotly_chart(charts.channel_mix(view), use_container_width=True)
left, right = st.columns(2)
left.plotly_chart(charts.revenue_by(view, "region", "Revenue by region"), use_container_width=True)
right.plotly_chart(charts.delivery_performance(view), use_container_width=True)
st.plotly_chart(charts.support_overview(view_tickets), use_container_width=True)

with st.expander("Top products"):
    st.dataframe(kpis.by(view, "product", top=10), use_container_width=True, hide_index=True)
with st.expander("Monthly table"):
    st.dataframe(kpis.monthly(view), use_container_width=True, hide_index=True)
