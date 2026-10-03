"""Command-line interface: ``python -m dashboard <command>``.

Thin wrapper around the existing modules:

    python -m dashboard generate [out_dir]          # dashboard.generate_data.generate
    python -m dashboard build [data_dir] [output]   # dashboard.build_static.build
    python -m dashboard summary [data_dir]          # dashboard.kpis.headline
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dashboard import __version__, kpis

SUMMARY_LABELS = [
    ("revenue", "Revenue", "${:,.2f}"),
    ("orders", "Orders", "{:,}"),
    ("avg_order_value", "Avg. order value", "${:,.2f}"),
    ("gross_margin_pct", "Gross margin", "{}%"),
    ("active_customers", "Active customers", "{:,}"),
    ("repeat_customer_pct", "Repeat customers", "{}%"),
    ("return_rate_pct", "Return rate", "{}%"),
    ("on_time_delivery_pct", "On-time delivery", "{}%"),
    ("avg_resolution_hours", "Avg. resolution hours", "{}"),
    ("csat_pct", "CSAT (4-5 stars)", "{}%"),
]


def summary(data_dir: Path) -> str:
    """Return the headline KPIs for the CSVs in ``data_dir`` as aligned text lines."""
    data = kpis.load(data_dir)
    values = {**kpis.headline(data.orders, data.tickets),
              "repeat_customer_pct": kpis.repeat_customer_rate(data.orders)}
    width = max(len(label) for _, label, _ in SUMMARY_LABELS)
    return "\n".join(f"{label:<{width}}  {fmt.format(values[key])}" for key, label, fmt in SUMMARY_LABELS)


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser with the ``generate``, ``build`` and ``summary`` subcommands."""
    parser = argparse.ArgumentParser(prog="python -m dashboard",
                                     description="Business KPI dashboard: demo data, static report and KPI summary.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="command")

    gen = sub.add_parser("generate", help="write 12 months of synthetic demo CSVs")
    gen.add_argument("out_dir", type=Path, nargs="?", default=Path("data"), help="output folder (default: data)")

    build = sub.add_parser("build", help="build the self-contained static HTML report")
    build.add_argument("data_dir", type=Path, nargs="?", default=Path("data"), help="folder with the CSVs (default: data)")
    build.add_argument("output", type=Path, nargs="?", default=Path("docs/index.html"),
                       help="HTML file to write (default: docs/index.html)")

    summ = sub.add_parser("summary", help="print the headline KPIs for a data folder")
    summ.add_argument("data_dir", type=Path, nargs="?", default=Path("data"), help="folder with the CSVs (default: data)")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return the process exit code (0 = success, 1 = missing file or column)."""
    args = build_parser().parse_args(argv)
    try:
        if args.command == "generate":
            from dashboard.generate_data import generate

            for name, path in generate(args.out_dir).items():
                print(f"{name}: {path}")
        elif args.command == "build":
            from dashboard.build_static import build

            print(f"Static dashboard: {build(args.data_dir, args.output)}")
        else:
            print(summary(args.data_dir))
    except FileNotFoundError as exc:
        print(f"error: file not found: {exc.filename}", file=sys.stderr)
        return 1
    except (KeyError, ValueError) as exc:
        print(f"error: unexpected input data ({type(exc).__name__}: {exc})", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
