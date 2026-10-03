"""Plotly figures shared by the Streamlit app and the static HTML build."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboard import kpis

PALETTE = ["#1F4E79", "#2E86C1", "#48C9B0", "#F5B041", "#EC7063"]
LAYOUT = dict(template="plotly_white", margin=dict(l=10, r=10, t=50, b=10), font=dict(family="Inter, Arial"))


def revenue_trend(orders: pd.DataFrame) -> go.Figure:
    """Monthly revenue bars with an orders line on a secondary axis."""
    m = kpis.monthly(orders)
    fig = go.Figure()
    fig.add_bar(x=m["month"], y=m["revenue"], name="Revenue", marker_color=PALETTE[0])
    fig.add_scatter(x=m["month"], y=m["orders"], name="Orders", yaxis="y2", mode="lines+markers",
                    line=dict(color=PALETTE[3], width=3))
    fig.update_layout(title="Monthly revenue and orders", yaxis=dict(title="Revenue (USD)"),
                      yaxis2=dict(title="Orders", overlaying="y", side="right", showgrid=False),
                      legend=dict(orientation="h", y=-0.15), **LAYOUT)
    return fig


def revenue_by(orders: pd.DataFrame, column: str, title: str) -> go.Figure:
    """Horizontal bar chart of delivered revenue by ``column``, labelled with share %."""
    data = kpis.by(orders, column)
    fig = px.bar(data, x="revenue", y=column, orientation="h", text="share_pct", title=title,
                 color_discrete_sequence=[PALETTE[1]])
    fig.update_traces(texttemplate="%{text}%", textposition="inside", insidetextanchor="end",
                      textfont=dict(color="white"))
    fig.update_layout(yaxis=dict(autorange="reversed", title=""), xaxis_title="Revenue (USD)", **LAYOUT)
    return fig


def channel_mix(orders: pd.DataFrame) -> go.Figure:
    """Donut chart of delivered revenue by sales channel."""
    data = kpis.by(orders, "channel")
    fig = px.pie(data, names="channel", values="revenue", hole=0.55, title="Revenue by sales channel",
                 color_discrete_sequence=PALETTE)
    fig.update_layout(**LAYOUT)
    return fig


def delivery_performance(orders: pd.DataFrame) -> go.Figure:
    """Monthly on-time delivery % against the 90% target."""
    done = kpis.completed(orders).copy()
    done["month"] = done["order_date"].dt.to_period("M").dt.to_timestamp()
    on_time = (done.assign(on_time=done["delivery_days"] <= done["promised_days"])
               .groupby("month")["on_time"].mean().mul(100).round(1).reset_index())
    fig = px.line(on_time, x="month", y="on_time", markers=True, title="On-time delivery (%)",
                  color_discrete_sequence=[PALETTE[2]])
    fig.add_hline(y=90, line_dash="dash", line_color=PALETTE[4], annotation_text="Target 90%")
    fig.update_layout(yaxis=dict(range=[0, 100], title="%"), xaxis_title="", **LAYOUT)
    return fig


def support_overview(tickets: pd.DataFrame) -> go.Figure:
    """Tickets per topic, coloured by average resolution hours."""
    data = kpis.tickets_by_topic(tickets)
    fig = px.bar(data, x="topic", y="tickets", color="avg_hours", color_continuous_scale="Blues",
                 title="Support tickets by topic (color = avg. resolution hours)")
    fig.update_layout(xaxis_title="", **LAYOUT)
    return fig
