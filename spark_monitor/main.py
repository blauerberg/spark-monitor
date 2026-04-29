from __future__ import annotations

import argparse
import enum
import time

import psutil
import pynvml
from rich.live import Live

from .collectors import collect
from .display import render_all, render_compact_horizontal, render_compact_vertical


class DisplayMode(enum.Enum):
    FULL = "full"
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DGX Spark resource monitor")
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        metavar="SEC",
        help="Refresh interval in seconds (default: 1.0)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--compact-vertical",
        action="store_true",
        help="Show minimal metrics in a compact 3-line layout",
    )
    group.add_argument(
        "--compact-horizontal",
        action="store_true",
        help="Show all metrics in a single line",
    )
    return parser


def main() -> None:
    args = _make_parser().parse_args()

    if args.compact_vertical:
        mode = DisplayMode.VERTICAL
    elif args.compact_horizontal:
        mode = DisplayMode.HORIZONTAL
    else:
        mode = DisplayMode.FULL

    pynvml.nvmlInit()
    # Prime psutil so the first cpu_percent() call returns a real value
    psutil.cpu_percent(interval=None)

    try:
        with Live(auto_refresh=False, screen=True) as live:
            while True:
                cpu, ram, gpu, procs = collect()
                if mode is DisplayMode.VERTICAL:
                    live.update(render_compact_vertical(cpu, ram, gpu))
                elif mode is DisplayMode.HORIZONTAL:
                    live.update(render_compact_horizontal(cpu, ram, gpu))
                else:
                    live.update(render_all(cpu, ram, gpu, procs))
                live.refresh()
                time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        pynvml.nvmlShutdown()


if __name__ == "__main__":
    main()
