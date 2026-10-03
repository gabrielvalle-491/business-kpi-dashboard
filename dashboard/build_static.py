"""Build a self-contained HTML version of the dashboard (published with GitHub Pages).

    python -m dashboard.build_static data docs/index.html
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from dashboard import charts, kpis

TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Business KPI Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"></script>
<style>
 body{{font-family:Inter,Arial,sans-serif;margin:0;background:#F4F6F9;color:#1B2631}}
 header{{background:#1F4E79;color:#fff;padding:20px 28px}} header h1{{margin:0;font-size:24px}}
 header p{{margin:4px 0 0;opacity:.8}} main{{max-width:1200px;margin:auto;padding:20px}}
 .kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}}
 .kpi{{background:#fff;border-radius:10px;padding:14px 16px;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
 .kpi span{{display:block;font-size:12px;color:#5D6D7E;text-transform:uppercase;letter-spacing:.04em}}
 .kpi b{{font-size:24px}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:12px;margin-top:12px}}
 .card{{background:#fff;border-radius:10px;padding:6px;box-shadow:0 1px 3px rgba(0,0,0,.08);margin-top:12px}}
 footer{{text-align:center;color:#5D6D7E;font-size:12px;padding:20px}}
 @media(max-width:600px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body>
<header><h1>📊 Business KPI Dashboard</h1><p>{period} · synthetic demo data · built with Python, pandas & Plotly</p></header>
<main><div class="kpis">{kpis}</div>
<div class="card">{trend}</div>
<div class="grid"><div class="card">{category}</div><div class="card">{channel}</div></div>
<div class="grid"><div class="card">{region}</div><div class="card">{delivery}</div></div>
<div class="card">{support}</div></main>
<footer>Generated {generated} · <a href="https://github.com/gabrielvalle-491/business-kpi-dashboard">Source code</a></footer>
</body></html>"""


def build(data_dir: Path, output: Path) -> Path:
    data = kpis.load(data_dir)
    k = kpis.headline(data.orders, data.tickets)
    cards = [
        ("Revenue", f"${k['revenue']:,.0f}"), ("Orders", f"{k['orders']:,}"),
        ("Avg. order value", f"${k['avg_order_value']:,.2f}"), ("Gross margin", f"{k['gross_margin_pct']}%"),
        ("Active customers", f"{k['active_customers']:,}"),
        ("Repeat customers", f"{kpis.repeat_customer_rate(data.orders)}%"),
        ("On-time delivery", f"{k['on_time_delivery_pct']}%"), ("CSAT (4-5★)", f"{k['csat_pct']}%"),
    ]

    def html(fig) -> str:
        return fig.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

    period = f"{data.orders['order_date'].min():%b %Y} – {data.orders['order_date'].max():%b %Y}"
    page = TEMPLATE.format(
        period=period,
        kpis="".join(f'<div class="kpi"><span>{name}</span><b>{value}</b></div>' for name, value in cards),
        trend=html(charts.revenue_trend(data.orders)),
        category=html(charts.revenue_by(data.orders, "category", "Revenue by category")),
        channel=html(charts.channel_mix(data.orders)),
        region=html(charts.revenue_by(data.orders, "region", "Revenue by region")),
        delivery=html(charts.delivery_performance(data.orders)),
        support=html(charts.support_overview(data.tickets)),
        generated=date.today().isoformat(),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", type=Path, nargs="?", default=Path("data"))
    parser.add_argument("output", type=Path, nargs="?", default=Path("docs/index.html"))
    args = parser.parse_args()
    print(f"Static dashboard: {build(args.data_dir, args.output)}")


if __name__ == "__main__":
    main()
